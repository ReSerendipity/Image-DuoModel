"""tests/test_llm_usage_metrics.py — LLM 用量聚合与 Token 预算告警（v2.9 评估·LLM 应用工程 P1-2）"""

from __future__ import annotations

import time

import pytest

from app.integrated_app.agent.llm_metrics import LLMUsageTracker
from app.integrated_app.observability.alerts import AlertEngine


def test_tracker_aggregates_today() -> None:
    t = LLMUsageTracker()
    t.record(outcome="ok", latency_s=1.0, prompt_tokens=100, completion_tokens=20, first_token_s=0.2, model="m")
    t.record(outcome="ok", latency_s=3.0, prompt_tokens=10, completion_tokens=5, first_token_s=0.4, model="m")
    t.record(outcome="error", latency_s=0.5)
    s = t.snapshot()
    assert s["calls_ok"] == 2
    assert s["calls_error"] == 1
    assert s["prompt_tokens"] == 110
    assert s["completion_tokens"] == 25
    assert s["tokens_today"] == 135
    assert s["latency_max_s"] == 3.0
    assert s["first_token_avg_s"] == pytest.approx(0.3)
    assert s["model"] == "m"


def test_tracker_snapshot_zero_when_empty() -> None:
    s = LLMUsageTracker().snapshot()
    assert s["calls_ok"] == 0 and s["calls_error"] == 0 and s["tokens_today"] == 0
    assert s["latency_avg_s"] == 0.0 and s["first_token_avg_s"] == 0.0


def test_llm_token_budget_alert_fires_only_when_budget_set() -> None:
    eng = AlertEngine()
    now = time.time()
    alerts = eng.evaluate(
        {
            "llm_tokens_today": 1500.0,
            "llm_token_budget": 1000.0,
            "llm_token_budget_exceeded": True,
            "now": now,
        }
    )
    assert "LLMTokenBudgetExceeded" in [a.name for a in alerts]
    fired = [a for a in alerts if a.name == "LLMTokenBudgetExceeded"][0]
    assert fired.runbook == "docs/runbooks/llm_token_budget.md"
    # 未启用预算（budget=0）不触发
    alerts2 = eng.evaluate(
        {
            "llm_tokens_today": 9999.0,
            "llm_token_budget": 0.0,
            "llm_token_budget_exceeded": False,
            "now": now + 1,
        }
    )
    assert "LLMTokenBudgetExceeded" not in [a.name for a in alerts2]
