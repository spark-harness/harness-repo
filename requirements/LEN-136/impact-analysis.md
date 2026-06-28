---
requirement_id: "LEN-136"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-28"
approved_by: "forest"
approved_at: "2026-06-28T16:35:12+08:00"
decision: "批准 LEN-136 service-repo-check；业务服务路径通过服务矩阵解析，基础设施和 Caddy 作为 GitOps 组件影响处理，不作为业务服务条目。"
idl_impact: "no"
idl_impact_reason: "本需求只调整 GitOps、Kubernetes runtime 配置和 Harness 文档，不修改 protobuf 或生成契约。"
---

# Impact Analysis

## Summary

LEN-136 影响 Lendora 运行环境的 GitOps 目标状态、Argo CD 应用集合、共享基础设施、Consul 配置、PostgreSQL database、Redis logical DB、Caddy 入口和旧 STA 清理边界。它不修改业务功能、protobuf IDL 或生成契约。

## Affected Domains

- GitOps 环境入口：新增或替换 `dev-1`、`sta-1` 和共享基础设施入口。
- Kubernetes namespace：业务按环境 namespace 隔离，基础设施按组件 namespace 隔离。
- Argo CD：服务应用按环境和服务拆分，`dev-1` 自动同步，`sta-1` 手动同步。
- Consul：共享实例，KV key 与服务发现名称按环境隔离。
- PostgreSQL：共享实例，database 和 username 按环境隔离。
- Redis：共享实例，logical DB 按环境隔离。
- Caddy：四个公网域名分别路由到对应环境前端和 API。
- 清理：旧 `lendora-sta-*` namespace、PVC、入口和 GitOps 表达在新环境验证后删除或废弃。

## Affected Services And Repos

| Service / Component | Repo | Impact | IDL Required |
|---|---|---|---|
| fides | `gitops-repo` | 新增 dev-1 / sta-1 overlay 和公网 Web 路由 | No |
| fides-bff | `gitops-repo` | 新增 dev-1 / sta-1 overlay、BFF 配置和 API 路由 | No |
| applicant-api | `gitops-repo` | 新增 dev-1 / sta-1 overlay、PostgreSQL / Redis / Consul 配置 | No |
| quote-api | `gitops-repo` | 新增 dev-1 / sta-1 overlay、PostgreSQL / Consul 配置 | No |
| origination-api | `gitops-repo` | 新增 dev-1 / sta-1 overlay、PostgreSQL / Consul / quote-api 配置 | No |
| PostgreSQL | `gitops-repo` | 共享基础设施 namespace 和环境 database 初始化 | No |
| Redis | `gitops-repo` | 共享基础设施 namespace 和 logical DB 分配 | No |
| Consul | `gitops-repo` | 共享基础设施 namespace、KV 和 catalog 隔离 | No |
| Harness lifecycle | `harness-repo` | LEN-136 requirement / impact / design / tasks | No |

## Upstream / Downstream Consumers

- 上游用户：dev-1 和 sta-1 的公开前端访问者。
- fides：调用同环境 `*-api.fuzzytails.fun` 的 BFF API。
- fides-bff：通过 Consul 查询同环境 applicant-api、quote-api、origination-api。
- applicant-api：使用同环境 PostgreSQL database、Redis logical DB 和 Consul service registration。
- quote-api：使用同环境 PostgreSQL database 和 Consul service registration。
- origination-api：使用同环境 PostgreSQL database，调用同环境 quote-api。
- Argo CD：按 GitOps 目标状态同步或展示 drift。
- Caddy：按域名路由到对应环境服务。

## API And Protobuf Contract Impact

- Protobuf files: no change.
- Buf config: no change.
- Generated contracts: no change.
- External HTTP API shape: no endpoint shape change; only hostnames and runtime routing change.
- Compatibility risk: low at contract layer; runtime routing and configuration isolation risk is material.

## Data, Cache, And Runtime Storage Impact

- PostgreSQL:
  - 共享实例运行在 `lendora-shared-postgres`。
  - database 按环境和服务拆分，例如 `dev_1_applicant`、`sta_1_quote`。
  - username 按环境和服务拆分，避免跨环境权限复用。
- Redis:
  - 共享实例运行在 `lendora-shared-redis`。
  - logical DB 按环境分配：`dev-1` 使用 DB 1，`sta-1` 使用 DB 2。
  - 本需求不新增业务 key prefix 能力。
- Consul:
  - 共享实例运行在 `lendora-shared-consul`。
  - KV 和 catalog 均按环境隔离。
- PVC:
  - 共享基础设施保留 PVC。
  - 旧 `lendora-sta-*` PVC 在新环境验证通过后允许删除。

## Config / Permission / Observability Impact

- Config:
  - overlay patch 注入环境 namespace、database、Redis DB、Consul URL、Consul key、Consul service name、CORS、BFF route。
  - `dev-1` 与 `sta-1` 不从旧 `lendora-sta` 继承运行配置。
- Permission:
  - AppProject destinations 必须允许两个业务 namespace 和三个共享基础设施 namespace。
  - Secret 值仍由 bootstrap 或外部 Secret 管理，不进入 Git。
- Observability:
  - OTEL 环境字段应区分 `dev-1` 与 `sta-1`。
  - 验证日志不得泄漏手机号、OTP、token 或 applicantId。
- Network:
  - 业务服务同环境 namespace 内互访。
  - 业务 namespace 允许访问共享 Consul、Redis、PostgreSQL。

## Rollout And Rollback

Rollout:

1. 同步共享基础设施。
2. 部署 `dev-1` 服务应用并自动同步最新 digest。
3. 验证 `dev-1` 入口、登录、试算和草稿保存。
4. 手工指定 `sta-1` digest 并手动同步服务应用。
5. 验证 `sta-1` 主链路。
6. 清理旧 `lendora-sta-*` 资源和入口。

Rollback:

- `dev-1`：回退 GitOps digest 或暂停自动同步后切回上一 digest。
- `sta-1`：保持手动同步，回退指定 digest 后人工同步。
- 共享基础设施：优先不删除；配置错误通过 Git revert 和重新同步修复。
- 旧 STA 清理后不作为回滚路径；清理前必须保留验证证据。

## Risks And Mitigations

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| dev 自动最新 digest 与仓库现有 digest-only policy 冲突 | 可能需要 workflow 支持 dev overlay 自动 promotion | 先将 dev overlay 纳入 image release promotion 路径；如 workflow 不支持多目标，记录后续补强 | Codex |
| sta 手动 sync 与 Argo CD Application 自动同步默认不一致 | 可能误自动发布 STA | sta-1 Application 不设置 `syncPolicy.automated` | Codex |
| Redis logical DB 配置未完整注入 | 两环境可能共享缓存 | overlay 显式设置 `SPRING_DATA_REDIS_DATABASE`，验证渲染结果 | Codex |
| Consul 裸服务名残留 | BFF 可能跨环境发现服务 | overlay 显式 patch service name 和 registry metadata | Codex |
| 旧 `sta1/sta2` skeleton 与新 Lendora 目标混淆 | 评审者可能误认为旧 skeleton 仍有效 | 文档和 GitOps 入口使用 `dev-1` / `sta-1`，旧 `sta2` 不纳入目标状态 | Codex |
| 真实集群 Secret 不存在 | Argo sync 后 Pod 无法启动 | 提供 bootstrap 文档并保留 Secret 同名约定 | Forest |

