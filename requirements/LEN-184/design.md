---
requirement_id: "LEN-184"
owner: "forest"
status: "approved"
updated_at: "2026-07-05"
approved_by: "forest"
approved_at: "2026-07-05T03:32:57+08:00"
decision: "用户本轮明确授权处理 LEN-184 的任何事项，包括批准 design。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, R2, AC1, AC2 | D1：新增 `GrpcQuoteGateway`，调用 `QuoteService.GetQuote`。 | 消费 Java contract `0.2.7`。 |
| R3, AC3, AC4 | D2：删除 `HttpQuoteGateway` 使用路径、HTTP client bean 和 quote HTTP 配置。 | 不保留 fallback。 |
| R4 | D3：保留 `LoanApplicationHttpAdapter`、HTTP exception handler、health/readiness。 | 最终 HTTP 清理由 `LEN-196` 执行。 |
| R5, AC5 | D4：GitOps 删除 `ORIGINATION_QUOTE_API_BASE_URL` 和 quote HTTP timeout。 | 搜索 base URL 作为证据。 |
| R6, AC6 | D5：确认 `origination-api` 到 `quote-api` 的 gRPC 9090 NetworkPolicy。 | 不删除 `lendora-shared-consul`。 |
| R7, AC7 | D6：验证 trace 只出现 quote gRPC client/server span，不出现业务 HTTP span。 | live 验证依赖环境。 |

## Summary

方案在 `origination-api` 基础设施层替换出站 adapter。应用层仍依赖 `QuoteGateway` port，创建和更新贷款申请 use case 不感知协议变化。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| origination-api | 新增 gRPC quote gateway，删除 quote HTTP gateway 和 HTTP quote 配置 | 硬切内部业务调用 |
| quote-api | 无代码变更 | 既有 gRPC server 作为下游 |
| origination-api GitOps | 删除 quote HTTP base URL/timeout，保留自身 HTTP 和 9090 | 防止配置继续允许 HTTP fallback |

## API / Contract Design

- IDL change: none.
- Consumed contract: `com.vesta.lendora.quote.v1.QuoteServiceGrpc`。
- RPC: `GetQuote`。
- Identity: 从 `RequestPrincipalContext` 读取 applicant ID，作为 `x-applicant-id` gRPC metadata 发送。
- Amount: quote decimal string 转换为 `BigDecimal`，不改变语义。
- Timeout: gRPC stub 使用 deadline；超时映射为 `QuoteUnavailableException`。

## Application Design

- `QuoteGateway` port 保持不变。
- `GrpcQuoteGateway` 位于 `infrastructure`，实现 `QuoteGateway`。
- `OriginationConfiguration` 装配 `ManagedChannel`、`QuoteServiceBlockingStub` 和 `GrpcQuoteGateway`。
- `HttpQuoteGateway` 文件和使用路径删除。
- `LoanApplicationHttpAdapter` 和 `LoanApplicationHttpExceptionHandler` 保留。

## Error Handling

| quote gRPC result | origination application exception |
|---|---|
| `Status.Code.NOT_FOUND` | `QuoteNotFoundException` |
| `Status.Code.FAILED_PRECONDITION` | `QuoteExpiredException` |
| `Status.Code.PERMISSION_DENIED` | `ForbiddenException` |
| `Status.Code.UNAVAILABLE` | `QuoteUnavailableException` |
| `Status.Code.UNKNOWN` | `QuoteUnavailableException` |
| malformed response or missing principal | `QuoteUnavailableException` |

## Data / Config / Permission

- Data model: no schema change.
- Removed config:
  - `ORIGINATION_QUOTE_API_BASE_URL`
  - `ORIGINATION_QUOTE_API_TIMEOUT`
  - `spark.origination.quote-api-base-url`
  - `spark.origination.quote-api-timeout`
- Added config:
  - `spark.origination.quote-api-grpc-target`
  - `spark.origination.quote-api-timeout`
- Permission: ensure `quote-api` NetworkPolicy allows caller namespaces on 9090 and `origination-api` egress/ingress rules do not block 9090.

## Observability

- Tracing: OpenTelemetry gRPC instrumentation should produce client span from `origination-api` and server span in `quote-api` when runtime instrumentation is enabled.
- Logs: no quote body logging.
- Metrics: no custom metrics required.
- Evidence: trace query or explicit environment blocker is recorded under `evidence/`.

## Testing Strategy

- Test-first: add `GrpcQuoteGatewayTest` before production change; expected initial failure is missing `GrpcQuoteGateway` and HTTP config assertions.
- Unit/in-process gRPC: cover successful GetQuote, identity metadata, `NOT_FOUND`, `FAILED_PRECONDITION`, `PERMISSION_DENIED`, `UNAVAILABLE`, `UNKNOWN` mappings.
- Wiring/config: prove application context wires `GrpcQuoteGateway` and application YAML no longer contains quote HTTP base URL.
- Regression: existing loan application gRPC and HTTP inbound tests continue passing.
- GitOps: render dev-1 and sta-1 overlays and search rendered output for absence of quote HTTP base URL under origination-api.

## Rollout And Rollback

- Rollout: deploy after `quote-api` gRPC server is live and Java artifact `0.2.7` is available.
- Rollback: revert `origination-api` image and GitOps config together.
- No partial fallback: do not reintroduce HTTP fallback as a runtime switch.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| gRPC deadline too low or target wrong | Use configurable target/deadline and test config binding | forest |
| NetworkPolicy misses 9090 | kustomize render and live connectivity/trace verification | forest |
| HTTP cleanup scope creep | Preserve own HTTP inbound files and explicitly defer final HTTP cleanup to `LEN-196` | forest |
