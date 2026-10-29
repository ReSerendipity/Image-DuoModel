# 发布 / 回滚 / SLA 规范（Release Governance）

> **来源与权威**：公共条款一律遵循 `ReSerendipity/.github` 的 `REPOSITORY_GUIDELINES.md` §10（发布 / 分发统一规范）与 `RELEASE_GOVERNANCE_TEMPLATE.md`；本文件只填本仓特有项，不改写、不抵触 §10 公共条款。
> **适用范围**：Image-DuoModel 全项目发布、回滚与运行稳定性。

---

## 0. 远端优先（根原则，不可改写）

发布链的构建、打包、扫描、上传、推送**全部在 GitHub Actions 远端完成**；本地只做三件事：改版本位、落 CHANGELOG、`git tag` + `git push`。本地不执行打包 / 镜像构建 / 发布上传。

与 §10.1 一致的其余根原则（不再展开）：tag 驱动（`push: tags: v*` 触发发布链）；产物须可校验（`SHA256SUMS.txt` + 桌面壳 Ed25519 签名）；**不使用 GPG 分离签名**（2026-10-18 裁决撤掉）。

## 1. 版本号规范

- 遵循 **SemVer** `MAJOR.MINOR.PATCH`；预发布用 `-alpha.N` / `-beta.N` / `-rc.N`（同 §10.2）。
- **唯一权威版本位**：`config.yaml` 顶层 `version`（当前 **2.1.1**，与应用版本基线 `v2.1.1` 对齐；基线由 release-please 托管的 `version.txt` 承载，见下）。
- 必须同步的其它版本位：
  - `CHANGELOG.md`（发版节标题 `[X.Y.Z] - YYYY-MM-DD`）
  - `AGENTS.md` 顶部「对应项目版本」（本地维护、不入库，见家族规范 §7）
- 版本位漂移校验入口：`tests/test_version_consistency.py`——当前仅扫描源码中硬编码旧版本（0.1.0 / 0.0.1）；**跨位点一致性自动对账 待定（负责人 + 触发条件：补全 `version.txt` / `config.yaml` / `CHANGELOG.md` 三点的断言）**。
- **自动化方式（2026-10-18 已恢复自动）**：`release-please.yml` + `release-please-config.json` + `.release-please-manifest.json` 三件套已恢复（manifest 与 `version.txt` 基线均为 `2.1.1`），采用 `release-type: simple`。
- **位点分工**：`version.txt` 由 release-please **自动**改写并据此打 tag；`config.yaml` 顶层 `version` **绝不交给 release-please**（遵从本仓既有约束），须在合并 release PR 时**人工补齐**；tag 打出后由 `release.yml` 在远端构建产物。
  > 说明（2026-10-18）：release-please 已按上条恢复；「哪些位自动改、哪些位必须人补」已在上条写明。远端 `v1.5.0` / `v1.5.1` 为 release-please 时代历史产物，原地保留、不再延续、不作为版本基线；当前版本基线为 `v2.1.1`。

## 2. CHANGELOG 管理

（公共条款，同 §10.2）遵循 **Keep a Changelog**：`Added / Changed / Deprecated / Removed / Fixed / Security`；每次合入 `main` 在 `[Unreleased]` 追加，`feat→Added`、`fix→Fixed`、`refactor→Changed`；发版时 `[Unreleased]` → `[VERSION] - YYYY-MM-DD`。

## 3. 发布流程（远端）

公共流程同 §10.2 / 模板 §3，本仓特有项：

1. 确认 `[Unreleased]` 条目完整
2. 同步版本位：release PR 自动改 `version.txt` 后，**人工补** `config.yaml` + `CHANGELOG.md`（+ 本地 `AGENTS.md`）使其一致
3. 版本依赖：仅 `pyproject.toml` 声明源；依赖改动补 `requirements.txt` / `requirements-lock.txt`
4. 本地打 tag 并推送：`git tag v<X.Y.Z>` → `git push origin v<X.Y.Z>`
5. 远端凭 tag 触发 **`release.yml`** 构建产物（release-please 自动开 Release PR 并打 tag，见 §1；应急仍可手动 `git tag`）
6. 远端建 Release 并挂资产 → 盯 `gh run list` 到终态；红了当场修或 revert 止损

## 4. 分发产物与完整性

公共条款同 §10.3（容器镜像推 ghcr.io、tag 取 semver+sha、禁 floating `latest`、Trivy 阻断、provenance+sbom 推荐、无 GPG）。本仓当前产物：

| 产物 | 构建位置 | 标签 / 命名 | 完整性手段 |
|---|---|---|---|
| 容器镜像 `image-duomodel:<tag>` | 远端（release.yml / deploy.yml，ubuntu-latest） | 不可变 semver（`build_metadata.json` 产出的 image_tag）+ git sha | SBOM（`release/sbom.json`）+ build metadata；**推 ghcr.io 待定（负责人 + 触发条件：阶段 B 评估 registry 迁移）** |
| SBOM + 构建元数据 | 远端（release.yml） | `release/sbom.json`、`release/build_metadata.json` | 随 Release 资产发布 |
| 桌面增量包（Windows） | 远端（release.yml `desktop-package`，windows-latest） | `release/packages/app-v<X.Y.Z>.zip` | **Ed25519 签名**（`MANIFEST_SIGNING_KEY_B64` Secrets 注入，`verify_manifest_signature_ed25519` 验签） |
| 便携包（Windows 全量） | **当前本机**（`scripts/pack_portable.ps1`），与远端优先目标态有差距 | 待定（负责人 + 触发条件：阶段 B 评估迁 Windows runner 远端构建） | 随打包流程补 `SHA256SUMS.txt` |

- **不使用 GPG 分离签名**（2026-10-18 裁决，同 §10.3 / §10.6）；完整性由 Ed25519 签名 + `SHA256SUMS.txt` 承担。
- `SHA256SUMS.txt` 自动生成步骤：**待定（负责人 + 触发条件：阶段 B 在 release.yml 末尾补生成）**。
- Trivy 镜像扫描：**未配置，待定（负责人 + 触发条件：阶段 B 加 Trivy 阻断步骤）**。
- provenance + sbom：SBOM 已产出（`sbom.json`）；`provenance: true` **待定（负责人 + 触发条件：阶段 B 切 `docker/build-push-action` 时开启）**（当前未用该 action，走本地 `docker build`）。

## 5. 回滚

- **判定阈值**（满足任一即触发，本仓特有）：
  1. 生成成功率 / 首页可用性跌破阈值
  2. readiness 持续 degraded（引擎加载失败 / 显存熔断）
  3. P0/P1 安全告警（路径穿越 / 权重完整性校验失败）
  4. 关键 API 契约断裂流入生产
- **执行**：公共条款同 §10.2——`git revert <bad-release-commit>`（保历史、可再 forward），人工 push 后重启服务；不可变产物按上版 tag 重推。本仓特有：
  - 配置回滚：`git revert` 对应 `config.yaml` 提交；容器以只读挂载 `config.yaml` + 环境变量注入密钥。
  - 权重回滚：`pretrained_models/` / `model/` 禁区，SHA-256 复验（`app/integrated_app/security/weight_integrity.py`）后再动；永不在运行时改权重。
  - 容器回滚：`scripts/deploy/bluegreen.sh rollback`（deploy.yml promotion 失败时自动调用）。
- **破坏性动作红线**：重指向 / 删除 tag、移动任何远端 ref 须仓库所有者单独授权（同 §10.2）。
- **回滚后验证**（闭环）：
  1. `GET /api/health` 返回健康状态；`GET /api/system/health` 桌面壳就绪
  2. Web UI（端口 8288）渲染正常
  3. `python scripts/post_deploy_smoke.py --base-url <url> --timeout 15 --generation-timeout 120`
  4. `pytest tests/smoke/test_startup_smoke.py`
  5. 观察关键指标回升、无新告警

## 6. SLA / 错误预算

- 目标可用性 **≥99.5%（月度）** ⇒ 错误预算 **≈3.6h/月**。
- 超出错误预算：冻结非紧急发布、优先稳定项、复盘。
- liveness = 内存级探针（不碰 DB/GPU）；readiness = 深度检查（模型 + DB + GPU）。

## 7. 部署目标

公共条款同 §10.4（远端可完成的一律远端；本地运行边界内的不做远端化改造）。本仓部署目标：

- **GitHub Pages**：`demo/` 静态站，`pages-deploy.yml` push main 触发，自动部署。
- **Staging / Production 容器**：`deploy.yml` 经 SSH 到 GPU 主机，blue-green 双槽位部署；staging 需 post-deploy smoke 通过后方可晋级 production（production 需 GitHub environment 人工批准）。未配置 staging secrets 时走演练模式（不具备晋级资格）。
- **桌面分发**：Windows 增量包经 GitHub Release 资产下载；Tauri 壳构建与签名在远端完成，密钥经 Actions Secrets 注入。

## 8. 发布前检查清单

（公共项同模板 §7；本仓命令如下）

- [ ] 版本位全部同步（`config.yaml` + `CHANGELOG.md` + 本地 `AGENTS.md`）
- [ ] CHANGELOG `[Unreleased]` 已改版本 + 日期
- [ ] 全量 `pytest tests/ --cov=app/integrated_app --cov-fail-under=65` 通过
- [ ] `ruff` / `ruff-format` 全绿
- [ ] `scripts/precheck.ps1 -Full` 通过；`python scripts/check_spec_refs.py` 退出码 0
- [ ] 引擎 / 权重改动时 `scripts/check_config_refs.py` 对账通过
- [ ] **本地未产出任何发布交付物**（全部远端构建，同 §0）
- [ ] tag 已推送

## 9. 镜像名变更记录

- **变更日期**：2026-10-21
- **旧名**：`image-multimodel`
- **新名**：`image-duomodel`（与仓名 `Image-DuoModel` 对齐，全小写连字符）
- **影响范围**：`docker-compose*.yml`、`.github/workflows/{deploy,release,security}.yml`、`scripts/build_release_metadata.py`、`docs/ops/release_artifacts.md`、`README.md`、本文件
- **GHCR 包处置**：
  - 历史 GHCR 包（`ghcr.io/.../image-multimodel:*`）**保留不删除**，可继续按旧 digest 拉取
  - 首次以新名 `image-duomodel` 发布时会在 GHCR 生成新包，旧包 tag 不迁移
  - 生产部署通过 `IMAGE_DIGEST` 固定 digest，镜像名变更不影响按 digest 拉取的稳定性
- **未改**：`app/integrated_app/mcp_server.py` 的 `MCP_SERVER_NAME` 常量（MCP 协议逻辑名，非 Docker 镜像名，改它可能影响 MCP 客户端连接，另行决策）
