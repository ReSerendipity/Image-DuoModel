# CI / 门禁红灯交接台账

> 本台账是 **被 git 跟踪、随仓库分发** 的红灯交接账本，取代原先仅本地保留的 `FIX_LOG.md`
> （那份文件在 `.gitignore` 里，干净克隆与 CI 检出不存在它，于是「读交接账本再动手」这条
> 铁律只对一台机器成立）。登记口径与 [drill_ledger.md](drill_ledger.md) 一致：
> 数值带口径、结论可复算、禁止用计划冒充记录。

## 规则（活动契约铁律 ⑦ 的事实来源）

1. 格式：**失败签名（关键报错行） → 假设 → 动作 → 结果**，四列缺一不可。
2. **同一失败签名第二次出现，禁止再朝同方向重试**：必须读完整失败日志，或 `git revert` 换策略。
3. 同一仓库同一时刻只允许一个修复者。
4. 签名里必须带 **run id / job name / step name**，让下一个人能用只读命令复算，而不是靠描述。

复算用的只读命令（不改远端、不写数据）：

```bash
# main 最近若干次 CI 运行及其结论
gh api "repos/<owner>/<repo>/actions/runs?branch=main&per_page=15" \
  --jq '.workflow_runs[]|select(.name=="CI")|[.id,.head_sha[0:7],.event,.status,.conclusion,.created_at]|@tsv'

# 某次运行里失败的 job 与其失败步骤（签名的来源）
gh api "repos/<owner>/<repo>/actions/runs/<run_id>/jobs?per_page=40" \
  --jq '.jobs[]|select(.conclusion=="failure")|{name,failed_steps:[.steps[]|select(.conclusion=="failure")|.name]}'
```

---

## 交接记录

| # | 日期 | 失败签名（run / job / step） | 假设 | 动作 | 结果 |
|---|------|------------------------------|------|------|------|
| 1 | 2026-09-05 | run 33957856101 `Test + Coverage (3.13)`：`tests/smoke/test_startup_smoke.py::test_app_boots_and_health_ok` setup ERROR `sqlite3.OperationalError: database is locked`（`history_db.py:345 _init_db`） | ① 新门禁测试直接引发 DB 竞争——**证伪**（纯只读哈希，不碰 DB）；② `conftest` 会话隔离只 patch 顶层 `integrated_app.config` 单例，而 `create_app()` 经 `app.integrated_app.*` 相对导入走另一单例（实测 `top is pkg == False`），重定向失效 → xdist 双 worker 在真实 `data/history.db` 上竞速 | `tests/conftest.py::_isolate_history_db_for_tests` 同时重定向两个导入身份的单例（db_path / uploads / cleanup_cron，恢复亦双份） | 本地 xdist `-n 2` smoke + 门禁 7 passed；全量 1005 passed rc=0；推送后 CI 复绿 |
| 2 | 2026-09-11 | run 34562117669 `Test + Coverage (3.12/3.13)`：`tests/integration/test_fake_generation_flow.py` 3 个 setup ERROR — `history_db.py:345 _init_db` 执行 `PRAGMA journal_mode=WAL` → `database is locked` | ① 先怀疑 09-05 的「双导入身份」复发——**证伪**（双身份重定向代码仍在）；② 实读 conftest 发现装饰器被写进了注释行（`# ── 反模式 #4 防护 … ──@pytest.fixture(...)`）→ `_isolate_history_db_for_tests` **从未被 pytest 注册**，会话级重定向从未执行，各 worker 直连真实库并发建库/切 WAL | ① 装饰器拆到独占行（根因修复）；② 对 `integrated_app.config` / `app.integrated_app.config` 的 `load_config`/`load_validated_config` 加包装，使「单例被整体替换」后重定向仍生效（第二道防线）；③ 新增 `tests/test_history_db_isolation.py` 锁定契约 | 原始 conftest 下 `-n auto` 全量 6 failed / 1013 passed（含目标集成测试 2 项失败）；修复后目标集成测试全绿、新增 3 项回归测试通过；剩余失败均为本机缺 ComfyUI 原生源码 / PIL 解压炸弹等环境项（单独跑通过） |

## 尚未闭合项

| 编号 | 日期 | 失败签名（run / job / step） | 已确认的事实 | 尚未做的 | 归属 |
|---|---|---|---|---|---|
| OPEN-1 | 2026-10-17 | run 38862263716（CI，`schedule`，head `e030930`，2026-10-16T06:37:27Z → 06:40:22Z，conclusion=failure）job `Test + Coverage (Python 3.13)`，失败步骤 **`Junit skip-quota gate (3.13)`** | 红的不是用例本身，而是跳过配额闸：台账 `.github/ci_skip_ledger.python-3.13.json` 要求与 junit 产物里的跳过集合**精确相等**（该闸的自述是「不许放宽成 warning」）。同头 `e030930` 的 push run（2026-10-15T07:08:18Z）与 `07f659a` 的 schedule（2026-10-15T06:49:18Z）同为 failure ⇒ main 连续三次 CI 红 | 未读该 step 的完整失败日志确认是「新增跳过」还是「跳过消失」；未改台账；未修代码 | 待拍板：配额漂移属 3.13 兼容性覆盖，改台账还是改用例需维护者定 |
| OPEN-2 | 2026-10-17 | 同 run 38862263716，job `Lock Solvability (pip resolver dry-run)`，失败步骤 **`Resolve declared floors together with the lock`** | 声明地板与锁文件在同一解析器里不可同时满足（该 job 正是 dry-run 解析器探测）。此 context 同样列在 main 的 required_status_checks 里 | 未定位是哪个包/标记的地板与锁冲突；未重生成锁 | 待拍板：动 `requirements*.txt` / 锁文件属依赖治理，需与维护者定优先级（勿与 OPEN-1 混在同一次改动里） |
| OPEN-3 | 2026-10-17 | `Test + Coverage (Python 3.13)` 既在 required contexts（live 实测 15 条含它，`docs/ci/branch-protection.json` 也声明），又按 `ci.yml` 的 `if: github.event_name != 'pull_request'` 在 PR 上不产出 | 实测 PR 122：该 context = SKIPPED，`mergeStateStatus = BLOCKED`。能落地的改动走的是 `enforce_admins=false` 的管理员直推 | 未改 required 列表（那是远端写操作，属红线外） | 待拍板：从 required 移除 ①或让 3.13 在 PR 上也跑 ②；见 `.github/workflows/ci.yml` 的 `test-313` 注释与 `branch-protection.json._pending_approval` |

> 注：OPEN-1 与 OPEN-3 涉及同一个 job，但**成因与归属不同**——前者是配额台账漂移，后者是必需检查与事件门禁的矛盾。合并处理会掩盖其中一个。
