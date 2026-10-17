"""crash_telemetry.py — 本地崩溃遥测（v2.9 评估·运维稳定性 P1-2，X2 局部落地）

桌面形态保留照评项 X2 的**本地优先**实现：
- Python 侧（本模块）：faulthandler（硬崩溃：段错误/abort 时倾泻全部线程栈到
  固定文件）+ sys.excepthook / threading.excepthook（未捕获异常），落盘到
  ``<project_root>/logs/crash_reports/crash-python-*.log``；
- 壳（Rust）侧：``desktop/src-tauri/src/crash_telemetry.rs`` 的 panic hook 落盘
  ``<app_dir>/logs/crash_reports/crash-shell-*.log``（同一目录约定）；
- 消费：``count_crash_reports()`` 由 routes/metrics_routes.py 暴露为
  crash_reports_total / crash_reports_recent_24h gauge；AlertEngine 规则
  CrashReportsDetected 在 24h 内出现新崩溃留痕时告警（runbook: crash_reports.md）。

远端上报（第三方 SDK）与符号服务器归档需要联网与新增依赖，按修复批次约束
**不在本批实施**（登记于《执行对照表》受阻/后续项）；崩溃率阈值口径为
会话崩溃率 ≤ 0.1%，由 runbook 与发布流程按台账执行。
"""

from __future__ import annotations

import faulthandler
import sys
import threading
import time
import traceback
from pathlib import Path

CRASH_DIR_PARTS = ("logs", "crash_reports")
_installed = False


def crash_reports_dir(project_root: str | Path) -> Path:
    """崩溃留痕目录：``<project_root>/logs/crash_reports``（与壳侧约定一致）。"""
    return Path(project_root).joinpath(*CRASH_DIR_PARTS)


def _default_project_root() -> Path:
    # app/integrated_app/crash_telemetry.py → 项目根 = parents[2]
    return Path(__file__).resolve().parents[2]


def _write_report(root: Path, kind: str, body: str) -> Path | None:
    """落盘一份崩溃留痕；任何失败都静默（观测不得放大故障）。"""
    try:
        d = crash_reports_dir(root)
        d.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        path = d / f"crash-{kind}-{ts}.log"
        path.write_text(body, encoding="utf-8")
        return path
    except Exception:
        return None


def install(project_root: str | Path | None = None) -> Path:
    """安装崩溃留痕钩子（幂等）；返回崩溃目录。

    - faulthandler：硬崩溃（段错误/abort）时把全部线程栈追加到 faulthandler.log；
    - sys.excepthook：主线程未捕获异常（保留既有 hook 链式调用）；
    - threading.excepthook：工作线程未捕获异常。
    """
    global _installed
    root = Path(project_root) if project_root is not None else _default_project_root()
    d = crash_reports_dir(root)
    try:
        d.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    if _installed:
        return d
    try:
        # faulthandler 需要长期持有句柄（enable 期间持续写入），不能随 with 块关闭
        fh = open(d / "faulthandler.log", "a", encoding="utf-8")  # noqa: SIM115
        faulthandler.enable(file=fh)
    except Exception:
        pass
    prev_hook = sys.excepthook

    def _uncaught_hook(tp, val, tb) -> None:
        try:
            body = "".join(traceback.format_exception(tp, val, tb))
            path = _write_report(
                root,
                "python",
                f"kind: python-uncaught\ntime: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n{body}",
            )
            if path is not None:
                print(f"[CRASH-TELEMETRY] 未捕获异常已留痕: {path}", file=sys.stderr)
        finally:
            if prev_hook is not None and prev_hook is not sys.__excepthook__:
                prev_hook(tp, val, tb)

    def _thread_hook(args: threading.ExceptHookArgs) -> None:
        try:
            body = "".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback))
            _write_report(
                root,
                "python-thread",
                "kind: python-thread-uncaught\n"
                f"thread: {args.thread.name if args.thread else '?'}\n"
                f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n{body}",
            )
        except Exception:
            pass

    sys.excepthook = _uncaught_hook
    try:
        threading.excepthook = _thread_hook
    except Exception:
        pass
    _installed = True
    return d


def count_crash_reports(project_root: str | Path | None = None, within_s: float | None = 86400.0) -> dict[str, int]:
    """统计崩溃留痕文件（python + shell 同目录约定；data/crash_reports 为备用目录）。

    返回 ``{"total": N, "recent": M}``；recent 为 within_s（默认 24h）内新建数。
    目录缺失一律返回 0（从未崩溃是正常态，不视为错误）。
    """
    root = Path(project_root) if project_root is not None else _default_project_root()
    total = 0
    recent = 0
    now = time.time()
    for rel in (("logs", "crash_reports"), ("data", "crash_reports")):
        d = root.joinpath(*rel)
        try:
            if not d.is_dir():
                continue
            for p in d.glob("crash-*.log"):
                total += 1
                if within_s is not None:
                    try:
                        if now - p.stat().st_mtime <= within_s:
                            recent += 1
                    except OSError:
                        continue
        except OSError:
            continue
    return {"total": total, "recent": recent}
