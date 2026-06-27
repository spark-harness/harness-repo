---
requirement_id: "LEN-133"
owner: "core"
status: "approved"
created_at: "2026-06-28"
related_branch: "feature/LEN-133-fides-bff-origination-facade"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
approved_by: "forest"
approved_at: "2026-06-28T05:59:05+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-133 requirement-review，按 Jira 范围实现 fides-bff origination facade，不修改 IDL，不交付 GitOps runtime 配置或前端接入。"
---

# fides-bff origination facade

## Background

`origination-api` 已由 LEN-9 提供 loan application draft create/get/patch 能力，并由 LEN-134 部署到 `lendora-sta`。前端不能直连 Java 服务，贷款申请草稿必须通过 BFF 进入后端。

这条需求不是什么：它不是创建 `origination-api`，不是部署下游配置，不是前端 Continue 接入，也不是新增 protobuf IDL。

它是什么：它在 `fides-bff` 增加受保护的 loan application facade。BFF 从 LEN-22 principal context 读取 applicantId，调用 `origination-api`，传播 `x-applicant-id` 和 W3C trace headers，并把下游错误映射成统一 BFF error envelope。

## Goals

- 暴露 `POST /api/v1/loan-applications`。
- 暴露 `GET /api/v1/loan-applications/{applicationId}`。
- 暴露 `PATCH /api/v1/loan-applications/{applicationId}`。
- 复用 LEN-22 AuthFilter 和 principal context。
- 只信 Authorization 派生的 applicantId，忽略外部伪造的 `x-applicant-id`。
- 调用 `origination-api` create/get/patch。
- 向下游传播 `x-applicant-id`、`traceparent` 和 `tracestate`。
- POST/PATCH 传播 `Idempotency-Key`。
- 返回前端需要的 draft summary/detail 字段。
- 将下游错误映射为稳定 BFF 错误码。

## Non-Goals

- 不修改 `origination-api` 业务逻辑、repository、migration 或 deployment。
- 不直接访问 application DB。
- 不新增或修改 protobuf IDL。
- 不实现 GitOps runtime 下游地址、服务发现、超时配置交付；LEN-135 负责。
- 不修改前端第二页；LEN-11 负责。
- 不实现 KYC、银行账户、最终提交或审批流。

## User / Business Scenarios

### Scenario 1: 已登录 applicant 创建草稿

Given: 前端携带有效 access token、loan terms、quoteId 和 Idempotency-Key。

When: 前端调用 `POST /api/v1/loan-applications`。

Then: BFF 调用 `origination-api` 创建 draft，返回 `applicationId`、`status=draft`、`currentStep=loan_request`。

### Scenario 2: 已登录 applicant 读取本人草稿

Given: applicant 已有 applicationId。

When: 前端调用 `GET /api/v1/loan-applications/{applicationId}`。

Then: BFF 返回 loan、acceptedQuote、status 和 currentStep，用于页面回填。

### Scenario 3: Continue 静默保存已有草稿

Given: applicant 已有 applicationId，并在当前页修改 loan terms 和 quoteId。

When: 前端调用 `PATCH /api/v1/loan-applications/{applicationId}` 并携带 Idempotency-Key。

Then: BFF 调用 `origination-api` 保存草稿，返回 summary；前端后续由 LEN-11 负责保持当前页不跳转、不 toast。

### Scenario 4: 缺失或无效 token

Given: 请求缺失 access token 或 token 无效。

When: 前端调用任一 loan application facade。

Then: BFF 返回 401 `unauthorized`，不调用 `origination-api`。

### Scenario 5: 攻击者伪造 x-applicant-id

Given: 请求同时携带有效 token 和外部伪造的 `x-applicant-id`。

When: BFF 调用 `origination-api`。

Then: BFF 忽略外部 header，只向下游传播 token principal 中的 applicantId。

## Business Rules

- BR1: loan application facade 必须是受保护接口。
- BR2: applicantId 只能来自 LEN-22 principal context，不得信任外部传入的 `x-applicant-id`。
- BR3: BFF 调用 `origination-api` 时必须带上 `x-applicant-id`。
- BR4: BFF 调用 `origination-api` 时必须传播 `traceparent`，存在 `tracestate` 时也必须传播。
- BR5: POST/PATCH 必须向下游传播 `Idempotency-Key`。
- BR6: BFF 不保存草稿状态，不直接访问 application DB。
- BR7: BFF 不改变金额 decimal 字段语义，不用 float 解析、计算或重写金额。
- BR8: `origination-api` 400 `idempotency_key_required` 映射为 BFF 400 同名错误码。
- BR9: `origination-api` 403 `forbidden` 映射为 BFF 403 同名错误码。
- BR10: `origination-api` 404 `not_found` 映射为 BFF 404 同名错误码。
- BR11: `origination-api` 410 `quote_expired` 映射为 BFF 410 同名错误码。
- BR12: `origination-api` 422 `amount_out_of_range` 或 `validation_error` 映射为 BFF 422 同名错误码。
- BR13: `origination-api` 不可用、超时、5xx、invalid JSON 或未知错误映射为 BFF 502 `origination_unavailable`。

## Acceptance Criteria

- AC1: 无 token 或无效 token 请求任一 loan application facade 返回 401 `unauthorized`，且不调用 `origination-api`。
- AC2: `POST /api/v1/loan-applications` 成功返回 `applicationId`、`status`、`currentStep`。
- AC3: `GET /api/v1/loan-applications/{applicationId}` 成功返回 loan、acceptedQuote、status、currentStep。
- AC4: `PATCH /api/v1/loan-applications/{applicationId}` 成功返回 `applicationId`、`status`、`currentStep`。
- AC5: 下游请求包含 Authorization 派生的 `x-applicant-id`，并忽略外部伪造的 `x-applicant-id`。
- AC6: 下游请求包含 `traceparent`，并在存在时传播 `tracestate`。
- AC7: POST/PATCH 下游请求包含原始 `Idempotency-Key`。
- AC8: 下游 400/403/404/410/422 错误按 BR8-BR12 映射成统一 BFF error envelope。
- AC9: 下游不可用、超时或不可映射错误被映射为 502 `origination_unavailable`。
- AC10: Go 测试覆盖 token 缺失、token 无效、create/get/patch 成功、错误映射、身份传播、trace 传播和 idempotency 传播。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| LEN-133 是否修改 GitOps 下游配置？ | core | 2026-06-28 | resolved: 不修改；LEN-135 负责 runtime address、service discovery 和 timeout |
| BFF 与 origination-api 使用 HTTP 还是 protobuf/gRPC？ | core | 2026-06-28 | resolved: LEN-9 暴露 HTTP；LEN-133 以 HTTP client adapter 调用，不改 IDL |
| BFF 是否保存草稿或访问 application DB？ | core | 2026-06-28 | resolved: 不保存；BFF 只做 facade 和错误映射 |

## Notes

- LEN-133 依赖 LEN-22、LEN-9、LEN-134 已完成。
- LEN-11 后续前端只消费 BFF facade，不直连 Java 服务。

