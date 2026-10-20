# 引擎出图基线（Engine Quality Baseline）

> 对应 MLOps 评估报告 M4：当前**零漂移检测、零自动图像质量评分**——引擎升级或权重替换后，
> 出图是否劣化只能靠人眼。本目录固化一份「固定 prompt + 固定 seed」的回归集，
> 每次引擎接入 / 权重升级 / 发版前跑一遍，留痕对比。

## 1. 目的

现有 CI 的视觉基线（`tests/e2e/` 的 `homepage.linux-chromium.png`）只覆盖 **UI 像素**，
不覆盖**生成内容质量**。本基线回答三个问题：

1. 新引擎在同一组 prompt 上能不能出合法图（不崩、不黑图、不截断）；
2. 升级权重后，同 seed 的结果与上一版相比有没有肉眼可辨的劣化；
3. FP8/INT8 量化档与 BF16 原档在关键 prompt 上的差距是否在可接受范围。

## 2. 固定回归集

- **Prompt 数量**：10 条（覆盖人物 / 风景 / 静物 / 城市 / 建筑 / 食物 / 抽象 / 科幻 / 产品）。
- **种子**：每条 prompt 固定 `seed=42`，`steps=8`、`cfg=1.0`（与蒸馏引擎推荐一致）。
- **尺寸**：1024×1024（与 `config.yaml` 默认一致）。
- **定义文件**：`docs/reports/engine_baseline/prompts.json`（2026-10-11 定稿，NEXT P1-4）。
- **存储**：`docs/reports/engine_baseline/runs/<YYYYMMDD>/<engine_name>/` 下存 PNG + 一个 `meta.json`
  （记录 engine、seed、逐条 task_id/status/outputs、生成时间；人评分数 1-5 记入 `notes`）。

## 3. 执行方式（脚本化）

```powershell
# 只读校验（无 GPU 依赖，CI/本机直接跑）——评估集完整性 + 引擎注册 + 权重引用可解析
python scripts/engine_baseline.py --dry-run

# 真实推理（需 GPU 环境 + 本地服务已启动；本机红线不强跑，由 GPU runner / 人工触发）
# 1) 启动服务（start.bat）
# 2) python scripts/engine_baseline.py --run [--engines flux2_klein_native]
```

## 4. 判读

- 任一 prompt 崩图 / 黑图 / 内容安全拦截误触发 → **block release**。
- 同 seed 与上一版基线对比出现结构级差异（构图/主体漂移）→ 人工判断是否接受，记录在 `meta.json` 的 `notes`。
- 人评均分较上一版下降 ≥ 1.0（5 分制）→ 触发 `docs/GOTCHAS.md` 记录并回退权重。

## 5. 现状（2026-10-11，NEXT P1-4 更新）

- [x] 10 条固定 prompt 已定稿：`prompts.json`（seed=42，覆盖 10 类场景）。
- [x] 执行器已落地：`scripts/engine_baseline.py`（--dry-run 只读校验；--run 真实推理留 GPU 环境）。
- [ ] 尚无自动 CLIP-score（需要 GPU + CLIP 模型，列入长期路线图）。
- [ ] 现有引擎 z_image_turbo / flux2_klein / krea2_turbo 均无历史基线存档（首次 --run 后产生）。
- [ ] **已知阻断（需人工决策）**：z_image_turbo_native 与 qwen_image_native 的 UNET 权重
  （`z_image_turbo_int8_convrot.safetensors`、`qwen_image_2.1_int8_convrot.safetensors`）在本机
  模型库中不存在（v3→v3.2 迁移后未同步），`--dry-run` 会如实 FAIL；补权重或改 config 后即可通过。
  （详见 NEXT 落地台账：需人工决策清单。）
