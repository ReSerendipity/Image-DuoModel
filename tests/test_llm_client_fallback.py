"""tests/test_llm_client_fallback.py — LLM 降级链与指数退避（v2.9 评估·LLM 应用工程 P1-1）"""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from app.integrated_app.agent import llm_client as llm_mod
from app.integrated_app.agent.llm_client import AgentLLMConfig, LLMClient, LLMError

PRIMARY = "http://127.0.0.1:8081/v1"
FALLBACK = "http://127.0.0.1:9999/v1"


def _patch_transport(monkeypatch: pytest.MonkeyPatch, handler) -> None:
    real_client = httpx.AsyncClient

    def factory(*args: Any, **kwargs: Any) -> Any:
        kwargs["transport"] = httpx.MockTransport(handler)
        return real_client(*args, **kwargs)

    monkeypatch.setattr(llm_mod.httpx, "AsyncClient", factory)


def _cfg(**overrides: Any) -> AgentLLMConfig:
    base: dict[str, Any] = {
        "base_url": PRIMARY,
        "fallback_base_url": FALLBACK,
        "fallback_model": "fallback-model",
        "max_retries": 0,
        "retry_base_delay_s": 0.0,
    }
    base.update(overrides)
    return AgentLLMConfig(**base)


async def test_non_stream_falls_back_when_primary_500(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        if ":8081" in str(request.url):
            return httpx.Response(500, content=b"boom")
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    _patch_transport(monkeypatch, handler)
    client = LLMClient(_cfg())
    result = await client.chat_completion([{"role": "user", "content": "hi"}], tools=[])
    assert result["choices"][0]["message"]["content"] == "ok"
    assert len(calls) == 2
    assert ":9999" in calls[1]


async def test_stream_falls_back_before_first_delta(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if ":8081" in str(request.url):
            return httpx.Response(500, content=b"boom")
        body = (
            'data: {"choices":[{"delta":{"content":"hel"}}]}\n\n'
            'data: {"choices":[{"delta":{"content":"lo"}}]}\n\n'
            "data: [DONE]\n\n"
        )
        return httpx.Response(200, content=body)

    _patch_transport(monkeypatch, handler)
    client = LLMClient(_cfg())
    events = [e async for e in client.chat_completion_stream([{"role": "user", "content": "hi"}], tools=[])]
    deltas = [e for e in events if e["type"] == "delta"]
    assert [d["text"] for d in deltas] == ["hel", "lo"]
    assert events[-1]["type"] == "done"


async def test_all_endpoints_down_raises_llm_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, content=b"down")

    _patch_transport(monkeypatch, handler)
    client = LLMClient(_cfg())
    with pytest.raises(LLMError, match="全部端点不可用"):
        await client.chat_completion([{"role": "user", "content": "hi"}], tools=[])


async def test_retry_backoff_then_success(monkeypatch: pytest.MonkeyPatch) -> None:
    state = {"n": 0}
    sleeps: list[float] = []

    async def fake_sleep(delay: float) -> None:
        sleeps.append(delay)

    monkeypatch.setattr(llm_mod, "_sleep", fake_sleep)

    def handler(request: httpx.Request) -> httpx.Response:
        state["n"] += 1
        if state["n"] == 1:
            return httpx.Response(500, content=b"transient")
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    _patch_transport(monkeypatch, handler)
    client = LLMClient(_cfg(max_retries=1, retry_base_delay_s=0.5))
    result = await client.chat_completion([{"role": "user", "content": "hi"}], tools=[])
    assert result["choices"][0]["message"]["content"] == "ok"
    assert state["n"] == 2
    assert sleeps == [0.5]


async def test_no_fallback_configured_single_attempt(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        return httpx.Response(500, content=b"boom")

    _patch_transport(monkeypatch, handler)
    client = LLMClient(_cfg(fallback_base_url="", fallback_model=""))
    assert client.fallback_configured is False
    with pytest.raises(LLMError):
        await client.chat_completion([{"role": "user", "content": "hi"}], tools=[])
    assert len(calls) == 1


async def test_stream_error_after_first_delta_propagates(monkeypatch: pytest.MonkeyPatch) -> None:
    """已产出 delta 后失败：不得重放（防重复输出），LLMError 直接上抛。"""
    client = LLMClient(_cfg())

    async def broken_stream(*args: Any, **kwargs: Any):
        yield {"type": "delta", "text": "par"}
        raise LLMError("mid-stream death")

    monkeypatch.setattr(client, "_stream_once", broken_stream)
    got: list[dict[str, Any]] = []
    with pytest.raises(LLMError, match="mid-stream death"):
        async for e in client.chat_completion_stream([{"role": "user", "content": "hi"}], tools=[]):
            got.append(e)
    assert [e["type"] for e in got] == ["delta"]


def test_endpoints_order_and_fallback_flag() -> None:
    client = LLMClient(_cfg())
    assert client.fallback_configured is True
    assert client._endpoints()[0][0] == PRIMARY
    assert client._endpoints()[1][0] == FALLBACK


async def test_backoff_sleep_seam_does_not_hijack_stdlib(monkeypatch: pytest.MonkeyPatch) -> None:
    """回归锁：退避打点只能记自己的 sleep，不能劫持进程内的 asyncio.sleep。

    旧写法 `monkeypatch.setattr(llm_mod.asyncio, "sleep", fake)` 换掉的是**标准库模块属性**，
    补丁存续期内进程里任何 `await asyncio.sleep()`（如 app/integrated_app/testing/fake_engine.py
    的 0.001s 轮询）都会写进同一个列表——单进程全量跑时 `assert sleeps == [0.5]` 因此间歇性变红
    （实测：单跑 3/3 通过、整文件 7/7 通过、全量 -q 挂；-n auto 下不复现）。
    """
    import asyncio as _a

    seen: list[float] = []

    async def spy(delay: float) -> None:
        seen.append(delay)

    real_sleep = _a.sleep
    monkeypatch.setattr(llm_mod, "_sleep", spy)

    await _a.sleep(0.001)  # 其它组件的正常用法，不该被本测试的记录点捕获

    assert _a.sleep is real_sleep, "asyncio.sleep 被整体替换 = 污染整个进程"
    assert seen == [], f"外来 sleep 被记进来了：{seen}"
