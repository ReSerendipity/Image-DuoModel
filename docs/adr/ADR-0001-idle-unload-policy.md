# ADR-0001：引擎常驻显存 vs 空闲自动卸载（idle_unload_minutes 默认 0）

- 状态：Accepted
- 日期：2026-09-04
- 关联：成本资源治理评估报告 §二·显存治理 / §五-⑦；`cost_governance.IdleUnloadManager`

## 背景

`config.yaml → runtime.idle_unload_minutes: 0` 使空闲自动卸载（`IdleUnloadManager` + `app_server.idle_unload_loop`）默认关闭。机制本身已实现且经过单测，但"默认关闭"此前没有留下决策记录，评估时会被判为「无自动显存回收」的半开放缺陷。

## 决策

**保持默认 `idle_unload_minutes: 0`（引擎常驻显存），并以此 ADR 作为显式决策记录。**

## 理由

1. **单用户本地工具**：服务与用户在同一台机器（127.0.0.1:8288），请求间隔中"空载占显存"不影响其他租户；空闲释放只服务「让显存给其它 GPU 程序」这一个场景。
2. **冷启动代价不对称**：Z-Image Turbo 权重（TE+UNet+VAE）冷加载远大于单次推理（均值 5.57s）；自动卸载后每个新请求都要付冷启动，交互体验劣化。
3. **泄漏已有监控兜底**：`VRAMLeakMonitor` + `MetricsStore.record_leak` + `GpuVramLow` 告警（free<15% 持续 2min）覆盖了常驻的主要风险（累积泄漏→OOM）；泄漏可观测后，手动 `/api/engine/unload` 已够用。
4. **vram_scheduler 保持 disabled 的理由一致**：单 worker 串行下 batch_size 恒为用户请求值，水位调度无收益（详见 `generation_service.py` 注释）。

## 何时重新评估

- 同机运行其它大显存程序（游戏/训练）成为常态 → 建议改 `idle_unload_minutes: 30`。
- 出现进程生命周期内无法回收的泄漏（`leak_detected` 持续 true）→ 先修泄漏，再考虑兜底性定时卸载。
- 未来引入多 worker / 多引擎并发 → 重新评估常驻策略与水位调度。

## 备注

- 本 ADR 只记录默认值决策；运行时可随时通过 `config.yaml` 或 `PUT /api/config` 调整，无需改代码。
- 容量侧的「显存峰值是否够用」问题由每日容量快照（`capacity_snapshots.peak_used_gb`）回答，不依赖空闲卸载。
