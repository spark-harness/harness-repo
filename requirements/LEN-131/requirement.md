---
requirement_id: "LEN-131"
owner: "core"
status: "approved"
created_at: "2026-06-28"
related_branch: "feature/LEN-131-quote-api-lendora-sta-deploy"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
  - gitops-repo
approved_by: "forest"
approved_at: "2026-06-28T02:35:00+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-131 quote-api lendora-sta 部署需求和影响分析，范围限定为 quote-api 镜像、GitOps 部署、quote DB、readiness、k8s/Consul 服务发现和 runtime smoke，不包含 BFF facade 或前端接入。"
---

# quote-api lendora-sta 部署

## Background

LEN-10 已交付 `quote-api` Java Spring 服务和 Quote 持久化能力，但服务尚未部署到 lendora-sta。后续 LEN-132、LEN-11 和 LEN-5 需要一个可访问、可写 quote DB、可被服务发现的运行时服务。

这条需求不是什么：它不是实现 quote 业务逻辑，不是实现 `fides-bff` pricing facade，也不是前端真实 API 接入。

它是什么：它补齐 `quote-api` 的镜像构建入口、lendora-sta GitOps 资产、quote DB 运行配置、readiness、k8s Service 和 Consul 可发现性，并用运行时 smoke 验证服务可用。

## Goals

- 为 `business-repo/apps/quote-api` 增加可发布镜像构建入口。
- 在 `gitops-repo` 新增 `apps/quote-api/base` 和 `overlays/lendora-sta`。
- 在 lendora-sta app-of-apps 中纳入 quote-api Argo CD Application 和 namespace。
- 为 quote-api 提供独立 quote DB 连接配置和 Secret 引用。
- 部署后验证 `/ready` 返回 READY，且 quote DB 写入可用。
- 验证 k8s Service 和 Consul 都能发现 `quote-api`。
- 保持部署由 GitOps 驱动，不依赖手工 `kubectl apply` 维护目标状态。

## Non-Goals

- 不修改 protobuf IDL 或生成契约。
- 不改变 LEN-10 的 Quote 计算、校验和持久化业务规则。
- 不实现 `fides-bff` `/api/v1/pricing/quotes` facade；LEN-132 负责。
- 不实现前端贷款请求屏真实 API 接入；LEN-11 负责。
- 不设计长期数据库 operator、ExternalSecret 或生产级多副本 PostgreSQL。
- 不把 quote 表放进 applicant-api 业务库。

## User / Business Scenarios

### Scenario 1: quote-api 运行时就绪

Given: lendora-sta 已同步 quote-api GitOps Application。

When: 运维或后续服务访问 `quote-api` `/ready`。

Then: quote-api 返回 READY，Pod Ready，且 readiness 包含 quote DB 可用性。

### Scenario 2: Quote 写入数据库

Given: 已认证请求携带 `x-applicant-id` 调用 quote-api 试算接口。

When: 请求金额和期限在 LEN-10 允许范围内。

Then: quote-api 返回 quoteId，并在 quote DB 写入一条 Quote。

### Scenario 3: 服务发现可用

Given: quote-api 已部署并注册。

When: 从集群内查询 k8s Service 或 Consul catalog/health。

Then: `quote-api` 可通过 `quote-api.lendora-sta-quote-api.svc.cluster.local` 和 Consul 服务名发现。

### Scenario 4: quote DB 不可用时阻断流量

Given: quote DB 不可用或 quote-api 无法连接 DB。

When: Kubernetes 或 Consul health check 访问 `/ready`。

Then: readiness 失败，服务不应被视为可接收流量。

## Business Rules

- BR1: quote-api 必须部署在独立 namespace `lendora-sta-quote-api`。
- BR2: quote DB 配置必须使用 quote-api 专属 database/schema 和 Secret 引用，不复用 applicant-api runtime Secret。
- BR3: quote-api 镜像必须由 business-repo Dockerfile 构建，并在 GitOps overlay 中使用不可变 digest 或明确的 release 输入更新。
- BR4: `/ready` 必须覆盖 quote DB 连接可用性。
- BR5: Consul 注册地址必须使用集群内可达 Service DNS，不能注册 Pod 内 `127.0.0.1`。
- BR6: GitOps 目标状态必须能通过 `kubectl kustomize` 渲染，并由 Argo CD Application 管理。
- BR7: Secret 值不得提交到仓库；仓库只保存 Secret 名称、key 和非密配置。
- BR8: quote-api 部署不得提前暴露公网入口。

## Acceptance Criteria

- AC1: `kubectl kustomize apps/quote-api/overlays/lendora-sta` 和 `kubectl kustomize clusters/lendora-sta` 通过。
- AC2: business-repo 能构建 quote-api 镜像，且 GitOps image release/promotion 路径包含 quote-api。
- AC3: lendora-sta 中 quote-api Argo CD Application Healthy/Synced。
- AC4: `kubectl -n lendora-sta-quote-api get deploy,svc quote-api` 可见，Pod Ready。
- AC5: `quote-api /ready` 返回 READY，并在 quote DB 不可用时失败。
- AC6: 调用 `POST /api/v1/pricing/quotes` 能返回 quoteId，并能从 quote DB 验证写入。
- AC7: Consul 可发现 `quote-api` 服务，服务地址为集群内可达地址。
- AC8: 运行时 smoke 证据记录部署 commit、镜像 digest、ready、DB 写入和服务发现结果。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| quote DB 是否独立 PostgreSQL 实例还是复用 lendora-sta PostgreSQL 并创建独立 database？ | core | 2026-06-28 | resolved: 当前 STA 先复用现有 PostgreSQL 实例，使用独立 `quote` database/user；长期 operator 不在本票 |
| fides-bff 是否必须在本票联调 pricing facade？ | core | 2026-06-28 | resolved: 不需要；本票只保证 quote-api 可被发现和直接 smoke，BFF facade 属于 LEN-132 |
| quote-api 是否需要 gRPC 端口？ | core | 2026-06-28 | resolved: LEN-10 使用 HTTP/JDBC 边界，本票只暴露 HTTP |

## Notes

- LEN-131 依赖 LEN-10 已合并的 quote-api 服务代码。
- 当前集群为 vincent-k3s，lendora-sta 由 Argo CD app-of-apps 管理。
- Consul 注册必须遵守当前 service-DNS-based 发现口径。
