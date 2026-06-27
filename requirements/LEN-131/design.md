---
requirement_id: "LEN-131"
owner: "core"
status: "approved"
updated_at: "2026-06-28"
approved_by: "forest"
approved_at: "2026-06-28T02:35:00+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-131 设计，采用 business-repo quote-api Dockerfile/Consul runtime 支撑和 gitops-repo lendora-sta Application/overlay/DB/服务发现方案。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| BR1, AC3, AC4 | D1: 新增 `lendora-sta-quote-api` namespace 和 Argo CD Application | 与 applicant-api/fides-bff 的 app-of-apps 模式一致 |
| BR2, AC5, AC6 | D2: quote-api 使用独立 `quote` database/user 和 runtime Secret 引用 | 不复用 applicant-api DB secret |
| BR3, AC2 | D3: 增加 quote-api Dockerfile，并把 image release workflow 纳入 quote-api build/scan/promotion | overlay 使用 digest |
| BR4, AC5 | D4: `/ready` 保留 DB probe，并把 Consul 注册状态作为可选 runtime probe | DB 不可用时 readiness 失败 |
| BR5, AC7 | D5: quote-api 运行时注册 Consul，address 使用 k8s Service DNS | 不注册 127.0.0.1 |
| BR6, AC1, AC8 | D6: GitOps overlay 和 cluster app-of-apps 都必须可渲染，并记录 smoke evidence | 所有部署目标状态在 gitops-repo |
| BR7, BR8 | D7: 只提交 Secret 引用和内网 Service，不提交真实 secret，不暴露公网入口 | fides-bff facade 后续接入 |

## Summary

LEN-131 交付 quote-api 的运行时部署面。business-repo 提供镜像和最小 Consul 注册能力；gitops-repo 提供 lendora-sta 目标状态；Harness 记录验证证据和门禁。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| quote-api | Dockerfile、Consul runtime registration、runtime config docs/tests | 让服务可部署、可发现、可验证 |
| quote-api GitOps app | Deployment、Service、ConfigMap、Secret 引用、overlay、Argo CD Application | 在 lendora-sta 运行 |
| image release workflow | 构建、扫描、promote quote-api image digest | 保证 GitOps overlay 引用可发布镜像 |

## API / Contract Design

- Protobuf IDL required: no.
- Proto files: none.
- Generated outputs: none.
- HTTP runtime endpoints:
  - `GET /health`
  - `GET /ready`
  - `POST /api/v1/pricing/quotes`
- Service discovery:
  - Kubernetes DNS: `quote-api.lendora-sta-quote-api.svc.cluster.local`
  - Consul service name: `quote-api`
  - Consul health check: `http://quote-api.lendora-sta-quote-api.svc.cluster.local:80/ready`

## Application Design

### business-repo

- 新增 `apps/quote-api/Dockerfile`，结构对齐 applicant-api：
  - 先构建并安装同分支 `packages/java/spring-starter`。
  - 再构建 `apps/quote-api` Spring Boot jar。
  - 运行镜像使用 JRE 21，非 root 用户。
- quote-api 新增 Consul runtime registration：
  - 属性挂在 `spark.quote.consul.*`。
  - enabled=true 时启动注册到 `/v1/agent/service/register`。
  - 注册 address 使用配置值。
  - health check URL 可显式配置。
  - 注册成功状态作为 `/ready` dependency 之一。
- quote-api profile/config：
  - local 默认可以关闭 Consul 或使用 localhost。
  - sta/prod 通过环境变量或 Consul config 设置非密配置。

### gitops-repo

- 新增 `apps/quote-api/base`：
  - `deployment.yaml`
  - `service.yaml`
  - `configmap.yaml`
  - `consul-config.yaml`
  - `networkpolicy.yaml`
  - `kustomization.yaml`
- 新增 `apps/quote-api/overlays/lendora-sta`：
  - namespace `lendora-sta-quote-api`
  - image digest placeholder/update target
  - replica count
- 新增 `clusters/lendora-sta/argocd-apps/quote-api.yaml` 并加入 cluster kustomization。
- 更新 `clusters/lendora-sta/namespaces.yaml` 增加 quote-api namespace。
- 更新 image release workflow：
  - build quote-api
  - scan quote-api
  - update `apps/quote-api/overlays/lendora-sta/kustomization.yaml`
  - validate quote-api render

## Data / Config / Permission

- Data:
  - 使用 lendora-sta PostgreSQL 实例中的 `quote` database/user。
  - Quote 表由 quote-api Flyway migration 创建。
- Config:
  - `QUOTE_JDBC_URL`
  - `QUOTE_JDBC_USERNAME`
  - `QUOTE_JDBC_PASSWORD`
  - `SPARK_QUOTE_CONSUL_ENABLED`
  - `SPARK_QUOTE_CONSUL_URL`
  - `SPARK_QUOTE_CONSUL_SERVICE_ADDRESS`
  - `SPARK_QUOTE_CONSUL_HEALTH_CHECK_URL`
  - OTEL traces endpoint/header。
- Permission:
  - Service 仅 ClusterIP。
  - 不新增公网 Ingress。
  - Secret 只通过 Kubernetes Secret 引用。

## Observability

- Logs:
  - 不输出 JDBC password、Authorization、OTLP header。
- Metrics:
  - 保留 actuator/OTel 默认指标。
- Tracing:
  - `otel.service.name=quote-api`。
  - 使用 W3C traceparent。
- Events:
  - 不新增事件。

## Testing Strategy

- business-repo:
  - quote-api unit/integration tests。
  - Consul registration request test。
  - Dockerfile build 或等价 Argo image release evidence。
- gitops-repo:
  - `kubectl kustomize apps/quote-api/overlays/lendora-sta`。
  - `kubectl kustomize clusters/lendora-sta`。
  - server-side dry-run when applicable。
- runtime:
  - Argo CD Application Healthy/Synced。
  - Pod Ready。
  - `/ready` returns READY。
  - pricing quote smoke returns quoteId。
  - DB query confirms quote row.
  - Consul catalog/health confirms quote-api.

## Rollout And Rollback

- Rollout:
  - Merge business-repo and gitops-repo changes.
  - Build/promote quote-api image digest.
  - Sync quote-api Application in lendora-sta.
  - Run runtime smoke and record evidence.
- Rollback:
  - Revert GitOps quote-api Application or overlay digest.
  - Scale quote-api Deployment to zero for emergency stop.
  - Keep quote DB schema; no destructive data rollback.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Existing PostgreSQL only initializes one database | Add explicit bootstrap evidence or init job for quote database/user | core |
| Secret bootstrap not managed by Git | Record required Secret name/key and live verification; future ExternalSecret ticket can replace it | core |
| Consul registration succeeds but address is wrong | Register Service DNS and verify from in-cluster consumer | core |
| Image release workflow grows slow | Keep quote-api as parallel build/scan task | core |
