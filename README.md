# Image DuoModel

> 多模型 AI 图像生成平台：进程内原生引擎复用 ComfyUI 源码，在同一个 Web UI 中接入 Z-Image Turbo / Qwen-Image 2.1 Edit / Flux.2 Klein。

![CI](https://github.com/ReSerendipity/Image-DuoModel/actions/workflows/ci.yml/badge.svg)
[![Release](https://img.shields.io/github/v/release/ReSerendipity/Image-DuoModel?label=release)](https://github.com/ReSerendipity/Image-DuoModel/releases)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-Apache%202.0-green)
![Last commit](https://img.shields.io/github/last-commit/ReSerendipity/Image-DuoModel)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-orange)](https://github.com/ReSerendipity/Image-DuoModel/pulls)

[中文](#中文) | [English](#english)

---

## 中文

### 项目简介

**Image DuoModel** 是一个面向本地运行的多模型 AI 图像生成工作台。自 v1.2.0 起，平台**完全脱离外部 ComfyUI 进程**，通过 `sys.path` 注入复用项目内 `comfy_kernel` 源码，在同一进程内完成「加载 → 编码 → 采样 → 解码」。它以单页 Web UI 统一接入三个核心扩散引擎：

- **Z-Image Turbo** —— 高速文生图（默认引擎，Apache-2.0 权重）
- **Qwen-Image 2.1 Edit** —— 指令式图像编辑（支持参考图）
- **Flux.2 Klein 9B** —— 照片级高质量文生图

另注册了 4 个进阶实验引擎（Qwen3-VL 看图、Qwen-Image 文生图、Krea2-turbo、FLUX.1-dev），按需加载。

> 治理规范：[ReSerendipity/.github/governance](https://github.com/ReSerendipity/.github/tree/main/governance)。参与贡献请遵循组织级贡献指南（Conventional Commits + DCO 签名）。

### 核心特性

- **原生进程内引擎**：复用 `comfy_kernel/` + aki-v3 自定义节点，单进程推理，无需启动外部 ComfyUI。
- **声明式多引擎**：`config.yaml → models.engines.*` 注册，同一 `NativeEngine` 框架下内置 7 个引擎。
- **六层 LoRA 叠加 + 显存预检**：推理前自动估算 VRAM，推荐 FP8/FP16 与 batch chunk。
- **异步任务队列 + SSE**：批量生成、任务取消、断点续跑，进度实时推送到前端。
- **Eses 双图对比**：原图 vs 对比图水平 / 垂直 / 滑动三种拼接方式。
- **历史与预设**：SQLite 历史库支持搜索筛选；常用参数组合可存为预设一键复用。
- **DCT 频域水印**：所有输出图自动嵌入 `product_id · task_id · timestamp` 水印，可溯源。
- **安全加固**：PathGuard 路径防护、CSRF、速率限制、关键模块 SHA256 完整性自检。
- **五语言界面**：中文、繁体中文、英文、日文、韩文。

### 界面展示

> 以下截图在无 GPU 的云端环境实拍（CPU 后端、引擎未加载、未放置权重），图库与历史因此呈空态；实际生成画面请在配好 NVIDIA GPU 与权重的本机使用。

**生图工作台主页** —— Prompt 输入、引擎切换、最近生成结果一览：

![主界面](https://gcore.jsdelivr.net/gh/ReSerendipity/Image-DuoModel@main/docs/assets/readme-image-duomodel-1-main.png)

**高级参数面板** —— CFG / Steps / 尺寸 / Seed / 六层 LoRA 等 22 项参数即时生效：

![高级参数](https://gcore.jsdelivr.net/gh/ReSerendipity/Image-DuoModel@main/docs/assets/readme-image-duomodel-2-params.png)

**图片展示** —— 全部 / 原图 / 超分 / 对比图分类浏览生成产物：

![结果展示](https://gcore.jsdelivr.net/gh/ReSerendipity/Image-DuoModel@main/docs/assets/readme-image-duomodel-3-results.png)

**对比与显存预留设置** —— Eses 双图对比开关、对比轴（h/v/s）与 ReservedVRAM 显存预留：

![对比与显存预留](https://gcore.jsdelivr.net/gh/ReSerendipity/Image-DuoModel@main/docs/assets/readme-image-duomodel-4-compare.png)

**历史记录** —— SQLite 任务历史，支持搜索、状态筛选、引擎筛选与详情：

![历史记录](https://gcore.jsdelivr.net/gh/ReSerendipity/Image-DuoModel@main/docs/assets/readme-image-duomodel-5-history.png)

**系统架构** —— 从浏览器到进程内原生引擎的分层结构：

![架构图](https://gcore.jsdelivr.net/gh/ReSerendipity/Image-DuoModel@main/docs/assets/readme-image-duomodel-6-architecture.svg)

### 快速开始

#### 系统要求

| 项目 | 要求 |
|---|---|
| 操作系统 | Windows 10/11（推荐）/ Linux |
| GPU | NVIDIA CUDA GPU，推荐 8GB+ 显存 |
| Python | 3.10+（推荐 3.12），或使用内置 WinPython |
| 推理引擎 | 进程内原生引擎，**无需外部 ComfyUI 进程** |

#### 安装与启动

```bat
:: 1. 安装 Python 3.10+（安装时勾选 Add Python to PATH）
python --version

:: 2. 双击运行安装脚本（自动安装 PyTorch CUDA 版与全部依赖）
install.bat

:: 3. 确认模型权重已放入 pretrained_models/（portable 模式，不随仓库分发）

:: 4. 启动
start.bat
```

浏览器自动打开 `http://127.0.0.1:8288`（端口可在 `config.yaml → server.port` 修改）。

#### Docker

```bash
docker build -t image-duomodel .
docker run --gpus all -p 8288:8288 \
  -v ./pretrained_models:/app/pretrained_models \
  -v ./outputs:/app/outputs \
  image-duomodel
```

#### 最小验证

启动后访问健康检查接口：

```bash
curl http://127.0.0.1:8288/api/health
```

返回 `{"status":"ok",...}` 即后端就绪；引擎状态为 `unloaded` 属正常——引擎在首次生成时按需加载。

### 使用示例

提交一次文生图任务：

```bash
curl -X POST http://127.0.0.1:8288/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"a peaceful mountain lake at dawn","engine":"z_image_turbo_native"}'
```

主要 API：

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/health` | GET | 后端 / 引擎 / 队列 / GPU 状态 |
| `/api/events` | GET (SSE) | 实时事件流 |
| `/api/generate` | POST | 提交生成任务 |
| `/api/engine/engines` | GET | 引擎列表 |
| `/api/engine/load` | POST | 加载引擎 |
| `/api/tasks` | GET | 任务列表 |

### FAQ

**Q1：必须装 ComfyUI 吗？**
不需要。v1.2.0 起走进程内原生引擎，复用项目内 `comfy_kernel` 源码，单进程完成推理。

**Q2：没有 GPU 能启动吗？**
Web UI 本身可以在 CPU 环境启动浏览界面与配置；实际图像生成需要 NVIDIA CUDA GPU。

**Q3：模型权重在哪里？**
权重不随仓库分发。将对应引擎的权重放入 `pretrained_models/`（portable 模式），路径与精度在 `config.yaml → models.engines.<key>` 配置。

**Q4：商用有什么限制？**
项目代码为 Apache-2.0。但模型权重许可各异：Z-Image Turbo 可商用；Qwen-Image 2.1 Edit、Flux.2 Klein 9B 等为研究/非商业许可，商用前请参阅各模型卡与 [NOTICE](NOTICE)。

**Q5：输出图可以追溯吗？**
可以。所有输出图自动嵌入 DCT 频域水印，用 `python scripts/verify_watermark.py <png>` 校验。

### 文档与治理

- [CHANGELOG.md](CHANGELOG.md) —— 版本变更记录
- [SECURITY.md](SECURITY.md) —— 安全策略与漏洞上报
- [docs/AGENT_CONSTRAINTS.md](docs/AGENT_CONSTRAINTS.md) —— 引擎与 comfy_kernel 架构硬约束
- [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md) —— 发布检查清单

### 贡献 / 安全 / 支持

欢迎 Issue 与 PR。提交前请启用仓库钩子 `git config core.hooksPath .githooks`，并通过 `python -m pytest -q` 与 `python -m ruff check app tests`。安全问题请按 [SECURITY.md](SECURITY.md) 私下上报。

### 许可证

本项目代码采用 [Apache License 2.0](LICENSE)。模型权重的许可清单见 [NOTICE](NOTICE) 与上表说明。

---

## English

### Introduction

**Image DuoModel** is a local-first, multi-model AI image generation workbench. Since v1.2.0 it runs a **fully in-process native engine** — it injects the project's own `comfy_kernel` sources via `sys.path` and performs loading, encoding, sampling and decoding in a single process, with **no external ComfyUI process required**. One single-page Web UI fronts three core diffusion backends:

- **Z-Image Turbo** — fast txt2img (default engine, Apache-2.0 weights)
- **Qwen-Image 2.1 Edit** — instruction-driven image editing (reference image supported)
- **Flux.2 Klein 9B** — photorealistic, high-quality txt2img

Four additional experimental engines are registered on demand (Qwen3-VL visual chat, Qwen-Image txt2img, Krea2-turbo, FLUX.1-dev).

> Governance: [ReSerendipity/.github/governance](https://github.com/ReSerendipity/.github/tree/main/governance). Follow the org contribution guide (Conventional Commits + DCO sign-off).

### Key Features

- **In-process native engine** — reuses `comfy_kernel/` + aki-v3 custom nodes; single-process inference.
- **Declarative multi-engine registry** — 7 engines under one `NativeEngine`, configured in `config.yaml → models.engines.*`.
- **6-layer LoRA stacking + VRAM pre-check** — estimates VRAM and recommends FP8/FP16 and batch chunks.
- **Async task queue + SSE** — batch generation, cancellation, checkpoint resume, live progress.
- **Eses dual-image compare** — horizontal / vertical / slider layout of original vs. comparison image.
- **History & presets** — SQLite history with search/filter; reusable parameter presets.
- **DCT frequency-domain watermark** — embeds `product_id · task_id · timestamp` into every output.
- **Hardened security** — PathGuard, CSRF, rate limiting, SHA256 integrity self-check.
- **5 UI languages** — zh, zh-TW, en, ja, ko.

### Screenshots

> These screenshots were captured on a CPU-only cloud build (no GPU, engines unloaded, no weights), so the gallery and history show their empty state. Generate real images on a machine with an NVIDIA GPU and the model weights installed.

**Generation workbench home** — prompt input, engine switch, recent generations:

![Main UI](https://gcore.jsdelivr.net/gh/ReSerendipity/Image-DuoModel@main/docs/assets/readme-image-duomodel-1-main.png)

**Advanced parameters** — CFG / Steps / size / seed / 6-layer LoRA, 22 settings applied live:

![Advanced params](https://gcore.jsdelivr.net/gh/ReSerendipity/Image-DuoModel@main/docs/assets/readme-image-duomodel-2-params.png)

**Gallery** — browse outputs by all / original / upscale / compare:

![Results gallery](https://gcore.jsdelivr.net/gh/ReSerendipity/Image-DuoModel@main/docs/assets/readme-image-duomodel-3-results.png)

**Compare & VRAM reservation settings** — Eses dual-image toggle, compare axis (h/v/s), and ReservedVRAM:

![Compare settings](https://gcore.jsdelivr.net/gh/ReSerendipity/Image-DuoModel@main/docs/assets/readme-image-duomodel-4-compare.png)

**History** — SQLite task history with search, status and engine filters:

![History](https://gcore.jsdelivr.net/gh/ReSerendipity/Image-DuoModel@main/docs/assets/readme-image-duomodel-5-history.png)

**Architecture** — layered view from browser to the in-process native engine:

![Architecture](https://gcore.jsdelivr.net/gh/ReSerendipity/Image-DuoModel@main/docs/assets/readme-image-duomodel-6-architecture.svg)

### Quick Start

#### Requirements

| Item | Requirement |
|---|---|
| OS | Windows 10/11 (recommended) / Linux |
| GPU | NVIDIA CUDA GPU, 8GB+ VRAM recommended |
| Python | 3.10+ (3.12 recommended), or bundled WinPython |
| Engine | In-process native engine; **no external ComfyUI** |

#### Install & Run

```bat
:: 1. Install Python 3.10+ (check "Add Python to PATH")
python --version

:: 2. Run the installer (installs PyTorch CUDA + all deps)
install.bat

:: 3. Place model weights under pretrained_models/ (not shipped in repo)

:: 4. Launch
start.bat
```

Open `http://127.0.0.1:8288` (configurable in `config.yaml → server.port`).

#### Docker

```bash
docker build -t image-duomodel .
docker run --gpus all -p 8288:8288 \
  -v ./pretrained_models:/app/pretrained_models \
  -v ./outputs:/app/outputs \
  image-duomodel
```

#### Minimal smoke test

```bash
curl http://127.0.0.1:8288/api/health
```

`{"status":"ok",...}` means the backend is ready. Engines report `unloaded` until first use — they load on demand.

### Example

Submit a txt2img task:

```bash
curl -X POST http://127.0.0.1:8288/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"a peaceful mountain lake at dawn","engine":"z_image_turbo_native"}'
```

Key API endpoints:

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | backend / engine / queue / GPU status |
| `/api/events` | GET (SSE) | real-time event stream |
| `/api/generate` | POST | submit a generation task |
| `/api/engine/engines` | GET | list engines |
| `/api/engine/load` | POST | load an engine |
| `/api/tasks` | GET | task list |

### FAQ

**Q1: Do I need to install ComfyUI?**
No. Since v1.2.0 the app uses an in-process native engine that reuses the project's own `comfy_kernel` sources.

**Q2: Can I run the UI without a GPU?**
The Web UI and config screens can start on CPU; actual image generation requires an NVIDIA CUDA GPU.

**Q3: Where do the model weights go?**
Weights are not shipped. Place them under `pretrained_models/` (portable mode); paths and precision are configured in `config.yaml → models.engines.<key>`.

**Q4: What about commercial use?**
Project code is Apache-2.0. Model weights vary: Z-Image Turbo is commercial-friendly; Qwen-Image 2.1 Edit and Flux.2 Klein 9B are research/non-commercial licenses. Read each model card and [NOTICE](NOTICE) before commercial use.

**Q5: Are outputs traceable?**
Yes. Every output carries a DCT frequency-domain watermark; verify with `python scripts/verify_watermark.py <png>`.

### Docs & Governance

- [CHANGELOG.md](CHANGELOG.md) — release history
- [SECURITY.md](SECURITY.md) — security policy and reporting
- [docs/AGENT_CONSTRAINTS.md](docs/AGENT_CONSTRAINTS.md) — engine/kernel hard constraints
- [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md) — release checklist

### Contributing / Security / Support

Issues and PRs welcome. Before submitting, enable hooks with `git config core.hooksPath .githooks` and pass `python -m pytest -q` plus `python -m ruff check app tests`. Report security issues privately per [SECURITY.md](SECURITY.md).

### License

Project code is licensed under [Apache License 2.0](LICENSE). Model weight licenses are listed in [NOTICE](NOTICE) and described above.
