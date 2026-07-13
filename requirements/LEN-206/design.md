---
status: "approved"
approved_by: "forest"
approved_at: "2026-07-12T16:58:45+08:00"
decision: "用户授权交付 LEN-206；批准当前 design，按官方 OpenTelemetry instrumentation 与独立 Principal metadata 组件实现。"
---

# LEN-206 Design

## Requirement Traceability

| Requirement | Design |
| --- | --- |
| R1, AC1 | `fides-bff` HTTP server 使用官方 `otelhttp.NewMiddleware`，通过 Kratos v3 transport filter 接入；`TraceFilter` 不再创建 span。 |
| R2, AC2 | BFF gRPC clients 在 dial options 中挂 `otelgrpc.NewClientHandler()`。 |
| R3, AC3 | Java starter 用 `GrpcTelemetry.createServerInterceptor()` 替代自研 server interceptor。 |
| R4, AC4 | `origination-api` quote channel 挂 `GrpcTelemetry.createClientInterceptor()`。 |
| R5, AC5 | 新增 `RequestPrincipalGrpcClientInterceptor` 注入 `x-applicant-id`。 |

## Summary

硬切原则是把 tracing 交给官方库，把 Principal metadata 交给独立组件。业务 adapter 和 gateway 不再负责 trace context 注入或 span 生命周期。

## Affected Services

- `apps/fides-bff`
- `apps/origination-api`
- `apps/quote-api`
- `packages/go/bffkit`
- `packages/java/spring-starter`

## Application Design

### Go BFF

- `internal/server/http.go` 增加官方 `otelhttp.NewMiddleware`，通过 Kratos v3 transport filter 接入。
- `bffkit.TraceFilter` 只负责 access log、correlation header 和 metrics，不再创建 server span。
- `ApplicantAuthClient`、`QuoteClient`、`OriginationClient` 的 dial options 增加 `grpc.WithStatsHandler(otelgrpc.NewClientHandler())`。
- `bffkit.OutgoingGRPCContext` 保留 `x-trace-id`、`x-correlation-id`、`x-applicant-id`，不写 W3C trace headers。

### Java

- 删除自研 `OpenTelemetryGrpcServerInterceptor`。
- `GrpcServerAutoConfiguration` 通过官方 `GrpcTelemetry` 暴露 server interceptor，并由独立 metadata interceptor 保留 `x-trace-id` response metadata 和稳定错误码 enrich。
- 新增 `RequestPrincipalGrpcClientInterceptor` 和独立 auto-configuration，从 `RequestPrincipalContext` 注入 `x-applicant-id`。
- `OriginationConfiguration` 在 `quoteApiChannel` 上挂官方 tracing client interceptor 和 principal client interceptor。
- `GrpcQuoteGateway` 只保留业务调用、响应转换和错误映射。

## API / Contract Design

无 IDL、HTTP 或错误码契约变更；既有 gRPC `x-trace-id` response metadata 保持兼容。

## Data / Config / Permission

无数据变更。Principal metadata 只来自服务端已认证上下文。

## Observability

目标 trace 拓扑必须在部署后验证：

```text
fides http.client -> fides-bff http.server -> fides-bff rpc -> origination-api CreateLoanApplication -> origination-api rpc -> quote-api GetQuote
```

## Testing Strategy

- Go：`go test ./...` in `apps/fides-bff`。
- Go：`go test ./...` in `packages/go/bffkit`。
- Java：starter gRPC auto-config / lifecycle / principal client interceptor tests。
- Java：`GrpcQuoteGatewayTest` 验证 quote-api 收到 trace context 和 applicant metadata。
- Runtime：LEN-210 在真实环境直连服务，使用 Sentry trace view 验证 quote child 出现在同一 trace。

## Rollout And Rollback

先合并业务仓，部署验证环境后执行 LEN-210。失败时回滚 business-repo commit，无需数据处理。

## Risks

- 本地 Java 验证受 Maven Central 403 和 GitHub Packages 401 影响，CI 或网络恢复后必须补跑。
- 如果 runtime 未启用 Java OTel exporter，即使 span 创建正确也不会进入目标 Sentry project。
