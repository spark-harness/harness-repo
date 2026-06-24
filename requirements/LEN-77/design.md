---
requirement_id: "LEN-77"
owner: "Codex"
status: "approved"
updated_at: "2026-06-23"
approved_by: "forest"
approved_at: "2026-06-23T19:56:08+08:00"
decision: "批准 LEN-77 生产化部署设计，按当前范围进入任务拆分和实现。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, AC1, AC2 | D1: 在 `gitops-repo` 建立 Lendora STA app-of-apps、namespace 和 Argo CD Application 入口 | 覆盖 `LEN-78` |
| R2, AC3, AC4 | D2: 在 `business-repo` 提供三服务生产 Dockerfile，并在 `gitops-repo` 接入 image release digest promotion | 覆盖 `LEN-79` |
| R3, AC5, AC6 | D3: 在 `gitops-repo` 管理 PostgreSQL、Redis、Consul 独立 namespace、PVC、ClusterIP、Secret 引用、资源和健康检查 | 覆盖 `LEN-80` |
| R4, AC7, AC11 | D4: applicant-api 只暴露 ClusterIP 和内网 gRPC/HTTP readiness，使用 NetworkPolicy 限制 fides-bff 访问 | 覆盖 `LEN-81` |
| R5, AC8 | D5: fides-bff 通过公网 API route 暴露 REST，对内使用 Consul 发现 applicant-api，并限制 CORS 来源 | 覆盖 `LEN-82` |
| R6, AC9, AC10 | D6: fides 前端作为公网 HTTPS 入口，运行配置指向 STA BFF | 覆盖 `LEN-83` |
| R7, AC10, AC11, AC12, AC13, AC14 | D7: 增加 smoke、回滚、日志 / 指标 / trace 和公网不可达证据脚本与 evidence 记录 | 覆盖 `LEN-84` |

## Summary

设计以 GitOps 为 runtime 事实源，按依赖优先顺序交付：基础 namespace 和 app-of-apps -> 依赖 -> applicant-api -> fides-bff -> fides -> smoke / 回滚证据。业务服务代码只补生产化运行所需的 Dockerfile、配置入口和测试，不做非阻塞重构。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| applicant-api | 新增生产镜像构建入口和 STA GitOps overlay，部署为内网身份服务 | 支撑 OTP 和 Applicant 身份 |
| fides-bff | 新增生产镜像构建入口和 STA GitOps overlay，部署为公网 API 边界 | 前端不直接接触 applicant-api |
| fides | 新增生产镜像构建入口和 STA GitOps overlay，部署公网 HTTPS 入口 | 用户访问入口 |
| PostgreSQL | 新增 STA GitOps 资源 | applicant-api 持久化 |
| Redis | 新增 STA GitOps 资源 | OTP、幂等、token store |
| Consul | 新增 STA GitOps 资源 | 复用当前服务发现实现 |

## API / Contract Design

- Protobuf IDL required: No new IDL.
- Proto files: no change.
- Buf module: `local/lendora-applicant` reused.
- Generated outputs: no change.
- Breaking check baseline: not applicable.
- Compatibility strategy: runtime deployment consumes existing applicant-api contract.

## Application Design

### D1: Lendora STA GitOps Entry

在 `gitops-repo` 中新增 Lendora STA 环境入口：

- `clusters/lendora-sta/` 作为 app-of-apps 入口。
- 每个依赖和服务使用独立 namespace，例如 `lendora-sta-postgres`、`lendora-sta-redis`、`lendora-sta-consul`、`lendora-sta-applicant-api`、`lendora-sta-fides-bff`、`lendora-sta-fides`。
- 每个 app 使用单独 Argo CD Application，便于同步和回滚。
- labels 使用 `app.kubernetes.io/part-of: lendora` 和 `lendora.io/environment: sta`。

### D2: Image Release And Digest Promotion

三服务在 `business-repo` 保留生产 Dockerfile：

- applicant-api：Maven 构建 Spring Boot jar，运行时使用 JRE 镜像。
- fides-bff：Go 多阶段构建静态或最小运行镜像。
- fides：Next.js standalone 构建，运行时通过环境变量指向 BFF。

GitOps overlay 的 `images[].digest` 是部署事实源。初始 digest 可使用占位值，真实发布后由 image release workflow 或人工 promotion commit 更新。

### D3: Runtime Dependencies

依赖资源放入 `gitops-repo/apps/lendora-sta-dependencies/`：

- PostgreSQL：StatefulSet、PVC、ClusterIP Service、readiness/liveness、resource requests/limits、Secret 引用。
- Redis：StatefulSet、PVC、ClusterIP Service、readiness/liveness、resource requests/limits、Secret 引用。
- Consul：StatefulSet 或 Deployment、PVC、ClusterIP Service、readiness/liveness、resource requests/limits。

Secret 值不进入 Git。GitOps 只声明 secret 名称、key 约定和 bootstrap 文档。

### D4: applicant-api Internal Service

applicant-api overlay 设置：

- Spring `prod` profile。
- PostgreSQL、Redis、Consul env var 从 Secret / ConfigMap 注入。
- HTTP readiness/liveness 和 gRPC 业务端口。
- ClusterIP Service，不创建 Ingress。
- NetworkPolicy 只允许 fides-bff namespace 访问业务端口，允许 kubelet/ingress controller 必要健康检查。

### D5: fides-bff Public API Boundary

fides-bff overlay 设置：

- HTTP `/api/v1` 公网 route。
- applicant-api 使用内网发现地址。
- CORS 只允许 Lendora 前端域名。
- 健康检查和资源限制。
- applicant-api 不可用时返回统一错误信封，不暴露内部服务名或堆栈。

### D6: fides Public Frontend

fides overlay 设置：

- 公网 HTTPS route。
- 环境变量配置真实 STA BFF base URL。
- 页面错误提示保持用户可理解，不暴露内部服务信息。

### D7: Evidence And Smoke

证据分三层：

- 静态：`kubectl kustomize` 或 `kustomize build` 渲染 Lendora STA GitOps。
- 服务：applicant-api Maven 测试、fides-bff Go 测试、fides 前端依赖门禁和测试。
- 运行时：公网前端 OTP smoke、applicant-api 公网不可达探测、日志 / trace 敏感字段检查、任一服务 digest 回滚演练。

## Data / Config / Permission

- Data model: no new business schema beyond existing applicant-api migrations.
- Config: image digest, BFF URL, CORS origin, PostgreSQL / Redis / Consul addresses, Secret names, OTEL endpoint.
- Permission: namespace-scoped service accounts, registry pull secret, network policies.
- Secret: values stay outside Git.

## Observability

- Logs: service logs and smoke logs must not contain手机号、OTP、token、applicantId。
- Metrics: readiness, dependency health and request success/failure signals.
- Tracing: preserve W3C trace context where current frontend/BFF/applicant-api implementation supports it.
- Evidence: runtime checks are written under `requirements/LEN-77/evidence/`.

## Testing Strategy

- Harness:
  - `janus requirement status LEN-77`
  - `janus requirement verify --requirement LEN-77 --target merge`
- GitOps:
  - `kubectl kustomize clusters/lendora-sta`
  - `kubectl kustomize apps/lendora-sta-dependencies/overlays/sta`
  - `kubectl kustomize apps/applicant-api/overlays/lendora-sta`
  - `kubectl kustomize apps/fides-bff/overlays/lendora-sta`
  - `kubectl kustomize apps/fides/overlays/lendora-sta`
- Business:
  - `mvn test` in `services/backend/applicant-api`
  - `go test ./...` in `services/backend/fides-bff`
  - `pnpm lint:deps` and `pnpm test` in `services/frontend/fides`
- Runtime when cluster is reachable:
  - `kubectl --kubeconfig ~/.kube/wsl.yaml get ...`
  - E2E OTP smoke from public fides URL.
  - applicant-api public reachability negative test.
  - digest rollback exercise.

## Rollout And Rollback

- Rollout:
  - Apply/sync namespaces and dependencies.
  - Publish and promote applicant-api digest, then sync applicant-api.
  - Publish and promote fides-bff digest, then sync fides-bff.
  - Publish and promote fides digest, then sync fides.
  - Run smoke and evidence collection.
- Rollback:
  - Revert selected service overlay digest to previous known-good digest.
  - Sync Argo CD app.
  - Verify readiness and rerun smoke.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| kubeconfig 当前不可连接 API server | 先完成 GitOps 和本地渲染；集群恢复后补 smoke / rollback evidence | Forest |
| Secret 方案未定 | 只提交引用和 bootstrap 文档，不提交值 | Forest |
| Consul 后续可能被 Kubernetes DNS 替代 | 当前保留 Consul，后续优化票处理 | Forest |
| 镜像 digest 初始为空 | overlay 使用占位 digest，真实发布后 promotion 更新 | Codex |
