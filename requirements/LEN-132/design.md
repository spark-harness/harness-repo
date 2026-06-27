---
requirement_id: "LEN-132"
owner: "core"
status: "approved"
updated_at: "2026-06-28"
approved_by: "forest"
approved_at: "2026-06-28T03:34:39+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-132 design-review，按 Jira 范围实现 fides-bff pricing facade，不修改 IDL，不交付 GitOps runtime 配置。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| BR1, AC1 | 继续使用 `isProtectedPath` 下的 `/api/v1/pricing/` 保护规则 | LEN-22 已覆盖路径匹配 |
| BR2, BR3, AC3 | handler 从 `bffkit.PrincipalFromContext` 读取 applicantId，client 注入 `x-applicant-id` | 忽略外部 header |
| BR4, AC4 | quote client 复制入站 `traceparent` 和 `tracestate` 到下游 HTTP request | 同步 HTTP parent/child 传播 |
| BR5, AC2 | request/response 使用 `json.RawMessage` / string 字段保存 decimal 语义 | BFF 不计算不格式化 |
| BR6 | pricing usecase 只编排 quote-api client | 不访问 quote DB |
| BR7, BR8, BR9, AC5, AC6 | data client 将 quote-api 响应映射为 biz error，service 映射为 BFF error envelope | 不暴露下游细节 |
| AC7, AC8 | handler/client 测试和本地 smoke 证据 | smoke 使用本地或 port-forward quote-api |

## Summary

`fides-bff` 增加一个薄 pricing facade：HTTP handler 做协议解析和 principal 读取，biz usecase 定义 quote client 端口，data adapter 用 HTTP 调用 quote-api。BFF 不引入报价业务规则。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| fides-bff | 新增 pricing route、usecase、service、quote client 和 config | 对前端暴露试算 facade |
| quote-api | 无代码修改 | 作为下游 HTTP 服务被调用 |

## API / Contract Design

### BFF Endpoint

```text
POST /api/v1/pricing/quotes
```

Request:

```json
{
  "productCode": "PIL",
  "amount": "100000.00",
  "term": 12,
  "purpose": "debt_consolidation"
}
```

Response:

```json
{
  "quoteId": "quote_...",
  "monthly": "8560.75",
  "apr": "0.0520",
  "totalInterest": "2729.00",
  "totalPayable": "102729.00",
  "validUntil": "2026-06-28T03:00:00Z"
}
```

### Error Mapping

| Downstream / Local condition | BFF HTTP | BFF code |
|---|---:|---|
| missing or invalid token | 401 | `unauthorized` |
| quote-api 422 `amount_out_of_range` | 422 | `amount_out_of_range` |
| quote-api 422 `validation_error` | 422 | `validation_error` |
| quote-api timeout, network error, 5xx, invalid JSON, unknown error | 502 | `quote_unavailable` |

## Application Design

### HTTP Handler

- Register `POST /api/v1/pricing/quotes` under `/api/v1`.
- Decode JSON with `UseNumber` to avoid float coercion.
- Validate body is syntactically valid JSON; semantic field validation remains quote-api responsibility.
- Read principal from `bffkit.PrincipalFromContext`.
- Pass request, applicantId, trace headers and context to `PricingUsecase`.

### Biz Layer

- Add `PricingUsecase`.
- Define `QuoteClient` port owned by BFF usecase.
- Define `CreateQuoteCommand` and `QuoteResult`.
- Define stable pricing error codes:
  - `amount_out_of_range`
  - `validation_error`
  - `quote_unavailable`

### Data Adapter

- Add quote-api HTTP client.
- Resolve target base URL using:
  1. direct `quote.http.base_url` when present,
  2. Consul service resolver when direct URL is absent.
- Use context timeout from config.
- POST to `/api/v1/pricing/quotes`.
- Set downstream headers:
  - `Content-Type: application/json`
  - `x-applicant-id: <principal applicantId>`
  - `traceparent` if present on inbound request
  - `tracestate` if present on inbound request
- Close response bodies and map errors without leaking internals.

## Data / Config / Permission

- Data:
  - BFF does not add storage.
  - BFF does not mutate quote DB.
- Config:
  - `quote.http.base_url`
  - `quote.http.timeout`
  - `quote.consul.address`
  - `quote.consul.scheme`
  - `quote.consul.service_name`
- Permission:
  - Protected route enforced by LEN-22 AuthFilter.
  - applicantId source is principal context only.

## Observability

- BFF TraceFilter continues to create/extract request trace context.
- quote client propagates W3C TraceContext headers.
- Timeout and unavailable errors map to `quote_unavailable`.
- Logs must not include Authorization, token, or full request body.

## Testing Strategy

- Handler tests:
  - no token returns 401 and fake quote-api is not called.
  - invalid token returns 401 and fake quote-api is not called.
  - success returns required response fields.
  - attacker `x-applicant-id` is ignored.
  - `traceparent` and `tracestate` are propagated.
- Client/error tests:
  - quote-api 422 `amount_out_of_range` maps to BFF 422.
  - quote-api 422 `validation_error` maps to BFF 422.
  - quote-api unavailable or invalid response maps to 502 `quote_unavailable`.
- Verification:
  - `go test ./...` from `apps/fides-bff`.
  - local smoke against running quote-api where feasible.

## Rollout And Rollback

- Rollout:
  1. Merge BFF facade with tests.
  2. LEN-135 configures runtime quote-api endpoint and service discovery.
  3. LEN-11 consumes facade from frontend.
- Rollback:
  - Revert BFF facade code/config.
  - No DB rollback.
  - No quote-api rollback required.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Config surface added before runtime GitOps | Keep defaults local-only and document LEN-135 ownership | core |
| Downstream response decimal format changes | Contract-facing test asserts frontend fields exist and stay strings/raw decimal-compatible | core |
| Trace propagation omitted in client | Handler test asserts fake quote-api receives `traceparent` | core |
