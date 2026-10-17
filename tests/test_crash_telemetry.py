"""tests/test_crash_telemetry.py — 本地崩溃遥测（v2.9 评估·运维稳定性 P1-2，X2 局部落地）"""

from __future__ import annotations

import sys
import threading

import pytest

from integrated_app import crash_telemetry as ct


@pytest.fixture()
def fresh_root(tmp_path):
    return tmp_path / "proj"


def test_install_writes_report_on_uncaught(fresh_root, monkeypatch):
    monkeypatch.setattr(ct, "_installed", False)
    saved_hook = sys.excepthook
    try:
        d = ct.install(fresh_root)
        assert d.exists()
        assert sys.excepthook is not saved_hook
        try:
            raise ValueError("boom-telemetry")
        except ValueError:
            sys.excepthook(*sys.exc_info())
        reports = list(d.glob("crash-python-*.log"))
        assert len(reports) == 1
        assert "boom-telemetry" in reports[0].read_text(encoding="utf-8")
        stats = ct.count_crash_reports(fresh_root)
        assert stats["total"] == 1
        assert stats["recent"] == 1
    finally:
        sys.excepthook = saved_hook


def test_threading_hook_writes_report(fresh_root, monkeypatch):
    monkeypatch.setattr(ct, "_installed", False)
    saved = threading.excepthook
    saved_sys = sys.excepthook
    try:
        ct.install(fresh_root)
        try:
            raise RuntimeError("thread-boom")
        except RuntimeError:
            exc_info = sys.exc_info()
        args = threading.ExceptHookArgs((exc_info[0], exc_info[1], exc_info[2], None))
        # _thread_hook 是 install() 内的闭包（非模块属性），须经 threading.excepthook 触发
        threading.excepthook(args)
        reports = list((fresh_root / "logs" / "crash_reports").glob("crash-python-thread-*.log"))
        assert len(reports) == 1
        assert "thread-boom" in reports[0].read_text(encoding="utf-8")
    finally:
        threading.excepthook = saved
        sys.excepthook = saved_sys


def test_count_missing_dir_returns_zero(tmp_path):
    stats = ct.count_crash_reports(tmp_path / "never-created")
    assert stats == {"total": 0, "recent": 0}


def test_install_is_idempotent(fresh_root, monkeypatch):
    monkeypatch.setattr(ct, "_installed", False)
    saved_hook = sys.excepthook
    try:
        d1 = ct.install(fresh_root)
        hook1 = sys.excepthook
        d2 = ct.install(fresh_root)
        assert d1 == d2
        assert sys.excepthook is hook1  # 幂等：第二次不覆盖钩子
    finally:
        sys.excepthook = saved_hook
