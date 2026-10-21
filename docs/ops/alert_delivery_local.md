# 本地形态告警落地方案（设计稿）

> 来源：运维稳定性评估路线图 #8。上游定义：[alert_rules.md](alert_rules.md)（7 类规则，
> 代码为单一事实源）、[oncall.md](oncall.md)（其 Primary/Secondary 轮值模型面向团队形态，
> **本项目当前为单人单机自托管**，本文给出与之匹配的送达设计）。
> 状态：**设计稿（未实现）**；落地时按 §3 最小实现起步。

---

## 1. 问题定义

告警已在代码内定义并被蓝绿脚本消费（`bluegreen.sh` 观察窗口轮询 `/api/alerts`），
但**无人值守时告警不会到达任何人**——`/api/alerts` 只有主动拉取才可见，
日志 notifier 只写文件。单机形态的真实风险：OOM / 磁盘满 / 服务假死发生时，
用户可能数小时后才从"生成怎么一直失败"发现故障。

## 2. 送达渠道评估（按单机形态 ROI 排序）

| 渠道 | 优点 | 缺点 | 结论 |
|---|---|---|---|
| **Windows Toast 通知** | 免费直达用户当前桌面；无需账号/网络 | 需要一个轻量 watcher 进程常驻 | **首选**。P0/critical 即时弹 |
| **结构化日志标记** | 零成本，已有（`[ALERT]` / `[ALERT-RESOLVED]` 前缀） | 用户不看日志 | 保留为底座（审计与排查依据） |
| **服务健康页自证** | `/api/alerts` 已有 | 被动 | 保留 |
| **退出码 / 启动横幅** | 服务崩溃时由进程管理器兜底 | 只覆盖崩溃类故障 | 保留 `restart: unless-stopped` |
| IM / 邮件 webhook | 离机可达 | 需账号与网络配置，单人本地形态收益低 | 二期（远程访问出现后再接） |
| 电话/SMS | 团队 on-call 形态 | 与单人本地形态完全不匹配 | 不适用（写「不适用」） |

## 3. 最小实现设计（P0 范围）

1. **watcher 脚本** `scripts/alert_toast_watch.py`（建议，未实现）：
   - 轮询 `GET /api/alerts`（间隔 30s，与 alerts.py 的 for_s 量级匹配）；
   - 检测 `firing=true && severity=critical` 的新条目（本地 set 去重，恢复时弹 resolved）；
   - 弹 Windows Toast：PowerShell `Windows.UI.Notifications` 原生调用即可，
     **无需安装 BurntToast 等第三方模块**（保持便携模式零依赖原则）；
   - 崩溃自愈：由任务计划程序（登录时启动 + 失败重启）托管，与守护服务同生命周期。
2. **映射**：7 类规则全部接入；`warning`（QueueOverloaded）默认只记日志不弹窗，
   避免疲劳（与 alert_rules.md 去重疲劳设计一致）。
3. **静默窗口**：允许 `IMM_TOAST_QUIET=HH:MM-HH:MM` 配置夜间静默
   （critical 仍弹，与 oncall.md 的夜间首响目标对齐）。

## 4. 验收口径（落地时）

- 人为触发 DiskSpaceLow（占满测试盘 / 调低阈值）→ 30s 内桌面出现 toast；
- 告警恢复 → 收到 resolved toast；同一告警持续 firing 不重复弹；
- watcher 崩溃被任务计划程序拉起；服务离线时 watcher 静默降级为日志记录，不弹窗轰炸。
