---
id: "LEN-206"
title: "[OBS] 硬切 gRPC tracing 到官方中间件并统一 Principal metadata"
status: "draft"
related_branch: "feature/LEN-206-observability-grpc-tracing-principal"
target_branch: "master"
release_branch: "master"
affected_repositories:
  - harness-repo
  - business-repo
---

# gRPC tracing 与 Principal metadata 硬切

## 背景

当前贷款申请链路必须在 Sentry trace 中形成完整 parent/child 拓扑：

```text
fides http.client -> fides-bff http.server -> fides-bff rpc -> origination-api CreateLoanApplication -> origination-api rpc -> quote-api GetQuote
```

它不是什么：不是继续维护各服务自写 `traceparent` / `tracestate` 拼接逻辑，也不是在业务 command 或 gateway 中夹带 tracing 细节。

它是什么：把 HTTP/gRPC span 创建、context 提取和注入硬切到官方中间件或 instrumentation；Principal metadata 作为独立组件传播。

## 目标

- R1：`fides-bff` HTTP server span 使用官方 OpenTelemetry HTTP instrumentation，并通过 Kratos v3 transport filter 接入。
- R2：`fides-bff` 出站 gRPC client span 使用官方 OpenTelemetry gRPC instrumentation。
- R3：Java gRPC server span 使用官方 OpenTelemetry gRPC instrumentation。
- R4：`origination-api -> quote-api` gRPC client span 使用官方 OpenTelemetry gRPC instrumentation。
- R5：`x-applicant-id` Principal metadata 通过独立组件传递，不与 tracing 注入耦合。
- R6：本地验证覆盖 BFF gRPC metadata、Java quote gateway metadata 和 trace context 传递。

## 非目标

- 不修改 protobuf IDL。
- 不修改 `fides-web` 浏览器 tracing。
- 不改变现有 HTTP API、gRPC API、错误码和业务响应 shape。
- 不新增 HTTP fallback 或旧 trace header fallback。

## 场景

### Scenario 1: BFF 收到前端请求

Given：`fides` 发起受保护 HTTP 请求并携带 W3C trace context。

When：`fides-bff` 处理该请求。

Then：HTTP server span 由官方 OpenTelemetry HTTP instrumentation 创建，BFF access/correlation filter 只保留 `x-trace-id`、`x-correlation-id` 和日志指标。

### Scenario 2: BFF 调用 origination-api

Given：BFF 已从 token 得到 applicant principal。

When：BFF 通过 gRPC 调用 `origination-api CreateLoanApplication`。

Then：trace context 由 `otelgrpc` 注入，`x-applicant-id` 由 BFF metadata helper 注入。

### Scenario 3: origination-api 调用 quote-api

Given：`origination-api` gRPC server 从 metadata 恢复 Principal。

When：业务用例调用 `quote-api GetQuote`。

Then：client span 与下游 `quote-api` server span 由官方 OpenTelemetry gRPC instrumentation 串联；Principal metadata 由 `RequestPrincipalGrpcClientInterceptor` 注入。

## 业务规则

- BR1：禁止在业务 gateway 中手写 `traceparent` / `tracestate` 注入。
- BR2：禁止在 BFF data client 中手写 gRPC CLIENT span。
- BR3：Java gRPC server tracing 不再使用自研 server interceptor。
- BR4：Principal metadata key 统一为 `x-applicant-id`。
- BR5：无 Principal 时不得伪造 applicant metadata。

## 验收标准

- AC1：`fides-bff` 使用官方 OpenTelemetry HTTP instrumentation 处理 HTTP server tracing，并通过 Kratos v3 transport filter 接入。
- AC2：`fides-bff` gRPC client 使用 `otelgrpc.NewClientHandler()`。
- AC3：Java starter gRPC server tracing 使用 `GrpcTelemetry.createServerInterceptor()`。
- AC4：`origination-api -> quote-api` 使用 `GrpcTelemetry.createClientInterceptor()`。
- AC5：`RequestPrincipalGrpcClientInterceptor` 覆盖 Java 出站 Principal metadata。
- AC6：本地测试记录 Go 通过结果；Java 若因外部依赖无法解析，必须记录具体状态码和 artifact。

## Open Questions

- Java CI 环境是否能访问 Maven Central 的 `io.opentelemetry.instrumentation:opentelemetry-grpc-1.6:2.26.0-alpha`。
- LEN-210 的 Sentry trace 拓扑验证需要部署后用真实 trace id 补证据。
