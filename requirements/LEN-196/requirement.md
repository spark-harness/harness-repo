---
requirement_id: "LEN-196"
owner: "forest"
status: "approved"
created_at: "2026-07-05"
related_branch: "feature/LEN-196-dev-sta-grpc-http-cleanup"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
  - gitops-repo
approved_by: "forest"
approved_at: "2026-07-05T09:08:32+08:00"
decision: "用户本轮明确授权处理 LEN-196 的任何事项；批准 requirement 与 impact-analysis，范围限定为 dev-1/sta-1 验证和内部业务 HTTP 包袱清理。"
---

# dev-1 / sta-1 整体切换并清理内部 HTTP 包袱

## Background

`LEN-176`、`LEN-180`、`LEN-184`、`LEN-188`、`LEN-192` 已把 quote、origination、BFF 到后端服务的主要内部业务调用切到 gRPC。当前剩余工作不是再加一条业务能力，而是验证整体运行效果，并删除最后的旧业务 HTTP 暴露面和 bootstrap 入口。

它不是什么：本需求不是删除 `fides-web -> fides-bff` 的外部 HTTP，不是删除 Java health/readiness HTTP，也不是删除 `lendora-shared-consul`。

它是什么：本需求只处理内部服务间业务 HTTP 包袱，包括 quote/origination 的业务 HTTP controller、服务 client namespace 的 HTTP ingress、旧 Consul KV bootstrap Job，以及 dev-1 先行、sta-1 后续的整体 smoke 和 trace 证据。

## Goals

- R1：dev-1 必须先完成报价、申请、身份资料、步骤推进的整体 smoke。
- R2：sta-1 只能在 dev-1 通过后验证同一业务流程。
- R3：内部服务间业务调用只允许 gRPC，不再允许服务间业务 HTTP。
- R4：删除 quote-api 和 origination-api 的业务 HTTP controller、业务 HTTP exception handler 和对应测试。
- R5：GitOps 不再允许业务 client namespace 访问 quote-api、origination-api、applicant-api 的 HTTP 业务端口。
- R6：删除 quote-api、origination-api、applicant-api 和 fides-bff 的旧 Consul KV bootstrap Job。
- R7：保留 Java health/readiness HTTP、BFF 外部 HTTP、Consul 服务发现和 `lendora-shared-consul`。
- R8：保留 trace/observability 的 OTLP HTTP exporter 配置；它不是内部业务 HTTP。

## Non-Goals

- 不修改 protobuf IDL、Buf 配置或生成契约。
- 不删除 `lendora-shared-consul`。
- 不删除 `fides-bff` 对外 HTTP API 或 `fides-web` 访问路径。
- 不删除 Java 服务的 `/health`、`/ready` 或 Kubernetes/Consul health check 所需 HTTP。
- 不删除服务注册到 Consul 所需的 HTTP API 调用。
- 不删除 OTLP `http/protobuf` exporter。
- 不改变贷款申请、报价、身份资料、OTP、数据库 schema 或业务状态机。

## User / Business Scenarios

### Scenario 1：dev-1 先行验证

Given：dev-1 已部署 quote-api、origination-api、applicant-api、fides-bff 和 fides-web。

When：执行 OTP、报价、创建申请、查询申请、更新申请、身份资料保存、步骤推进 smoke。

Then：业务请求成功，并且内部服务间链路只依赖 gRPC。

### Scenario 2：sta-1 后续验证

Given：dev-1 整体 smoke 已通过。

When：sta-1 部署同一清理结果并执行相同业务 smoke。

Then：sta-1 业务请求成功，并且内部服务间链路只依赖 gRPC。

### Scenario 3：内部业务 HTTP 清理

Given：前置 Story 已把调用方切到 gRPC。

When：搜索业务仓、GitOps 渲染结果和 live config。

Then：不存在 quote/origination 业务 HTTP controller、内部业务 HTTP base URL、业务 HTTP fallback、旧 Consul KV bootstrap 或 client namespace 的业务 HTTP ingress。

### Scenario 4：允许的 HTTP 边界

Given：Java 服务仍需要 health/readiness，BFF 仍向前端提供 HTTP API，Consul/OTLP 自身使用 HTTP。

When：执行扫描。

Then：这些非业务服务间 HTTP 被明确列为允许项，不作为遗留包袱删除。

## Business Rules

- BR1：dev-1 必须先于 sta-1 通过。
- BR2：删除旧 HTTP 配置和 bootstrap 必须在 LEN-176/LEN-180/LEN-184/LEN-188/LEN-192 全部完成后执行。
- BR3：内部业务 HTTP controller/client/config/fallback 不允许保留。
- BR4：Java health/readiness HTTP 可以保留。
- BR5：BFF 外部 HTTP 可以保留。
- BR6：`lendora-shared-consul` 必须保留。
- BR7：Consul API HTTP、OTLP HTTP exporter 和 Kubernetes health check HTTP 不属于业务服务间 HTTP。

## Acceptance Criteria

| AC | Given | When | Then |
|---|---|---|---|
| AC1 | dev-1 已部署全部相关服务 | 执行报价、申请、身份资料、步骤推进 smoke | 业务成功且内部调用全为 gRPC |
| AC2 | dev-1 已通过 | 切换 sta-1 并执行相同 smoke | sta-1 业务 smoke 通过 |
| AC3 | 完成环境切换 | 搜索业务仓和 GitOps 渲染结果 | 不存在内部业务 HTTP base URL、业务 HTTP fallback 或 quote/origination/applicant/BFF 旧 Consul KV bootstrap |
| AC4 | 查看 trace 或等效运行证据 | 筛选核心业务流程 | trace 连续且内部服务间只有 gRPC span |
| AC5 | 检查 GitOps NetworkPolicy | 渲染 dev-1 / sta-1 | 业务 client namespace 只能访问 gRPC；Consul health/readiness HTTP 例外保留 |
| AC6 | 检查 business-repo | 搜索 quote/origination HTTP adapter | 仅保留 health/readiness HTTP adapter |

## Open Questions

- 当前无阻塞型开放问题。若 trace 后端不可用，允许用 live config、smoke、服务日志和仓库扫描组合证明内部业务 HTTP 已清理，并在 evidence 中说明缺口。

## Notes

- 本需求完成后才进入旧 HTTP 包袱的最终清理状态。
- 清理中不得扩大到 `LEN-196` 之外的业务重构。
