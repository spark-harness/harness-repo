---
requirement_id: "LEN-157"
owner: "forest"
status: "approved"
created_at: "2026-07-02"
related_branch: "feature/LEN-157-gitops-bff-tracing"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - gitops-repo
approved_by: "forest"
approved_at: "2026-07-03T02:17:52+08:00"
decision: "用户授权 Agent 批准所有需要的文件；批准 LEN-157 requirement 与 impact-analysis。"
---

# [GitOps] dev/sta 配置内网 BFF 地址并验证跨服务 trace

## Background

LEN-156 已在 fides-web 内提供同源 `/api/v1` 代理，并把 `FIDES_BFF_BASE_URL`
收敛为服务端代理目标。当前 dev-1 和 sta-1 GitOps 仍保留旧公网 BFF URL，
Consul runtime config 也把 public `bffBaseUrl` 指向公网 API 域名。

它不是什么：本需求不修改 protobuf、SDK、前端业务代码或 BFF 业务代码。

它是什么：本需求只把 dev-1 / sta-1 的 GitOps 和 Consul bootstrap 调整到
LEN-156 后的新运行时模型，并验证跨 fides、fides-bff、applicant-api、
quote-api、origination-api 的 trace 连续性。

## Goals

- R1：dev-1 和 sta-1 的 fides-web public runtime config 返回 `bffBaseUrl=/api/v1`。
- R2：dev-1 和 sta-1 的 fides Deployment 注入 server-only `FIDES_BFF_BASE_URL`
  到集群内 fides-bff URL。
- R3：fides-bff 的 OTEL exporter 在 GitOps 与 Consul bootstrap 中保持开启。
- R4：fides-bff 的 Sentry / OTLP endpoint 和 headers 不写入 Git，运行时从
  Consul 私密配置保留。
- R5：applicant-api、quote-api、origination-api 保持或补齐 trace context
  接收与 OTEL bootstrap。
- R6：Argo 同步后配置不回退到旧公网 BFF URL。
- R7：旧公网 BFF 域名仅保留为临时 smoke / debug 入口，不再作为 fides-web
  浏览器 runtime config。

## Non-Goals

- 不提交真实 Sentry DSN、token、header 或其他 secret。
- 不删除 Caddy 旧公网 API 路由；本票只让 fides-web 不再依赖它。
- 不修改业务接口行为。
- 不新增数据库、缓存或消息队列变更。

## User / Business Scenarios

### Scenario 1：浏览器调用同源代理

Given：用户打开 dev-1 或 sta-1 的 fides-web。

When：前端读取 `/api/runtime-config`。

Then：返回的 `bffBaseUrl` 是 `/api/v1`，不会暴露集群内 fides-bff 地址。

### Scenario 2：服务端代理访问内网 BFF

Given：fides-web route handler 收到 `/api/v1/*` 请求。

When：服务端读取 `FIDES_BFF_BASE_URL`。

Then：请求被代理到同 namespace 内 `fides-bff` Service 的 `/api/v1`。

### Scenario 3：跨服务 trace 连续

Given：fides-web、fides-bff 和下游服务都启用 OTEL，并保留私密 exporter header。

When：用户完成一次申请流程操作。

Then：Sentry 中能看到同一 trace 贯穿 fides、fides-bff 和实际触达的下游服务。

## Business Rules

- BR1：public runtime config 不得包含公网 BFF URL 或集群内 BFF URL。
- BR2：`FIDES_BFF_BASE_URL` 只允许在 fides Deployment 服务端环境中出现。
- BR3：真实 Sentry header 只能来自私密运行时配置，不能进入 Git。
- BR4：Consul bootstrap Job 不得覆盖已经存在的 OTEL endpoint / headers。
- BR5：GitOps 是 dev-1 / sta-1 配置真相源；不得依赖手工 `kubectl edit`。

## Acceptance Criteria

- AC1：dev-1 / sta-1 的 fides runtime-config Consul bootstrap 写入
  `bffBaseUrl=/api/v1`。
- AC2：dev-1 / sta-1 的 fides Deployment 渲染结果中，`FIDES_BFF_BASE_URL`
  指向 `http://fides-bff.<namespace>.svc.cluster.local:8000/api/v1`。
- AC3：dev-1 / sta-1 的 fides-bff 渲染结果中，OTEL enabled 为 true，
  endpoint / headers 不包含真实 secret，并保留运行时已有值。
- AC4：applicant-api、quote-api、origination-api 的 GitOps / Consul bootstrap
  保持 OTEL trace context 接收配置。
- AC5：`kubectl kustomize` 渲染 dev-1 / sta-1 相关 overlays 通过。
- AC6：Argo 应用 Synced / Healthy 后，live Deployment 与 Consul KV 不回退旧公网 BFF URL。
- AC7：一次申请流程操作的 trace 可在 Sentry 中串联 fides、fides-bff 和对应下游服务。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 旧公网 BFF 域名是否立即删除 | forest | LEN-157 验收前 | Resolved：本票保留为临时 smoke / debug 入口，不作为 fides runtime config。 |
| 真实 Sentry endpoint / headers 是否可提交 | forest | LEN-157 实施前 | Resolved：不可提交；只保留变量名和运行时保留逻辑。 |

## Notes

- 用户已授权 Agent 批准所有需要的文件。
- 本票必须在 LEN-156 合并并清理 worktree 后开始，当前前置条件已满足。
