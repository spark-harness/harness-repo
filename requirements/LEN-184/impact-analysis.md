---
requirement_id: "LEN-184"
analyst: "forest"
status: "approved"
updated_at: "2026-07-05"
idl_impact: "no"
idl_impact_reason: "quote-api gRPC 服务端和 Java SDK 0.2.7 已由 LEN-176 完成；本需求只消费既有 QuoteService.GetQuote。"
approved_by: "forest"
approved_at: "2026-07-05T04:02:47+08:00"
decision: "用户本轮明确授权处理 LEN-184 的任何事项，包括批准 impact-analysis 进入服务仓库检查。"
---

# Impact Analysis

## Summary

本需求把 `origination-api` 对 `quote-api` 的报价读取从内部 HTTP 改为 gRPC。影响集中在 `origination-api` 出站 adapter、应用配置、GitOps 配置清理、NetworkPolicy 和 trace 验证。

## Affected Domains

- 申请人域：创建和更新贷款申请时的报价读取协议变化。
- 报价与试算：`quote-api` 作为既有 gRPC 下游被消费，不改变服务端能力。
- GitOps：移除 `origination-api` quote HTTP base URL/timeout，保留 gRPC 端口与 NetworkPolicy。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| origination-api | `{business-repo}/apps/origination-api` | 替换 quote 出站 adapter 和配置装配 | Yes, consume only |
| quote-api | `{business-repo}/apps/quote-api` | 作为既有 gRPC server 被调用，本需求不修改 | Yes, no change |
| origination-api GitOps | `{gitops-repo}/apps/origination-api` | 删除 quote HTTP config，确认 9090 NetworkPolicy | No |
| quote-api GitOps | `{gitops-repo}/apps/quote-api` | 确认 9090 端口可达，本需求不要求删除 HTTP | No |

## Upstream / Downstream

- Upstream: `fides-bff` 仍通过 `origination-api` 既有入口访问申请能力，本需求不修改。
- Downstream: `origination-api -> quote-api` 从 HTTP 改为 gRPC。

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: no.
- Consumed Java artifact: `com.spark.contract:spark-idl-java:0.2.7`。
- Consumed service: `com.vesta.lendora.quote.v1.QuoteService`。
- Consumed RPC: `GetQuote(GetQuoteRequest) returns (GetQuoteResponse)`。
- Proto source: `idl-repo/vesta/lendora/quote/v1/quote.proto`。
- Buf change: none.
- Generated contract change: none.
- Compatibility risk: no IDL change；runtime risk is client/server deployment ordering and NetworkPolicy reachability.

## Data Impact

- Database schema: none.
- Data migration: none.
- Backfill: none.
- Cache: none.
- Runtime storage: existing origination repositories remain.

## Config / Permission / Observability Impact

- Config removed:
  - `ORIGINATION_QUOTE_API_BASE_URL`
  - `ORIGINATION_QUOTE_API_TIMEOUT`
  - `spark.origination.quote-api-base-url`
  - `spark.origination.quote-api-timeout`
- Config added or retained:
  - quote gRPC target config for `GrpcQuoteGateway`
  - `SPARK_GRPC_SERVER_PORT=9090`
  - `SPARK_ORIGINATION_CONSUL_GRPC_PORT=9090`
- Permission: `origination-api` must be allowed to call `quote-api` on TCP 9090.
- Logs: no sensitive quote payload logging.
- Metrics: use existing OpenTelemetry/gRPC instrumentation where available.
- Tracing: must show gRPC client/server spans and no business HTTP span for quote read.
- Events: none.

## Error Codes

| Downstream Status | Origination Exception | Origination gRPC Mapping | Meaning | Retryable |
|---|---|---|---|---:|
| `NOT_FOUND` / `QUOTE-STATE-0001` | `QuoteNotFoundException` | `ORIGINATION-QUOTE-0001` | 引用报价不存在 | No |
| `FAILED_PRECONDITION` / `QUOTE-STATE-0002` | `QuoteExpiredException` | `ORIGINATION-QUOTE-0002` | 引用报价已过期或不可用 | No |
| `PERMISSION_DENIED` / `QUOTE-PERMISSION-0001` | `ForbiddenException` | `ORIGINATION-PERMISSION-0001` | 申请人无权访问该报价 | No |
| `UNAVAILABLE` / `UNKNOWN` / network error | `QuoteUnavailableException` | `ORIGINATION-QUOTE-0003` | quote 依赖不可用 | Yes |

## Rollout And Rollback

- Rollout: 确认 `quote-api` gRPC server 和 Java artifact `0.2.7` 已可用，再合并 `origination-api` 与 GitOps。
- Kill switch: 回滚 `origination-api` 镜像和 GitOps 配置到上一版本。
- Rollback: 因本需求删除 HTTP fallback，回滚必须恢复旧镜像和旧配置；不能只回滚部分 NetworkPolicy。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| quote-api gRPC 端口或 Consul metadata 不可达 | 创建/更新贷款申请失败 | GitOps 渲染和 live trace/连通性验证一起检查 9090 | forest |
| 旧 HTTP base URL 未完全删除 | 仍可能走 HTTP fallback，违背硬切 | 代码、配置、GitOps 全仓搜索并纳入门禁证据 | forest |
| trace backend 不可用 | AC7 无法 live 证明 | 保留本地配置/代码证据，并记录 live trace 阻塞根因 | forest |
