---
requirement_id: "LEN-77"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-23"
approved_by: "forest"
approved_at: "2026-06-23T19:56:08+08:00"
decision: "批准 LEN-77 服务仓库检查，三仓同名分支已隔离，当前不修改 IDL。"
idl_impact: "no"
idl_impact_reason: "复用已存在 applicant-api protobuf 契约和生成契约，不修改 .proto。"
---

# Impact Analysis

## Summary

LEN-77 影响 Lendora STA runtime GitOps、三服务镜像发布、Kubernetes 部署、依赖资源、入口、NetworkPolicy、smoke、回滚和证据。它复用当前 applicant-api 契约，不修改 protobuf IDL。

## Affected Domains

- Runtime GitOps：Lendora STA app-of-apps、namespace、Kustomize overlay、Argo CD Application。
- 镜像发布：applicant-api、fides-bff、fides 的生产 Dockerfile、release workflow 参数和 digest promotion。
- 后端服务：applicant-api 内网身份服务、fides-bff 公网 API 边界。
- 前端服务：fides 公网前端入口和真实 BFF 配置。
- 运行依赖：PostgreSQL、Redis、Consul、Secret 引用、PVC、ClusterIP。
- Kubernetes 安全边界：Ingress、Service、NetworkPolicy、资源限制。
- 验收证据：E2E smoke、日志 / 指标 / trace 检查、回滚演练。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| applicant-api | `business-repo` / `gitops-repo` | 构建镜像并部署为内网身份服务 | Yes, reuse existing |
| fides-bff | `business-repo` / `gitops-repo` | 构建镜像并部署为公网 API 边界，内调 applicant-api | No |
| fides | `business-repo` / `gitops-repo` | 构建前端镜像并部署公网 HTTPS 入口 | No |
| PostgreSQL | `gitops-repo` | STA applicant 持久化依赖 | No |
| Redis | `gitops-repo` | OTP、幂等和 token runtime store | No |
| Consul | `gitops-repo` | 当前 applicant-api / fides-bff 服务发现依赖 | No |

## Upstream / Downstream Consumers

- 上游用户：公网 Lendora fides 前端用户。
- fides：调用 fides-bff REST `/api/v1/auth/*`。
- fides-bff：调用 applicant-api gRPC。
- applicant-api：依赖 PostgreSQL、Redis、Consul。
- GitOps / Argo CD：同步 Lendora STA 目标状态。
- Argo Workflows / image release：构建、扫描、推广 digest。

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: No protobuf source change.
- Contract repo: `idl-repo` is not edited.
- Proto files: existing `vesta/lendora/applicant/v1` only.
- Buf module: `local/lendora-applicant`.
- Buf config version: v2.
- Required buf checks: not required for source edits; smoke verifies generated-contract consumption.
- Breaking baseline: not applicable.
- Compatibility risk: deployment/runtime only; protobuf schema compatibility risk is unchanged.

## Generated Contract Impact

- Java generated contracts: reused by applicant-api.
- Go generated contracts: reused by fides-bff if current implementation already consumes them.
- No generated contract repo changes are planned.

## Data Impact

- Database schema: applicant-api existing migration must run or be available before Ready.
- Data migration: no business data migration; initial STA schema bootstrap only.
- Backfill: none.
- Cache: Redis keys for OTP, idempotency and session tokens.
- Runtime storage: PostgreSQL PVC and Redis PVC for STA.

## Config / Permission / Observability Impact

- Config: service env vars, Secret references, image digests, BFF base URL, CORS origins, Consul/Kubernetes service discovery, OTEL endpoint.
- Permission: namespace-scoped service accounts, network policies, registry pull secret references, Secret bootstrap ownership.
- Metrics: service readiness and runtime dependency health; smoke result evidence.
- Logs: smoke and service logs must avoid手机号、OTP、token、applicantId 明文泄漏。
- Tracing: W3C trace context must flow fides -> fides-bff -> applicant-api where implemented.
- Events: Argo CD sync events, rollout events, Kubernetes events.

## Rollout And Rollback

- Gray release: STA only; no prod traffic.
- Kill switch: revert or suspend Argo CD app sync for affected service if runtime drift threatens stability.
- Rollout steps:
  - Build/publish three images and promote digest into STA overlays.
  - Sync dependencies first, then applicant-api, fides-bff, fides.
  - Run readiness checks, smoke and public/private reachability checks.
- Rollback steps:
  - Revert selected service overlay digest to previous known-good digest.
  - Sync Argo CD application.
  - Re-run smoke and record evidence.

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| 当前 kubeconfig 无法连接 API server | 无法完成真实集群 apply、smoke 和回滚验证 | 先完成 GitOps、镜像和可本地渲染资产；集群恢复后补运行证据 | Forest |
| Secret 方案未确定 | 依赖和服务无法真实启动 | Git 中只提交 Secret 引用和 bootstrap 文档，不提交值 | Forest |
| Consul 与 Kubernetes DNS 选择不明确 | fides-bff 连接 applicant-api 可能失败 | 当前先保留 Consul 以匹配已实现服务发现；若改为 DNS，另记后续任务 | Codex |
| 镜像 registry 凭据或 digest promotion 失败 | 服务无法部署或回滚 | 复用现有 image release template，记录 digest promotion evidence | Platform |
| 生产化范围过大 | 延误 CI/CD runtime 闭环 | 当前只实现 LEN-78 至 LEN-84 验收闭环，技术债另建 ticket | Forest |
