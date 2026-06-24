---
requirement_id: "LEN-98"
owner: "Codex"
status: "approved"
created_at: "2026-06-24"
related_branch: "feature/LEN-98-fides-bff-openapi-ts-client"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - idl-repo
  - idl-openapi-repo
  - gitops-repo
  - business-repo
  - idl-ts-repo
approved_by: "Forest"
approved_at: "2026-06-24T10:24:33+08:00"
decision: "批准 LEN-98 requirement 与 impact-analysis，允许进入设计和实现阶段。"
---

# [FE+BFF] fides-bff OpenAPI v3 与 TS client 生成仓

## Background

父 Story `LEN-2` 要求手机验证链路覆盖发码、冷却、验码、错误映射、过期、锁定、`+852` 限制和登录态刷新。`LEN-43` 已将 `fides`、`fides-bff` 和 `applicant-api` 串成真实 FE+BFF 调用链，并在 `idl-repo/vesta/lendora/fides-bff/v1/auth.proto` 中定义了带 `google.api.http` 的 BFF-facing proto。

本需求不是重新定义 OTP 业务规则，也不是新增真实短信渠道。它要解决的是契约生成链路：BFF 的 FE-facing API 必须从 IDL 生成 OpenAPI v3，再生成 TypeScript HTTP client，`fides` 只能在 adapter / infrastructure 层消费该 client。

## Goals

- R1：`idl-repo` 能从 `vesta/lendora/fides-bff/v1/*.proto` 生成 OpenAPI v3 YAML，并同步到独立 `idl-openapi-repo` 中跟随 proto 路径的目录。
- R2：`idl-repo` 能生成 fides-bff Kratos HTTP registration 所需 Go 代码，BFF 不以手写 auth route 作为主契约入口。
- R3：建立 `spark-harness/idl-ts-repo` 的本地仓结构和 `@spark-harness/idl-ts-client` 包，源契约来自已推送的 `idl-openapi-repo`。
- R4：`fides` 在基础设施 adapter 层消费 generated TS client；presentation、domain、application、adapters 层不得直接依赖生成物。
- R5：保留统一错误信封、`Idempotency-Key`、trace header、冷却/锁定倒计时和裸 HTTP 错误兼容映射。
- R6：生成链路和 stale check 可由 CI 执行，禁止手改 OpenAPI 或 client 后绕过检查。

## Non-Goals

- 不修改 `applicant-api` OTP 业务规则。
- 不新增 `Health` endpoint 到 OpenAPI；`/api/v1/health` 仍是运行时健康检查，不属于 BFF auth 契约。
- 不通过 GitHub Packages/npm registry 发布 TS 包；消费者通过私有 GitHub repo tag 依赖。
- 不把 generated TS client import 到 `fides` presentation 或 application 层。
- 不把本地 `replace github.com/spark-harness/idl-go-repo` 作为 release-bound 最终状态。

## Scenarios

### Scenario 1：IDL 生成 OpenAPI v3

Given：`auth.proto` 中 RPC 带 `google.api.http` 注解。

When：执行 OpenAPI 生成命令。

Then：`idl-openapi-repo/vesta/lendora/fides-bff/v1/openapi.yaml` 包含三条 auth POST 路径，且为 OpenAPI v3。

### Scenario 2：BFF 注册 generated HTTP service

Given：`idl-go-repo` 已包含 fides-bff Kratos HTTP generated registration。

When：`fides-bff` 启动 HTTP server。

Then：auth 路由由 `RegisterFidesBffAuthServiceHTTPServer` 注册，业务 service 只实现 generated interface。

### Scenario 3：FE 消费 TS client

Given：`idl-ts-repo` 已通过 OpenAPI Generator 生成 `@spark-harness/idl-ts-client`。

When：`fides` real BFF adapter 发起发码、验码或刷新请求。

Then：adapter 包装 generated client，并继续输出 application 层定义的结果和错误语义。

## Business Rules

- BR1：OpenAPI 只收录带 `google.api.http` 的业务 RPC；健康检查不纳入 auth OpenAPI。
- BR2：OpenAPI 输出仓固定为 `spark-harness/idl-openapi-repo`，路径固定为 `vesta/lendora/fides-bff/v1/openapi.yaml`。
- BR3：TS client 仓固定为 `spark-harness/idl-ts-repo`，包名固定为 `@spark-harness/idl-ts-client`，同一 npm 包按服务路径导出生成 client。
- BR4：`fides` 只能在 `src/infrastructure/**` 消费 generated client。
- BR5：冷却、锁定、过期、未授权和系统错误映射必须保持 LEN-2 用户体验语义。
- BR6：CI 必须能发现 OpenAPI 或 TS client 漂移。

## Acceptance Criteria

- AC1：`buf lint` 通过。
- AC2：OpenAPI 生成命令能稳定生成 `idl-openapi-repo/vesta/lendora/fides-bff/v1/openapi.yaml`，且 stale check 能发现漂移。
- AC3：Go 生成物包含 `auth_http.pb.go` 和 `RegisterFidesBffAuthServiceHTTPServer`。
- AC4：`fides-bff` 使用 generated HTTP registration，`go test ./...` 通过。
- AC5：`idl-ts-repo` 包含 `@spark-harness/idl-ts-client`，`pnpm build` 通过。
- AC6：`fides` adapter 层消费 generated client，`pnpm test`、`pnpm lint:deps` 和 build 通过。
- AC7：`fides` presentation、domain、application、adapters 层不直接 import generated client。
- AC8：记录远端 `spark-harness/idl-ts-repo` 创建状态和发布前剩余风险。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| `spark-harness/idl-ts-repo` 远端仓创建权限和 token 由谁提供 | Platform | 合并前 | Closed：已创建私有仓并推送 `v0.1.0-len98.4` |
| `fides-bff` release-bound 最终应消费哪个 formal `idl-go-repo` tag | Platform / BFF | 合并前 | Closed：当前验证 tag 为 `v0.2.2-len98.1` |

## Notes

- `spark-harness/idl-ts-repo` 已创建，`fides` 通过 Git tag 依赖消费。
- `fides-bff` 已移除 local replace，并通过 `GOPRIVATE=github.com/spark-harness/*` 验证私有 Go tag。
