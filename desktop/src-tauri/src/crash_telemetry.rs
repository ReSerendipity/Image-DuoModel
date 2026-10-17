//! 本地崩溃遥测（v2.9 评估·运维稳定性 P1-2，X2 局部落地）
//!
//! 壳进程 panic hook：把 panic 信息落盘到 `<app_dir>/logs/crash_reports/crash-shell-<ts>.log`，
//! 与 Python 侧（`app/integrated_app/crash_telemetry.py`）共用同一目录约定，
//! 由 `/api/metrics` 的 `crash_reports_total` / `crash_reports_recent_24h` 暴露。
//! 远端上报与符号服务器归档需要联网与第三方 SDK，按修复批次约束暂不实施（见执行对照表）。

use std::fs;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, Ordering};

static INSTALLED: AtomicBool = AtomicBool::new(false);

/// 崩溃报告目录：`<app_dir>/logs/crash_reports`
pub fn crash_dir(app_dir: &std::path::Path) -> PathBuf {
    app_dir.join("logs").join("crash_reports")
}

/// 安装全局 panic hook（幂等）。panic payload 为字符串时记录原文，否则记录占位说明；
/// location（文件:行:列）即壳侧最小符号化信息。
pub fn install(app_dir: &std::path::Path) {
    if INSTALLED.swap(true, Ordering::SeqCst) {
        return;
    }
    let dir = crash_dir(app_dir);
    let _ = fs::create_dir_all(&dir);
    std::panic::set_hook(Box::new(move |info| {
        let payload = if let Some(s) = info.payload().downcast_ref::<&str>() {
            (*s).to_string()
        } else if let Some(s) = info.payload().downcast_ref::<String>() {
            s.clone()
        } else {
            "<non-string panic payload>".to_string()
        };
        let location = info
            .location()
            .map(|l| format!("{}:{}:{}", l.file(), l.line(), l.column()))
            .unwrap_or_default();
        let thread_name = std::thread::current()
            .name()
            .unwrap_or("<unnamed>")
            .to_string();
        let ts = chrono::Local::now().format("%Y%m%d_%H%M%S%.3f");
        let body = format!(
            "product: Image MultiModel (shell)\nkind: shell-panic\nthread: {thread_name}\nlocation: {location}\ntime: {}\npanic: {payload}\n",
            chrono::Local::now().format("%Y-%m-%d %H:%M:%S%.3f")
        );
        let path = dir.join(format!("crash-shell-{ts}.log"));
        match fs::OpenOptions::new().create(true).append(true).open(&path) {
            Ok(mut f) => {
                let _ = f.write_all(body.as_bytes());
            }
            Err(e) => eprintln!("[CRASH-TELEMETRY] 写入崩溃留痕失败: {e}"),
        }
        eprintln!("[CRASH-TELEMETRY] panic 已留痕: {}", path.display());
    }));
}
