"""
agent/llm_client.py — OpenAI 兼容 LLM 客户端(本地 llama.cpp / 云 API 双适配)

设计要点(评估报告第八/九章):
- 提供两条通道:``chat_completion``(非流式,一次性返回)与 ``chat_completion_stream``
  (流式,逐分片产出)。工具调用阶段两条通道都会聚合 ``tool_calls``——llama.cpp 的流式
  ``tool_calls`` 是**分片增量**的,必须按 ``index`` 累积合并,这里统一处理;
- 配置经环境变量注入(.env 由 config._load_dotenv 加载,零 config.yaml 侵入);
- 健康探测:llama-server 是外部进程,不自动拉起,只探测 + 明确降级;
- 降级链(v2.9 评估·LLM 应用工程 P1-1):主端点失败(连接/非 200)按指数退避重试,
  耗尽后自动切换 fallback 端点(fallback_base_url+fallback_model 同时配置才启用);
  流式在「首个 delta 产出之前」失败才允许切换,已流出后失败直接上抛防重复输出;
- api_key 绝不进入 system prompt / 日志。

环境变量:
    IMAGE_MM_AGENT_LLM_BASE_URL   默认 http://127.0.0.1:8081/v1
    IMAGE_MM_AGENT_LLM_API_KEY    默认 not-needed(llama.cpp 不校验)
    IMAGE_MM_AGENT_LLM_MODEL      默认 qwen3.6-35b-a3b
    IMAGE_MM_AGENT_LLM_TEMPERATURE 默认 0.3
    IMAGE_MM_AGENT_LLM_MAX_TOKENS 默认 1024
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

import httpx

from ..observability.metrics import get_metrics
from .llm_metrics import llm_usage

logger = logging.getLogger(__name__)

_SSE_DATA_PREFIX = "data:"


def _record_usage(
    *,
    outcome: str,
    latency_s: float,
    result: dict[str, Any] | None = None,
    first_token_s: float | None = None,
    model: str = "",
) -> None:
    """记录一次 LLM 调用到日聚合与 Prometheus 注册表（观测异常不外抛）。"""
    try:
        usage = (result or {}).get("usage") or {}
        prompt_tokens = int(usage.get("prompt_tokens") or 0)
        completion_tokens = int(usage.get("completion_tokens") or 0)
        llm_usage.record(
            outcome=outcome,
            latency_s=latency_s,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            first_token_s=first_token_s,
            model=model,
        )
        m = get_metrics()
        m.llm_calls_total.inc(1.0, outcome=outcome)
        if prompt_tokens:
            m.llm_prompt_tokens_total.inc(float(prompt_tokens))
        if completion_tokens:
            m.llm_completion_tokens_total.inc(float(completion_tokens))
        if outcome == "ok":
            m.llm_last_latency_seconds.set(max(0.0, float(latency_s)))
            if first_token_s is not None:
                m.llm_first_token_last_seconds.set(max(0.0, float(first_token_s)))
    except Exception:  # noqa: BLE001 - 观测永不阻断业务
        logger.debug("llm usage record failed", exc_info=True)


class LLMError(RuntimeError):
    """LLM 调用失败(网络/协议/非 200)。"""


@dataclass(frozen=True)
class AgentLLMConfig:
    base_url: str = "http://127.0.0.1:8081/v1"
    api_key: str = "not-needed"
    model: str = "qwen3.6-35b-a3b"
    temperature: float = 0.3
    max_tokens: int = 1024
    timeout_s: float = 120.0
    # ── 降级模型链（v2.9 评估·LLM 应用工程 P1-1）──────────────
    # 主端点失败（连接失败/非 200）时按指数退避重试，耗尽后切换降级端点。
    # fallback_base_url 与 fallback_model 同时非空才启用降级链。
    fallback_base_url: str = ""
    fallback_api_key: str = "not-needed"
    fallback_model: str = ""
    # 每个端点尝试 1 + max_retries 次；退避从 retry_base_delay_s 指数增长，
    # 封顶 retry_max_delay_s。
    max_retries: int = 1
    retry_base_delay_s: float = 0.5
    retry_max_delay_s: float = 4.0

    @classmethod
    def from_env(cls) -> AgentLLMConfig:
        return cls(
            base_url=os.environ.get("IMAGE_MM_AGENT_LLM_BASE_URL", cls.base_url),
            api_key=os.environ.get("IMAGE_MM_AGENT_LLM_API_KEY", cls.api_key),
            model=os.environ.get("IMAGE_MM_AGENT_LLM_MODEL", cls.model),
            temperature=float(os.environ.get("IMAGE_MM_AGENT_LLM_TEMPERATURE", cls.temperature)),
            max_tokens=int(os.environ.get("IMAGE_MM_AGENT_LLM_MAX_TOKENS", cls.max_tokens)),
            fallback_base_url=os.environ.get("IMAGE_MM_AGENT_LLM_FALLBACK_BASE_URL", cls.fallback_base_url),
            fallback_api_key=os.environ.get("IMAGE_MM_AGENT_LLM_FALLBACK_API_KEY", cls.fallback_api_key),
            fallback_model=os.environ.get("IMAGE_MM_AGENT_LLM_FALLBACK_MODEL", cls.fallback_model),
            max_retries=int(os.environ.get("IMAGE_MM_AGENT_LLM_MAX_RETRIES", cls.max_retries)),
        )


class LLMClient:
    """OpenAI 兼容 /v1/chat/completions 客户端(非流式,tool 阶段安全)。"""

    def __init__(self, config: AgentLLMConfig | None = None) -> None:
        self.config = config or AgentLLMConfig.from_env()

    def _headers(self, api_key: str | None = None) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {api_key if api_key is not None else self.config.api_key}",
            "Content-Type": "application/json",
        }

    async def chat_completion(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]:
        """非流式 chat.completions（带端点降级链与指数退避重试）。

        调用链：主端点 → 降级端点（若配置 fallback_base_url+fallback_model）；
        每个端点尝试 1 + max_retries 次。全部失败时抛 LLMError（携带最后一次
        错误），由调用方转成 error 事件。
        """
        last_err: Exception | None = None
        endpoints = self._endpoints()
        t0 = time.perf_counter()
        for ep_index, (base_url, api_key, model) in enumerate(endpoints):
            for attempt in range(self.config.max_retries + 1):
                try:
                    result = await self._chat_completion_once(messages, tools, base_url, api_key, model)
                    _record_usage(outcome="ok", latency_s=time.perf_counter() - t0, result=result, model=model)
                    return result
                except LLMError as exc:
                    last_err = exc
                    if attempt < self.config.max_retries:
                        delay = self._backoff_s(attempt)
                        logger.warning(
                            "LLM 调用失败（端点 %d/%s 第 %d 次，%.1fs 后重试）: %s",
                            ep_index + 1,
                            base_url,
                            attempt + 1,
                            delay,
                            exc,
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.warning("LLM 端点 %d/%s 重试上限已达: %s", ep_index + 1, base_url, exc)
        _record_usage(outcome="error", latency_s=time.perf_counter() - t0, model=self.config.model)
        raise LLMError(f"LLM 全部端点不可用（{len(endpoints)} 个）: {last_err}")

    async def _chat_completion_once(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        base_url: str,
        api_key: str,
        model: str,
    ) -> dict[str, Any]:
        """对单个端点执行一次非流式调用（无重试，重试/降级由 chat_completion 编排）。"""
        payload = self._payload(messages, tools, model=model)
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_s) as client:
                resp = await client.post(
                    f"{base_url.rstrip('/')}/chat/completions",
                    json=payload,
                    headers=self._headers(api_key),
                )
        except httpx.HTTPError as exc:
            raise LLMError(f"LLM 请求失败: {exc}") from exc
        if resp.status_code != 200:
            raise LLMError(f"LLM 返回 {resp.status_code}: {resp.text[:200]}")
        return resp.json()

    async def chat_completion_stream(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]
    ) -> AsyncIterator[dict[str, Any]]:
        """流式 chat.completions（带端点降级链）。

        产出两类事件：
        - ``{"type": "delta", "text": <增量文本>}``：仅当分片带 content 时产出；
        - ``{"type": "done", "message": {"content": ..., "tool_calls": [...]}}``：收尾，
          聚合后的完整消息（``tool_calls`` 按 ``index`` 累积合并）。

        失败语义分两段：**首个 delta 产出之前**失败（连接失败/非 200/流建立失败）
        视为端点不可用，指数退避后重试本端点、耗尽后切换降级端点；**已产出 delta
        之后**失败则无法安全重放（重放会重复输出已渲染文本），立即抛出 LLMError
        由调用方兜底（orchestrator 用「泄露命中则整体替换」的策略处理流式文本）。
        """
        last_err: Exception | None = None
        endpoints = self._endpoints()
        t0 = time.perf_counter()
        first_token_s: float | None = None
        done_message: dict[str, Any] | None = None
        for ep_index, (base_url, api_key, model) in enumerate(endpoints):
            for attempt in range(self.config.max_retries + 1):
                emitted = False
                try:
                    async for event in self._stream_once(messages, tools, base_url, api_key, model):
                        if event.get("type") == "delta":
                            if first_token_s is None:
                                first_token_s = time.perf_counter() - t0
                            emitted = True
                        elif event.get("type") == "done":
                            done_message = event.get("message") or {}
                        yield event
                    _record_usage(
                        outcome="ok",
                        latency_s=time.perf_counter() - t0,
                        result={"usage": (done_message or {}).get("usage")},
                        first_token_s=first_token_s,
                        model=model,
                    )
                    return
                except LLMError as exc:
                    last_err = exc
                    if emitted:
                        # 已有增量流出：重放会重复输出，直接上抛
                        raise
                    if attempt < self.config.max_retries:
                        delay = self._backoff_s(attempt)
                        logger.warning(
                            "LLM 流式连接失败（端点 %d/%s 第 %d 次，%.1fs 后重试）: %s",
                            ep_index + 1,
                            base_url,
                            attempt + 1,
                            delay,
                            exc,
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.warning("LLM 流式端点 %d/%s 重试上限已达: %s", ep_index + 1, base_url, exc)
        _record_usage(
            outcome="error",
            latency_s=time.perf_counter() - t0,
            first_token_s=first_token_s,
            model=self.config.model,
        )
        raise LLMError(f"LLM 全部端点不可用（{len(endpoints)} 个）: {last_err}")

    async def _stream_once(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        base_url: str,
        api_key: str,
        model: str,
    ) -> AsyncIterator[dict[str, Any]]:
        """对单个端点执行一次流式调用（无重试，重试/降级由 chat_completion_stream 编排）。"""
        payload = self._payload(messages, tools, model=model)
        payload["stream"] = True
        content_parts: list[str] = []
        tool_calls: dict[int, dict[str, Any]] = {}
        usage: dict[str, Any] | None = None

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_s) as client:
                async with client.stream(
                    "POST",
                    f"{base_url.rstrip('/')}/chat/completions",
                    json=payload,
                    headers=self._headers(api_key),
                ) as resp:
                    if resp.status_code != 200:
                        body = (await resp.aread()).decode("utf-8", errors="replace")
                        raise LLMError(f"LLM 返回 {resp.status_code}: {body[:200]}")
                    async for line in resp.aiter_lines():
                        chunk = self._parse_sse_line(line)
                        if chunk is None:
                            continue
                        if isinstance(chunk.get("usage"), dict):
                            usage = chunk["usage"]
                        for choice in chunk.get("choices") or []:
                            delta = choice.get("delta") or {}
                            text = delta.get("content")
                            if text:
                                content_parts.append(str(text))
                                yield {"type": "delta", "text": str(text)}
                            self._accumulate_tool_calls(tool_calls, delta.get("tool_calls"))
        except httpx.HTTPError as exc:
            raise LLMError(f"LLM 流式请求失败: {exc}") from exc

        message: dict[str, Any] = {"content": "".join(content_parts)}
        if tool_calls:
            message["tool_calls"] = [tool_calls[i] for i in sorted(tool_calls)]
        if usage:
            message["usage"] = usage
        yield {"type": "done", "message": message}

    # ── 内部工具 ────────────────────────────────────────────
    def _payload(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        model: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model or self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        if tools:
            payload["tools"] = tools
        return payload

    def _endpoints(self) -> list[tuple[str, str, str]]:
        """调用链：主端点优先，其后是配置完整的降级端点（fallback_base_url+fallback_model）。"""
        chain = [(self.config.base_url, self.config.api_key, self.config.model)]
        if self.config.fallback_base_url and self.config.fallback_model:
            chain.append((self.config.fallback_base_url, self.config.fallback_api_key, self.config.fallback_model))
        return chain

    @property
    def fallback_configured(self) -> bool:
        """是否配置了降级端点（供 /api/agent/health 与 UI 展示）。"""
        return bool(self.config.fallback_base_url and self.config.fallback_model)

    def _backoff_s(self, attempt: int) -> float:
        """第 attempt 次重试（0 起）前的退避秒数：指数增长，封顶 retry_max_delay_s。"""
        return min(self.config.retry_base_delay_s * (2**attempt), self.config.retry_max_delay_s)

    @staticmethod
    def _parse_sse_line(line: str) -> dict[str, Any] | None:
        """解析一行 SSE；非 data 行/心跳/[DONE]/坏 JSON 一律返回 None。"""
        line = (line or "").strip()
        if not line or not line.startswith(_SSE_DATA_PREFIX):
            return None
        raw = line[len(_SSE_DATA_PREFIX) :].strip()
        if not raw or raw == "[DONE]":
            return None
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            logger.debug("忽略无法解析的流式分片: %s", raw[:120])
            return None
        return parsed if isinstance(parsed, dict) else None

    @staticmethod
    def _accumulate_tool_calls(acc: dict[int, dict[str, Any]], fragments: Any) -> None:
        """按 index 合并流式 tool_calls 分片。

        OpenAI 兼容协议的流式 tool_calls 形如
        ``[{"index":0,"id":"call_1","function":{"name":"gen","arguments":"{\\"a\\":"}}]``，
        name 可能只来一次、arguments 是逐段拼接的字符串；缺失 index 时按 0 处理。
        """
        if not isinstance(fragments, list):
            return
        for frag in fragments:
            if not isinstance(frag, dict):
                continue
            try:
                idx = int(frag.get("index", 0))
            except (TypeError, ValueError):
                idx = 0
            slot = acc.setdefault(
                idx,
                {"id": "", "type": "function", "function": {"name": "", "arguments": ""}},
            )
            if frag.get("id"):
                slot["id"] = str(frag["id"])
            if frag.get("type"):
                slot["type"] = str(frag["type"])
            fn = frag.get("function")
            if isinstance(fn, dict):
                if fn.get("name"):
                    slot["function"]["name"] = str(fn["name"])
                if fn.get("arguments"):
                    slot["function"]["arguments"] += str(fn["arguments"])

    async def health_check(self, base_url: str | None = None, api_key: str | None = None) -> bool:
        """GET {base_url}/models 探测;任何异常返回 False(不抛出)。

        缺省探测主端点；传入降级端点参数可探测降级链（/api/agent/health 用）。
        """
        target = base_url or self.config.base_url
        key = api_key if api_key is not None else self.config.api_key
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"{target.rstrip('/')}/models",
                    headers=self._headers(key),
                )
            return resp.status_code == 200
        except httpx.HTTPError:
            return False
