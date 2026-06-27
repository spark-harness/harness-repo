---
requirement_id: "LEN-134"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-28"
idl_impact: "no"
idl_impact_reason: "本需求只新增 origination-api runtime 部署、镜像、application DB bootstrap 和服务发现配置，不修改 protobuf IDL、generated contracts 或 Buf 配置。"
approved_by: "forest"
approved_at: "2026-06-28T04:48:48+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-134 impact-analysis 和 service-repo-check，涉及 harness-repo、business-repo、gitops-repo，IDL 无影响。"
---

# Impact Analysis

## Summary

LEN-134 将 LEN-9 的 origination-api 部署到 lendora-sta，补齐镜像构建、GitOps Application、application DB runtime、readiness 和服务发现验证。

## Affected Domains

- Applicant / Origination runtime：origination-api 从代码能力变成 lendora-sta 可运行服务。
- GitOps delivery：新增 origination-api app、namespace、Argo CD Application、image promotion。
- Runtime storage：新增 application DB database/user/Secret 引用。

## Affected Services

| Service / Module | Repo | Reason | Protobuf Required |
|---|---|---|---|
| origination-api | business-repo | 增加 Dockerfile、Consul 注册能力和部署配置支持 | no |
| origination-api GitOps app | gitops-repo | 新增 base、lendora-sta overlay、Argo CD Application、namespace 和 image promotion | no |
| lendora-sta dependencies | gitops-repo | 复用现有 PostgreSQL 实例，补充 origination database/user bootstrap 或 init 配置 | no |
| lendora-sta runtime docs | gitops-repo | 纳入 Secret bootstrap、image promotion 和 render 验证清单 | no |
| Harness LEN-134 lifecycle | harness-repo | 保存需求、影响分析、设计、任务、门禁和证据 | no |

## Upstream / Downstream Consumers

- Upstream:
  - 本票直接 smoke origination-api HTTP endpoint。
  - LEN-133 后续由 `fides-bff` 调用 origination-api。
- Downstream:
  - quote-api HTTP internal Quote 读取边界。
  - lendora-sta PostgreSQL origination database。
  - lendora-sta Consul，用于服务发现。
  - Kubernetes Service，用于集群内 DNS 发现。

## API / Contract Impact

- External contract: 不新增 BFF 对外契约。
- origination-api service HTTP endpoint: 复用 LEN-9 已交付的 `/health`、`/ready`、`POST /api/v1/loan-applications`、`GET /api/v1/loan-applications/{applicationId}`、`PATCH /api/v1/loan-applications/{applicationId}`。
- Protobuf IDL: no changes.
- Generated contracts: no changes.
- Compatibility risk: 无现有 origination-api runtime 消费者；LEN-133 后续按服务发现接入。

## Data Impact

- 需要 origination-api 专属 database/user 或 schema。
- LoanApplication、accepted quote snapshot 和 idempotency 表仍由 origination-api Flyway migration 创建。
- 不迁移 quote-api 或 applicant-api 数据，不写 quote/applicant DB。
- Secret 值不进入 Git；GitOps 只引用 Secret name/key。

## Config / Permission / Observability Impact

- Config:
  - 新增 origination-api ConfigMap。
  - 新增 origination-api runtime Secret 引用。
  - 配置 origination JDBC URL、username、password、quote-api base URL、quote-api timeout、Consul URL、service address、health check URL、OTLP traces endpoint/header。
- Permission:
  - 不新增公网访问。
  - origination-api 仍依赖 LEN-22 `x-applicant-id` principal。
  - NetworkPolicy 只允许标记为 origination-api client 的 namespace 和 Consul health check 访问。
- Logs:
  - 不记录 token、JDBC password、OTLP header、applicant 敏感信息或完整申请内容。
- Tracing:
  - `service.name=origination-api`。
  - 保留 `traceparent` / `tracestate` 到 quote-api 的传播能力。
- Metrics:
  - 不新增业务指标门禁；保留 actuator/OTel 默认观测。
- Events:
  - 不新增事件。

## Rollout And Rollback

- Rollout:
  - 合入 business-repo origination-api Dockerfile/runtime 支撑。
  - 合入 gitops-repo origination-api app、namespace、Application、DB init 和 image promotion。
  - 触发或执行 image release，更新 lendora-sta overlay digest。
  - Argo CD 同步 origination-api Application；若当前集群无 Argo CD，用渲染清单手工 apply 做 runtime smoke，并记录 WARN。
  - 执行 runtime smoke。
- Rollback:
  - 回滚 origination-api Argo CD Application 或 overlay digest 到上一版本。
  - 如只需止血，可缩容 origination-api Deployment。
  - application DB schema 保留；不做破坏性数据回滚。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| origination-api 未注册 Consul | LEN-133 无法通过服务发现调用 | 在 origination-api runtime 增加 Consul 注册并用 runtime smoke 验证 | core |
| application DB Secret 缺失 | Pod 无法 Ready | 在 evidence 记录 bootstrap 命令和 Secret key；不提交真实值 | core |
| image promotion 未包含 origination-api | GitOps 无法部署最新镜像 | 更新 image release workflow 和 lendora-sta runtime 文档 | core |
| readiness 未覆盖 DB 或 Consul | 服务不可写或不可发现但被接流量 | `/ready` 覆盖 DB probe 和 Consul registration probe | core |
| Consul 注册不可达地址 | BFF 发现后调用失败 | 使用 Service DNS 注册 address 和 health check URL | core |
| quote-api 下游不可达 | draft 创建 smoke 失败 | GitOps 配置使用 quote-api Service DNS；smoke 前验证 quote-api ready | core |
