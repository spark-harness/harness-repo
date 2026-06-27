---
requirement_id: "LEN-10"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-28"
idl_impact: "no"
idl_impact_reason: "本需求新建 quote-api HTTP/JDBC 服务，不修改 protobuf IDL、generated contracts 或 Buf 配置。"
approved_by: "forest"
approved_at: "2026-06-28T01:39:43+08:00"
decision: "用户授权 Agent 批准 LEN-10 服务仓库检查；quote-api 已加入 service matrix，IDL 无影响。"
---

# Impact Analysis

## Summary

LEN-10 新增 `quote-api` Java Spring 服务和 quote 持久化模型，提供 pricing quote 创建和内部 Quote 校验边界。不部署服务，不修改 IDL。

## Affected Domains

- Pricing 子域：新增 Quote 计算和持久化。
- Origination 后续依赖：LEN-9 将用内部 Quote 校验边界校验 quoteId。
- 前端/BFF 后续依赖：LEN-132 和 LEN-11 将通过 BFF facade 使用本服务。

## Affected Services

| Service / Module | Repo | Reason | Protobuf Required |
|---|---|---|---|
| quote-api | business-repo | 新建 Java Spring 服务、quote domain/application/adapter/infrastructure、migration 和测试 | no |
| service matrix | harness-repo | 新增 quote-api 服务条目，供 Janus service-repo-check 解析 | no |
| Harness LEN-10 lifecycle | harness-repo | 保存需求、影响分析、设计、任务、门禁和证据 | no |

## Upstream / Downstream Consumers

- Upstream:
  - 当前 ticket 可直接调用 quote-api HTTP。
  - LEN-132 后由 `fides-bff` 暴露 `/api/v1/pricing/quotes` 并传播 principal/tracing。
- Downstream:
  - quote DB，用于持久化 Quote。
  - LEN-9 `origination-api` 后续调用内部 Quote 校验边界。

## API / Contract Impact

- External contract: 新增 quote-api 服务内 HTTP endpoint，但不修改 BFF 对外契约。
- Protobuf IDL: no changes.
- Generated contracts: no changes.
- Error semantics:
  - 422 `amount_out_of_range`
  - 422 `validation_error`
  - 403 `forbidden`
  - 404 `quote_not_found`
  - 410 `quote_expired`
- Compatibility risk: 无既有 quote-api 消费者；后续 BFF facade 会适配本服务。

## Data Impact

- 新增 quote DB migration。
- Quote 表至少包含：
  - quote_id
  - applicant_id
  - product_code
  - amount
  - term_months
  - purpose
  - monthly
  - apr
  - total_interest
  - total_payable
  - valid_until
  - trace_id
  - created_at
- 金额字段使用 decimal/numeric，并在 Java 使用 BigDecimal。
- 不写 application draft，不写 applicant 数据。

## Config / Permission / Observability Impact

- Config:
  - 新增 `spark.quote.*` 配置组。
  - local 默认可使用 H2；STA/prod quote DB 配置由 LEN-131 提供。
- Permission:
  - applicantId 来自 LEN-22 `RequestPrincipalContext`。
  - 内部 Quote 校验必须做 applicantId 归属检查。
- Logs:
  - 记录 quoteId、operation、trace_id、error_code。
  - 不记录 token、Authorization 或敏感个人信息。
- Tracing:
  - 使用 Spring/OpenTelemetry starter。
  - traceparent 由上游传播，不参与鉴权。
- Metrics:
  - 可复用 actuator/OTel 默认指标；本 ticket不新增业务指标门禁。
- Events:
  - 不新增事件。

## Rollout And Rollback

- Rollout:
  - LEN-10 合入代码和测试。
  - LEN-131 部署 quote-api 和 quote DB。
  - LEN-132 接 BFF facade。
- Rollback:
  - 回滚 quote-api 代码和 service matrix。
  - LEN-10 未部署时无 runtime rollback。
  - 若后续部署后回滚，由 LEN-131 回滚清单和 DB runtime。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| 金额计算使用浮点 | 还款金额不稳定 | 使用 BigDecimal 并用单元测试锁定计算结果 | core |
| Quote 未持久化就返回 quoteId | 后续草稿无法校验 | CreateQuoteUseCase 在事务内计算并保存 | core |
| 内部校验忽略 applicantId | 越权引用他人 Quote | 使用 RequestPrincipalContext 和 repository 查询后归属校验 | core |
| ready 不检查 DB | 部署后服务看似可用但无法写 Quote | ready adapter 使用 RuntimeDependencyProbe 检查 DB | core |
