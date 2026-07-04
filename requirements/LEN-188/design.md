---
requirement_id: "LEN-188"
owner: "forest"
status: "approved"
updated_at: "2026-07-05"
approved_by: "forest"
approved_at: "2026-07-05T03:55:15+08:00"
decision: "用户本轮明确授权处理 LEN-188 的任何事项，包括批准 design。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision |
|---|---|
| R1, AC1, AC2 | D1：`QuoteClient` 调用 `QuoteService.CreateQuote` gRPC。 |
| R2, AC3, AC4 | D2：删除 quote HTTP client、HTTP DTO、fallback 和 HTTP 配置模型。 |
| R3, AC6 | D3：`QuoteGRPCConsulResolver` 通过 Consul health API 读取 `grpc_port` metadata。 |
| R4 | D4：保留 BFF HTTP server、auth filter 和响应 shape。 |
| R5, AC5 | D5：GitOps 删除 `QUOTE_HTTP_*`，加入 `QUOTE_GRPC_*`。 |
| R6, AC7 | D6：用 gRPC span 和配置搜索证明硬切。 |

## Summary

方案只替换 `internal/data/quote_client.go` 的下游协议。`PricingService` 和 HTTP server 仍处理原有请求/响应；业务 command 不再携带 HTTP raw body 或手写 trace header。

## Application Design

- `QuoteClient` 持有 `ServiceResolver`、timeout 和 gRPC dial options。
- `NewQuoteClient` 从 `quote.consul` 和 `quote.grpc` 构造 gRPC client。
- `CreateQuote` 把 BFF request 映射为 `CreateQuoteRequest`。
- `bffkit.OutgoingGRPCContext` 负责 trace/applicant metadata。
- `QuoteGRPCConsulResolver` 返回 `host:grpc_port`，不返回 HTTP URL。

## Config Design

- `quote.http` 删除。
- `quote.grpc.timeout` 和 `quote.grpc.plaintext` 与 applicant/origination gRPC 配置保持一致。
- GitOps `QUOTE_GRPC_TIMEOUT=3s`、`QUOTE_GRPC_PLAINTEXT=true`。

## Testing Strategy

- test-first 目标：旧 `idl-go-repo v0.2.5` 不含 quote package，新增 quote gRPC 测试先失败。
- `internal/data`：覆盖 gRPC request、metadata、trace ID、错误映射和 Consul `grpc_port`。
- `internal/server`：保留 BFF HTTP 入口与 principal 清洗测试。
- `cmd/fides-bff`：配置 loader 覆盖 `QUOTE_GRPC_*`。
- GitOps：渲染 dev-1/sta-1，搜索无 `QUOTE_HTTP_*`。

## Rollout And Rollback

- Rollout: merge BFF and GitOps after tests and render pass.
- Rollback: revert BFF image and GitOps config together.
- Final HTTP cleanup remains `LEN-196`。
