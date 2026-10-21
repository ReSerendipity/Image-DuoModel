# Image-DuoModel 安全矩阵

> 本文档列出项目的安全控制措施，供安全审计和合规检查参考。

## 身份与访问控制

| 控制项 | 实现方式 | 状态 |
|---|---|---|
| 分支保护 | GitHub Branch Protection（main 需 required checks；仓库所有者 admin 已开**直推豁免**，非 admin 仍需 PR + 1 审批） | ✅ |
| DCO 签名 | .githooks/commit-msg 强制 Signed-off-by | ✅ |
| 代码审查 | PR 需 review | ⚠️ 待配置 CODEOWNERS |

## 代码安全

| 控制项 | 实现方式 | 状态 |
|---|---|---|
| 密钥扫描 | gitleaks（pre-commit + CI） | ✅ |
| 依赖漏洞扫描 | pip-audit / Dependabot | ✅ |
| SAST | CodeQL / Semgrep | ✅ |
| 静态分析 | ruff / flake8 / eslint | ✅ |
| 完整性校验 | Ed25519 签名清单 | ✅ |

## 数据安全

| 控制项 | 实现方式 | 状态 |
|---|---|---|
| 敏感配置不入库 | .env.example 模板，真实配置 gitignore | ✅ |
| 路径遍历防护 | path_guard / CSRF middleware | ✅ |
| 输入校验 | 参数验证 / schema 校验 | ✅ |

## 发布安全

| 控制项 | 实现方式 | 状态 |
|---|---|---|
| 签名发布 | Ed25519 清单/增量包签名（`scripts/sign_integrity_manifest.py` + `.github/workflows/release.yml` 的 Verify package Ed25519 signature 步骤） | ✅ |
| 制品不可变 | Immutable Release Artifacts | ✅ |

---
*最后更新：2026-09-20*
