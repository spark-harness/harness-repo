---
requirement_id: "LEN-154"
owner: "forest"
status: "approved"
created_at: "2026-07-02"
related_branch: "feature/LEN-154-fides-bff-generated-binding"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
  - idl-repo
approved_by: "forest"
approved_at: "2026-07-02T16:13:19Z"
decision: "用户授权 Agent 批准所有需要的文件；批准 LEN-154 requirement 和 impact-analysis，范围限定为 fides-bff 消费 LEN-153 已合并生成契约并切换 generated HTTP binding，不修改 proto、前端代理或 GitOps 配置。"
---

# [BFF] fides-bff 全面切换到生成 HTTP binding

## Background

`LEN-153` 已补齐 fides-bff auth、identity-profile、pricing、loan-application 的生成契约和 SDK 输出。当前 `fides-bff` 仍对 identity-profile、pricing、loan-application 使用手工 Kratos route 和 `khttp.Context` handler。

它不是什么：本需求不是新增业务规则，不改变 FE 页面行为，也不修改下游 applicant-api、quote-api、origination-api 的契约。

它是什么：让 `fides-bff` 的已入 IDL 业务路由统一由生成 HTTP binding 注册，service 实现生成接口，并继续保留现有鉴权、幂等、trace context 和错误映射行为。

## Goals

- R1：`fides-bff` 注册生成的 auth、identity-profile、pricing、loan-application HTTP server。
- R2：停止使用已入 IDL 业务路由的手工 Kratos route 注册。
- R3：service 方法签名切换为 generated interface 的 `context.Context` + proto request / response。
- R4：继续从请求上下文提取 principal、`Idempotency-Key`、`traceparent`、`tracestate` 并传递给下游。
- R5：保留 `/api/v1/health` 和 `/api/v1/protected/session:probe` 运行时路由。
- R6：单测覆盖 generated HTTP binding 下的 auth、identity-profile、pricing、loan-application。

## Non-Goals

- 不修改 protobuf IDL；LEN-153 已完成。
- 不修改 fides-web TS SDK 消费；LEN-155 负责。
- 不新增 `/api/v1` 应用内代理或 fetch 自动追踪；LEN-156 负责。
- 不修改 dev / sta GitOps 配置；LEN-157 负责。
- 不改变下游服务业务规则、数据库或部署配置。

## User / Business Scenarios

### Scenario 1：生成路由处理报价请求

Given：用户已登录并进入贷款请求步骤。

When：前端调用 `POST /api/v1/pricing/quotes`。

Then：请求由 generated pricing HTTP binding 进入 BFF service，并继续调用 quote-api 下游。

### Scenario 2：生成路由处理申请草稿

Given：用户已获得 quote 并保存草稿。

When：前端调用 create、get 或 patch loan application。

Then：请求由 generated loan-application HTTP binding 进入 BFF service，并继续调用 origination-api 下游。

### Scenario 3：生成路由处理身份资料

Given：用户进入身份资料步骤。

When：前端读取或保存 identity profile。

Then：请求由 generated identity-profile HTTP binding 进入 BFF service，并继续调用 applicant-api / origination-api 下游。

### Scenario 4：运行时探针保留

Given：部署系统或前端 session 检查仍调用健康和 session probe。

When：访问 `/api/v1/health` 或 `/api/v1/protected/session:probe`。

Then：路由保持现有行为，不强行纳入 IDL。

## Business Rules

- BR1：已进入 IDL 的业务路由不得再使用手工 route 注册作为主入口。
- BR2：`/api/v1/health` 和 session probe 可以保留手工路由。
- BR3：principal 只能来自 BFF 鉴权上下文，不接受请求体 applicantId。
- BR4：写操作的 `Idempotency-Key` 继续从 header 读取并传给下游。
- BR5：trace context 继续从请求 header 读取并传给下游。
- BR6：错误码、HTTP status 和响应 envelope 不因路由切换发生用户可见回退。

## Acceptance Criteria

- AC1：`fides-bff` 注册 generated auth、identity-profile、pricing、loan-application HTTP server。
- AC2：pricing、loan-application、identity-profile 不再通过手工 Kratos route 注册。
- AC3：service 层实现 generated HTTP server interface。
- AC4：单测覆盖四类 generated binding 路径的成功、鉴权、trace/idempotency 或错误映射关键行为。
- AC5：`make test`、`go vet ./...`、`make build` 通过。
- AC6：父 Story AC1-AC4、AC6 的 BFF 行为有验证证据。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| LEN-154 是否需要发布新的 idl-go formal tag | forest | 实现前 | Resolved：已发布 `idl-repo v0.2.5` -> `34c4f17456d5032bf4aecc765b641094d7ab0b5e`，`idl-go-repo v0.2.5` -> `e519b232cbaa043b38a7138e926f8641be6b7a11`。 |

## Notes

- 用户已授权 Agent 批准所有需要的文件；本需求按授权推进生命周期文件和门禁。
- `LEN-154` 只能在 `LEN-153` 已合并并清理 worktree 后开始；该条件已满足。
