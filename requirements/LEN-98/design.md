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
| R1, AC2 | D1: `idl-repo` 使用 `buf.gen.openapi.yaml` 生成 OpenAPI v3 到 `idl-openapi-repo`，目录跟随 proto 路径 |
| R2, AC3, AC4 | D2: `buf.gen.go.yaml` 增加 Kratos HTTP 生成，`fides-bff` 使用 `RegisterFidesBffAuthServiceHTTPServer` |
| R3, AC5, AC8 | D3: `idl-ts-repo` 使用 OpenAPI Generator 固定镜像从 `idl-openapi-repo` 生成 TS SDK，TS 仓不包含手写 SDK wrapper |
| R4, R5, AC6, AC7 | D4: `fides` infrastructure adapter 包装 generated TS client，application-facing port 不变 |
| R6 | D5: OpenAPI stale check 和 TS build/test 作为 CI 候选命令 |

## Summary

方案把 `auth.proto` 作为 FE-facing HTTP 契约入口。IDL 仓生成 OpenAPI v3 和 Kratos HTTP registration；BFF service 实现 generated interface；FE 只在 infrastructure 层包装 generated TS client。

## API / Contract Design

- Source proto：`idl-repo/vesta/lendora/fides-bff/v1/auth.proto`
- OpenAPI output：`idl-openapi-repo/vesta/lendora/fides-bff/v1/openapi.yaml`
- Go HTTP generated file：`auth_http.pb.go`
- TS package：`@spark-harness/idl-ts-client`

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

`RestOtpAuthGateway` 继续实现 application 层 `OtpAuthGateway` port。它内部构造 OpenAPI Generator 生成的 `FidesBffAuthServiceApi`，并负责：

- 注入 `Idempotency-Key`。
- 注入 W3C trace headers 和 `X-Trace-Id`。
- 将 generated client error 映射回 application 层 `BffOtpError`。
- 保留裸 401、429、timeout 兼容语义。

## Testing Strategy

- IDL：`buf lint`、Go generate、Java generate、OpenAPI generate、OpenAPI stale check。
- OpenAPI：`idl-openapi-repo` 必须先完成同名分支 push。
- TS client：从 `idl-openapi-repo` clone 同名分支后，使用 `openapitools/openapi-generator-cli:v7.14.0` 生成，再执行 `pnpm build`。
- BFF：`go test ./...`。
- TS client：`pnpm build`。
- FE：`pnpm test`、`pnpm lint:deps`、`pnpm build`。

## Rollout / Rollback

合并前依赖处理：

- `spark-harness/idl-openapi-repo` 已创建私有远端并保存生成 OpenAPI。
- `spark-harness/idl-ts-repo` 已创建私有远端并推送 tag `v0.1.0-len98.4`。
- `idl-go-repo` 已推送包含 Kratos HTTP generated file 的 tag `v0.2.2-len98.1`。
- CI / 本地验证私有 Go module 时必须设置 `GOPRIVATE=github.com/spark-harness/*`。

Rollback 通过回退 `fides` client tag 和 `fides-bff` 服务版本完成，因为 HTTP 路径和 JSON 字段保持兼容。

## Risks

- 当前不再依赖本地 file dependency 或 local Go replace。
- CI 必须能访问 Buf remote plugins、Kratos HTTP Go module 和固定 OpenAPI Generator 镜像，否则 OpenAPI / TS SDK / Go HTTP stale check 会失败。
