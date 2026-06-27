---
requirement_id: "LEN-132"
owner: "core"
status: "approved"
created_at: "2026-06-28"
related_branch: "feature/LEN-132-fides-bff-pricing-facade"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
approved_by: "forest"
approved_at: "2026-06-28T03:34:39+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-132 requirement-review，按 Jira 范围实现 fides-bff pricing facade，不修改 IDL，不交付 GitOps runtime 配置。"
---

# fides-bff pricing facade

## Background

贷款请求页需要通过 BFF 调用真实 `quote-api` 试算。`quote-api` 已由 LEN-10 提供创建 Quote 能力，并由 LEN-131 部署到 `lendora-sta`。

这条需求不是什么：它不是 quote-api 算法实现，不是 quote DB 访问，不是 GitOps 下游配置交付，也不是前端页面接入。

它是什么：它在 `fides-bff` 增加受保护的 pricing facade，让前端只调用 BFF，由 BFF 基于 LEN-22 principal context 调用 `quote-api` 并统一错误信封。

## Goals

- 暴露 `POST /api/v1/pricing/quotes`。
- 复用 LEN-22 AuthFilter 和 principal context；只信 Authorization 派生的 applicantId。
- 调用 `quote-api` 创建 Quote。
- 向下游传播 `x-applicant-id`、`traceparent` 和 `tracestate`。
- 返回前端需要的 `quoteId`、`monthly`、`apr`、`totalInterest`、`totalPayable`、`validUntil`。
- 将 quote-api 422、不可用、超时和不可映射错误转换为稳定 BFF 错误码。
- 保持金额 decimal 语义，避免 float 精度丢失。

## Non-Goals

- 不实现 APR、月供、总息、总还款额计算。
- 不直接访问 quote DB。
- 不新增或修改 protobuf IDL。
- 不新增 quote-api GitOps runtime 配置；下游地址、服务发现和环境配置由 LEN-135 交付。
- 不实现 origination 草稿创建或静默保存；LEN-9 和 LEN-133 负责。
- 不修改前端第二页；LEN-11 负责。

## User / Business Scenarios

### Scenario 1: 已登录 applicant 发起试算

Given: 前端携带有效 access token 请求 `POST /api/v1/pricing/quotes`。

When: BFF 校验 token 并调用 quote-api。

Then: BFF 返回 quote-api 创建的 Quote 字段，并且下游请求包含 principal 派生的 `x-applicant-id` 和 trace context。

### Scenario 2: 缺失或无效 token

Given: 请求缺失 access token 或 access token 无效。

When: 前端调用 pricing facade。

Then: BFF 返回 401 `unauthorized`，不调用 quote-api。

### Scenario 3: 攻击者伪造 x-applicant-id

Given: 请求同时携带有效 token 和外部伪造的 `x-applicant-id`。

When: BFF 调用 quote-api。

Then: BFF 忽略外部 header，只向 quote-api 传播 token principal 中的 applicantId。

### Scenario 4: quote-api 返回可映射 422

Given: quote-api 返回 `amount_out_of_range` 或 `validation_error`。

When: BFF 收到下游响应。

Then: BFF 保持 422，并返回同名稳定错误码。

### Scenario 5: quote-api 不可用或超时

Given: quote-api 不可达、超时或返回不可映射错误。

When: BFF 调用 quote-api。

Then: BFF 返回 502 `quote_unavailable`，不暴露内部异常或下游地址。

## Business Rules

- BR1: `/api/v1/pricing/quotes` 必须是受保护接口。
- BR2: applicantId 只能来自 LEN-22 principal context，不得信任外部传入的 `x-applicant-id`。
- BR3: BFF 调用 quote-api 时必须带上 `x-applicant-id`。
- BR4: BFF 调用 quote-api 时必须传播 `traceparent`，存在 `tracestate` 时也必须传播。
- BR5: BFF 请求和响应金额字段必须保持 JSON decimal 语义，不使用 float 参与解析、计算或重写。
- BR6: BFF 不实现报价算法，不直接访问 quote DB。
- BR7: quote-api 返回 422 `amount_out_of_range` 时，BFF 返回 422 `amount_out_of_range`。
- BR8: quote-api 返回 422 `validation_error` 时，BFF 返回 422 `validation_error`。
- BR9: quote-api 不可用、超时、5xx 或不可映射错误时，BFF 返回 502 `quote_unavailable`。

## Acceptance Criteria

- AC1: 无 token 或无效 token 请求 pricing facade 返回 401 `unauthorized`，且不调用 quote-api。
- AC2: 成功请求会调用 quote-api，返回 `quoteId`、`monthly`、`apr`、`totalInterest`、`totalPayable`、`validUntil`。
- AC3: 下游请求包含 Authorization 派生的 `x-applicant-id`，并忽略外部伪造的 `x-applicant-id`。
- AC4: 下游请求包含 `traceparent`，并在存在时传播 `tracestate`。
- AC5: quote-api 422 `amount_out_of_range` 和 `validation_error` 被映射为 BFF 422 同名错误码。
- AC6: quote-api 不可用、超时或不可映射错误被映射为 502 `quote_unavailable`。
- AC7: Go 测试覆盖 token 缺失、token 无效、成功调用、422 映射、不可用映射、身份传播和 trace 传播。
- AC8: 本地 smoke 可通过 BFF pricing facade 调用 quote-api，并在 quote-api/quote DB 看到对应 Quote。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| LEN-132 是否修改 GitOps 下游配置？ | core | 2026-06-28 | resolved: 不修改；LEN-135 负责部署态下游地址、端口、服务发现和超时 |
| BFF 与 quote-api 使用 HTTP 还是 protobuf/gRPC？ | core | 2026-06-28 | resolved: LEN-10 暴露 HTTP；LEN-132 以 HTTP client adapter 调用，不改 IDL |
| decimal 字段在 BFF 是否重新计算或格式化？ | core | 2026-06-28 | resolved: 不计算、不格式化；BFF 透传 quote-api decimal 字段 |

## Notes

- LEN-132 依赖 LEN-22、LEN-10、LEN-131 已完成。
- LEN-11 后续前端只消费 BFF facade，不直连 Java 服务。
