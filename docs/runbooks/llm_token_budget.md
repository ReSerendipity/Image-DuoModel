# Runbook — LLMTokenBudgetExceeded（LLM Token 日预算超限）

> 告警引擎规则：`observability/alerts.py::LLMTokenBudgetExceeded`（warning，立即触发）。
> 预算来源：`config.yaml → finops.budget_llm_tokens_per_day`（0 = 不启用；模型字段
> `config_models.FinOpsConfig`，v2.9 评估·LLM 应用工程 P1-2 落地）。

## 症状
- `/api/alerts` 出现 `LLMTokenBudgetExceeded`（warning）；快照带 `llm_tokens_today` / `llm_token_budget`。
- `/api/metrics/prometheus` 中 `llm_calls_total`、`llm_prompt_tokens_total`、`llm_completion_tokens_total` 增速异常。

## 确认命令
```bash
curl -s http://127.0.0.1:8288/api/alerts | grep -A3 LLMTokenBudget
curl -s http://127.0.0.1:8288/api/metrics/prometheus | grep llm_
curl -s http://127.0.0.1:8288/api/agent/health   # 主/降级端点状态
```

## 影响判断
- Token 用量只统计端点 usage 上报值（不上报记 0），超预算=真实调用放量或 usage 口径异常。
- 判断是否伴随 `llm_calls_total{outcome="error"}` 上升（重试风暴会成倍烧 Token）。

## 临时缓解
1. 调高 `finops.budget_llm_tokens_per_day`（确认放量合理时）或临时改为 0 关闭告警；
2. 限制调用方：切 `MANUAL_ASSIST` 模式（不代执行、只出建议），或暂停 Agent 对话入口；
3. 缩短上下文：`IMAGE_MM_AGENT_LLM_MAX_TOKENS` 调低。

## 回滚/重启
- 配置类变更经 `/api/config` 或 config.yaml 修改后重启服务生效；无数据回滚面。

## 恢复验证
- `/api/alerts` 无 firing；`llm_tokens_today` 回落至预算内并持续观察一个使用高峰。

## 升级联系人
- 仓库 OWNER（ReSerendipity）；见 `.github/CODEOWNERS`。
