---
requirement_id: "LEN-131"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-28"
idl_impact: "no"
idl_impact_reason: "本需求只新增 quote-api runtime 部署、镜像和服务发现配置，不修改 protobuf IDL、generated contracts 或 Buf 配置。"
approved_by: "forest"
approved_at: "2026-06-28T02:35:00+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-131 impact-analysis 和 service-repo-check，涉及 harness-repo、business-repo、gitops-repo，IDL 无影响。"
---

# Impact Analysis

## Summary

LEN-131 将 LEN-10 的 quote-api 部署到 lendora-sta，补齐镜像构建、GitOps Application、quote DB runtime、readiness 和服务发现验证。

## Affected Domains

- Pricing runtime：quote-api 从代码能力变成 lendora-sta 可运行服务。
- GitOps delivery：新增 quote-api app、namespace、Argo CD Application、image promotion。
- Runtime storage：新增 quote DB database/user/Secret 引用。

## Affected Services

| Service / Module | Repo | Reason | Protobuf Required |
|---|---|---|---|
| quote-api | business-repo | 增加 Dockerfile、运行时 Consul 注册能力和部署配置支持 | no |
| quote-api GitOps app | gitops-repo | 新增 base、lendora-sta overlay、Argo CD Application、namespace 和 image promotion | no |
| lendora-sta dependencies | gitops-repo | 复用现有 PostgreSQL 实例，补充 quote database/user bootstrap 或 init 配置 | no |
| Harness LEN-131 lifecycle | harness-repo | 保存需求、影响分析、设计、任务、门禁和证据 | no |

## Upstream / Downstream Consumers

- Upstream:
  - 本票直接 smoke quote-api HTTP endpoint。
  - LEN-132 后续由 `fides-bff` 调用 quote-api。
- Downstream:
  - lendora-sta PostgreSQL quote database。
  - lendora-sta Consul，用于服务发现。
  - Kubernetes Service，用于集群内 DNS 发现。

## API / Contract Impact

- External contract: 不新增 BFF 对外契约。
- quote-api service HTTP endpoint: 复用 LEN-10 已交付的 `/health`、`/ready`、`/api/v1/pricing/quotes` 和内部 Quote 读取边界。
- Protobuf IDL: no changes.
- Generated contracts: no changes.
- Compatibility risk: 无现有 quote-api runtime 消费者；LEN-132 后续按服务发现接入。

## Data Impact

- 需要 quote-api 专属 database/user 或 schema。
- Quote 表仍由 quote-api Flyway migration 创建。
- 不迁移 applicant-api 数据，不写 applicant DB。
- Secret 值不进入 Git；GitOps 只引用 Secret name/key。

## Config / Permission / Observability Impact

- Config:
  - 新增 quote-api ConfigMap。
  - 新增 quote-api runtime Secret 引用。
  - 配置 quote JDBC URL、username、password、Consul URL、service address、health check URL、OTLP traces endpoint/header。
- Permission:
  - 不新增公网访问。
  - quote-api 仍依赖 LEN-22 `x-applicant-id` principal。
  - 如现有 NetworkPolicy 阻断访问，需要允许 fides-bff namespace 后续访问；本票至少保证 smoke 和 health path 可验证。
- Logs:
  - 不记录 token、JDBC password、OTLP header 或 applicant 敏感信息。
- Tracing:
  - `service.name=quote-api`。
  - 保留 traceparent 传播能力。
- Metrics:
  - 不新增业务指标门禁；保留 actuator/OTel 默认观测。
- Events:
  - 不新增事件。

## Rollout And Rollback

- Rollout:
  - 合入 business-repo quote-api Dockerfile/runtime 支撑。
  - 合入 gitops-repo quote-api app、namespace、Application 和 image promotion。
  - 触发或执行 image release，更新 lendora-sta overlay digest。
  - Argo CD 同步 quote-api Application。
  - 执行 runtime smoke。
- Rollback:
  - 回滚 quote-api Argo CD Application 或 overlay digest 到上一版本。
  - 如只需止血，可缩容 quote-api Deployment。
  - quote DB schema 保留；不做破坏性数据回滚。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| quote-api 未注册 Consul | LEN-132 无法通过服务发现调用 | 在 quote-api runtime 增加 Consul 注册并用 runtime smoke 验证 | core |
| quote DB Secret 缺失 | Pod 无法 Ready | 在 evidence 记录 bootstrap 命令和 Secret key；不提交真实值 | core |
| image promotion 未包含 quote-api | GitOps 无法部署最新镜像 | 更新 image release workflow 和 lendora-sta runtime 文档 | core |
| readiness 未覆盖 DB | 服务不可写但被接流量 | `/ready` 继续依赖 RuntimeDependencyProbe DB check | core |
| Consul 注册不可达地址 | 容器间发现后调用失败 | 使用 Service DNS 注册 address 和 health check URL | core |
