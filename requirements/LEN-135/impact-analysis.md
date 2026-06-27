---
requirement_id: "LEN-135"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-28"
idl_impact: "no"
idl_impact_reason: "本需求只修改 fides-bff lendora-sta GitOps runtime 配置和验证证据，不修改 protobuf IDL、generated contracts 或 Buf 配置。"
approved_by: "forest"
approved_at: "2026-06-28T06:27:11+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-135 service-repo-check 更新，fides-bff runtime Secret 引用不改变 IDL 或服务矩阵。"
---

# Impact Analysis

## Summary

LEN-135 将 fides-bff 的 quote-api 和 origination-api 下游配置补齐到 lendora-sta GitOps 目标状态，并用运行时 smoke 验证 BFF 到真实下游链路。

## Affected Domains

- Frontend BFF runtime：`fides-bff` 从只配置 applicant 下游扩展为配置 quote/origination 下游。
- GitOps delivery：`apps/fides-bff/base/configmap.yaml` 目标状态变化。
- Runtime verification：新增 BFF 到 quote/origination 的 smoke 证据。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides-bff | gitops-repo | 配置 quote/origination Consul discovery 和 HTTP timeout | yes, existing only |
| quote-api | gitops-repo | 下游服务发现和 smoke 依赖，不改部署目标 | no |
| origination-api | gitops-repo | 下游服务发现和 smoke 依赖，不改部署目标 | no |
| Harness LEN-135 lifecycle | harness-repo | 保存需求、设计、任务、门禁和证据 | no |

## API / Contract Impact

- External API: 不新增或修改 BFF 对外 API。
- BFF endpoints used by smoke:
  - `POST /api/v1/pricing/quotes`
  - `POST /api/v1/loan-applications`
  - `GET /api/v1/loan-applications/{applicationId}`
  - `PATCH /api/v1/loan-applications/{applicationId}`
- Protobuf IDL: no changes.
- Generated contracts: no changes.
- Compatibility risk: 配置变更只影响运行时下游目标；若 Consul service name 错误，BFF 会返回下游不可用。

## Data Impact

- 不新增数据库 schema、migration、backfill 或 cache。
- Pricing smoke 会写 quote DB。
- Origination smoke 会写 application DB。
- Evidence 只记录业务 ID、状态和验证结论，不记录敏感申请内容。

## Config / Permission / Observability Impact

- Config:
  - 新增 `quote.consul.address/scheme/service_name`。
  - 新增 `quote.http.base_url/timeout`。
  - 新增 `origination.consul.address/scheme/service_name`。
  - 新增 `origination.http.base_url/timeout`。
  - 新增 `auth.token_mode/access_token_ttl`。
  - 新增 `AUTH_TOKEN_SECRET` Secret 引用。
- Permission:
  - 依赖 `lendora-sta-fides-bff` namespace 已有 quote/origination client labels。
  - 不新增公网入口。
- Metrics:
  - 不新增指标。
- Logs:
  - 不记录 token、Authorization、trace baggage、OTLP header 或完整请求体。
- Tracing:
  - 继续传播 W3C `traceparent` 和 `tracestate`。
- Events:
  - 不新增事件。

## Rollout And Rollback

- Rollout:
  - 合入 fides-bff ConfigMap 目标状态。
  - 确认运行镜像包含 LEN-133 facade；如未包含，刷新 fides-bff digest。
  - 应用或同步 GitOps manifests。
  - 重启 fides-bff 使 ConfigMap 生效。
  - 执行 runtime smoke。
- Rollback:
  - 回滚 ConfigMap 到上一版本。
  - 回滚 fides-bff overlay digest 到上一可用镜像。
  - 如需止血，可缩容 fides-bff 或停止前端入口流量。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| 运行镜像不含 LEN-133 facade | loan application smoke 404 或 405 | smoke 前确认 digest 或刷新 fides-bff 镜像 | core |
| Consul service name 配错 | BFF 返回下游不可用 | 使用 service matrix 和 runtime Consul 查询验证 `quote-api`、`origination-api` | core |
| ConfigMap 更新后 Pod 未重启 | 运行时仍读旧配置 | rollout restart 并记录新 Pod config | core |
| 当前集群无 Argo CD | 无法验证 Healthy/Synced | evidence 记录 WARN，不伪造通过 | platform/gitops |
| 手工 apply 与 GitOps 主干短暂漂移 | 运行时与 GitOps 合并状态不同 | 先提交 PR，runtime smoke 记录 commit/digest/config，并在合并后清理漂移 | core |
| fides-bff token secret 缺失 | 受保护接口全部 401 | 使用 `fides-bff-runtime/token-secret` runtime Secret 引用，Secret 值不入仓 | core |
