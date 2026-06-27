---
requirement_id: "LEN-133"
owner: "core"
status: "approved"
updated_at: "2026-06-28"
approved_by: "forest"
approved_at: "2026-06-28T05:59:05+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-133 design-review，复用 LEN-132 BFF facade 模式调用 origination-api，传播 principal、trace 和 Idempotency-Key。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| BR1, AC1 | 复用 `isProtectedPath` 下已覆盖的 `/api/v1/loan-applications` 保护规则 | LEN-22 AuthFilter 已在 server 层生效 |
| BR2, BR3, AC5 | handler 从 `bffkit.PrincipalFromContext` 读取 applicantId，client 注入 `x-applicant-id` | 忽略外部 header |
| BR4, AC6 | origination client 复制入站 `traceparent` 和 `tracestate` 到下游 HTTP request | 同步 HTTP parent/child 传播 |
| BR5, AC7 | POST/PATCH 从入站 request 读取 `Idempotency-Key` 并转发 | GET 不要求 idempotency |
| BR6, BR7, AC2-AC4 | BFF 只透传 HTTP JSON body 和 response fields，不保存草稿、不计算金额 | 保持 decimal string/raw JSON 语义 |
| BR8-BR13, AC8, AC9 | data client 将 origination-api 响应映射为 biz error，service 映射为 BFF error envelope | 不暴露下游地址或内部异常 |
| AC10 | handler/client 测试覆盖成功、鉴权、身份、trace、idempotency 和错误映射 | 运行 `go test ./...` |

## Summary

`fides-bff` 增加一个薄 origination facade：HTTP handler 做协议解析和 principal 读取，biz usecase 定义 origination client 端口，data adapter 用 HTTP 调用 `origination-api`。BFF 不引入草稿业务规则。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| fides-bff | 新增 origination route、usecase、service、client 和 config | 对前端暴露 loan application facade |
| origination-api | 无代码修改 | 作为下游 HTTP 服务被调用 |

## API / Contract Design

### BFF Endpoints

```text
POST /api/v1/loan-applications
GET /api/v1/loan-applications/{applicationId}
PATCH /api/v1/loan-applications/{applicationId}
```

POST request:

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

PATCH request:

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

Summary response:

```json
{
  "applicationId": "app_...",
  "status": "draft",
  "currentStep": "loan_request"
}
```

Detail response:

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

### Error Mapping

| Downstream / Local condition | BFF HTTP | BFF code |
|---|---:|---|
| missing or invalid token | 401 | `unauthorized` |
| origination-api 400 `idempotency_key_required` | 400 | `idempotency_key_required` |
| origination-api 403 `forbidden` | 403 | `forbidden` |
| origination-api 404 `not_found` | 404 | `not_found` |
| origination-api 410 `quote_expired` | 410 | `quote_expired` |
| origination-api 422 `amount_out_of_range` | 422 | `amount_out_of_range` |
| origination-api 422 `validation_error` | 422 | `validation_error` |
| origination-api timeout, network error, 5xx, invalid JSON, unknown error | 502 | `origination_unavailable` |

## Application Design

### HTTP Handler

- Register routes under `/api/v1`:
  - `POST /loan-applications`
  - `GET /loan-applications/{applicationId}`
  - `PATCH /loan-applications/{applicationId}`
- Read principal from `bffkit.PrincipalFromContext`。
- Decode POST/PATCH JSON with `UseNumber` for syntax validation。
- Keep original JSON bytes for downstream request body。
- Read `Idempotency-Key` for POST/PATCH。
- Pass applicantId, trace headers, idempotency key and raw body to `OriginationUsecase`。

### Biz Layer

- Add `OriginationUsecase`。
- Define `OriginationClient` port owned by BFF usecase。
- Define commands:
  - `CreateLoanApplicationCommand`
  - `GetLoanApplicationCommand`
  - `PatchLoanApplicationCommand`
- Define results:
  - `LoanApplicationSummary`
  - `LoanApplicationDetail`
- Define stable error codes:
  - `idempotency_key_required`
  - `forbidden`
  - `not_found`
  - `quote_expired`
  - `amount_out_of_range`
  - `validation_error`
  - `origination_unavailable`

### Data Adapter

- Add `origination-api` HTTP client。
- Resolve target base URL using:
  1. direct `origination.http.base_url` when present,
  2. Consul service resolver when direct URL is absent.
- Use context timeout from config。
- Send:
  - `POST /api/v1/loan-applications`
  - `GET /api/v1/loan-applications/{applicationId}`
  - `PATCH /api/v1/loan-applications/{applicationId}`
- Set downstream headers:
  - `Content-Type: application/json` for POST/PATCH
  - `x-applicant-id: <principal applicantId>`
  - `traceparent` if present
  - `tracestate` if present
  - `Idempotency-Key` for POST/PATCH if present
- Close response bodies and map errors without leaking internals。

## Data / Config / Permission

- Data:
  - BFF does not add storage。
  - BFF does not mutate application DB directly。
- Config:
  - `origination.http.base_url`
  - `origination.http.timeout`
  - `origination.consul.address`
  - `origination.consul.scheme`
  - `origination.consul.service_name`
- Permission:
  - Protected route enforced by LEN-22 AuthFilter。
  - applicantId source is principal context only。

## Observability

- BFF TraceFilter continues to create/extract request trace context。
- origination client creates outbound HTTP client span。
- origination client propagates W3C TraceContext headers。
- Timeout and unavailable errors map to `origination_unavailable`。
- Logs must not include Authorization, token, or full request body。

## Testing Strategy

- Handler tests:
  - no token returns 401 and fake origination-api is not called。
  - invalid token returns 401 and fake origination-api is not called。
  - create returns summary。
  - get returns detail。
  - patch returns summary。
  - attacker `x-applicant-id` is ignored。
  - `traceparent` and `tracestate` are propagated。
  - POST/PATCH propagate `Idempotency-Key`。
- Client/error tests:
  - origination-api 400/403/404/410/422 maps to expected BFF error。
  - origination-api unavailable, 5xx or invalid response maps to 502 `origination_unavailable`。
- Verification:
  - `go test ./...` from `apps/fides-bff`。
  - local smoke against running `origination-api` when runtime config is available。

## Rollout And Rollback

- Rollout:
  1. Merge BFF facade with tests。
  2. LEN-135 configures runtime origination endpoint and service discovery。
  3. LEN-11 consumes facade from frontend。
- Rollback:
  - Revert BFF facade code/config。
  - No DB rollback。
  - No origination-api rollback required。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Config surface added before runtime GitOps | Keep defaults local-only and document LEN-135 ownership | core |
| Downstream response shape changes | Client tests assert summary/detail fields | core |
| Trace propagation omitted in client | Handler and client tests assert fake origination-api receives trace headers | core |
| Idempotency header omitted | Handler/client tests assert POST/PATCH propagation | core |

