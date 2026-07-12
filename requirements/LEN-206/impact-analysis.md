# LEN-206 Impact Analysis

## Summary

本需求影响 BFF Go 服务、Java Spring starter、`origination-api` 到 `quote-api` 的 gRPC 出站调用，以及本地验证证据。

## Affected Services And Repos

| 服务或组件 | 仓库 | 影响 |
| --- | --- | --- |
| fides-bff | business-repo | HTTP tracing middleware、gRPC client instrumentation、metadata helper |
| origination-api | business-repo | quote-api gRPC channel instrumentation、Principal client interceptor 使用 |
| quote-api | business-repo | 作为 gRPC server 接收 trace context 和 Principal metadata |
| applicant-api | business-repo | 共享 starter tracing 变更后的 gRPC adapter 测试适配 |
| Java spring starter | business-repo | server tracing auto-configuration、Principal client interceptor |
| Harness requirement | harness-repo | LEN-206 追溯、任务和证据 |

服务矩阵已有 `fides-bff -> origination-api -> quote-api` 依赖，不新增服务。

## Contract Impact

- Protobuf IDL：无变更。
- HTTP contract：无变更。
- gRPC contract：无字段变更；metadata 行为仍使用 `x-applicant-id`，并保留既有 `x-trace-id` response metadata。
- Error code：无新增或变更。

## Data And Storage

- 无数据库 schema、migration、cache 或持久化格式变更。

## Config And Runtime

- `fides-bff` 新增 Go dependency `otelgrpc`，并随其要求升级 Go OTel API/SDK 到 `1.44.0`。
- Java 新增官方 gRPC instrumentation dependency `opentelemetry-grpc-1.6`。
- 无新增 Secret。

## Permission And Security

- Principal metadata 只从已认证的 context 生成，不转发外部伪造 header。
- 不把 token、Cookie、Authorization 或 PII 写入 trace attributes。

## Observability

- HTTP server span：由官方 OpenTelemetry HTTP instrumentation 接管，并通过 Kratos v3 transport filter 接入。
- Go gRPC client span：由 `otelgrpc.NewClientHandler()` 接管。
- Java gRPC server/client span：由官方 `GrpcTelemetry` 接管。
- BFF access/correlation filter 继续输出 `x-trace-id` 和 `x-correlation-id`，但不创建 span。

## Rollout And Rollback

- Rollout：先合并 business-repo，实现和测试通过后部署到验证环境，再执行 LEN-210 Sentry trace 拓扑 smoke。
- Rollback：回滚 business-repo 变更即可恢复旧 tracing 实现；无数据回滚。

## Risks

- Java official gRPC instrumentation artifact 当前本机 Maven Central 访问返回 403，CI 需确认可解析。
- Go OTel 版本升级需关注 exporter 版本兼容；本地 BFF Go 测试已通过。
- 真实 Sentry 拓扑仍需部署后验证，单元测试只能证明 metadata 和 instrumentation 装配。
