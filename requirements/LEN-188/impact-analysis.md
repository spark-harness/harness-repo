---
requirement_id: "LEN-188"
analyst: "forest"
status: "approved"
updated_at: "2026-07-05"
idl_impact: "no"
idl_impact_reason: "quote-api gRPC 服务端和 Go SDK v0.2.6 已由 LEN-176 完成；本需求只消费既有 QuoteService.CreateQuote。"
approved_by: "forest"
approved_at: "2026-07-05T04:02:01+08:00"
decision: "用户本轮明确授权处理 LEN-188 的任何事项，包括批准 impact-analysis 进入服务仓库检查。"
---

# Impact Analysis

## Summary

本需求把 `fides-bff` 对 `quote-api` 的报价创建从内部 HTTP 改为 gRPC。影响集中在 BFF quote client、配置模型、GitOps 环境变量、Go contract 版本和 trace 验证。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides-bff | `{business-repo}/apps/fides-bff` | 替换 quote 出站 client 和配置 | Yes, consume only |
| quote-api | `{business-repo}/apps/quote-api` | 既有 gRPC server 被调用，本需求不修改 | Yes, no change |
| fides-bff GitOps | `{gitops-repo}/apps/fides-bff` | 删除 quote HTTP config，加入 quote gRPC config | No |

## Upstream / Downstream

- Upstream: `fides-web` 仍通过 BFF HTTP API 发起报价，本需求不修改。
- Downstream: `fides-bff -> quote-api` 从 HTTP 改为 gRPC。

## API / Contract Impact

- IDL change: none.
- Go module consumed: `github.com/spark-harness/idl-go-repo v0.2.6`。
- RPC: `QuoteService.CreateQuote`。
- Compatibility risk: no IDL change；runtime risk is Consul `grpc_port` metadata and NetworkPolicy reachability.

## Data / Config / Permission / Observability

- Data and storage: none.
- Removed config: `QUOTE_HTTP_BASE_URL`, `QUOTE_HTTP_TIMEOUT`, `quote.http.*`。
- Added config: `QUOTE_GRPC_TIMEOUT`, `QUOTE_GRPC_PLAINTEXT`。
- Permission: BFF namespace must be allowed to call quote-api TCP 9090.
- Observability: gRPC client span uses `rpc.system=grpc` and `vesta.lendora.quote.v1.QuoteService/CreateQuote` semantics.

## Error Codes

| quote gRPC result | BFF error code | HTTP response to frontend | Retryable |
|---|---|---|---:|
| `INVALID_ARGUMENT` / `QUOTE-PARAM-0002` | `amount_out_of_range` | 422 | No |
| `INVALID_ARGUMENT` / `QUOTE-PARAM-0001` | `validation_error` | 422 | No |
| `UNAVAILABLE` / `DEADLINE_EXCEEDED` / unknown | `quote_unavailable` | 502 | Yes |

## Rollout And Rollback

- Rollout: after `quote-api` gRPC server and `idl-go-repo v0.2.6` are available.
- Rollback: revert BFF image and GitOps config together.
- No partial fallback: do not reintroduce `QUOTE_HTTP_BASE_URL`.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Consul metadata lacks `grpc_port` | BFF may dial HTTP port | resolver test proves `grpc_port` preference; live Consul evidence is collected before closeout |
| old HTTP config remains | hard-cut violated | code/GitOps search evidence |
| trace backend unavailable | live AC delayed | record local gRPC span evidence and live blocker |
