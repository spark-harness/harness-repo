# LEN-21 T2-T4 — fides-bff 横切约定证据

## Context

- Requirement: `LEN-21`
- Tasks:
  - `T2`：统一错误信封、校验中间件、gRPC status → REST 映射
  - `T3`：幂等中间件 + `IdempotencyStore`
  - `T4`：结构化访问日志 + traceId/correlationId + gRPC metadata 透传
- Services / packages:
  - `business-repo/packages/bffkit`
  - `business-repo/services/backend/fides-bff`
- Branch: `feature/fides-bff/LEN-21`
- Checked at: `2026-06-17T00:15:16+08:00`

## Implementation Summary

- 新增共享 Go 包 `github.com/spark/bffkit`，作为 BFF 横切能力包。
- `bffkit` 提供：
  - 统一错误信封 `{error:{code,message,field?,traceId,details?}}`
  - `ValidationError` 与字段级 `details[]`
  - gRPC status → HTTP status / 稳定错误码映射
  - Kratos HTTP status → 稳定错误码映射
  - gRPC 下游错误使用受控 public message，不直接暴露 downstream `status.Message()`
  - `Idempotency-Key` 写请求回放中间件：缺 key 返回 422，相同 key 不同请求指纹返回 409，并发相同 key 只执行一次 handler
  - 幂等安全限制：key 长度 / 字符集校验、请求体指纹读取上限、内存 store 记录数上限
  - 内存 `IdempotencyStore`（MVP，可后替 Redis），由 bootstrap 注入到 server
  - `X-Trace-Id` / `X-Correlation-Id` filter
  - OpenTelemetry HTTP server span，错误 span 带稳定 `error_code`
  - RED 基线指标：`http.server.requests`、`http.server.duration`，使用低基数 route 标签
  - 结构化访问日志使用低基数 operation，错误请求带稳定 `error_code`
  - gRPC outgoing metadata 注入工具
- `fides-bff` HTTP server 已装配：
  - `http.ErrorEncoder(bffkit.ErrorEncoder)`
  - `bffkit.TraceFilter(...)`
  - `bffkit.IdempotencyFilter(...)`

## Test-First Record

先补共享包与服务端测试，再实现：

- `packages/bffkit/errors_test.go`
  - `TestErrorFromGRPC_mapsStatusToHTTPAndStableCode`
  - `TestErrorFromGRPC_usesControlledPublicMessages`
  - `TestErrorEncoder_writesEnvelopeWithTraceIDAndValidationDetails`
  - `TestErrorEncoder_mapsKratosStatusToStableCode`
- `packages/bffkit/idempotency_test.go`
  - `TestIdempotencyFilter_replaysFirstWriteResponseForSameKey`
  - `TestIdempotencyFilter_doesNotCacheReadRequests`
  - `TestIdempotencyFilter_rejectsWriteRequestWithoutKey`
  - `TestIdempotencyFilter_rejectsSameKeyWithDifferentRequestFingerprint`
  - `TestIdempotencyFilter_concurrentSameKeyExecutesHandlerOnce`
  - `TestIdempotencyFilter_rejectsInvalidOrLongKey`
  - `TestIdempotencyFilter_rejectsRequestBodyAboveLimit`
  - `TestMemoryIdempotencyStore_capsStoredRecords`
- `packages/bffkit/trace_test.go`
  - `TestTraceFilter_setsContextHeadersAndStructuredLogFields`
  - `TestTraceFilter_logsErrorCodeForFailure`
  - `TestOutgoingGRPCContext_propagatesTraceMetadata`
- `services/backend/fides-bff/internal/server/http_test.go`
  - `TestHTTPServer_ErrorEnvelope_includesTraceID`
  - `TestHTTPServer_KratosError_usesUnifiedEnvelope`
  - `TestHTTPServer_Idempotency_replaysFirstWriteResponse`

红灯记录：新增测试在实现接入前分别因缺少 `bffkit` 实现、服务端未装配 error encoder / filter、module replace 路径不正确而失败；修复后转绿。

## Commands & Results

共享包：

```bash
cd business-repo/packages/bffkit
GOCACHE=/Users/forest/Code/spark/.worktrees/feature-fides-bff-LEN-21/business-repo/.gocache go test ./...    # PASS
GOCACHE=/Users/forest/Code/spark/.worktrees/feature-fides-bff-LEN-21/business-repo/.gocache go vet ./...     # PASS
GOCACHE=/Users/forest/Code/spark/.worktrees/feature-fides-bff-LEN-21/business-repo/.gocache go build ./...   # PASS
GOLANGCI_LINT_CACHE=/Users/forest/Code/spark/.worktrees/feature-fides-bff-LEN-21/business-repo/.golangci-cache golangci-lint run ./...  # 0 issues
```

服务：

```bash
cd business-repo/services/backend/fides-bff
GOCACHE=/Users/forest/Code/spark/.worktrees/feature-fides-bff-LEN-21/business-repo/.gocache go test ./...    # PASS
GOCACHE=/Users/forest/Code/spark/.worktrees/feature-fides-bff-LEN-21/business-repo/.gocache go vet ./...     # PASS
GOCACHE=/Users/forest/Code/spark/.worktrees/feature-fides-bff-LEN-21/business-repo/.gocache go build ./...   # PASS
GOLANGCI_LINT_CACHE=/Users/forest/Code/spark/.worktrees/feature-fides-bff-LEN-21/business-repo/.golangci-cache golangci-lint run ./... # 0 issues
```

实际测试包结果：

```text
ok   github.com/spark/bffkit                         PASS
?    github.com/spark/fides-bff/cmd/fides-bff        [no test files]
ok   github.com/spark/fides-bff/internal/biz         PASS
?    github.com/spark/fides-bff/internal/conf        [no test files]
ok   github.com/spark/fides-bff/internal/server      PASS
?    github.com/spark/fides-bff/internal/service     [no test files]
```

## Acceptance Coverage

| AC | 说明 | 证据 |
|---|---|---|
| AC2 | 错误信封 + 422 details | `bffkit.ValidationError` 与 `ErrorEncoder` 测试断言 `422`、`details[]`、`traceId`；Kratos 401/403/404/409 映射到稳定 `BFF-*` code；gRPC 错误使用受控 public message；`fides-bff` server 测试断言统一信封已装配 |
| AC3 | `Idempotency-Key` 重复写请求回放首次结果 | `bffkit` filter 测试与 `fides-bff` server 测试断言相同 key 只调用一次 handler，第二次响应体与首次一致；并发相同 key 只执行一次；缺 key 返回 422；同 key 不同请求指纹返回 409；非法/超长 key、超限请求体、内存记录数上限均有测试覆盖 |
| AC4 | traceId 在请求链路与 gRPC metadata 中可见 | `TraceFilter` 创建 OTel server span、记录 RED 指标、写入响应头/context/结构化日志字段；日志、metric、span 使用低基数 route/operation，错误请求带稳定 `error_code`；`OutgoingGRPCContext` 测试断言 metadata 中存在 `x-trace-id` / `x-correlation-id` |
| AC6 | gRPC status → REST 映射 | `ErrorFromGRPC` 覆盖 `INVALID_ARGUMENT`、`NOT_FOUND`、`ALREADY_EXISTS`、`ABORTED`、`PERMISSION_DENIED`、`UNAUTHENTICATED`、默认 `500`，且不向前端暴露下游原始错误 message |

## Notes

- T4 当前落地的是无外部 collector 依赖的可运行基线：入口 trace/correlation filter、OTel server span、RED 指标、结构化访问日志字段、gRPC metadata 透传工具。部署环境接入 collector/exporter 后即可导出 span/metric；后续接入真实下游 gRPC 客户端时，应在 client 调用处使用 `bffkit.OutgoingGRPCContext(ctx)`。
- T3 的 `MemoryIdempotencyStore` 是 MVP 实现，符合 design.md 的「共享端口隔离、bootstrap 注入、后替 Redis」决议；当前已限制 key 格式 / 长度、请求体读取和进程内记录数。生产持久化替换可作为后续配置/基础设施任务。
