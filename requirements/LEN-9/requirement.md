---
requirement_id: "LEN-9"
owner: "core"
status: "approved"
created_at: "2026-06-28"
related_branch: "feature/LEN-9-origination-api-drafts"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
approved_by: "forest"
approved_at: "2026-06-28T04:04:10+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-9 requirement-review，按 Jira 范围新建 origination-api draft 能力，不修改 IDL，不交付 GitOps runtime 部署。"
---

# origination-api 申请草稿创建与静默保存

## Background

贷款申请第二页 Continue 需要把 loan terms 和 quoteId 静默保存成草稿。当前系统已有 quote-api 试算能力，但缺少承载申请草稿、状态和回填的 Origination 服务。

这条需求不是什么：它不是 BFF facade，不是前端 Continue 接入，不是 Kubernetes 部署，也不是 KYC、银行账户或最终提交。

它是什么：它新建 `origination-api`，管理 LoanApplication draft 聚合，支持多笔并行草稿、创建、读取回填、PATCH 静默保存、幂等和 quoteId 归属/有效期校验。

## Goals

- 新建 `business-repo/apps/origination-api` Java Spring 服务。
- 支持 `POST /api/v1/loan-applications` 创建 draft。
- 支持 `GET /api/v1/loan-applications/{id}` 读取本人草稿并回填 loan 和 acceptedQuote。
- 支持 `PATCH /api/v1/loan-applications/{id}` 保存当前 loan terms 与 quoteId。
- 同一 applicant 可存在多笔并行 draft。
- Continue 创建/保存必须使用 Idempotency-Key。
- 保存 quoteId 前校验 quote 存在、属于当前 applicant、未过期，并与 loan terms 一致。
- 初始和保存成功后保持 `status=draft`、`currentStep=loan_request`。
- 新增 application DB migration 和 repository 测试。

## Non-Goals

- 不修改 `fides-bff`，LEN-133 负责 BFF origination facade。
- 不修改前端，LEN-11 负责 Continue 调用 BFF。
- 不部署 `origination-api` 或 application DB，LEN-134 负责。
- 不实现 KYC、银行账户、AIP、under_review、submit 或审批流。
- 不修改 protobuf IDL 或 generated contracts。
- 不实现 pricing 算法；quote 校验通过 quote-api 内部读取边界完成。

## User / Business Scenarios

### Scenario 1: Continue 创建新草稿

Given: 已认证 applicant 在 loan request 页已有 quoteId。

When: 调用 `POST /api/v1/loan-applications` 并携带 Idempotency-Key。

Then: 服务校验 Quote 后创建一笔 draft，返回 `applicationId`、`status=draft`、`currentStep=loan_request`。

### Scenario 2: Continue 保存已有草稿

Given: applicant 已有 draft applicationId。

When: 调用 `PATCH /api/v1/loan-applications/{id}` 保存 loan terms 与 quoteId。

Then: 服务更新同一草稿，状态仍为 draft，不推进步骤。

### Scenario 3: 打开同一草稿回填

Given: applicant 保存过 draft。

When: 调用 `GET /api/v1/loan-applications/{id}`。

Then: 返回 applicationId、loan、acceptedQuote、status 和 currentStep，用于前端回填。

### Scenario 4: 同一 applicant 多笔并行草稿

Given: 同一 applicant 多次发起不同贷款请求。

When: 使用不同 Idempotency-Key 调用创建接口。

Then: 返回不同 applicationId，草稿互不覆盖。

### Scenario 5: Quote 不可用于保存

Given: quoteId 不存在、已过期、不属于当前 applicant 或与 loan terms 不一致。

When: 创建或保存草稿。

Then: 服务拒绝请求，返回稳定错误码，且不写入错误草稿。

## Business Rules

- BR1: applicantId 只能来自 LEN-22 principal context，不接受请求体 applicantId。
- BR2: `POST` 和 `PATCH` 必须要求 Idempotency-Key。
- BR3: 同一 applicant、同一 operation、同一 Idempotency-Key 重试必须返回同一结果，不重复创建草稿。
- BR4: 同一 applicant 允许存在多笔 draft。
- BR5: 新建草稿初始 `status=draft`、`currentStep=loan_request`。
- BR6: Continue 保存成功后仍保持 `status=draft`、`currentStep=loan_request`。
- BR7: 保存 quoteId 前必须调用 quote-api 内部 Quote 读取/校验边界。
- BR8: acceptedQuote 必须保存 Quote 快照，至少包含 quoteId、monthly、apr、totalInterest、totalPayable、validUntil。
- BR9: GET/PATCH 只能访问当前 applicant 自己的 application。
- BR10: 金额字段使用 BigDecimal/decimal，不使用 double/float。

## Acceptance Criteria

- AC1: `POST /api/v1/loan-applications` 创建 draft，并返回 applicationId、status、currentStep。
- AC2: 同一 applicant 可创建多笔 draft，applicationId 独立。
- AC3: `PATCH /api/v1/loan-applications/{id}` 可保存 loan terms 和 acceptedQuote，且不推进步骤。
- AC4: `GET /api/v1/loan-applications/{id}` 可回填 loan、acceptedQuote、status、currentStep。
- AC5: quote 不存在、过期、不属于当前 applicant、与 loan terms 不一致时拒绝保存。
- AC6: 缺少 Idempotency-Key 返回 `idempotency_key_required`，同 key 重试不重复创建或重复变更。
- AC7: 跨 applicant 读取或保存他人 application 返回 `forbidden`。
- AC8: Repository/integration 测试覆盖 migration、draft 写入、读取、更新和幂等记录。
- AC9: Maven test 和 Java quality 配置覆盖 `origination-api`。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| LEN-9 是否新增 protobuf IDL？ | core | 2026-06-28 | resolved: 不新增；本 ticket 使用服务内 HTTP contract，BFF facade 后续由 LEN-133 适配 |
| LEN-9 是否部署 application DB？ | core | 2026-06-28 | resolved: 不部署；LEN-134 负责 runtime DB 和 readiness 验证 |
| POST 是否必须携带 quoteId？ | core | 2026-06-28 | resolved: Jira 明确 Continue 创建/保存当前 loan terms 与 quoteId；MVP POST 要求 quoteId |

## Notes

- LEN-9 依赖 LEN-22、LEN-10、LEN-131 和 LEN-132 已完成。
- LEN-133 后续让前端经 BFF 调用 origination-api。
