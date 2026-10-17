# 演练执行台账（备份恢复 / 回滚）

> 对应 v2.9 评估《运维稳定性_Flash报告》P1-3：restore-drill 与 bluegreen rollback
> 能力早已存在，但缺执行记录与暴露项闭环台账——本文件即该台账。
> 登记口径遵循提示词库《证据模板库》模板①（演练记录）与模板②（恢复核销）：
> 数值带口径、结论可复算、禁止用计划冒充记录。

## 演练项与周期

| 编号 | 演练项 | 命令 | 周期 | 判定标准 |
|---|---|---|---|---|
| D1 | 历史库备份恢复演练 | `python scripts/backup_state.py restore-drill` | 每年 1/4/7/10 月首周 | 退出码 0：备份→还原→integrity_check=ok→行数一致→还原库可查询 |
| D2 | 蓝绿发布回滚演练 | `bash scripts/deploy/bluegreen.sh rollback` | 每年 1/4/7/10 月首周（需 Docker 与已构建镜像环境） | 回滚后 `/api/health` 200 + LAST_GOOD 版本对外服务 + 观察窗无 firing 告警 |

## 台账（只登记已执行记录；计划中的演练不得写入本表）

| 记录编号 | 时间戳 | 类型 | 命令与范围 | 实测耗时 | 校验结果 | 暴露项与闭环 | 责任人 |
|---|---|---|---|---|---|---|---|
| DR-2026-1015-01 | 2026-10-15 21:16 (+08:00) | D1 备份恢复演练 | `python scripts/backup_state.py restore-drill`；源库 `data/history.db`（tasks=5766 / outputs=97 / user_version=7） | 3.3 s | integrity_check=ok；行数与 manifest 一致；还原库查询 completed tasks=2136 / presets=285 | 无 | ReSerendipity（v2.9 评估阶段二实录，任务ID=Image-MultiModel-v29-remediate） |

## 计划与到期

- 下次 D1 / D2 演练到期：**2027-01 首周**；D2 受环境约束（需 Docker + 镜像构建）在具备条件时随当期一并执行。
- 演练暴露项一律登记到本表「暴露项与闭环」列并跟踪至闭环；无暴露项写「无」，禁止留空。
