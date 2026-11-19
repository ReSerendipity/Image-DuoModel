# P3 — LoRA 训练模块（T-34 决策=是 · 2026-10-01 立项）

> 关联：T-34（决策：是否做 LoRA 训练模块）= **是**；`docs/roadmap/README.md` 能力切片总览；
> `docs/repo-analysis/学习报告全量待办任务清单_20260912.md` 领域 C（LoRA 训练）。
> 本文件即 T-34 验收所需的「决策记录」（写入 roadmap）。

## 决策记录（T-34）

- **裁定**：**做** LoRA 训练模块（2026-10-01，用户「全部都做」授权）。
- **依据**：学习报告借鉴价值矩阵把 LoRA 训练列为 P0 高价值（fluxgym / sd-scripts 均为 ★★★）
  但项目当前是**纯推理服务**（无训练模块、无训练路线图）。本决策解除对 T-12~T-16、T-22 的阻塞。
- **落点**：本文件即决策记录，并在 `docs/roadmap/README.md` 能力切片总览新增 P3 行。
- **后端选型（T-12 POC，2026-10-02 源码级实证）**：采用**路径 A — AI-Toolkit 后端 + 轻前端**；
  路径 B（自扩展）与 sd-scripts 均被实证否掉，依据见下节「事实约束」。

## 事实约束（来自复查报告代码级实证，非臆测）
> 已归档（2026-11-19）→ [_archive/执行记录/2026-11/2026-11-19-p3-lora-training-closed.md](../../_archive/执行记录/2026-11/2026-11-19-p3-lora-training-closed.md)

## 关键推论

1. **Z-Image LoRA 训练不能直用 sd-scripts**（已复核确认）→ 走 **AI-Toolkit**（T-12 已实证支持 Z-Image + comfy 格式 + int8_convrot）。
2. **sd-scripts 的 LUMINA 训练器≠「能训 Lumina2」**：它硬编码 `NextDiT_2B` 结构，只适用于 Lumina 官方 NextDiT 权重；**训 Z-Image 会「静默错配」**——`strict=False` 不会报键名错误，缺 `dec_net` 整套解码分支也能加载成功，最后训出结构错乱的模型（详见 GOTCHAS #45）。
3. **训练 UI** → 取 AI-Toolkit 自带的轻 UI（它本身就带 `ui/` + `run_windows.bat`，无需 fluxgym 那套 Gradio 外壳），本仓侧只做「任务编排 + 状态回写 + 产物移交推理引擎」的薄层。
4. **Caption / Tagger** → **不需要 SDNext**：AI-Toolkit 内置 `extensions_built_in/captioner`（LMM/LLM 打标）与 `dataset_tools`（数据集合理/分桶）。若将来要 WD14 / DeepDanbooru 这类传统 tagger，再单独接节点，不在 T-22 主路径内。

## 候选实现路径（已选型，2026-10-02）
> 已归档（2026-11-19）→ [_archive/执行记录/2026-11/2026-11-19-p3-lora-training-closed.md](../../_archive/执行记录/2026-11/2026-11-19-p3-lora-training-closed.md)

## 待办（挂原清单 T 项）
> 已归档（2026-11-19）→ [_archive/执行记录/2026-11/2026-11-19-p3-lora-training-closed.md](../../_archive/执行记录/2026-11/2026-11-19-p3-lora-training-closed.md)

## 阻塞 / 前置
> 已归档（2026-11-19）→ [_archive/执行记录/2026-11/2026-11-19-p3-lora-training-closed.md](../../_archive/执行记录/2026-11/2026-11-19-p3-lora-training-closed.md)

## T-12 实跑记录（2026-10-02，最小 smoke job）
> 已归档（2026-11-19）→ [_archive/执行记录/2026-11/2026-11-19-p3-lora-training-closed.md](../../_archive/执行记录/2026-11/2026-11-19-p3-lora-training-closed.md)

## T-13 编排薄层实装记录（2026-10-03）

**定位边界（先划清，不许抬高）**：本仓**不出训练 UI**。AI-Toolkit 自带前端（仓库内 `ui/` 是 Next.js，
入口 `run_windows.bat` → `python -m manager launch`）承担训练界面的全部交互；本仓薄层只负责
「任务编排 → 调用 AI-Toolkit → 解析产出 → 状态回写 / 产物移交」，两者通过薄层产出的 `job.yaml` 与
`loss_log.db` 互通。

**新增模块**（新增文件，未改动任何 pinned 核心模块 → 完整性清单无需重签，`33/33 ✓` 保持通过）：

| 模块 | 职责 |
|---|---|
| `app/integrated_app/training/spec.py` | `TrainJobSpec`：job 参数模型 + 提交前校验（name 正则 / 路径绝对且存在 / model 是文件、extras-dataset 是目录 / resolution 16 倍数 / 数值下限 / dtype 白名单）+ 渲染 AI-Toolkit job 配置 |
| `app/integrated_app/training/store.py` | 状态记录：`<data>/training/jobs/<job_id>.json` 原子写（临时文件 + `fsync` + `os.replace`），全局写锁串行化后台泵与请求线程 |
| `app/integrated_app/training/progress.py` | 进度回读：只读 sqlite 回读 `loss_log.db` + stdout 日志尾部（尾读 `max_bytes` 上限） |
| `app/integrated_app/training/handoff.py` | 产物发现（终稿 / 中间档 / optimizer / 采样图 / config）+ 移交**规划**（只读给命令），搬运需显式发起 |
| `app/integrated_app/training/runner.py` | 编排核心：`submit`（校验→落 `job.yaml`→`Popen(run.py)`）→ 后台泵逐行落盘 `stdout.log` → 退出码定终态并回写 |
| `app/integrated_app/routes/train_routes.py` | HTTP 面 `/api/train/*`：`status / jobs / jobs/{id} / logs / artifacts / cancel / handoff / lora`（靠 `app_server` 的路由自动发现注册，**未改任何既有文件**） |

**真跑实证**（走薄层自己的 `submit()`，不是手敲 job.yaml）：

- 环境：`AITK_ROOT=<AI-Toolkit 仓库根>`、`AITK_PYTHON=<AI-Toolkit-env 解释器>`（**薄层不内置本机绝对路径**，
  两个环境变量驱动；`pre-commit` 的 `check_no_hardcoded_paths.py` 会拒收硬编码）。
- job：`t13_probe`，512² / **2 步** / rank 4 / adamw lr 1e-4 / bf16 / `low_vram` / `save_every=1` /
  `logging.use_ui_logger=True` / `log_every=1`，4 张 512² 图（latent/TE 缓存命中 T-12 那份）。
- 实测链路：`submit → running` →（轮询）`step=1 / total=2 / percent=50.0 / latest={learning_rate, loss/loss}` →
  `completed exit=0` → `artifacts` / `handoff_plan` / `logs` 全部正常返回。
- 产物（`data/training/<job_id>/t13_probe/`）：终稿 `t13_probe.safetensors` 21,318,744 B、
  中间档 `t13_probe_000000001.safetensors` 同体积（二者只差后缀，**所以判终稿必须名字精确相等**）、
  `optimizer.pt` 85.4 MB、`config.yaml`、采样图 2 张。
- 进度回读实证：`loss_log.db` 真实 schema = `steps(step, wall_time)` / `metrics(step, key, value_real, value_text)` /
  `metric_keys(key, first_seen_step, last_seen_step)`，WAL 模式；训练进程**正在写**时薄层用 `mode=ro` 只读连接
  照样读到数（不会抢写锁）。`use_ui_logger=False` 时根本不产这个库（T-12 那份就没有）。

**真跑抓出并修掉的两个真缺陷**（这正是"先真跑再下结论"的价值）：

1. 训练跑到 `completed` 后，接口回的 `progress.step` 仍是 `None`——因为进度刷新只改内存、非终态轮询不落盘，
   泵线程写终态时又没刷新。修：`_JobProcess._pump()` 定终态前补一次 `_refresh_progress()`，`cancel()` 同理。
2. 移交计划的 `target_dir` 成了**相对路径** `loras`——`Path("")` 归一化成 `Path(".")`，`str()` 是 `"."` **真值**，
   判空用 `str(Path(x))` 永远走"有值"分支。修：判空改用原始字符串。

（另在单测层抓到的两个：`training_folder` + `save_root` 双重拼接导致产物永远找不到；中间档识别按下划线判断会
把带下划线的 job 名自己的终稿误判成中间档。四条全部落 GOTCHAS #48.1~48.4 + 回归测试。）

**门禁**：`ruff check` / `ruff format --check` 全绿、`mypy app/integrated_app` `Success: no issues found in 105 source files`、
训练相关测试 **65 passed / 1 skipped**（`test_training_{spec,store,progress,handoff,runner}` + `test_train_routes`）、
`check_spec_refs --self` PASS、`check_config_refs` 通过、`check_integrity_manifest` `33/33 ✓`、
`check_no_hardcoded_paths` rc=0。

**口径边界**：这是**编排链路跑通**的实证（薄层能把事情送进 AI-Toolkit 并回读状态与产物），
**不是**「训练 UI 已完成」——交互界面仍是 AI-Toolkit 自带前端；真实训练的数据量/步数/收敛/视觉评测属 T-14~T-16。

## T-14 数据准备第一块（2026-10-03）：训练前数据集就绪校验

**动机**：T-12 实跑一次 22 分钟，坏数据（缺 caption / 空 caption）会在训练进程里才炸。薄层应在
提交训练前先确认数据集满足最低可用条件。

**新增**：

| 文件 | 职责 |
|---|---|
| `app/integrated_app/training/dataset.py` | `validate_dataset(folder, caption_ext, strict)` → `DatasetReport`（图像数 / 配对数 / 缺 caption / 空 caption / 其它文件）；`strict=True` 时缺/空/无图抛 `DatasetError` |
| `app/integrated_app/routes/train_routes.py` | `GET /api/train/datasets/validate?folder=<绝对路径>&caption_ext=txt`：非法路径 → 400，其余返回报告（`ok` 字段） |
| `scripts/validate_lora_dataset.py` | CLI：`python scripts/validate_lora_dataset.py <dir> [--caption-ext txt] [--strict] [--json]`，可用 rc=0、不可用 rc=1、传参错误 rc=2 |

**实测**：对 T-12 真实数据集（`C:\Users\Doro\AppData\Local\Temp\zimage_lora_ds`，4 图 4 caption + 1 个 `.aitk_size.json` 缓存标记）跑 CLI → `[OK] 数据集可用` rc=0；对缺 caption 的目录 → `[FAIL] 数据集不可用` rc=1。

**口径边界**：只做文件级校验（图 + 同名 caption 存在且非空），**不解码图像查真实分辨率**（AI-Toolkit 会按 `resolution` 分桶下采样，分辨率不是数据集有效性的阻断项）；不改写、不搬运任何文件。

## T-14 数据准备第二块（2026-10-03）：解码级分辨率/完整性预检

**动机**：第一块只校验「文件存在 + caption 齐全」，但**文件后缀对 ≠ 内容是合法图像**——
T-12 那类只用 `b"\x89PNG"` magic bytes 顶替的假图、下载截断图，会在训练进程里（22 分钟起步）
才炸；同时数据集若混入远低于训练分辨率的碎片图，也该在提交前预警。本块补这块盲区。

**设计取舍**：解码是 IO 重活，**默认不跑**——`validate_dataset(check_resolution=False)` 与旧口径
完全一致（零 Pillow 依赖、零额外磁盘读），保持向后兼容；显式 `check_resolution=True`
时才真实解码每张图。这样「日常快校验」与「提交前深校验」走同一 API 两档。

**新增/扩展**：

| 文件 | 变更 |
|---|---|
| `app/integrated_app/training/dataset.py` | `DatasetReport` 增 `corrupt_images` / `image_sizes` / `resolution_issues` 三字段 + `ok` 纳入「无损坏、无分辨率异常」；`validate_dataset` 增 `check_resolution / min_size=256 / max_size=2048`（keyword-only）；新增 `_inspect_image`（**函数内懒加载 Pillow**，解码失败即记为损坏，尺寸越界进 `resolution_issues`） |
| `scripts/validate_lora_dataset.py` | 增 `--check-resolution` / `--min-size` / `--max-size`；解码异常（缺/空 caption 之外的损坏/分辨率）仍以 rc=1 暴露、rc=2 仍是传参错误 |
| `app/integrated_app/routes/train_routes.py` | `GET /api/train/datasets/validate` 增 `check_resolution / min_size / max_size` query 参数，默认关 |
| `tests/test_training_dataset.py` | +8 例（默认不解码忽略损坏 / 解码抓损坏 / 报告真实尺寸 / 分辨率越界 / 宽边界放行 / strict 抛损坏 / strict 抛分辨率 / to_dict 含新字段） |
| `tests/test_train_routes.py` | +2 例（端点 `check_resolution=true` 回损坏+尺寸；默认不解码） |

**语义铁律**（写进单测锁死）：
- 损坏图像（`cannot identify image file`）**永远 fatal**——无论是否开启分辨率边界，只要解码过就记 `corrupt_images` 且 `ok=False`；`strict` 下抛 `DatasetError`。
- 分辨率越界只在 `check_resolution=True` 时判定；用 `--min-size/--max-size` 放宽边界可放行（例：训练走分桶、允许小图时设 `--min-size 16`）。
- 默认（`check_resolution=False`）路径**完全不碰 Pillow**、不计 `image_sizes`，与 T-14 第一块行为逐字节一致。

**实测**（合成数据集：1×512² 真图 + 1×32² 真图 + 1×损坏假图，均配 caption）：
- `validate_lora_dataset.py <dir>`（默认）→ `[OK] 数据集可用` rc=0（损坏图未解码故不报）；
- `--check-resolution` → `corrupt_images=["bad.png"]` + `image_sizes` 真实尺寸 + `resolution_issues=["tiny.png 32x32（超出 [256,2048]）"]` → rc=1；
- `--check-resolution --min-size 16 --max-size 4096` → 分辨率异常清空，损坏仍 fatal → rc=1。
- 真实 T-12 数据集（4×512²）`--check-resolution` 实测全 OK（尺寸在边界内、无损坏）。

## T-14 收尾护栏（2026-10-03）：训练提交前综合自检 preflight

**动机**：第一/二块给了「数据集就绪校验」能力，但训练提交入口 `TrainingRunner.submit` 仍只校验规格
（`TrainJobSpec.validate`），且「立即返回 job_id」契约不允许在 submit 里做重 IO。需一个「先体检再上车」
的独立入口——把规格校验与数据集可用性聚合成一次综合自检，在 22 分钟训练启动前挡下坏参数 / 坏数据集
（规格错 / 图缺 caption / 图损坏 / 分辨率越界）。

**设计取舍**：
- 与 `submit` 解耦：preflight 是独立入口，`submit` 保持「立即返回 job_id」契约**不变**。
- `preflight_spec` 设计为**模块级函数**（不依赖 `TrainingRunner` 实例），供路由与 CLI 直接复用——
  避免为了只读校验而实例化带 GPU 锁 / 训练根的 runner。
- 数据集校验用 `validate_dataset(..., strict=False)` 取**完整报告**（`missing_caption` / `corrupt_images` /
  `resolution_issues` 等明细），由 `report.ok` 驱动 `result["ok"]`，而非 `strict=True` 抛异常丢失明细。
- 规格校验失败时不跑数据集校验（`dataset_folder` 可能根本不存在），`dataset` 字段为 `None`。

**新增/扩展**：

| 文件 | 变更 |
|---|---|
| `app/integrated_app/training/runner.py` | 模块级 `preflight_spec(spec, *, check_resolution, min_size, max_size) -> dict{"ok","spec_errors","dataset"}`：先 `spec.validate()` 捕捉 `TrainSpecError`；通过后再 `validate_dataset(..., strict=False, ...)` 取完整报告；`TrainingRunner.preflight` 实例方法包装。`dataset` 在规格错时为 `None`。 |
| `app/integrated_app/routes/train_routes.py` | 新增 `POST /api/train/jobs/preflight`（`TrainJobRequest` + `check_resolution / min_size / max_size` query，返回 `preflight_spec(...)` 结果）。 |
| `scripts/preflight_train_job.py` | 新建 CLI：`--name/--model-path/--extras-path/--dataset-folder/--check-resolution/--min-size/--max-size/--json`，构造 `TrainJobSpec` 调 `preflight_spec`，可读文本 / JSON 输出，rc=0/1。 |
| `tests/test_train_routes.py` | +3 例（`test_preflight_ok` / `test_preflight_reports_dataset_problem` / `test_preflight_reports_spec_error`）。 |

**实测**（CLI / 端点）：
- 规格 OK + 数据集 OK（默认不解码）→ `[OK] 通过` rc=0，`dataset.ok=True`。
- 数据集缺 caption（移除同名 .txt）→ `[FAIL] 未通过`，`dataset.missing_caption` 含 1 项，rc=1。
- 坏 name（含空格）→ 规格错，`spec_errors` 非空，`dataset=None`，rc=1。

**踩坑实录（GOTCHAS #50）**：初版把 `def preflight_spec(` 误写在模块级（column 0），恰好落在
`_require_backend` 方法之后、`submit` 方法之前——这导致 `TrainingRunner` 类在 `_require_backend` 处提前
关闭，`submit / load / status / cancel / ... / _forget` 全部沦为 `preflight_spec` 内部的不可达嵌套函数，
`dir(TrainingRunner)` 实测缺失 `cancel` / `preflight` 等全部类方法，复跑测试 9 FAILED
（`'TrainingRunner' object has no attribute 'cancel'`）。修复：把 `preflight_spec` 整体搬到
`TrainingRunner` 类结束之后（`_forget` 之后、`aitk_root_env` 之前）成为真正模块级函数，让 `submit` 起的方法
重新归属类体。教训：在类体内新增模块级符号 / 函数时，务必核对缩进层级，`grep -nE "^(class |def )"`
是快速验证类-函数归属的硬手段。

## 验收（本 P3 立项目标）

- [x] T-34 决策记录（本文件 + README 索引）。
- [x] 训练后端选型 POC（2026-10-02 源码级实证）：路径 A（AI-Toolkit）胜出；路径 B 前提被证伪；sd-scripts 对 Z-Image 不适用。
- [x] T-22（Caption / Tagger 评估，改为不引入 SDNext，用 AI-Toolkit 内置 captioner + dataset_tools）。
- [x] T-28（sd-scripts LUMINA 深读：只吃 NextDiT_2B，且 `strict=False` 会静默错配）。
- [x] T-12 代码接入：安装 AI-Toolkit → 最小 Z-Image LoRA job 跑通（rc=0）→ 产出 LoRA 能被 `native/lora.py` 加载（180 patches / 0 条未加载告警）。
- [x] T-13 轻前端 / 状态回写薄层（2026-10-03：编排薄层实装 + 真跑实证 2 步 job rc=0；**UI 面采用 AI-Toolkit 自带前端，本仓只做编排与状态回写**，见「T-13 编排薄层实装记录」）。
- [x] T-14 数据准备（2026-10-03，三块）：① 文件级校验 `training/dataset.py` + `/api/train/datasets/validate` + `scripts/validate_lora_dataset.py`（真实 T-12 数据集 CLI rc=0、坏数据集 rc=1）；② 解码级预检（`check_resolution` 真实解码，暴露损坏图像 + 报告真实尺寸 + 标出分辨率越界，默认不跑保持向后兼容）；③ 提交前综合自检 `preflight_spec`（`POST /api/train/jobs/preflight` + `scripts/preflight_train_job.py`，聚合规格校验 + 数据集可用性，不阻塞 submit 的「立即返回 job_id」契约）。
- [ ] T-14~T-16（数据准备 / 采样 / 元数据）随 T-12 推进。
