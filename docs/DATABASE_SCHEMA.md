# 数据字典（DATABASE_SCHEMA.md）

> 对应数据治理评估报告 §4.3（数据字典缺失）。本文件为 `app/integrated_app/history_db.py`
> （`HistoryDB.SCHEMA_SQL` / `MIGRATION_COLUMNS`）的权威字段说明，
> 是所有数据消费者（前端、统计、血缘追溯）的单一事实来源。**与代码冲突时以代码为准并回改本文件**。

## 存储位置

- 主库：`data/history.db`（SQLite，WAL 模式）
- 备份：`data/history.backup.<ts>.db`（由 `HistoryDB.backup()` 经 `VACUUM INTO` 生成，保留最近 7 个）
- 容量日快照：同一库内 `capacity_snapshots` 表（当日 VRAM 峰值 / 数据卷用量 / GPU·小时）
- 全文索引：FTS5 虚拟表 `tasks_fts`（`task_id` UNINDEXED / `prompt` / `tags`，`tokenize='trigram'`；
  `negative_prompt` **不在**索引列内，<3 字符查询由 `list_tasks` 走 LIKE 回退）

## ERD（文本）

```
tasks (1) ──< (N) outputs        tasks.task_id = outputs.task_id
presets                          独立表（engine_name + name 唯一）；config 为预设参数快照，非 tasks 外键
capacity_snapshots               独立表（按 snapshot_date 唯一），无外键
```

## 表：`tasks`

| 列 | 类型 | 约束 | 说明 | 血缘/治理 |
|----|------|------|------|----------|
| task_id | TEXT | PK | 任务 ID（uuid4 hex 前 16 位；注：config 声明 `id_format: ulid` 但未实际启用） | — |
| engine | TEXT | | 引擎名（config.models.engines 键） | — |
| mode | TEXT | | `txt2img` / `batch` | — |
| prompt | TEXT | | 正向提示词 | FTS |
| negative_prompt | TEXT | | 负向提示词 | — （**不在** FTS 索引列内） |
| generation_config | TEXT(JSON) | | 完整生成参数（seed/steps/cfg/尺寸/LoRA 栈等） | 反序列化后使用 |
| tags | TEXT(JSON) | | 标签列表 | FTS |
| status | TEXT | | `pending/processing/completed/failed/cancelled`（+ `interrupted`） | 状态机 |
| error | TEXT | | 失败错误信息原文 | — |
| **error_code** | TEXT | | 失败错误归类码（`OOM_VRAM`/`TASK_TIMEOUT`/`LORA_APPLY`/`WEIGHT_INTEGRITY`/`WORKFLOW_LOAD`/`WATERMARK`/`UNKNOWN`） | **新增（§4.1）**：用于 FAILED 根因聚类 |
| processing_time_s | REAL | | 推理耗时（秒） | 指标口径 |
| output_count | INT | | 成功输出数 | — |
| thumbnail | TEXT | | 缩略图（base64 或路径） | — |
| **workflow_version** | TEXT | | 引擎 workflow 文件内容 sha256（不可变版本指纹） | **新增（§3.3）**：图像→workflow 版本追溯 |
| **lora_checksums** | TEXT(JSON) | | `[{name, strength, sha256}]` 每层 LoRA 权重指纹 | **新增（§3.3）**：图像→权重追溯 |
| **request_id** | TEXT | 提交侧 HTTP 请求的 request_id（与日志 `req=` 同源），提交→worker 边界最小关联键；旧库由 v5 迁移补齐 | **新增（v5）**：链路追踪/排障时按 id 串联提交与执行日志 |
| created_at | TEXT | | 创建时间（`datetime('now')`） | — |
| updated_at | TEXT | | 更新时间 | — |
| favorite | INT | | 收藏标记（清理时跳过） | 生命周期 |
| interrupted_at_reboot | INT | | 重启中断标记（0/1） | 状态机 |
| **deleted_at** | TEXT | | 软删除（回收站）时间戳；`NULL`=未删，非空=已删且可恢复 | **新增（v4）**：防误删，记录与磁盘文件均保留 |
| **rating** | INTEGER | | 用户反馈打分：`-1`=踩 / `0`=未评 / `1`=赞 | **新增（v7）**：MLOps M6 反馈闭环 |

索引：`idx_tasks_status`、`idx_tasks_engine`、`idx_tasks_created`、`idx_tasks_favorite`。
（`workflow_version` 无独立索引；`list_tasks` 默认带 `deleted_at IS NULL` 过滤。）

## 表：`outputs`

| 列 | 类型 | 说明 |
|----|------|------|
| id | INTEGER | PK（AUTOINCREMENT） |
| task_id | TEXT | NOT NULL，外键 → tasks.task_id（ON DELETE CASCADE） |
| path | TEXT | NOT NULL，输出图像路径（绝对或相对） |
| format | TEXT | 图像格式，默认 `png` |
| file_size | INTEGER | 文件字节数 |
| width / height | INTEGER | 输出尺寸 |
| seed | TEXT | 该输出的种子 |
| output_type | TEXT | `original` / `upscaled` / `compare` |
| sha256 | TEXT | 输出文件指纹（输出级血缘，数据治理报告 P2-4/Q1-①） |
| created_at | TEXT | 创建时间 |

索引：`idx_outputs_task_id`、`idx_outputs_path`。

## 表：`presets`

| 列 | 类型 | 说明 |
|----|------|------|
| id | INTEGER | PK（AUTOINCREMENT） |
| engine_name | TEXT | NOT NULL；与 `name` 组成 `UNIQUE(engine_name, name)` |
| name | TEXT | NOT NULL，预设名 |
| thumbnail | TEXT | 缩略图 |
| config | TEXT(JSON) | 预设生成参数（**不含 seed**） |
| created_at | TEXT | 创建时间 |

## 表：`capacity_snapshots`

| 列 | 类型 | 说明 |
|----|------|------|
| id | INTEGER | PK（AUTOINCREMENT） |
| snapshot_date | TEXT | NOT NULL，`UNIQUE`；快照归属日期（YYYY-MM-DD） |
| peak_used_gb | REAL | 当日 VRAM 已用峰值（GB） |
| disk_used_gb | REAL | 数据卷已用空间（GB） |
| gpu_hours_24h | REAL | 近 24h GPU·小时（`processing_time_s` 聚合） |
| created_at | TEXT | 创建时间 |

索引：`idx_capacity_snapshots_date`。

## 迁移策略

无 Alembic。`HistoryDB._init_db` 在 `CREATE TABLE IF NOT EXISTS`（基线列全量建表）之后执行
两条迁移路径：① `MIGRATION_COLUMNS`（`workflow_version` / `lora_checksums` / `error_code`，
PRAGMA table_info 探测后逐项 `ALTER TABLE ADD COLUMN`——SQLite 不支持 `ADD COLUMN IF NOT EXISTS`）；
② `_apply_migrations`（`PRAGMA user_version` 单调推进，`SCHEMA_VERSION = 7`，
含 v4 软删除、v5 request_id、v6 FTS rowid 对齐重建、v7 rating 列等），单步失败 fail-closed 终止启动。
新增列必须带 `DEFAULT`，禁止破坏性变更。重大 schema 变更应记录 ADR 并更新本文件。

## 血缘追溯示例

```sql
-- Q1：某张图 → 对应 workflow 版本 + 所有 LoRA 权重指纹
SELECT task_id, workflow_version, lora_checksums, generation_config
FROM tasks WHERE task_id = (SELECT task_id FROM outputs WHERE path = 'outputs/xxx.png');

-- 图像本身仅携带水印 task_id（无 EXIF），DB 为参数唯一事实来源；DB 损坏则血缘断链。
```
