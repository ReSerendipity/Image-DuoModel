# mypy 类型门禁接入组织级 reusable workflow（迁移记录）
> 2026-09-15 由原《家族模板迁移_mypy_ratchet_20260903.md》改名内化（去除跨仓措辞），原件归档于 `.spec_audit/family_archive_20260915/`。


日期：2026-09-03
来源：ReSerendipity/.github → `.github/workflows/python-quality-baseline.yml`
目标：Image_MultiModel `.github/workflows/ci.yml` 的 `mypy` job

## 变更内容

原内联 `mypy` job（name: Type Check (Mypy)）替换为 `uses:` 调用组织模板，
保留 `if: always()`（lint/test 失败时类型状态仍要出）。参数：

- `include_tests: false` —— 覆盖率 65% 门禁仍由本仓 `test` job
  （3.12/3.13 双版本矩阵）把守，不迁移
- `mypy_target: app/integrated_app` —— 检查范围不变
- 不传 `mypy_baseline_file` 的仓内文件：本仓无基线文件 → 模板零容忍分支

## 口径差异（诚实记录，均已实测）

| 维度 | 原 job | 新 job（模板） |
|---|---|---|
| mypy 版本 | 未锁定（pip install mypy → 装当时最新） | 锁定 2.3.1（组织级统一） |
| 项目依赖 | 全量 requirements.txt（`|| true` 容错） | 不装（第三方=Any）+ pyproject 配置仍生效 |
| python-version | CLI 显式传 3.12 | 由 pyproject [tool.mypy] 提供（同值） |
| 判定 | mypy 非零退出即红 | 错误数 > 基线(缺失=0) 即红，效果同 |

迁移前实测（2026-09-03）：两种口径错误数都是 **0**
（全依赖 venv：`Success: no issues`；纯 mypy 2.3.1：同样 0），
零容忍分支与"0 基线"语义等价，判定行为无漂移。

## 附带收益

原 job `pip install mypy` 不锁版本，是隐性的漂移源（新版 mypy 上线那天
门禁可能突然变红且无人改动代码）。模板锁定 2.3.1 并写明升级须重算基线，
消除该风险。
