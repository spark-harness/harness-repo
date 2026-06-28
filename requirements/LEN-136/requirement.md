---
requirement_id: "LEN-136"
owner: "forest"
status: "approved"
created_at: "2026-06-28"
related_branch: "feature/LEN-136-argocd-dev1-sta1"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - gitops-repo
approved_by: "forest"
approved_at: "2026-06-28T16:35:12+08:00"
decision: "刷新批准 LEN-136 requirement 与 impact-analysis；service-repo-check 审批写入 impact-analysis 后重新固化 gate 输入。"
---

# Lendora dev-1 / sta-1 GitOps 双环境

## Background

Lendora 旧 `lendora-sta` 环境来自临时部署和后续 GitOps 补齐。它能支撑主链路验证，但环境边界、配置隔离、入口命名和清理责任不够清晰。

它不是什么：本需求不是继续维护 `lendora-sta`，也不是创建生产 `prod` 环境，更不是改变贷款申请业务流程。

它是什么：用 Argo CD 管理同一 vincent-k3s 集群内的 `dev-1` 与 `sta-1` 两套 Lendora 业务环境，并用共享基础设施承载 PostgreSQL、Redis 和 Consul。业务环境按 namespace 隔离，配置和数据按环境隔离，旧 `lendora-sta` 在新环境验证后清理。

## Goals

- R1：GitOps 仓中存在 `dev-1`、`sta-1` 和共享基础设施的明确入口。
- R2：`dev-1` 和 `sta-1` 的业务服务分别部署在 `lendora-dev-1` 与 `lendora-sta-1` namespace。
- R3：PostgreSQL、Redis、Consul 分别部署在 `lendora-shared-postgres`、`lendora-shared-redis`、`lendora-shared-consul` namespace。
- R4：Consul KV、Consul 服务发现、PostgreSQL database、Redis logical DB 都按环境隔离。
- R5：`dev-1` 使用自动最新 digest 部署策略，`sta-1` 使用手工指定 digest 部署策略。
- R6：`dev-1` 自动同步，`sta-1` 手动同步。
- R7：四个公开入口域名按环境和前后端拆分。
- R8：新环境主链路验证通过后，旧 `lendora-sta-*` namespace、入口、PVC 和旧 GitOps 表达可以清理。

## Non-Goals

- 不改变贷款申请、登录、试算或草稿保存的用户流程。
- 不引入生产 `prod` 环境。
- 不引入真实短信、真实风控定价或新外部供应商。
- 不删除 Argo Workflows、Argo Events、Caddy、Kubernetes 系统 namespace 或与 Lendora 无关的资源。
- 不把真实 Secret 值写入 Git。

## User / Business Scenarios

### Scenario 1：交付负责人查看 GitOps 环境边界

Given：同一集群已安装 Argo CD。

When：交付负责人查看 Lendora Argo CD 应用集合。

Then：能看到共享基础设施、`dev-1` 服务应用和 `sta-1` 服务应用，并能区分自动同步和手动同步策略。

### Scenario 2：用户访问 dev-1

Given：`dev-1` 已部署。

When：用户访问 `https://dev-1-fides.fuzzytails.fun` 并调用 `https://dev-1-api.fuzzytails.fun/api/v1`。

Then：前端可打开，API 指向 `dev-1` BFF，主链路不访问 `sta-1` 服务。

### Scenario 3：用户访问 sta-1

Given：`sta-1` 已部署且人工同步。

When：用户访问 `https://sta-1-fides.fuzzytails.fun` 并调用 `https://sta-1-api.fuzzytails.fun/api/v1`。

Then：前端可打开，API 指向 `sta-1` BFF，主链路不访问 `dev-1` 服务。

### Scenario 4：共享 Consul 不串环境

Given：两个环境共用 Consul。

When：查询 Consul KV 和服务发现 catalog。

Then：KV 使用 `spark/lendora/{env}/{component}/{kind}`，服务名使用 `{env}-{service}`，`dev-1` 与 `sta-1` 不共享裸服务名或裸配置 key。

### Scenario 5：共享数据依赖不串环境

Given：两个环境共用 PostgreSQL 和 Redis。

When：检查 JDBC URL、database 名、Redis logical DB 和运行时配置。

Then：PostgreSQL 按环境独立 database，Redis 按环境独立 logical DB，不共享业务记录或缓存空间。

### Scenario 6：旧 STA 清理

Given：`dev-1` 和 `sta-1` 主链路验证通过。

When：清理旧 `lendora-sta` 资源。

Then：旧业务 namespace、旧入口、旧 PVC 和旧 GitOps 入口不再表达目标运行态，且不影响共享基础设施、Argo Workflows、Argo Events、Caddy 或系统 namespace。

## Business Rules

- BR1：目标业务环境固定为 `dev-1` 和 `sta-1`，不是 `sta-2`。
- BR2：业务 namespace 按环境拆分：`lendora-dev-1`、`lendora-sta-1`。
- BR3：共享基础设施 namespace 固定为 `lendora-shared-postgres`、`lendora-shared-redis`、`lendora-shared-consul`。
- BR4：Argo CD Application 仍按服务拆分，便于服务级同步、回滚和健康检查。
- BR5：Consul KV key 固定为 `spark/lendora/{env}/{component}/{kind}`。
- BR6：Consul service name 固定为 `{env}-{service}`，禁止新环境使用裸 `applicant-api`、`quote-api`、`origination-api`、`fides-bff`。
- BR7：PostgreSQL 使用共享实例，但 database 按环境和服务独立。
- BR8：Redis 使用共享实例，但 logical DB 按环境独立。
- BR9：`dev-1` 镜像由自动最新 digest promotion 更新。
- BR10：`sta-1` 镜像由人工指定 digest 更新。
- BR11：`dev-1` Argo CD 应用自动同步，`sta-1` Argo CD 应用手动同步。
- BR12：公网入口固定为 `dev-1-api.fuzzytails.fun`、`dev-1-fides.fuzzytails.fun`、`sta-1-api.fuzzytails.fun`、`sta-1-fides.fuzzytails.fun`。
- BR13：Secret 值不进入 Git；每个 namespace 内可保持同名 Secret。
- BR14：旧 `lendora-sta-*` PVC 在新环境验证通过后允许删除。

## Acceptance Criteria

- AC1：`gitops-repo` 中存在共享基础设施、`dev-1`、`sta-1` 的 cluster / app-of-apps 入口。
- AC2：`dev-1` 所有业务服务目标 namespace 为 `lendora-dev-1`。
- AC3：`sta-1` 所有业务服务目标 namespace 为 `lendora-sta-1`。
- AC4：共享 PostgreSQL、Redis、Consul 目标 namespace 分别为 `lendora-shared-postgres`、`lendora-shared-redis`、`lendora-shared-consul`。
- AC5：所有目标运行时资源可由 Argo CD Application 管理，且不依赖旧 `lendora-sta-*` 手工残留。
- AC6：Consul KV 写入 job 按环境写入 `spark/lendora/{env}/{component}/{kind}`。
- AC7：后端服务注册到 Consul 的服务名包含环境前缀，BFF 查询对应环境服务名。
- AC8：PostgreSQL database 和 JDBC username 按环境隔离。
- AC9：Redis logical DB 按环境隔离。
- AC10：`dev-1` 应用配置自动同步，`sta-1` 应用配置手动同步。
- AC11：四个公开域名在 Caddy 中分别路由到对应环境的 fides 或 fides-bff 服务。
- AC12：`dev-1` 和 `sta-1` 都能完成公开入口访问、登录、试算和草稿保存主链路验证。
- AC13：新环境验证通过后，旧 `lendora-sta-*` namespace、旧入口、旧 PVC 和旧 GitOps 入口有明确清理范围。
- AC14：渲染检查覆盖共享基础设施、两个环境的服务 overlay 和 cluster 入口。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 业务 namespace 是否按服务拆分 | Forest | 需求批准前 | Closed：不按服务拆；按环境拆为 `lendora-dev-1` 和 `lendora-sta-1` |
| STA 目标环境是 sta-1 还是 sta-2 | Forest | 需求批准前 | Closed：目标是 `sta-1` |
| 域名中是否使用 `fides` 拼写 | Forest | 需求批准前 | Closed：使用 `fides` |
| Redis 是否已有业务 key prefix 支持 | Codex | 实现前 | Closed：采用 Redis logical DB 隔离，不要求本需求新增 key prefix |

## Notes

- Jira `LEN-136` 原始描述写作 `sta-2`，本需求按用户澄清改为 `sta-1`。
- 用户于 2026-06-28 在对话中批准 Requirement Brief，允许创建需求文档、隔离 worktree 并进入实现。
- 文件审批字段保持空值；正式 Harness 审批需由用户运行 `janus requirement approve` 写入。

