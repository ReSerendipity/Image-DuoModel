# SRE 运行手册（SLA / SLO / 回滚 / 灾难恢复演练）

> **来源**：家族泛化自 TTS_MultiModel `docs/SRE_RUNBOOK.md`，本仓本地化。
> 配套：`docs/rollback_sop.md`、`docs/release-governance.md`。
> 适用版本：v2.1.1（与 `config.yaml` 顶层 `version` 一致）。

---

## 1. SLA / SLO

### 1.1 服务等级目标（SLO）

| 指标 | 目标 | 度量方式 | 数据源 |
|------|------|----------|--------|
| 可用性（月度） | ≥ 99.5% | liveness `/api/health` 探活成功率 | `app/integrated_app/routes/system_routes.py` |
| readiness（引擎就绪） | ≥ 99.0% | 启动后引擎可加载、`/api/system/...` 返回 ok | 同上 |
| P95 生成时延 | 设备相关 | `task_queue` 生成计时 | `task_queue.py` / `history_db` |
| 生成成功率 | ≥ 99.0% | 成功/失败计数 | `observability/generation_metrics.py` |
| 审计/完整性自检 | 100% | `integrity_selfcheck` 结果 | `security/integrity_selfcheck.py` |

### 1.2 错误预算（Error Budget）

- 月度可用性 99.5% ⇒ 允许不可用 ≈ **3.6 小时/月**。
- 超出时：冻结非紧急发布、优先稳定项、复盘（见 §4）。

### 1.3 探针（Probe）约定

- **liveness**：内存级，不碰 DB/GPU，失败即重启。
- **readiness**：深度检查（引擎加载状态 + DB 连通 + GPU），未就绪则不接流量。

---

## 2. 回滚（Rollback）

> 详情见 `docs/rollback_sop.md`，这里给出快速动作。

- **代码回滚**：`git revert <bad_commit>`，人工 push 后重启服务。
- **配置回滚**：`git revert` 对应 `config.yaml` 提交；容器/本地只读挂载 `config.yaml` + 环境变量注入密钥。
- **权重回滚**：`pretrained_models/` / `model/` 禁区，SHA-256 复验（`app/integrated_app/security/weight_integrity.py`）；永不在运行时改权重。

---

## 3. 灾难恢复演练（DR Drill）

| 场景 | RTO | RPO | 恢复手段 |
|------|-----|-----|----------|
| 服务进程崩溃 | < 1 min | 0 | 看门狗 / 手动重启（uvicorn） |
| 端口占用 | < 10 min | 0 | 排查占用进程再启动 |
| 配置误改 | < 10 min | 0 | Git 回滚配置 |
| 权重损坏/篡改 | < 30 min | 按留存 | 从备份恢复 + 完整性复验 |
| history_db 损坏 | < 15 min | ≤ 留存窗口 | 从备份恢复 SQLite |
| 密钥泄露 | < 5 min | — | 轮转并重启 |

> 演练步骤（每季度一次）：预发环境复制部署 → 注入故障（kill 进程 / 删 config / 损坏权重）→ 观测探针翻转 → 按 §2 恢复 → 复盘记录 RTO/RPO。

**数据备份**：`history_db`（SQLite）+ `config.yaml` 定期备份（无定制脚本时先 `sqlite3 .backup` 或复制文件 + 快照）；权重离线冷备 + 复验；密钥走 `.env.example` / Secret 管理。

---

## 4. 事故复盘（Postmortem）

模板：时间线（检测→响应→缓解→恢复）→ 影响面 → 根因（5 Whys）→ 改进项（owner+deadline）→ 是否触及错误预算。

---

## 5. 运维入口速查

| 用途 | 命令 / 端点 |
|------|-------------|
| 存活探针 | `/api/health` |
| 生成统计 | `observability/generation_metrics.py` / 日志 |
| 优雅关闭 | 停止 uvicorn 进程（信号处理） |
| 权重哈希清单 | `scripts/generate_integrity_manifest.py` + `app/integrated_app/security/weight_integrity.py` |

## 日志与勘误（Log Locations）

| 用途 | 位置 |
|------|------|
| 应用主日志 | `logs/app.log` |

> 勘误优先看 `logs/app.log` 尾部（含启动/推理/路由日志）。日志目录不入库（.gitignore 覆盖）。
