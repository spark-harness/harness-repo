---
requirement_id: "LEN-156"
owner: "forest"
status: "approved"
created_at: "2026-07-02"
related_branch: "feature/LEN-156-fides-web-api-proxy-tracing"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
approved_by: "forest"
approved_at: "2026-07-02T17:36:50Z"
decision: "用户授权 Agent 批准所有需要的文件；批准 LEN-156 requirement。"
---

# [FE] fides-web 增加 /api/v1 应用内代理与 fetch 自动追踪

## Background

LEN-155 已让 fides-web gateway 消费 generated TS SDK，并移除 gateway-local trace header。当前还缺同源 `/api/v1` 应用内代理和统一 fetch 自动追踪。

它不是什么：本需求不修改 IDL、不改 BFF runtime、不改 GitOps 内网地址。

它是什么：在 fides-web 内提供同源 `/api/v1/*` 代理到服务端 `FIDES_BFF_BASE_URL`，并用 OpenTelemetry fetch instrumentation 自动追踪浏览器访问 `/api/v1` 的请求。

## Goals

- R1：Next route handler 支持 `GET/POST/PUT/PATCH/DELETE /api/v1/*`。
- R2：代理保留 path、query、method、body 和业务 headers。
- R3：`FIDES_BFF_BASE_URL` 仅在服务端作为代理目标使用，不暴露给浏览器 runtime config。
- R4：浏览器 runtime `bffBaseUrl` 固定为 `/api/v1`。
- R5：OpenTelemetry fetch instrumentation 只对同源 `/api/v1` 传播 trace header。
- R6：Sentry / OTLP exporter 请求不被配置为业务 trace header 传播目标。

## Non-Goals

- 不修改 protobuf 或 generated SDK。
- 不修改 fides-bff Go 代码。
- 不修改 dev / sta GitOps 配置；LEN-157 负责。
- 不新增页面行为。

## Scenarios

### Scenario 1：浏览器同源调用 BFF

Given：浏览器 runtime config 返回 `/api/v1`。

When：gateway 发起 `/api/v1/loan-applications` 请求。

Then：Next route handler 将请求代理到服务端 `FIDES_BFF_BASE_URL` 指向的 BFF。

### Scenario 2：fetch 自动追踪

Given：浏览器 tracing 初始化。

When：浏览器 fetch `/api/v1/*`。

Then：fetch instrumentation 创建 client span 并传播 W3C trace context。

## Business Rules

- BR1：内网 BFF 地址不得进入 public runtime config。
- BR2：代理不得转发 hop-by-hop headers。
- BR3：代理必须保留 Authorization、Idempotency-Key、trace headers、method、query 和 body。
- BR4：fetch instrumentation 的 `propagateTraceHeaderCorsUrls` 只允许匹配同源 `/api/v1`。

## Acceptance Criteria

- AC1：`/api/v1/[...path]` route handler 存在并支持目标方法。
- AC2：代理单测覆盖 path、query、headers、method 和 body 转发。
- AC3：runtime config 单测证明 public `bffBaseUrl` 为 `/api/v1`，服务端 BFF 地址不暴露。
- AC4：browser tracing 单测证明注册 `FetchInstrumentation`，传播范围为 `/^\\/api\\/v1(?:\\/|$)/`。
- AC5：`pnpm test`、`pnpm lint`、`pnpm lint:deps`、`pnpm build` 通过。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 代理目标是否由 GitOps 注入 `FIDES_BFF_BASE_URL` | forest | LEN-157 | Open：LEN-157 负责 dev/sta 配置。 |
