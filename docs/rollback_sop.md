# 回滚 SOP（自动化回滚 / 版本化回滚）

> **来源**：家族泛化自 TTS_MultiModel `docs/rollback_sop.md`，本仓本地化。
> 配套：`docs/SRE_RUNBOOK.md`、`docs/release-governance.md`。
> 原则：**先止血（快速恢复服务），再定位（事后复盘）**。MTTR 目标 < 30 分钟。

## 0. 前置约定

- 版本位：`config.yaml` 顶层 `version` + `AGENTS.md` + `CHANGELOG.md` 三处一致。
- 回滚 = 将代码/配置/权重回退到上一个稳定版本。

## 1. 决策：何时回滚

满足任一即触发：

1. 上线后生成成功率跌破 SLO 阈值；
2. readiness 持续 degraded（引擎无法加载 / 显存熔断）；
3. P0/P1 安全告警（未授权访问 / 权重完整性校验失败）；
4. 关键 API 契约断裂流入生产。

## 2. 回滚步骤

```bash
# 查看最近提交，确认回退目标
git log --oneline -10

# 在当前分支生成一个「反向提交」回退到目标版本
git revert <bad_release_commit>
# 默认只生成提交，不自动 push；需人工 git push 后重启服务
```

## 3. 镜像/配置回滚

- 容器化：切镜像 digest 或 `docker compose` 重拉上一版本 tag，禁止 `:latest`。
- 配置：`git revert` 对应 `config.yaml` 提交并重新挂载；只读挂载配置 + 环境变量注入密钥。

## 4. 回滚后验证（闭环）

1. `GET /api/health` 返回 ok；
2. 打开 Web UI（8288）确认渲染；
3. 最小 smoke：`pytest tests/smoke/`；
4. 观察生成成功率回升、无新告警。

## 5. 数据库 / 历史库回滚说明

- `data/history.db`（SQLite）**不随代码回滚**；旧版本代码可继续读写（`history_db.py` 有迁移兼容，若有）。
- 回滚前备份：`cp data/history.db data/history.db.bak-$(date +%s)`。

## 6. 权重回滚

- `pretrained_models/` / `model/` 为权重禁区，禁止运行时修改。
- 权重回滚需人工确认 + `app/integrated_app/security/weight_integrity.py` 的 SHA-256 复验。

## 7. 事后（Postmortem）

回滚完成后 24 小时内产出简短复盘（见 `SRE_RUNBOOK.md` §4）：根因、MTTR、临时止血、永久修复项、负责人。
