# 告警通知通道配置（Alert Notifier）

> 对应 MLOps 评估报告 M7：`observability/alerts.py` 默认只把告警写结构化日志，
> **不外发**。本地桌面模式下用户就在机器前，这是对的；但一旦切到
> `docker-compose.yml` / `docker-compose.release.yml` 部署模式，critical 告警不会触达任何人。

## 默认行为（本地模式）

`app/integrated_app/observability/alerts.py`：

```python
# 默认仅记录结构化日志，避免误报风暴
# 真实 Alertmanager / 企业微信 / 邮件推送由部署侧配 channel
```

即 `set_notifier` 未被注入时，告警只进 `logs/app.log`。

## 部署到服务器时必须做的事

在服务启动前，调用方注入一个 notifier，例如：

```python
from integrated_app.observability import alerts


def webhook_notifier(alert: alerts.Alert) -> None:
    #  POST 到企业微信 / 钉钉 / 自建 Alertmanager webhook
    ...


alerts.set_notifier(webhook_notifier)
```

不注入的风险：

- `生成失败率 >5% 持续 5min`（critical）无人知道；
- `GPU 可用显存 <15% 持续 2min`（critical）会触发 OOM 但没人重启；
- `磁盘可用 <15%`（critical）会写爆数据卷。

## 现有告警阈值（来自 alerts.py）

`app/integrated_app/observability/alerts.py` 的 `AlertEngine._make_rules()` 共 **7 条**规则，阈值与 Runbook 一一对应（Runbook 路径亦由该文件的 `_RUNBOOK` 映射给出）：

| 告警 | 阈值 | 级别 | Runbook |
|---|---|---|---|
| 服务不健康 | ≥2 次连续 health 失败 | critical | docs/runbooks/service_startup.md |
| 生成失败率 | >5% 持续 5min | critical | docs/runbooks/generation_failures.md |
| 队列填充 | ≥85% 持续 5min | warning | docs/runbooks/queue_overload.md |
| GPU 可用显存 | <15% 持续 2min | critical | docs/runbooks/gpu_oom.md |
| 磁盘可用 | <15% | critical | docs/runbooks/disk_full.md |
| LLM Token 日预算 | 当日累计超 `finops.budget_llm_tokens_per_day` | warning | docs/runbooks/llm_token_budget.md |
| 崩溃留痕 | 24h 内新增 `logs/crash_reports/crash-*.log` | warning | docs/runbooks/crash_reports.md |

## 部署门禁建议

在 `deploy.yml` 或部署文档里加一条检查：远端部署时若 `alerts.set_notifier` 未被调用，
启动日志应打一行 WARNING，提示「critical 告警将仅写本地日志」。
