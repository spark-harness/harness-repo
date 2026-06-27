---
requirement_id: "LEN-9"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-28"
idl_impact: "no"
idl_impact_reason: "本需求新建 origination-api HTTP/JDBC 服务，不修改 protobuf IDL、generated contracts 或 Buf 配置。"
approved_by: "forest"
approved_at: "2026-06-28T04:04:10+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-9 service-repo-check，按 Jira 范围新建 origination-api draft 能力，不修改 IDL，不交付 GitOps runtime 部署。"
---

# Impact Analysis

## Summary

LEN-9 新建 `origination-api`，负责 LoanApplication draft 创建、读取、PATCH 静默保存、幂等和 Quote 校验。它新增 application DB migration 和 Java service tests，不做部署。

## Affected Domains

- Origination：新增 LoanApplication 聚合和 draft 状态。
- Pricing：通过 quote-api 内部 Quote 读取边界校验 quoteId。
- Frontend/BFF 后续依赖：LEN-133 和 LEN-11 将使用该服务能力。

## Affected Services And Repos

| Service / Module | Repo | Reason | Protobuf Required |
|---|---|---|---|
| origination-api | business-repo | 新建 Java Spring 服务、domain/application/adapter/infrastructure、migration 和测试 | no |
| service matrix | harness-repo | 新增 origination-api 条目和 quote-api downstream 关系 | no |
| Java quality project graph | business-repo | 将 origination-api 纳入 Java quality/CI 项目清单 | no |
| Harness LEN-9 lifecycle | harness-repo | 保存需求、影响分析、设计、任务、门禁和证据 | no |

## Upstream / Downstream Consumers

- Upstream:
  - 当前可直接调用 origination-api HTTP。
  - LEN-133 后由 `fides-bff` 暴露 loan application facade。
  - LEN-11 前端经 BFF 做 Continue 静默保存。
- Downstream:
  - quote-api internal quote read endpoint。
  - application DB。

## API / Contract Impact

- 新增 origination-api HTTP endpoints:
  - `POST /api/v1/loan-applications`
  - `GET /api/v1/loan-applications/{id}`
  - `PATCH /api/v1/loan-applications/{id}`
- Protobuf IDL: no changes.
- Generated contracts: no changes.
- Error semantics:
  - 400 `idempotency_key_required`
  - 403 `forbidden`
  - 404 `not_found`
  - 410 `quote_expired`
  - 422 `amount_out_of_range`
  - 422 `validation_error`
  - 502 `quote_unavailable`
- Compatibility risk:
  - 新增服务，无既有消费者。
  - 后续 BFF facade 必须保持字段名兼容。

## Data / Storage Impact

- 新增 application DB migration。
- `loan_applications` 至少包含：
  - application_id
  - applicant_id
  - product_code
  - status
  - current_step
  - amount
  - term_months
  - purpose
  - accepted_quote_id
  - accepted_quote_snapshot
  - created_at
  - updated_at
- `idempotency_records` 至少包含：
  - idempotency_key
  - applicant_id
  - operation
  - request_hash
  - response_body
  - status_code
  - created_at
- 不写 quote DB，不写 applicant 数据。

## Config / Permission / Observability Impact

- Config:
  - `spark.origination.jdbc-*`
  - `spark.origination.quote-api-base-url`
  - quote-api HTTP timeout。
  - Consul registration 配置面可沿用 quote-api 模式；runtime 注入由 LEN-134。
- Permission:
  - applicantId 来自 LEN-22 principal context。
  - GET/PATCH 必须校验 application applicantId。
  - quote 校验必须确认 quote applicantId。
- Logs:
  - 记录 applicationId、operation、trace_id、error_code。
  - 不记录 token、Authorization 或完整申请表单敏感字段。
- Tracing:
  - HTTP 下游 quote-api 调用传播 `traceparent`/`tracestate`。
- Events:
  - 不新增事件；提交事件留给后续 submit ticket。

## Rollout And Rollback

- Rollout:
  1. 合入 `origination-api` 代码、migration 和测试。
  2. 合入服务矩阵和 Java quality project graph。
  3. LEN-134 部署 `origination-api` 和 application DB。
  4. LEN-133 接 BFF facade。
- Rollback:
  - 回滚 `apps/origination-api` 和 service matrix。
  - 未部署时无 runtime rollback。
  - 部署后 DB runtime 回滚由 LEN-134 负责。

## Risks And Mitigations

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| Quote 校验只查存在不查归属 | applicant 可引用他人 Quote | QuoteGateway 返回 applicantId 并由 usecase 校验 | core |
| 幂等键作用域错误 | 不同 applicant 互相影响或重复创建 | 幂等 scope 使用 applicantId + operation + key | core |
| PATCH 推进步骤 | Continue 行为不符合静默保存 | 测试锁定 status/currentStep 不变 | core |
| acceptedQuote 未快照 | 后续回填受 quote-api 变化影响 | 保存 quote snapshot JSON | core |
| 新服务未纳入 Java quality | CI 漏检 | 更新 `tooling/java-quality/projects.yaml` | core |
