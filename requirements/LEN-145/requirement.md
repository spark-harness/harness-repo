---
requirement_id: "LEN-145"
owner: "core"
status: "approved"
created_at: "2026-07-01"
related_branch: "feature/LEN-145-consul-otel-config"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
  - gitops-repo
approved_by: "forest"
approved_at: "2026-07-01T22:42:00+08:00"
decision: "用户授权批准 LEN-145 需求定义阶段，包括 requirement.md 与 impact-analysis.md。"
---

# quote-api / origination-api 读取 Consul 配置并启用 OpenTelemetry

## Background

`quote-api` 与 `origination-api` 已经在 GitOps 中存在 Consul KV seed Job，也已有 OTLP header 的运行时 Secret surface，但服务本身没有像 `applicant-api` 一样通过 Spring Cloud Consul Config 读取 Consul 配置。

这条需求不是什么：它不是把真实 Sentry DSN、public key 或认证 header 提交进 Git，也不是新增 quote/origination 的业务 API 或业务规则。

它是什么：它补齐两个 Java 服务的标准 OpenTelemetry 和 Consul Config 启动期配置能力，让 dev-1 / sta-1 的私密 OTLP 配置可以保存在 Consul 中，并且服务重启或 Deployment 更新后继续生效。

## Goals

- 让 `quote-api` 启动期能读取 `spark/lendora/{env}/quote-api/config`。
- 让 `origination-api` 启动期能读取 `spark/lendora/{env}/origination-api/config`。
- 让两个服务使用 OpenTelemetry Spring Boot instrumentation 和标准 OTLP exporter 配置。
- 让 dev-1 与 sta-1 trace 带有 `deployment.environment`。
- 让 GitOps Consul seed Job 不清空已存在的私密 OTLP endpoint/header。
- 保证仓库中不保存真实 Sentry DSN、public key 或认证 header。

## Non-Goals

- 不修改 protobuf、generated contracts 或 IDL 发布流程。
- 不新增前端能力。
- 不修改 quote/origination 业务规则、数据库 schema 或外部 API。
- 不引入 Sentry SDK；只使用 OpenTelemetry 标准导出。
- 不建设完整 Secret 管理平台。

## User / Business Scenarios

### Scenario 1: quote-api 从 Consul 读取 OTLP 配置

Given: dev-1 或 sta-1 的 Consul 中存在 `quote-api` 的 OTLP 配置。

When: `quote-api` 启动或重启。

Then: 服务读取 Consul 中的 OTLP endpoint/header，并按 `service.name=quote-api` 导出 trace。

### Scenario 2: origination-api 从 Consul 读取 OTLP 配置

Given: dev-1 或 sta-1 的 Consul 中存在 `origination-api` 的 OTLP 配置。

When: `origination-api` 启动或重启。

Then: 服务读取 Consul 中的 OTLP endpoint/header，并按 `service.name=origination-api` 导出 trace。

### Scenario 3: GitOps 同步不清空私密配置

Given: Consul 中已有人工维护的 OTLP endpoint/header。

When: Argo CD 同步、Deployment 更新或 Consul seed Job 重跑。

Then: 已有私密 OTLP endpoint/header 不会被 GitOps 中的非密配置覆盖或清空。

### Scenario 4: 按环境区分 trace

Given: dev-1 与 sta-1 均运行 quote/origination。

When: 查询 Sentry 或 OTLP receiver 中的 trace。

Then: trace 能按 `service.name` 和 `deployment.environment` 区分服务与环境。

## Business Rules

- BR1: 真实 Sentry DSN、public key 和认证 header 不得提交到 Git、Harness 文档或 Jira。
- BR2: `quote-api` 与 `origination-api` 应使用与 `applicant-api` 一致的 Spring Boot ConfigData / Consul Config 模型。
- BR3: 本地开发默认不强依赖本地 Consul。
- BR4: dev-1 与 sta-1 必须使用不同 Consul prefix 和不同 `deployment.environment`。
- BR5: GitOps 可以管理非敏配置结构，但不能清空 Consul 中已存在的私密 OTLP endpoint/header。

## Acceptance Criteria

- AC1: `quote-api` 具备 Consul Config 读取能力，启动后能使用 Consul OTLP 配置导出 trace。
- AC2: `origination-api` 具备 Consul Config 读取能力，启动后能使用 Consul OTLP 配置导出 trace。
- AC3: Argo CD 同步、Deployment 更新或 Consul seed Job 重跑后，Consul 私密 OTLP 配置不丢失。
- AC4: 仓库中不存在真实 Sentry DSN、public key 或认证 header。
- AC5: dev-1 / sta-1 trace 可按 `service.name` 和 `deployment.environment` 区分。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 私密 OTLP 值长期由人工写 Consul、ExternalSecret 还是后续 Secret 管理系统维护？ | core | 2026-07-05 | open |

## Notes

- 本需求只补齐配置读取和运行时持久性，不改变业务契约。
