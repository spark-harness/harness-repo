---
requirement_id: "LEN-136"
owner: "Codex"
status: "approved"
updated_at: "2026-06-28"
approved_by: "forest"
approved_at: "2026-06-28T16:35:12+08:00"
decision: "刷新批准 LEN-136 design；impact-analysis 输入哈希已更新，设计仍按 dev-1 / sta-1 双环境 GitOps 方案执行。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, AC1, AC5 | D1: 建立 `clusters/lendora-shared`、`clusters/lendora-dev-1`、`clusters/lendora-sta-1` 三类 GitOps 入口 | 共享基础设施与业务环境分开 |
| R2, AC2, AC3 | D2: 业务服务按环境 namespace 部署，Argo Application 按服务拆分 | namespace 是环境边界，Application 是服务发布边界 |
| R3, AC4 | D3: PostgreSQL、Redis、Consul 使用独立共享 namespace | 避免业务环境名污染共享组件 |
| R4, AC6, AC7, AC8, AC9 | D4: Consul、PostgreSQL、Redis 全部显式环境化 | 避免配置、发现、数据和缓存串环境 |
| R5, R6, AC10 | D5: dev 自动 promotion / 自动 sync，sta 手工 digest / 手动 sync | dev 偏快速验证，sta 偏稳定验收 |
| R7, AC11, AC12 | D6: Caddy 域名按环境和 Web/API 拆分 | 不复用 `api.fuzzytails.fun` |
| R8, AC13 | D7: 旧 STA 清理在新环境验证后执行 | 清理包括 namespace、入口、PVC 和旧 GitOps 表达 |
| AC14 | D8: 以 kustomize 渲染和静态引用检查作为配置类验证 | 本需求不修改业务代码 |

## Summary

方案把 namespace 作为环境隔离单元，而不是服务隔离单元。`lendora-dev-1` 和 `lendora-sta-1` 分别承载对应环境的 fides、fides-bff、applicant-api、quote-api、origination-api。共享依赖仍拆到独立 namespace，便于保留基础设施生命周期和权限边界。

## Affected Services

| Service | Change |
|---|---|
| fides | 新增 dev-1 / sta-1 overlay，设置环境、Consul runtime key、API base URL 和域名路由 |
| fides-bff | 新增 dev-1 / sta-1 overlay，设置 CORS、Consul resolver service name、registry service name 和环境 metadata |
| applicant-api | 新增 dev-1 / sta-1 overlay，设置 JDBC、Redis DB、Consul registration 和 Consul KV |
| quote-api | 新增 dev-1 / sta-1 overlay，设置 JDBC、Consul registration 和 Consul KV |
| origination-api | 新增 dev-1 / sta-1 overlay，设置 JDBC、quote-api URL、Consul registration 和 Consul KV |
| PostgreSQL | 共享部署，初始化环境化 database / role |
| Redis | 共享部署，环境按 logical DB 隔离 |
| Consul | 共享部署，KV 和 catalog 通过 key / service name 隔离 |

## API / Contract Design

- Protobuf: no change.
- HTTP API: no path or body schema change.
- Public hostnames:
  - `dev-1-api.fuzzytails.fun`
  - `dev-1-fides.fuzzytails.fun`
  - `sta-1-api.fuzzytails.fun`
  - `sta-1-fides.fuzzytails.fun`
- Compatibility:
  - 旧 `api.fuzzytails.fun` 不作为新环境入口。
  - Caddy 可在清理前暂时保留旧路由，但新环境不得依赖旧路由。

## Application Design

### D1: GitOps Entries

新增目标入口：

```text
clusters/lendora-shared/
clusters/lendora-dev-1/
clusters/lendora-sta-1/
```

`lendora-shared` 管理 PostgreSQL、Redis、Consul。`lendora-dev-1` 和 `lendora-sta-1` 分别管理本环境业务应用。

### D2: Environment Namespace Model

业务 namespace：

```text
lendora-dev-1
lendora-sta-1
```

共享基础设施 namespace：

```text
lendora-shared-postgres
lendora-shared-redis
lendora-shared-consul
```

每个业务服务仍保留独立 Argo Application：

```text
lendora-dev-1-fides
lendora-dev-1-fides-bff
lendora-dev-1-applicant-api
lendora-dev-1-quote-api
lendora-dev-1-origination-api
```

STA 同理使用 `lendora-sta-1-*` Application 名称。Application 的 destination namespace 指向环境 namespace。

### D3: Shared Infrastructure

PostgreSQL、Redis、Consul 继续使用 GitOps 资源声明，不把 Secret 值写入 Git。

PostgreSQL database / role：

| Environment | applicant | quote | origination |
|---|---|---|---|
| dev-1 | `dev_1_applicant` | `dev_1_quote` | `dev_1_origination` |
| sta-1 | `sta_1_applicant` | `sta_1_quote` | `sta_1_origination` |

Redis logical DB：

| Environment | DB |
|---|---|
| dev-1 | `1` |
| sta-1 | `2` |

### D4: Consul Isolation

Consul URL：

```text
http://consul.lendora-shared-consul.svc.cluster.local:8500
```

KV key：

```text
spark/lendora/{env}/{component}/{kind}
```

Examples：

```text
spark/lendora/dev-1/applicant-api/config
spark/lendora/sta-1/fides-web/runtime-config
```

Service discovery name：

```text
{env}-{service}
```

Examples：

```text
dev-1-applicant-api
sta-1-quote-api
```

BFF 查询 service name 必须与所在环境一致。后端服务注册 address 指向同环境 namespace 内 Kubernetes Service，例如 `quote-api.lendora-dev-1.svc.cluster.local`。

### D5: Image And Sync Policy

`dev-1`：

- overlay 使用不可变 digest。
- image release workflow 自动更新 dev overlay 到最新 digest。
- Argo CD Application 设置 `automated.prune=true` 和 `selfHeal=true`。

`sta-1`：

- overlay 使用人工指定 digest。
- 不通过自动 promotion 覆盖。
- Argo CD Application 不配置 `syncPolicy.automated`，由维护者人工 sync。

### D6: Caddy Routing

API 域名：

```text
dev-1-api.fuzzytails.fun -> fides-bff.lendora-dev-1.svc.cluster.local:8000
sta-1-api.fuzzytails.fun -> fides-bff.lendora-sta-1.svc.cluster.local:8000
```

Web 域名：

```text
dev-1-fides.fuzzytails.fun -> fides.lendora-dev-1.svc.cluster.local:3000
sta-1-fides.fuzzytails.fun -> fides.lendora-sta-1.svc.cluster.local:3000
```

Web 的 BFF base URL 分别指向对应 API 域名。

### D7: Legacy STA Cleanup

清理对象：

- `lendora-sta-*` business / dependency namespace。
- `api.fuzzytails.fun` 中旧 Lendora 前端和 BFF 路由。
- `clusters/lendora-sta` 和 `apps/*/overlays/lendora-sta` 的目标状态表达，或至少从 active cluster 入口中移除。
- 旧 `lendora-sta-*` PVC。
- 旧 Consul KV `config/<service>/data` 和裸 service registration。

清理前置条件：

- `dev-1` 主链路验证通过。
- `sta-1` 主链路验证通过。
- 新入口不依赖旧 namespace、旧 PVC 或旧 Consul key。

## Data / Config / Permission

- Secret:
  - 每个 namespace 内保持同名 Secret。
  - `lendora-dev-1` 和 `lendora-sta-1` 各自包含业务服务需要的 runtime Secret。
  - 共享 namespace 包含基础设施 Secret。
- Network:
  - 业务 namespace 可访问共享 Consul、Redis、PostgreSQL。
  - 公网只经 Caddy 进入 fides / fides-bff。
- Config:
  - overlay 使用 patch 显式覆盖旧 `lendora-sta-*` base 值。
  - 新环境渲染结果不得引用旧 `lendora-sta-*` DNS。

## Observability

- `observability.otel.environment`、Consul metadata 和 Kubernetes labels 区分 `dev-1` 与 `sta-1`。
- smoke 证据记录公开域名、Argo app 状态、服务 readiness、主链路结果。
- 日志检查不得包含手机号、OTP、token、applicantId 明文。

## Testing Strategy

配置类 test-first 例外：

- 本需求主要修改 GitOps YAML 和 Harness 文档，不修改业务代码路径。
- 替代验证使用 Kustomize 渲染和静态引用检查。

验证命令：

```bash
kubectl kustomize clusters/lendora-shared
kubectl kustomize clusters/lendora-dev-1
kubectl kustomize clusters/lendora-sta-1
kubectl kustomize apps/lendora-shared-dependencies/overlays/shared
kubectl kustomize apps/applicant-api/overlays/dev-1
kubectl kustomize apps/applicant-api/overlays/sta-1
kubectl kustomize apps/quote-api/overlays/dev-1
kubectl kustomize apps/quote-api/overlays/sta-1
kubectl kustomize apps/origination-api/overlays/dev-1
kubectl kustomize apps/origination-api/overlays/sta-1
kubectl kustomize apps/fides-bff/overlays/dev-1
kubectl kustomize apps/fides-bff/overlays/sta-1
kubectl kustomize apps/fides/overlays/dev-1
kubectl kustomize apps/fides/overlays/sta-1
```

静态检查：

```bash
rg "lendora-sta" clusters/lendora-dev-1 clusters/lendora-sta-1 apps/*/overlays/dev-1 apps/*/overlays/sta-1
rg "config/(applicant-api|quote-api|origination-api)/data" apps/*/overlays/dev-1 apps/*/overlays/sta-1
```

Runtime 验证在集群同步后执行：

- Argo CD app health / sync 检查。
- 四个域名 HTTP 检查。
- 登录、试算、草稿保存主链路。
- Consul KV / catalog 查询。
- PostgreSQL database 查询。
- Redis logical DB 查询。

## Rollout And Rollback

Rollout 顺序：

1. 合并 GitOps 目标状态。
2. bootstrap 必要 Secret。
3. 同步共享基础设施。
4. 自动同步 `dev-1`，验证主链路。
5. 人工指定 `sta-1` digest，手动同步 `sta-1`。
6. 验证 `sta-1` 主链路。
7. 执行旧 STA 清理。

Rollback：

- 清理前：可回退 GitOps commit 或切回旧 `lendora-sta` 入口。
- 清理后：以新 GitOps commit revert 和 digest rollback 为主，不依赖旧 PVC 或旧 namespace。

## Risks

| Risk | Mitigation |
|---|---|
| dev 自动最新 digest 需要 workflow 调整 | 将 dev overlay 加入 image release promotion；sta overlay 不加入自动 promotion |
| Redis logical DB 配置遗漏 | 在 overlay 中显式设置 Redis DB，并通过渲染检查确认 |
| Consul service name 未完全环境化 | 在所有服务 config 和 BFF config 中 patch `{env}-{service}` |
| 旧 STA 清理过早 | 清理任务必须排在两个环境 runtime 验证之后 |

