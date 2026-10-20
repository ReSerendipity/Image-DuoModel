# 完成定义（Definition of Done）

> **来源**：家族通用 DOD 模板 `.spec_audit/family_DOD.md`（源自 SpiritPal definition-of-done.md 泛化；该家族模板已归档，2026-09-17 起按本仓本地化内容维护），本仓本地化。
> **适用范围**：Image_MultiModel 全项目所有功能开发任务。

---

## 0. DoD 等级

| 等级 | 适用场景 | 要求 |
|------|---------|------|
| **Full DoD** | 正式功能开发 / 大型 PR | 全部检查类 |
| **Lite DoD** | Bug 修复 / 小优化 | 代码完成 + 测试覆盖 + 构建验证 |
| **Hotfix DoD** | 紧急线上修复 | 代码完成 + 构建验证（事后补齐其余） |

> 判定「完成」必须先跑对应等级清单；不满足不得标注完成、不得提交 main。

## 1. 代码完成

- [ ] 功能已实现，覆盖 PRD / Spec 定义的所有验收标准（AC）
- [ ] `ruff` / `ruff-format` 通过（0 error；`pyproject.toml` line-length=120）
- [ ] 无调试残留（`print()` / `breakpoint()` / `pdb`，诊断日志除外需标记）
- [ ] 未引入跨层违规引用（遵守 AGENTS.md §2.3 分层约束 + §3 禁区表）
- [ ] 新增路由定义了模块级 `router`（`pkgutil` 自动发现）
- [ ] 新增功能已按 AGENTS.md §9 SOP 完成

## 2. 测试覆盖

- [ ] 新增/修改函数有对应 pytest 单测（`tests/` 扁平 + 分类子目录）
- [ ] 覆盖正常路径 + 边界条件 + 异常场景
- [ ] 全量 `pytest tests/ --cov=app/integrated_app --cov-fail-under=65 -q` 通过（不新增失败）
- [ ] GPU 依赖模块（native/ seedvr2_service/ preprocessors）在无 GPU 环境有 mock 覆盖，避免 CI 全 skip

## 3. 文档同步

- [ ] `AGENTS.md` 已同步（目录结构 / 模块地图 / 版本号 / 配置 / i18n）
- [ ] 新增模块在 AGENTS.md §3.1 有对应条目
- [ ] 踩坑已追加到 AGENTS.md §8 Known Gotchas（触发/现象/做法/日期）
- [ ] `CHANGELOG.md` 已记录变更（type 对应 Added/Fixed/…）
- [ ] `python scripts/check_spec_refs.py` 退出码 0（无幻影/死链/假门禁）

## 4. 国际化

- [ ] 新增 UI 文案已在 5 语言 JSON 同步（`app/integrated_app/locales/` 下 zh / zh-tw / en / ja / ko）
- [ ] 缺失 key 遵循回退逻辑，无真值空串反模式

## 5. 构建 & 验证

- [ ] 完整构建/启动通过：`python app/clean_launch.py` 或 `python -m uvicorn app.integrated_app.app_server:app`（端口 8288）
- [ ] 手动验证功能按预期工作（不仅是测试通过）
- [ ] 涉及引擎/权重改动时，`config.yaml → engines.<key>.workflow_file` 仍置空、`check_config_refs.py` 对账通过

## 6. 安全 & 隐私

- [ ] 无硬编码密钥 / API Key / 敏感常量（走 `.env.example`）
- [ ] 新增路由遵守安全中间件（auth / csrf / rate_limit / path_guard / content_filter）
- [ ] 未新增静默吞错（`except: pass` 等）
- [ ] 涉及禁区目录（comfy_kernel/ 权重/ 安全模块/ 发布）走人工确认流程

## 7. 可追溯性

- [ ] 变更有影响评估（破坏性 / 非破坏性）
- [ ] 涉及配置变更时：`config.yaml` 结构同步 Pydantic 模型 + `check_config_refs.py`
- [ ] 涉及版本：`config.yaml` 顶层 `version` 与 AGENTS.md「对应项目版本」一致
- [ ] 涉及 i18n / 引擎登记 / CI 变更时，AGENTS.md 自检清单逐项核对
