---
requirement_id: "LEN-9"
owner: "core"
status: "approved"
updated_at: "2026-06-28"
approved_by: "forest"
approved_at: "2026-06-28T04:04:10+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-9 design-review，按 Jira 范围新建 origination-api draft 能力，不修改 IDL，不交付 GitOps runtime 部署。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| BR1, BR9, AC7 | 使用 `RequestPrincipalContext` 获取 applicantId，并在 GET/PATCH 校验 application 归属 | 不接受请求体 applicantId |
| BR2, BR3, AC6 | `IdempotencyService` 按 applicantId + operation + key 存取响应 | POST/PATCH 必填 |
| BR4, AC2 | `CreateLoanApplicationUseCase` 每次新 key 创建新 draft | 同 applicant 多 draft |
| BR5, BR6, AC1, AC3 | `LoanApplication` 状态固定 draft/currentStep loan_request | 本票不推进状态 |
| BR7, BR8, AC5 | `QuoteGateway` 调用 quote-api internal read，保存 acceptedQuote 快照 | 校验归属、有效期和 loan terms |
| AC4 | `GetLoanApplicationUseCase` 返回 loan、acceptedQuote、status、currentStep | 支持回填 |
| AC8, AC9 | JDBC repository、migration、HTTP adapter 和 Java quality 测试 | 不部署 |

## Summary

`origination-api` 是 Origination 子域服务。它拥有 application DB，管理 LoanApplication draft。它只引用和快照 quote-api 已创建的 Quote，不计算报价。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| origination-api | 新建 Java Spring Boot 应用 | 提供 draft create/get/patch |
| quote-api | 无代码修改 | 作为 Quote 校验下游 |
| service matrix | 新增 origination-api | Janus 和后续 tickets 能定位服务 |
| Java quality project graph | 新增 origination-api | CI 覆盖新服务 |

## API / Contract Design

### Create Draft

```text
POST /api/v1/loan-applications
Idempotency-Key: <key>
```

Request:

```json
{
  "productCode": "PIL",
  "loan": {
    "amount": "100000.00",
    "term": 12,
    "purpose": "debt_consolidation"
  },
  "quoteId": "quote_..."
}
```

Response:

```json
{
  "applicationId": "app_...",
  "status": "draft",
  "currentStep": "loan_request"
}
```

### Get Draft

```text
GET /api/v1/loan-applications/{id}
```

Response:

```json
{
  "applicationId": "app_...",
  "loan": {
    "amount": "100000.00",
    "term": 12,
    "purpose": "debt_consolidation"
  },
  "acceptedQuote": {
    "quoteId": "quote_...",
    "monthly": "8560.75",
    "apr": "0.0520",
    "totalInterest": "2729.00",
    "totalPayable": "102729.00",
    "validUntil": "2026-06-28T03:00:00Z"
  },
  "status": "draft",
  "currentStep": "loan_request"
}
```

### Patch Draft

```text
PATCH /api/v1/loan-applications/{id}
Idempotency-Key: <key>
```

Request:

```json
{
  "loan": {
    "amount": "120000.00",
    "term": 24,
    "purpose": "debt_consolidation"
  },
  "quoteId": "quote_..."
}
```

Response:

```json
{
  "applicationId": "app_...",
  "status": "draft",
  "currentStep": "loan_request"
}
```

## Application Design

### Domain

- `LoanApplication`
- `LoanTerms`
- `AcceptedQuote`
- `ApplicationStatus`
- `ApplicationStep`

### Application

- `CreateLoanApplicationUseCase`
  1. 读取 principal applicantId。
  2. 校验 Idempotency-Key。
  3. 校验 request。
  4. 调用 QuoteGateway 获取 Quote。
  5. 校验 Quote applicantId、有效期和 loan terms。
  6. 创建 draft，保存 acceptedQuote snapshot。
  7. 保存幂等响应。
- `PatchLoanApplicationUseCase`
  1. 读取 application。
  2. 校验 applicantId 归属。
  3. 校验 quote。
  4. 更新 loan terms 和 acceptedQuote。
  5. 保持 draft/loan_request。
- `GetLoanApplicationUseCase`
  1. 读取 application。
  2. 校验 applicantId 归属。
  3. 返回回填 DTO。

### Infrastructure

- `JdbcLoanApplicationRepository`。
- `JdbcIdempotencyRepository`。
- `HttpQuoteGateway` 调用 `GET /internal/v1/pricing/quotes/{quoteId}`。
- `JdbcRuntimeDependencyProbe` 检查 application DB readiness。

## Data / Config / Permission

- Data:
  - Flyway migration 创建 `loan_applications` 和 `idempotency_records`。
  - BigDecimal 对应 numeric/decimal。
  - acceptedQuote snapshot 以 JSON 字符串存储，保持回填稳定。
- Config:
  - `spark.origination.jdbc-url`
  - `spark.origination.jdbc-username`
  - `spark.origination.jdbc-password`
  - `spark.origination.quote-api-base-url`
  - `spark.origination.quote-api-timeout`
- Permission:
  - `x-applicant-id` 由 LEN-22 starter filter 写入 RequestPrincipalContext。
  - 不接受前端 applicantId。

## Observability

- health: `/health`。
- ready: `/ready` 检查 DB。
- Downstream: quote-api HTTP 调用传播 trace context。
- Error logs: 使用稳定 error code，不记录 token 和完整敏感表单。

## Testing Strategy

- Application tests:
  - create draft 成功并保存 acceptedQuote。
  - same applicant 多 draft。
  - patch 不推进状态。
  - get 回填。
  - quote 不存在/过期/非本人/loan terms 不一致拒绝。
  - idempotency replay。
- Infrastructure tests:
  - Flyway migration。
  - JDBC save/find/update。
  - idempotency record save/find。
- HTTP tests:
  - POST/GET/PATCH contract。
  - missing Idempotency-Key。
  - forbidden/not_found/quote_expired/amount_out_of_range/validation_error mapping。
- Verification:
  - `mvn test`。
  - Java quality project graph 包含 `origination-api`。

## Rollout And Rollback

- LEN-9 只交付代码、migration、service matrix 和 Java quality 配置。
- LEN-134 负责 runtime deployment、application DB、readiness 和 smoke。
- 回滚 LEN-9 时移除 service code、service matrix entry 和 Java quality project entry。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| quote-api internal response 缺 applicantId | QuoteGateway contract test 使用 fake server 锁定 applicantId 字段 | core |
| 幂等响应保存格式与 HTTP adapter 耦合 | 应用层保存业务 response DTO，不保存原始 servlet 对象 | core |
| 后续 BFF 字段名不一致 | design 固定 LEN-9 HTTP 字段，LEN-133 适配同名字段 | core |
