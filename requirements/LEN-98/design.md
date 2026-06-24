---
requirement_id: "LEN-98"
owner: "Codex"
status: "approved"
updated_at: "2026-06-24"
approved_by: "Forest"
approved_at: "2026-06-24T10:25:23+08:00"
decision: "批准 LEN-98 design，允许进入任务拆分和实现验证。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision |
|---|---|
| R1, AC2 | D1: `idl-repo` 新增 `buf.gen.openapi.yaml`，使用本地 `protoc-gen-openapi` 直接生成 OpenAPI v3 YAML |
| R2, AC3, AC4 | D2: `buf.gen.go.yaml` 增加本地 `protoc-gen-go-http`，`fides-bff` 使用 `RegisterFidesBffAuthServiceHTTPServer` |
| R3, AC5, AC8 | D3: 新增 `idl-ts-repo` 本地仓结构和 `@spark-harness/fides-bff-client` 包 |
| R4, R5, AC6, AC7 | D4: `fides` infrastructure adapter 包装 generated TS client，application-facing port 不变 |
| R6 | D5: OpenAPI stale check 和 TS build/test 作为 CI 候选命令 |

## Summary

方案把 `auth.proto` 作为 FE-facing HTTP 契约入口。IDL 仓生成 OpenAPI v3 和 Kratos HTTP registration；BFF service 实现 generated interface；FE 只在 infrastructure 层包装 generated TS client。

## API / Contract Design

- Source proto：`idl-repo/vesta/lendora/fides-bff/v1/auth.proto`
- OpenAPI output：`idl-repo/openapi/fides-bff/openapi.yaml`
- Go HTTP generated file：`auth_http.pb.go`
- TS package：`@spark-harness/fides-bff-client`

OpenAPI v3 生成流程：

```text
buf generate --template buf.gen.openapi.yaml --path vesta/lendora/fides-bff/v1/auth.proto
```

Go HTTP 生成流程：

```text
buf generate --template buf.gen.go.yaml --path vesta/lendora/fides-bff/v1/auth.proto
```

## BFF Design

`internal/service.AuthService` 不再接收 Kratos `http.Context`，而是实现 generated interface：

```text
SendOtp(context.Context, *SendOtpRequest) (*SendOtpResponse, error)
VerifyOtp(context.Context, *VerifyOtpRequest) (*VerifyOtpResponse, error)
RefreshToken(context.Context, *RefreshTokenRequest) (*RefreshTokenResponse, error)
```

`internal/server.NewHTTPServer` 保留 health 手写路由，但 auth 路由由 generated registration 注册。`bffkit.TraceFilter` 将原始 HTTP request 放入 context，service 从 context 中读取 `Idempotency-Key`。

## Frontend Design

`RestOtpAuthGateway` 继续实现 application 层 `OtpAuthGateway` port。它内部构造 `FidesBffClient`，并负责：

- 注入 `Idempotency-Key`。
- 注入 W3C trace headers 和 `X-Trace-Id`。
- 将 generated client error 映射回 application 层 `BffOtpError`。
- 保留裸 401、429、timeout 兼容语义。

## Testing Strategy

- IDL：`buf lint`、OpenAPI generate、OpenAPI stale check。
- BFF：`go test ./...`。
- TS client：`pnpm build`。
- FE：`pnpm test`、`pnpm lint:deps`、`pnpm build`。

## Rollout / Rollback

合并前依赖处理：

- `spark-harness/idl-ts-repo` 已创建私有远端并推送 tag `v0.1.0-len98.3`。
- `idl-go-repo` 已推送包含 Kratos HTTP generated file 的 tag `v0.2.2-len98.1`。
- CI / 本地验证私有 Go module 时必须设置 `GOPRIVATE=github.com/spark-harness/*`。

Rollback 通过回退 `fides` client tag 和 `fides-bff` 服务版本完成，因为 HTTP 路径和 JSON 字段保持兼容。

## Risks

- 当前不再依赖本地 file dependency 或 local Go replace。
- CI 必须安装 `protoc-gen-openapi`，否则 OpenAPI stale check 会失败。
