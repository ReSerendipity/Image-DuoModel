# Security Policy

本文件为发行包内的安全策略入口页。完整事实来源（含威胁模型、内置防护机制详述、合规评估索引）见仓库 `.github/SECURITY.md`。

## Supported Versions

| Version | Status |
|---------|--------|
| 2.1.0（main branch） | ✅ Actively maintained |
| 1.x / v1.5.x（historical tags） | ❌ End of life |

## Reporting a Vulnerability

**Do not open public GitHub Issues for security vulnerabilities.**

Please use GitHub's private reporting channel:

- [Private vulnerability report](https://github.com/ReSerendipity/Image-DuoModel/security/advisories/new)

## Response Timeline

- Acknowledgement: within 48 hours
- Triage & remediation plan: within 5 business days
- Critical / High severity: prioritized patch release

## Scope

This project is designed as a **localhost-only, single-user self-hosted service** (`server.host` forced to `127.0.0.1`). Attacks requiring local physical access, modified local config, or user-replaced model weights are out of scope.

---

> Full security design notes, threat model, and built-in protection mechanisms are documented in `.github/SECURITY.md`.
