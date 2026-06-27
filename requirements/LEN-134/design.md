---
requirement_id: "LEN-134"
owner: "core"
status: "approved"
updated_at: "2026-06-28"
approved_by: "forest"
approved_at: "2026-06-28T04:48:48+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-134 设计，采用 business-repo origination-api Dockerfile/Consul runtime 支撑和 gitops-repo lendora-sta Application/overlay/application DB/服务发现方案。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| BR1, AC3, AC4 | D1: 新增 `lendora-sta-origination-api` namespace 和 Argo CD Application | 与 quote-api 的 app-of-apps 模式一致 |
| BR2, AC5, AC6, AC7 | D2: origination-api 使用独立 `origination` database/user 和 runtime Secret 引用 | 不复用 quote-api/applicant-api DB secret |
| BR3, AC2 | D3: 增加 origination-api Dockerfile，并把 image release workflow 纳入 origination-api build/scan/promotion | overlay 使用 digest |
| BR4, AC5 | D4: `/ready` 覆盖 application DB probe 和 Consul registration probe | DB 或 Consul 不可用时 readiness 失败 |
| BR5, AC8 | D5: origination-api 运行时注册 Consul，address 使用 k8s Service DNS | 不注册 127.0.0.1 |
| BR6, AC1, AC9 | D6: GitOps overlay 和 cluster app-of-apps 都必须可渲染，并记录 smoke evidence | 所有部署目标状态在 gitops-repo |
| BR7, BR8 | D7: 只提交 Secret 引用和内网 Service，不提交真实 secret，不暴露公网入口 | BFF facade 后续接入 |
| BR9, AC6, AC7 | D8: origination-api 配置 quote-api Service DNS 下游地址 | 继续传播 applicant principal 和 trace headers |

## Summary

LEN-134 交付 origination-api 的运行时部署面。business-repo 提供镜像和最小 Consul 注册能力；gitops-repo 提供 lendora-sta 目标状态、application DB bootstrap 和 image promotion；Harness 记录验证证据和门禁。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| origination-api | Dockerfile、Consul runtime registration、runtime config tests | 让服务可部署、可发现、可验证 |
| origination-api GitOps app | Deployment、Service、ConfigMap、Secret 引用、overlay、Argo CD Application | 在 lendora-sta 运行 |
| lendora-sta dependencies | origination database/user bootstrap job | 给 application DB 提供独立 database 和 user |
| image release workflow | 构建、扫描、promote origination-api image digest | 保证 GitOps overlay 引用可发布镜像 |

## API / Contract Design

- Protobuf IDL required: no.
- Proto files: none.
- Generated outputs: none.
- HTTP runtime endpoints:
  - `GET /health`
  - `GET /ready`
  - `POST /api/v1/loan-applications`
  - `GET /api/v1/loan-applications/{applicationId}`
  - `PATCH /api/v1/loan-applications/{applicationId}`
- Service discovery:
  - Kubernetes DNS: `origination-api.lendora-sta-origination-api.svc.cluster.local`
  - Consul service name: `origination-api`
  - Consul health check: `http://origination-api.lendora-sta-origination-api.svc.cluster.local:80/ready`

## Application Design

### business-repo

- 新增 `apps/origination-api/Dockerfile`，结构对齐 quote-api：
  - 先构建并安装同分支 `packages/java/spring-starter`。
  - 再构建 `apps/origination-api` Spring Boot jar。
  - 运行镜像使用 JRE 21，非 root 用户。
- origination-api 新增 Consul runtime registration：
  - 属性挂在 `spark.origination.consul.*`。
  - enabled=true 时启动注册到 `/v1/agent/service/register`。
  - 注册 address 使用配置值。
  - health check URL 可显式配置。
  - 注册成功状态作为 `/ready` dependency 之一。
- `HealthHttpAdapter` 改为聚合多个 `RuntimeDependencyProbe`：
  - `postgresql` probe 来自 application DB。
  - `consul` probe 只在 Consul registration bean 启用时存在。
  - 返回体包含 `service=origination-api` 和 dependency 状态，便于 smoke 记录。

### gitops-repo

- 新增 `apps/origination-api/base`：
  - `deployment.yaml`
  - `service.yaml`
  - `configmap.yaml`
  - `consul-config.yaml`
  - `networkpolicy.yaml`
  - `kustomization.yaml`
- 新增 `apps/origination-api/overlays/lendora-sta`：
  - namespace `lendora-sta-origination-api`
  - image digest placeholder/update target
  - replica count
- 新增 `clusters/lendora-sta/argocd-apps/origination-api.yaml` 并加入 cluster kustomization。
- 更新 `clusters/lendora-sta/namespaces.yaml` 增加 origination-api namespace，并让 `lendora-sta-fides-bff` 具备 `lendora.io/origination-api-client=true`。
- 更新 `clusters/lendora-sta/argocd-project.yaml` 允许 origination namespace。
- 更新 `apps/lendora-sta-dependencies/base` 增加 `origination-postgres-init` job。
- 更新 image release workflow：
  - build origination-api
  - scan origination-api
  - update `apps/origination-api/overlays/lendora-sta/kustomization.yaml`
  - validate origination-api render

## Data / Config / Permission

- Data:
  - 使用 lendora-sta PostgreSQL 实例中的 `origination` database/user。
  - LoanApplication 和 idempotency 表由 origination-api Flyway migration 创建。
- Config:
  - `ORIGINATION_JDBC_URL`
  - `ORIGINATION_JDBC_USERNAME`
  - `ORIGINATION_JDBC_PASSWORD`
  - `ORIGINATION_QUOTE_API_BASE_URL`
  - `ORIGINATION_QUOTE_API_TIMEOUT`
  - `SPARK_ORIGINATION_CONSUL_ENABLED`
  - `SPARK_ORIGINATION_CONSUL_URL`
  - `SPARK_ORIGINATION_CONSUL_SERVICE_NAME`
  - `SPARK_ORIGINATION_CONSUL_SERVICE_ADDRESS`
  - `SPARK_ORIGINATION_CONSUL_HEALTH_CHECK_URL`
  - OTEL traces endpoint/header。
- Permission:
  - Service 仅 ClusterIP。
  - 不新增公网 Ingress。
  - Secret 只通过 Kubernetes Secret 引用。
  - NetworkPolicy 允许 `lendora.io/origination-api-client=true` namespace 和 Consul namespace 访问。

## Observability

- Logs:
  - 不输出 JDBC password、Authorization、OTLP header、申请内容或 quote snapshot 明细。
- Metrics:
  - 保留 actuator/OTel 默认指标。
- Tracing:
  - `otel.service.name=origination-api`。
  - 使用 W3C traceparent，并继续向 quote-api 转发 `traceparent` / `tracestate`。
- Events:
  - 不新增事件。

## Testing Strategy

- business-repo:
  - origination-api unit/integration tests。
  - Consul registration request test。
  - Java quality project `origination-api`。
  - Dockerfile build 或等价 image release evidence。
- gitops-repo:
  - `kubectl kustomize apps/origination-api/overlays/lendora-sta`。
  - `kubectl kustomize apps/lendora-sta-dependencies/overlays/sta`。
  - `kubectl kustomize clusters/lendora-sta`。
  - server-side dry-run when applicable。
- runtime:
  - Argo CD Application Healthy/Synced，若当前集群无 Argo CD 则记录 WARN。
  - Pod Ready。
  - `/ready` returns READY。
  - loan application create returns applicationId。
  - loan application get returns same draft。
  - DB query confirms loan application and idempotency rows.
  - Consul catalog/health confirms origination-api.

## Rollout And Rollback

- Rollout:
  - Merge business-repo and gitops-repo changes.
  - Build/promote origination-api image digest.
  - Sync origination-api Application in lendora-sta.
  - Run runtime smoke and record evidence.
- Rollback:
  - Revert GitOps origination-api Application or overlay digest.
  - Scale origination-api Deployment to zero for emergency stop.
  - Keep application DB schema; no destructive data rollback.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Existing PostgreSQL only initializes one database | Add explicit bootstrap evidence or init job for origination database/user | core |
| Secret bootstrap not managed by Git | Record required Secret name/key and live verification; future ExternalSecret ticket can replace it | core |
| Consul registration succeeds but address is wrong | Register Service DNS and verify from in-cluster consumer | core |
| quote-api unavailable during smoke | Verify quote-api ready and use quote-api Service DNS | core |
| Argo CD unavailable in vincent-k3s | Record WARN instead of claiming Healthy/Synced | platform/gitops |
