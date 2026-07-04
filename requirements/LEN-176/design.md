---
requirement_id: "LEN-176"
owner: "forest"
status: "approved"
updated_at: "2026-07-05"
approved_by: "forest"
approved_at: "2026-07-05T00:35:00+08:00"
decision: "用户在 /goal 中授权处理下列任务中的任何事项，包括批准文件；批准 LEN-176 design。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, AC1 | D1：新增 `vesta.lendora.quote.v1.QuoteService`，包含 `CreateQuote` 和 `GetQuote`。 | Additive proto。 |
| R2, AC2 | D2：用 Buf 生成 Java/Go contract，不手写生成物。 | Java 供 quote-api 服务端编译。 |
| R3, AC3 | D3：新增 `QuoteGrpcAdapter implements BindableService`，调用现有 use case。 | 业务规则不进 adapter。 |
| R4, AC4 | D4：保留 `QuoteHttpAdapter` 和 `QuoteHttpExceptionHandler` 到 `LEN-196`。 | 防止调用方未切换时断链。 |
| R5, AC5, AC6 | D5：GitOps 暴露 9090，Consul 注册加入 `grpc_port`。 | Service/Deployment/NetworkPolicy 一起改。 |
| R6, AC7 | D6：保留 `HealthHttpAdapter`。 | readiness/liveness 不变。 |

## Summary

方案采用 contract-first：先新增 quote protobuf，再生成 Java contract，quote-api 通过公共 spring starter 自动启动 gRPC server。服务端业务逻辑继续复用 `CreateQuoteUseCase` 和 `GetQuoteUseCase`。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| quote-api | 新增 gRPC adapter，保留业务 HTTP adapter 到最终清理阶段 | 先提供服务端能力，再让调用方硬切 |
| quote-api GitOps | 暴露 9090 和 Consul `grpc_port` | 调用方通过服务发现连接 gRPC |
| service matrix | quote-api 标记 `idl_required: true` | 后续 gate 能识别 proto path |

## API / Contract Design

- Protobuf IDL required: yes.
- Proto files: `idl-repo/vesta/lendora/quote/v1/quote.proto`.
- Buf module: `local/lendora-quote`.
- Buf config version: v2.
- Generated outputs: `idl-java-repo/src/main/java`, `idl-java-repo/src/main/grpc-java`, `.generated/idl-go`.
- Breaking check baseline: `.git#branch=master`.
- Compatibility strategy: additive new service；HTTP 业务入口删除由 `LEN-196` 在调用方硬切完成后统一执行。

## Error Code Design

| Error Code | HTTP / gRPC Mapping | Meaning | Retryable | User Visible | Owner | Status |
|---|---|---|---:|---:|---|---|
| `QUOTE-PARAM-0001` | `INVALID_ARGUMENT` | quote 请求字段缺失或格式非法 | No | Yes | pricing | Active |
| `QUOTE-PARAM-0002` | `INVALID_ARGUMENT` | quote 金额超出报价范围 | No | Yes | pricing | Active |
| `QUOTE-AUTH-0001` | `UNAUTHENTICATED` | quote 请求缺少有效申请人身份 | No | Yes | pricing | Active |
| `QUOTE-PERMISSION-0001` | `PERMISSION_DENIED` | 申请人无权读取该报价 | No | Yes | pricing | Active |
| `QUOTE-STATE-0001` | `NOT_FOUND` | 报价不存在 | No | Yes | pricing | Active |
| `QUOTE-STATE-0002` | `FAILED_PRECONDITION` | 报价已过期 | No | Yes | pricing | Active |
| `QUOTE-SYSTEM-0001` | `UNKNOWN` | quote-api 未分类系统错误 | Yes | No | pricing | Active |

## Data / Config / Permission

- Data model: no schema change.
- Config:
  - `SPARK_GRPC_SERVER_PORT=9090`
  - `SPARK_QUOTE_CONSUL_GRPC_PORT=9090`
- Permission: quote-api NetworkPolicy 允许同环境命名空间访问 9090，Consul 继续访问 HTTP readiness。

## Observability

- Logs: 不新增敏感字段。
- Metrics: 沿用现有 Spring/gRPC starter 行为。
- Tracing: `CreateQuoteRequest.trace_id` 保留调用方 trace 传递点。
- Events: none.

## Rollout And Rollback

- Gray release: IDL/SDK 先合并发布，quote-api 代码随后合并，GitOps 最后更新端口和镜像。
- Kill switch: 回滚 quote-api 镜像或 GitOps overlay。
- Rollback: 因调用方尚未在本 Story 切换且业务 HTTP 保留，回滚 quote-api 不需要调用方同步回滚。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Java contract 版本未发布 | business PR 合并前切换到 SDK CI 发布的正式版本 | forest |
| gRPC adapter 错误码映射不完整 | adapter 测试覆盖成功、非法金额、读取报价 | forest |
| NetworkPolicy 漏 9090 | dev-1/sta-1 kustomize 渲染检查端口 | forest |
