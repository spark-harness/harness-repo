---
requirement_id: "LEN-11"
owner: "core"
status: "approved"
created_at: "2026-06-28"
related_branch: "feature/LEN-11-loan-request-real-pricing-draft"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
approved_by: "forest"
approved_at: "2026-06-28T07:11:29+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-11 requirement 和 impact-analysis，范围为 fides-web 第二页接真实 pricing/draft API，UI 参照 code.html，Continue 成功后停留当前页。"
---

# 贷款请求屏接试算与 Continue 静默保存

## Background

贷款申请第二页当前只有参考 HTML 原型和前端骨架，真实 `fides-web` 仍停留在手机号验证屏。前序票已交付：

- LEN-22：BFF 受保护接口鉴权、principal context、`x-applicant-id` 和 tracing。
- LEN-132：`fides-bff` pricing facade。
- LEN-133：`fides-bff` origination facade。
- LEN-135：lendora-sta 下游 discovery 和 runtime smoke。

这条需求不是什么：它不是新增 BFF 或 Java 服务能力，不是修改 IDL，不是做第三页身份信息导航。

它是什么：它把前端第二页变成可用屏幕，调用 BFF 真实 pricing 和 draft API，并在 Continue 成功后静默保存草稿、停留当前页。

## Goals

- 在 `fides-web` 中新增贷款请求屏，视觉和交互完全参照 `.docs/hk_loan_ui/2._loan_request_input_field/code.html`。
- 手机号验证成功后进入贷款请求屏，并保留 access token 在内存会话中供 BFF 请求使用。
- 贷款金额、期限、用途变更后调用 `POST /api/v1/pricing/quotes` 获取真实试算。
- 显示 BFF 返回的 monthly、APR、totalInterest、validUntil 等 quote 信息，不继续使用本地 `recalc()` 作为权威结果。
- Continue 调用 BFF loan application create 或 patch，保存 loan terms 和 quoteId。
- Continue 保存成功后停留当前页，不跳转、不 toast。
- 同一草稿重新进入时可以调用 `GET /api/v1/loan-applications/{applicationId}` 回填 loan 和 acceptedQuote。
- 所有请求只调用 BFF，不直连 `quote-api` 或 `origination-api`。

## Non-Goals

- 不实现第三页身份信息或后续步骤导航。
- 不新增或修改 `fides-bff` API。
- 不修改 protobuf IDL、generated contracts 或 BFF TS client。
- 不修改 Java `quote-api` / `origination-api`。
- 不提交真实 token、手机号、证件号或生产数据。
- 不实现离线跨设备恢复；本票只保留当前浏览器会话的 application pointer。

## User / Business Scenarios

### Scenario 1: 真实试算

Given: 用户已通过手机号验证并进入贷款请求屏。

When: 用户填写有效金额、期限和用途。

Then: 前端调用 BFF `POST /api/v1/pricing/quotes`，显示真实 quote 结果，并保存当前 quoteId 供 Continue 使用。

### Scenario 2: Continue 创建草稿

Given: 当前会话没有 applicationId，但已有有效 quoteId。

When: 用户点击 Continue。

Then: 前端调用 BFF `POST /api/v1/loan-applications` 创建草稿，保存返回的 applicationId，并停留在贷款请求屏。

### Scenario 3: Continue 静默保存已有草稿

Given: 当前会话已有 applicationId 和有效 quoteId。

When: 用户修改 loan terms 后点击 Continue。

Then: 前端调用 BFF `PATCH /api/v1/loan-applications/{applicationId}` 保存草稿，保存成功后停留当前页，不跳转、不 toast。

### Scenario 4: 同一草稿回填

Given: 当前会话保存过 applicationId。

When: 用户重新进入贷款请求屏。

Then: 前端调用 BFF `GET /api/v1/loan-applications/{applicationId}`，用返回的 loan 和 acceptedQuote 回填屏幕。

## Business Rules

- BR1: 前端只能调用 `fides-bff`，不得直连 `quote-api` 或 `origination-api`。
- BR2: pricing 请求必须携带 Authorization、Idempotency-Key 和 trace headers。
- BR3: draft create/patch/get 必须携带 Authorization；create/patch 必须携带 Idempotency-Key。
- BR4: 金额范围为 HKD 5,000 到 HKD 500,000。
- BR5: 期限选项只允许 3、6、9、12、24 个月。
- BR6: 用途必须从屏幕选项中选择，并映射为后端接受的 purpose code。
- BR7: pricing 成功返回前，Continue 不应提交草稿。
- BR8: Continue 保存成功后不得跳转、不得 toast、不得推进步骤。
- BR9: 当前浏览器会话只在内存保存 access token；sessionStorage 只保存非敏感 application pointer。
- BR10: BFF 返回 401/token 失效时，前端应回到手机号验证路径或展示重新验证信息。

## Acceptance Criteria

- AC1: 贷款请求屏视觉结构、文案、输入控件、summary、bottom bar 和 Step 2 progress 与 `code.html` 保持一致。
- AC2: 手机号验证成功后显示贷款请求屏。
- AC3: 有效 loan terms 触发真实 BFF pricing，并显示返回 quote。
- AC4: pricing loading/error 状态可见且不会使用本地假结果伪装成功。
- AC5: Continue 在无 applicationId 时调用 BFF create，保存 applicationId。
- AC6: Continue 在已有 applicationId 时调用 BFF patch。
- AC7: Continue 保存成功后停留当前页，不跳转、不 toast。
- AC8: 重新进入同一草稿时从 BFF get 回填 loan 和 acceptedQuote。
- AC9: 前端单元/组件测试覆盖 pricing、create、patch、get 回填和无跳转行为。
- AC10: runtime smoke 在 lendora-sta 访问前端，完成手机号验证后进入第二页，真实 pricing 和 Continue 保存可用。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 第二页成功保存后是否进入第三页？ | product | 2026-06-28 | resolved: 本票明确不跳转、不 toast，停留当前页 |
| 是否使用生成 TS client？ | core | 2026-06-28 | resolved: 现有 TS client 只覆盖 auth；本票用薄 HTTP gateway 调 BFF 已交付 REST facade |
| 草稿 pointer 是否可持久化到 localStorage？ | core | 2026-06-28 | resolved: 不保存敏感 token；只可在 sessionStorage 保存非敏感 applicationId/applicantId |

## Notes

- 当前 UI 目标来自 `.docs/hk_loan_ui/2._loan_request_input_field/code.html`。
- 当前集群为 vincent-k3s。

