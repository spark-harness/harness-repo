---
requirement_id: "LEN-158"
owner: "forest"
status: "approved"
created_at: "2026-07-04"
related_branch: "feature/LEN-158-vault-vso-config-migration"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
  - idl-repo
  - gitops-repo
approved_by: "forest"
approved_at: "2026-07-04T16:29:45+08:00"
decision: "用户在 2026-07-04 授权 Agent 批准任务执行中所有请求；批准 LEN-158 requirement 与 impact-analysis，idl-repo 仅用于同分支 proto readiness，不修改 protobuf。"
---

# Lendora 配置中心从 Consul 迁移到 Vault/VSO

## Background

当前 Lendora dev-1 和 sta-1 的运行配置同时存在 Consul KV、Kubernetes Secret、GitOps ConfigMap 和人工维护 Secret。配置来源分散，变更链路不够清晰，新增、回滚或排障时容易出现线上值、代码期望和 GitOps 引用不一致。

它不是什么：本需求不是服务发现迁移，不删除 `lendora-shared-consul`，也不把业务应用改成直接访问 Vault。

它是什么：本需求把目标服务的运行配置收敛到 Vault，由 Vault Secrets Operator 同步成 Kubernetes Secret，应用继续通过环境变量和框架原生配置读取配置。

## Goals

- R1：在 dev-1 和 sta-1 建立 VSO、VaultConnection、VaultAuth 和 ArgoCD 差异规则。
- R2：为 applicant-api、quote-api、origination-api、fides-bff、fides-web 建立环境级 Vault runtime path、最小权限 policy 和 role。
- R3：fides-bff 删除自定义 Consul KV config loader，回归 Kratos file/env source。
- R4：fides-web 建立唯一强类型 env 入口，并阻断业务代码散落读取 `process.env`。
- R5：quote-api、origination-api、applicant-api 移除 Spring Cloud Consul Config，继续保留 Consul 服务注册。
- R6：GitOps 通过 VSO Secret `envFrom` 注入运行配置，并删除目标服务的 Consul KV 配置 bootstrap。
- R7：dev-1 先切换并完成 smoke，再切换 sta-1；最后确认所有目标服务不再读 Consul KV。

## Non-Goals

- 不做动态配置热更新；配置变化通过 Secret 同步和 Pod 滚动重启生效。
- 不迁移或删除 Consul 服务注册与服务发现。
- 不提交真实 secret、token、证书、OTLP header 或 Vault 值。
- 不改变 fides-bff、fides-web 或 Java 服务的业务接口。
- 不扩展生产级多集群 Vault 拓扑。

## User / Business Scenarios

### Scenario 1：平台同步底座可用

Given：目标集群尚未安装 VSO。

When：GitOps 同步平台清单。

Then：VSO controller、CRD、VaultConnection 和 VaultAuth 可被业务 VaultStaticSecret 引用。

### Scenario 2：服务通过 env 读取 Vault 同步配置

Given：Vault 中已有目标服务 runtime path，VSO 已同步对应 Kubernetes Secret。

When：目标服务 Pod 滚动重启。

Then：服务从环境变量读取运行配置，不访问 Consul KV 配置中心。

### Scenario 3：浏览器只接收 public runtime config

Given：Vault 中同时存在 public 和非 public 配置 key。

When：用户请求 fides-web `/api/runtime-config`。

Then：响应只包含 public 白名单字段，不暴露非 public 值。

### Scenario 4：后端链路保留服务发现

Given：Consul 中仍有 applicant-api、quote-api、origination-api 和 fides-bff 服务注册。

When：用户触发 fides-web 到 BFF 再到后端的业务链路。

Then：跨服务调用仍通过现有服务发现能力完成，且目标服务不读取 Consul KV 配置。

### Scenario 5：分阶段切换和回滚

Given：dev-1 已完成 VSO 切换和 smoke。

When：sta-1 执行同样切换。

Then：五个目标服务 rollout、readiness、核心 smoke 和 trace 串联通过；如失败可回滚到上一组 GitOps Secret 引用和镜像配置。

## Business Rules

- BR1：GitOps 和 ArgoCD 只保存 Vault 地址、路径、role 和引用关系，不保存敏感值。
- BR2：只有 VSO 访问 Vault；业务应用和 ArgoCD 不直接访问 Vault。
- BR3：Vault key 使用最终环境变量名，适配 `envFrom`。
- BR4：每个服务使用独立 runtime path、policy、role 和输出 Secret。
- BR5：Consul 继续承担服务注册与发现，不能删除 `lendora-shared-consul`。
- BR6：删除 Consul KV bootstrap 必须发生在服务代码、VSO Secret 注入和环境验证之后。
- BR7：dev-1 必须先于 sta-1 切换；sta-1 不能跳过 dev-1 验证。
- BR8：fides-web 全项目只有 `src/config/env.ts` 允许读取 `process.env`。

## Acceptance Criteria

- AC1：dev-1 和 sta-1 中 VSO controller、CRD、VaultConnection、VaultAuth 可用。
- AC2：五个目标服务的 Vault runtime path 均存在，并同步为对应 Kubernetes Secret。
- AC3：fides-bff 启动时不访问 Consul KV 配置中心，仍能通过 Consul 访问下游服务。
- AC4：fides-web 通过强类型 env 和 `/api/runtime-config` 暴露 public 白名单字段，lint 阻断散落 `process.env`。
- AC5：quote-api、origination-api、applicant-api 不再依赖 Spring Cloud Consul Config，readiness 和关键依赖配置来自 env。
- AC6：GitOps 中目标服务使用 VSO Secret `envFrom`，并移除 Consul KV 配置 bootstrap。
- AC7：dev-1 五个目标服务 rollout、readiness、业务 smoke 和 trace 串联通过。
- AC8：sta-1 五个目标服务 rollout、readiness、业务 smoke 和 trace 串联通过。
- AC9：Consul KV bootstrap Job 已从 GitOps 清理，但 Consul 服务注册/发现和 NetworkPolicy 保留。
- AC10：ArgoCD 显示 Synced/Healthy，且仓库中没有真实敏感配置值。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| Vault 服务地址和认证方式是否已在集群可用 | forest | LEN-160 实施前 | Open：先从 live cluster 和现有 secret 盘点确认。 |
| 现有 Kubernetes Secret key 是否完整可迁移 | forest | LEN-161 实施前 | Open：迁移前记录 key 集合，不记录真实值。 |
| 镜像发布是否由本分支直接执行 | forest | 代码合并后 | Open：代码合并和镜像发布后才能合并对应 GitOps 切换。 |

## Notes

- Jira Epic：LEN-158。
- 关联 Story：LEN-159、LEN-162、LEN-165、LEN-168、LEN-172。
- 关联 Sub-task：LEN-160、LEN-161、LEN-163、LEN-164、LEN-166、LEN-167、LEN-169、LEN-170、LEN-171、LEN-173、LEN-174。
- `idl-repo` 只用于 fides-bff 和 applicant-api 的同分支 proto readiness 检查，不修改 protobuf。
- 用户已授权 Agent 批准任务执行中所有请求，包括 Janus approval。
