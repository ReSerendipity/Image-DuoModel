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
| CLOSED-1 | 2026-10-17 | run 38862263716（CI，`schedule`，head `e030930`，2026-10-16T06:37:27Z → 06:40:22Z，conclusion=failure）job `Test + Coverage (Python 3.13)`，失败步骤 **`Junit skip-quota gate (3.13)`** | 红的不是用例：下载该 run 的权威产物 `junit-python-3.13`（artifact id 12030450095）逐条核对得 **1482 用例 / 1248 执行出结论 / 234 skip / 0 失败 0 错误**，11 类去重原因。而 `ci_skip_ledger.python-3.12.json` 已是 234/11 类、`python-3.13.json` 仍停在 228/10 类——差 `原生引擎栈 206→209` 与缺失的「无 CUDA GPU，跳过」3 条（`tests/native/test_gpu_smoke.py` 的 `@requires_cuda` 用例）。即 **3.12 台账随 PR(feat/db-rating-column) 刷新时 3.13 没跟着动**，不是 ci.yml:228-230 猜的「版本相关 skip 漂移」（两版本分布逐条相同） | **已修（2026-10-17，指挥方授权）**：按权威产物把 `ci_skip_ledger.python-3.13.json` 对齐到 234/11 类（`min_executed` 维持 1150，产物实执行 1248 有余量），`source` 重绑到本 run/产物，`_comment` 加「两份台账必须同笔移动」的同步纪律。**未弱化门禁**：语义仍是精确相等、双向防漂移，只把基线换成权威产物实测值。本地验证：同产物 + 同分布的 3.12 台账跑真实 `scripts/check_junit_results.py` ⇒ exit 0 `[PASS] … 234 条 skip 分布与台账一致`；本机无 3.13 解释器（`py --list` 只有 3.12/3.9），台账守卫按设计拒跑 `python_version=3.13`，所以终判要等下一次 3.13 真跑（合入即验，不挡 PR） | 待 3.13 真跑复验 |
| OPEN-2 | 2026-10-17 | 同 run 38862263716，job `Lock Solvability (pip resolver dry-run)`，失败步骤 **`Resolve declared floors together with the lock`** | 声明地板与锁在同一解析器里不可同时满足。本机同环境复现（只读 `--dry-run`，不安装）：只解 lock **rc=0**、两文件联解 **rc=1** 且逐个点名冲突包。逐个排查得 3 处「锁针低于源下限」：`accelerate 1.14.0 < >=1.15.0`、`comfy-aimdo 0.4.13 < >=0.5.5`（下限由 e4768e5 抬）、`transformers 5.15.0 < >=5.17.0`（下限由合并的 Dependabot PR #61 / 提交 41614d0 抬）。CI 各 job 实际都从 `requirements.txt` 按下限安装并跑 `pip check`，故这些下限已被 CI 侧执行验证；本机实装另有 transformers 5.16.1、uvicorn 0.52.4 低于声明（属本文件头部既有「版本漂移提示」）。 | **试过并主动回退**：把三针抬到「下限最小满足值」后，`transformers==5.17.0` 与既有 `tokenizers==0.22.2` 冲突，连**只解 lock**都从 rc=0 变 rc=1——抬单针会破坏锁的传递闭包自洽性，比原状态更差，故 `git checkout -- requirements-lock.txt` 全量回退并复测恢复原行为（step1 rc=0 / step2 rc=1 点名 accelerate）。正确出路是**用解析器重生成整份 lock**（pip-compile 或 uv lock）在与发布口径一致的环境里，属需你定的环境与授权范围（会重写约 151 针，本机无法用真推理验证）。 | 待拍板（需重生成锁的运行环境 + 发布口径决策） |
| CLOSED-3 | 2026-10-17 | `Test + Coverage (Python 3.13)` 既在 required contexts（live 实测 15 条含它，`docs/ci/branch-protection.json` 也声明），又按 `ci.yml` 的 `if: github.event_name != 'pull_request'` 在 PR 上不产出 | 实测 PR 122：该 context = SKIPPED，`mergeStateStatus = BLOCKED`。能落地的改动走的是 `enforce_admins=false` 的管理员直推 | **已处置（2026-10-17，指挥方授权）**：从 required contexts 摘掉该条并 `--apply`；远端回读 contexts 15→14、has3.13=false，其余字段与 live 同值未变；PR 122 的 EXPECTED/QUEUED 检查归零（仍 BLOCKED，但原因变为它自身的真红检查 + 待审批）。恢复为必需检查的前提是先修 OPEN-1 | 已闭合 |

> 注：OPEN-1 与 OPEN-3 涉及同一个 job，但**成因与归属不同**——前者是配额台账漂移，后者是必需检查与事件门禁的矛盾。合并处理会掩盖其中一个。
