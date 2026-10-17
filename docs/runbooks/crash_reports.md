# Runbook — CrashReportsDetected（本地崩溃留痕）

> 告警引擎规则：`observability/alerts.py::CrashReportsDetected`（warning，立即触发）。
> 触发条件：24h 内 `logs/crash_reports/`（壳与 Python 共用目录约定）新增 `crash-*.log`。
> 崩溃率阈值口径：**会话崩溃率 ≤ 0.1%**（分母 = 当期会话数，来源 = 崩溃留痕 + 正常退出记录），
> 由发布流程按《演练执行台账》同期复核。

## 症状
- `/api/alerts` 出现 `CrashReportsDetected`（warning）。
- `/api/metrics/prometheus`：`crash_reports_total` / `crash_reports_recent_24h` 上升。
- 桌面壳日志（`logs/seedvr2-shell.log`）出现 `[CRASH-TELEMETRY] panic 已留痕`。

## 确认命令
```bash
curl -s http://127.0.0.1:8288/api/metrics/prometheus | grep crash_
ls -lt logs/crash_reports/ | head
cat logs/crash_reports/crash-shell-*.log   # 壳 panic（location 即文件:行:列）
cat logs/crash_reports/crash-python-*.log  # Python 未捕获异常栈
```

## 影响判断
- `crash-shell-*`：壳进程 panic（Rust 侧）；`crash-python-*`：后端未捕获异常；`faulthandler.log`：硬崩溃线程栈。
- 单个用户的本地崩溃不外泄：留痕仅存本机，需用户主动反馈/诊断包导出时提交。

## 临时缓解
- 反复崩溃时先回滚到上一个可用版本包（增量包回滚链见 `docs/SOPS.md` §4）；
- 收集 `logs/crash_reports/` 与 `logs/seedvr2-shell.log` 供定位。

## 符号归档（发布流程约定）
- Windows 发布构建保留 PDB（`cargo build --release` 产物 `desktop/src-tauri/target/release/*.pdb`）
  与崩溃留痕中的 `location`（文件:行:列）共同定位；PDB 随发布元数据归档，不入仓库。

## 回滚/重启
- 壳崩溃自动看门狗重启（`main.rs::start_watchdog`）；Python 崩溃由壳重启；
  多次重启失败按启动页提示走 `retry_start`。

## 恢复验证
- 修复版本发布后 `crash_reports_recent_24h` 回落为 0 且 `/api/health` 正常。

## 升级联系人
- 仓库 OWNER（ReSerendipity）；见 `.github/CODEOWNERS`。
