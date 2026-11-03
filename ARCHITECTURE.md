# 架构 — Image-DuoModel

> 治理定位：`delivery=release`、`lifecycle=maintenance`（`governance/desired-state.json`）。
> 本文按 2026-11-03 的实际目录结构生成；数据流与边界须由维护者在实现变更时同步复核。

## 1. 定位

[中文](#中文) | [English](#english)

## 2. 组件与依赖方向

```text
应用层：app/ (136)、desktop/ (70)
工具层：scripts/ (67)
资产层：model/ (5)
测试层：tests/ (170)
支撑层：docs/ (83)、.github/ (29)
其他层：workflows/ (27)、demo/ (14)、.githooks/ (10)、.qoder/ (1)、release/ (1)
根级层：根级文件 (29)
```

| 组件 | 目录 | 文件数 | 代表文件 |
|---|---|---|---|
| `tests` | `tests/` | 170 | `tests/__init__.py`, `tests/capture-screenshots.js`, `tests/conftest.py` |
| `app` | `app/` | 136 | `app/clean_launch.py`, `app/downloads_catalog.json`, `app/install.bat` |
| `docs` | `docs/` | 83 | `docs/AGENT_CONSTRAINTS.md`, `docs/CODING_STANDARDS.md`, `docs/DATABASE_SCHEMA.md` |
| `desktop` | `desktop/` | 70 | `desktop/installer/7za.exe`, `desktop/installer/killimgmulti.ps1`, `desktop/installer/pretrained_models_README.md` |
| `scripts` | `scripts/` | 67 | `scripts/_inject_wf_version.py`, `scripts/_poll_task.py`, `scripts/analyze_workflows.py` |
| 根级文件 | `/` | 29 | `.dockerignore`, `.editorconfig`, `.env.example` |
| `workflows` | `workflows/` | 27 | `workflows/blueprints/Edit/flux2_klein_edit.json`, `workflows/blueprints/Edit/qwen_2_1_edit.json`, `workflows/blueprints/Edit/qwen_edit_2511.json` |
| `demo` | `demo/` | 14 | `demo/README.md`, `demo/assets/gallery/gen-01.jpg`, `demo/assets/gallery/gen-02.jpg` |
| `.githooks` | `.githooks/` | 10 | `.githooks/README.md`, `.githooks/commit-msg`, `.githooks/install.sh` |
| `model` | `model/` | 5 | `model/README.md`, `model/loras/put_loras_here`, `model/text_encoders/put_text_encoders_here` |
| `.qoder` | `.qoder/` | 1 | `.qoder/rules/agent-baseline.md` |
| `release` | `release/` | 1 | `release/.gitkeep` |

依赖方向：入口层（应用 / 页面）调用领域层（业务模块），领域层依赖基础设施层（脚本、配置、模型资产）；反向引用不允许。

## 3. 数据流

上传图片 → 后端推理服务 → 前端展示与导出；桌面壳承载本地运行。

## 4. 外部依赖

| 依赖 | 用途 | 不可用时 |
|---|---|---|
| Python 依赖（requirements.txt） | 推理后端 | 无法处理图像 |
| Node.js / npm | 桌面壳与测试 | 仅剩 Web 前端 |

## 5. 边界与非目标

- 发布链只走 §10：远端优先、tag 驱动、资产附 `SHA256SUMS.txt`。
- 分发产物由 CI 生成，不入库。
- 不入库：密钥 / token / 口令 / 连接串、本机绝对路径、`local/` 与 `AGENTS.md`、构建产物。
- 治理正文只在 `ReSerendipity/.github/governance`，本仓不复制规则正文。

## 6. 变更影响面

| 改什么 | 必须同步 | 由谁校验 |
|---|---|---|
| 目录结构 / 入口 | 本文「组件与依赖方向」与「数据流」 | 维护者 |
| CI 与门禁 | 本仓 `README.md` 的测试命令；治理仓 §20 远端载体口径 | `audit-drift.py` |
| 依赖清单 | 锁文件与 `.github/dependabot.yml` 的生态段 | Dependabot / `lock-consistency` |
| README 展示图 | §8.1 真实性红线（图必须来自真实运行） | 治理仓 `readme-image-provenance` |
