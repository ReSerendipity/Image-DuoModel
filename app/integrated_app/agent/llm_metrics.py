"""agent/llm_metrics.py — LLM 用量/延迟日聚合（v2.9 评估·LLM 应用工程 P1-2）

进程内、零第三方依赖的 LLM 调用聚合：按自然日累计 ok/error 次数、
prompt/completion Token、整轮与首字延迟。供两处消费：
- Prometheus 注册表（llm_calls_total / llm_*_tokens_total / llm_*_last_seconds，
  由 agent/llm_client.py 在记录时同步递增）；
- finops 预算告警（AlertEngine 规则 LLMTokenBudgetExceeded 读 snapshot()
  的 tokens_today 对比 finops.budget_llm_tokens_per_day）。

Token 口径：只统计端点在响应 usage 中上报的值（OpenAI 兼容 chat.completions；
流式以 done 帧携带的 usage 为准）。端点不上报 usage 时记 0——不做字符数估算，
避免「模糊数值」进入度量体系。
"""

from __future__ import annotations

import threading
import time
from typing import Any


class LLMUsageTracker:
    """按自然日键聚合 LLM 调用量与 Token 用量（进程内，重启即清零）。"""

    _DAY_FIELDS = (
        "calls_ok",
        "calls_error",
        "prompt_tokens",
        "completion_tokens",
        "latency_sum_s",
        "latency_max_s",
        "first_token_sum_s",
        "first_token_n",
        "last_latency_s",
        "last_first_token_s",
    )

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._days: dict[str, dict[str, Any]] = {}

    def record(
        self,
        *,
        outcome: str,
        latency_s: float,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        first_token_s: float | None = None,
        model: str = "",
    ) -> None:
        day = time.strftime("%Y-%m-%d", time.localtime())
        with self._lock:
            d = self._days.setdefault(day, {k: 0.0 for k in self._DAY_FIELDS})
            d["model"] = model or str(d.get("model", ""))
            if outcome == "ok":
                d["calls_ok"] = float(d.get("calls_ok", 0.0)) + 1.0
            else:
                d["calls_error"] = float(d.get("calls_error", 0.0)) + 1.0
            lat = max(0.0, float(latency_s or 0.0))
            d["prompt_tokens"] = float(d.get("prompt_tokens", 0.0)) + max(0, int(prompt_tokens or 0))
            d["completion_tokens"] = float(d.get("completion_tokens", 0.0)) + max(0, int(completion_tokens or 0))
            d["latency_sum_s"] = float(d.get("latency_sum_s", 0.0)) + lat
            d["latency_max_s"] = max(float(d.get("latency_max_s", 0.0)), lat)
            d["last_latency_s"] = lat
            if first_token_s is not None:
                ft = max(0.0, float(first_token_s))
                d["first_token_sum_s"] = float(d.get("first_token_sum_s", 0.0)) + ft
                d["first_token_n"] = float(d.get("first_token_n", 0.0)) + 1.0
                d["last_first_token_s"] = ft

    def snapshot(self) -> dict[str, Any]:
        """今日聚合快照；无记录时返回零值结构（字段稳定，供告警与看板直接消费）。"""
        day = time.strftime("%Y-%m-%d", time.localtime())
        with self._lock:
            d = dict(self._days.get(day) or {})
        ok = float(d.get("calls_ok", 0.0))
        n_ft = float(d.get("first_token_n", 0.0))
        prompt = int(d.get("prompt_tokens", 0.0))
        completion = int(d.get("completion_tokens", 0.0))
        return {
            "date": day,
            "calls_ok": int(ok),
            "calls_error": int(float(d.get("calls_error", 0.0))),
            "prompt_tokens": prompt,
            "completion_tokens": completion,
            "tokens_today": prompt + completion,
            "latency_avg_s": round(float(d.get("latency_sum_s", 0.0)) / ok, 3) if ok else 0.0,
            "latency_max_s": round(float(d.get("latency_max_s", 0.0)), 3),
            "first_token_avg_s": round(float(d.get("first_token_sum_s", 0.0)) / n_ft, 3) if n_ft else 0.0,
            "last_latency_s": round(float(d.get("last_latency_s", 0.0)), 3),
            "last_first_token_s": round(float(d.get("last_first_token_s", 0.0)), 3),
            "model": str(d.get("model", "")),
        }


llm_usage = LLMUsageTracker()
