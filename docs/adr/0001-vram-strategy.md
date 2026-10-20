# ADR-0001 · 显存治理策略：保持 vram_scheduler / idle_unload 默认禁用

- 状态：**已接受**（2026-10-11，NEXT P2-8）
- 决策类型：记录决策（不启用新功能）

## 背景

`cost_governance.py` 已实现两套显存治理能力并挂载进 `app_server`：
- `VRAMScheduler`（按水位启停批处理/队列，`config.yaml runtime.vram_scheduler`）
- `IdleUnloadManager`（空闲 N 分钟卸载模型，`config.yaml runtime.idle_unload_minutes`）

当前配置（`config.yaml` L477-484）：`vram_scheduler.enabled: false`、`idle_unload_minutes: 0`（0=禁用）。

## 决策

**维持默认禁用，不启用**，仅记录决策与理由。

## 理由（基于现场证据）

1. **配置曾缺失导致启动失败**：`config_models.py` L341 注释记载 "cost_governance 的
   idle_unload_minutes 引用，此前缺失导致 create_app 启动失败"——显存治理路径历史上
   出过启动级回归，开启等于引入新的运行时风险面。
2. **无量化收益证据**：项目为单进程交互式推理服务（FastAPI :8288），当前无批量并发
   压测数据支撑"启用后可观测的显存/吞吐收益"；治理收益是假设而非实测。
3. **收益-风险不对称**：VRAM 水位调度在推理峰值误判会引入排队/卸载延迟（用户可感知）；
   启用前应先有 GPU 峰值显存基线（见 `docs/reports/engine_baseline/` 评估集，尚未产生首次 --run 基线）。

## 后果

- 正面：规避启用的启动/运行时风险；保持现状的确定性行为。
- 负面：峰值显存无自动治理；多引擎轮换时显存由 Comfy 内核既有机制管理。
- 未来触发启用条件：① 出现同机并发/峰值显存压测基线；② 实测 OOM 或显存瓶颈证据；
  ③ 变更时须先在 CI/本机跑 `tests/native/test_gpu_smoke.py` 全量 GPU 冒烟。
