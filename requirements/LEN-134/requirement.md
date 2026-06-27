---
requirement_id: "LEN-134"
owner: "core"
status: "approved"
created_at: "2026-06-28"
related_branch: "feature/LEN-134-origination-api-deploy"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
  - gitops-repo
approved_by: "forest"
approved_at: "2026-06-28T04:47:07+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-134 origination-api lendora-sta 部署需求和影响分析，范围限定为 origination-api 镜像、GitOps 部署、application DB、readiness、k8s/Consul 服务发现和 runtime smoke，不包含 BFF facade、下游配置或前端接入。"
---

# origination-api lendora-sta 部署

## Background

LEN-9 已交付 `origination-api` 申请草稿服务、application DB migration、幂等和 Quote 校验能力，但服务尚未部署到 lendora-sta。后续 LEN-133 BFF facade、LEN-11 前端 Continue 静默保存和 LEN-5 Story 验收都依赖一个可访问、可写 application DB、可被服务发现的运行时服务。

这条需求不是什么：它不是实现 origination 业务逻辑，不是实现 `fides-bff` loan application facade，也不是前端真实 API 接入。

它是什么：它补齐 `origination-api` 的镜像构建入口、lendora-sta GitOps 资产、application DB 运行配置、readiness、k8s Service 和 Consul 可发现性，并用运行时 smoke 验证 draft 创建、读取和 DB 写入。

## Goals

- 为 `business-repo/apps/origination-api` 增加可发布镜像构建入口。
- 为 `origination-api` 补齐 Consul runtime registration，使服务可被后续 BFF 通过 Consul 发现。
- 在 `gitops-repo` 新增 `apps/origination-api/base` 和 `overlays/lendora-sta`。
- 在 lendora-sta app-of-apps 中纳入 origination-api Argo CD Application 和 namespace。
- 为 origination-api 提供独立 application DB 连接配置和 Secret 引用。
- 部署后验证 `/ready` 返回 READY，且 application DB 写入和读取可用。
- 验证 k8s Service 和 Consul 都能发现 `origination-api`。
- 保持部署由 GitOps 驱动，不依赖手工 `kubectl apply` 维护目标状态。

## Non-Goals

- 不修改 protobuf IDL 或生成契约。
- 不改变 LEN-9 的草稿创建、读取、PATCH、幂等、Quote 校验和持久化业务规则。
- 不实现 `fides-bff` loan application create/get/patch facade；LEN-133 负责。
- 不实现 `fides-bff` quote/origination 下游配置；LEN-135 负责。
- 不实现前端贷款请求屏 Continue 静默保存；LEN-11 负责。
- 不设计长期数据库 operator、ExternalSecret 或生产级多副本 PostgreSQL。
- 不把 application 表放进 quote-api 或 applicant-api 业务库。
- 不新增公网入口。

## User / Business Scenarios

### Scenario 1: origination-api 运行时就绪

Given: lendora-sta 已同步 origination-api GitOps Application。

When: 运维或后续服务访问 `origination-api` `/ready`。

Then: origination-api 返回 READY，Pod Ready，且 readiness 包含 application DB 和 Consul 注册状态。

### Scenario 2: 申请草稿写入和读取

Given: 已认证请求携带 `x-applicant-id`，并提供属于同一 applicant 的有效 `quoteId`。

When: 请求调用 `POST /api/v1/loan-applications` 创建草稿，再调用 `GET /api/v1/loan-applications/{applicationId}` 读取。

Then: origination-api 返回 draft applicationId，application DB 写入 loan application 和幂等记录，并能读取同一草稿用于回填。

### Scenario 3: 服务发现可用

Given: origination-api 已部署并注册。

When: 从集群内查询 k8s Service 或 Consul catalog/health。

Then: `origination-api` 可通过 `origination-api.lendora-sta-origination-api.svc.cluster.local` 和 Consul 服务名发现。

### Scenario 4: application DB 不可用时阻断流量

Given: application DB 不可用或 origination-api 无法连接 DB。

When: Kubernetes 或 Consul health check 访问 `/ready`。

Then: readiness 失败，服务不应被视为可接收流量。

## Business Rules

- BR1: origination-api 必须部署在独立 namespace `lendora-sta-origination-api`。
- BR2: application DB 配置必须使用 origination-api 专属 database/schema 和 Secret 引用，不复用 quote-api/applicant-api runtime Secret。
- BR3: origination-api 镜像必须由 business-repo Dockerfile 构建，并在 GitOps overlay 中使用不可变 digest 或明确的 release 输入更新。
- BR4: `/ready` 必须覆盖 application DB 连接可用性。
- BR5: Consul 注册地址必须使用集群内可达 Service DNS，不能注册 Pod 内 `127.0.0.1`。
- BR6: GitOps 目标状态必须能通过 `kubectl kustomize` 渲染，并由 Argo CD Application 管理。
- BR7: Secret 值不得提交到仓库；仓库只保存 Secret 名称、key 和非密配置。
- BR8: origination-api 部署不得提前暴露公网入口。
- BR9: origination-api 调用 quote-api 时必须使用集群内可达 quote-api 地址，并继续传播 `x-applicant-id` 与 trace headers。

## Acceptance Criteria

- AC1: `kubectl kustomize apps/origination-api/overlays/lendora-sta`、`kubectl kustomize apps/lendora-sta-dependencies/overlays/sta` 和 `kubectl kustomize clusters/lendora-sta` 通过。
- AC2: business-repo 能构建 origination-api 镜像，且 GitOps image release/promotion 路径包含 origination-api。
- AC3: lendora-sta 中 origination-api Argo CD Application Healthy/Synced；若当前集群缺少 Argo CD，必须记录环境 WARN，不得伪造通过。
- AC4: `kubectl -n lendora-sta-origination-api get deploy,svc origination-api` 可见，Pod Ready。
- AC5: `origination-api /ready` 返回 READY，并在 application DB 或 Consul 注册不可用时失败。
- AC6: 调用 `POST /api/v1/loan-applications` 能返回 applicationId，并能从 application DB 验证 loan application 和 idempotency 记录。
- AC7: 调用 `GET /api/v1/loan-applications/{applicationId}` 能读取同一草稿。
- AC8: Consul 可发现 `origination-api` 服务，服务地址为集群内可达地址。
- AC9: 运行时 smoke 证据记录部署 commit、镜像 digest、ready、draft 写入/读取、DB 写入和服务发现结果。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| application DB 是否独立 PostgreSQL 实例还是复用 lendora-sta PostgreSQL 并创建独立 database？ | core | 2026-06-28 | resolved: 当前 STA 先复用现有 PostgreSQL 实例，使用独立 `origination` database/user；长期 operator 不在本票 |
| fides-bff 是否必须在本票联调 loan application facade？ | core | 2026-06-28 | resolved: 不需要；本票只保证 origination-api 可被发现和直接 smoke，BFF facade 属于 LEN-133 |
| origination-api 是否需要 gRPC 端口？ | core | 2026-06-28 | resolved: LEN-9 使用 HTTP/JDBC 边界，本票只暴露 HTTP |

## Notes

- LEN-134 依赖 LEN-9 已合并的 origination-api 服务代码。
- 当前集群为 vincent-k3s，lendora-sta 采用 Argo CD app-of-apps 目标结构；若集群缺少 Argo CD，只能用 WARN 记录环境缺口。
- Consul 注册必须遵守当前 service-DNS-based 发现口径。
