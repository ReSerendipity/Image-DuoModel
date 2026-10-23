# MLOps 迭代台账（Image-MultiModel）

> 本目录将散落在代码/脚本/文档中的 MLOps 迭代集中文档化（NEXT P2-7 落地，2026-10-11）。
> 唯一执行台账：`C:/Users/Doro/.zcode/workspace/default/doubao-eval-prompts/next-ledger/Image-MultiModel.md`
> 评估报告：`doubao-eval-prompts/Image-MultiModel.md`（总分 60/100，8 项待改进 → 见「NEXT 落地」）。

## 1. M 系迭代清单（M1–M6 + 安全约束 M-05）

| 编号 | 主题 | 内容 | 证据文件（真实存在） |
|---|---|---|---|
| M1 | GPU 冒烟 | GPU 路径最小冒烟测试，失败仅记录不阻断（skip 台账精确相等门禁） | `tests/native/test_gpu_smoke.py` |
| M2 | 训练环境指纹 | 训练侧 AI-Toolkit 环境指纹随 job 落盘（best-effort，失败字段 unknown） | `app/integrated_app/training/runner.py` |
| M3 | 权重清单收敛 | manifest 只保留 config 当前注册引擎的权重 + loras 用户自选；剔除僵尸权重 | `scripts/generate_weight_manifest.py` |
| M4 | 生成质量基线 + 问 AI | 固定 prompt+seed 回归集（零漂移检测）；历史首图发起多模态对话 | `docs/reports/engine_baseline/`、`templates/index.html` |
| M5 | 训练 job 可观测 | 训练 job 只读查询 CLI（血缘/状态/参数） | `scripts/query_training_jobs.py` |
| M6 | 用户反馈闭环 | schema v7 `tasks.rating`（-1/0/1）+ 幂等迁移 + API 评分/汇总 | `history_db.py`、`migrate_add_rating_column.py`、`routes/task_routes.py` |
| M-05 | 安全安装约束 | 缺失依赖只从 `requirements-lock.txt` 安装（版本钉死防投毒）；禁硬编码外部解释器路径 | `app/clean_launch.py` |

## 2. NEXT 落地（评估报告 8 项待改进 → 阶段 0-4）

| 项 | 状态 | 摘要 |
|---|---|---|
| P0-1 模型链接修复 | ✅ | 15 悬空链接→16 Junction 指向 v3.2 库；新增 `scripts/check_model_links.py` 探针（20 引用 17 OK / 3 文件级缺失） |
| P0-2 权重清单覆盖 | ✅ | manifest 重生成（14 在用文件）；`allow_unregistered_weights: false` 收紧 |
| P1-3 rating 闭环 | ✅ | `POST /api/tasks/{id}/rating` + `GET /api/tasks/rating-summary`（引擎聚合）+ 前端赞/踩按钮 + 5 用例测试 |
| P1-4 固定评估集 | ✅ | `docs/reports/engine_baseline/prompts.json`（10 条/seed42）+ `scripts/engine_baseline.py`（dry-run 可验 / run 留 GPU） |
| P1-5 产物一致性 | ✅ 巡检 | `reconcile_db_disk.py` dry-run：745 行 / 648 假引擎 Temp 死记录 / 58 孤儿缩略图；清理待用户决策 |
| P2-6 双依赖锁合并 | ✅ | `requirements-lock.txt` 为权威底合并 frozen 快照（151 条）；记录 CUDA 漂移；pip dry-run 可解析 |
| P2-7 MLOps 文档化 | ✅ | 本文件 |
| P2-8 显存策略决策 | ✅ | 见 `docs/adr/0001-vram-strategy.md`（记录"保持默认禁用"决策，非启用） |

> 注：`docs/` 目录整体在 `.gitignore`（L64）中，以上 P1-4 评估集定义与 P2-7/P2-8 文档
> 均为本地落盘产物（不入库）；执行器脚本已入库（`scripts/engine_baseline.py`）。

**需人工决策**：① 2 个缺失 UNET 权重（z_image_turbo/qwen_image 的 int8_convrot）——补权重或改 config；
② 648 条死记录清理（`reconcile_db_disk.py --apply`，自动备份）；③ lock 版本漂移
（声明 torch 2.14.0 vs 实测 2.11.0+cu128）。

## 3. 质量门禁（CI 实读 ci.yml）

```
ruff check app/ tests/ scripts/          # lint
mypy（app/integrated_app，ratchet 0）     # 类型零容忍
pytest 并行 + junit：skip 台账精确相等（当前 234）+ min_executed 1150 + coverage ≥65%
```

## 4. 回滚点

`rollback/next-landing-p0-20261011`、`rollback/next-landing-p1-20261011`、`rollback/next-landing-p2-20261011`（git tag）。
