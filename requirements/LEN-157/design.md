---
requirement_id: "LEN-157"
owner: "forest"
status: "approved"
updated_at: "2026-07-02"
approved_by: "forest"
approved_at: "2026-07-03T02:17:52+08:00"
decision: "用户授权 Agent 批准所有需要的文件；批准 LEN-157 design。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, AC1 | D1：fides runtime-config Consul bootstrap 写入 public `bffBaseUrl: "/api/v1"`。 | 浏览器不再知道公网或内网 BFF URL。 |
| R2, AC2 | D2：fides Deployment env 的 `FIDES_BFF_BASE_URL` 按环境指向内网 Service URL。 | dev-1 与 sta-1 分别使用本 namespace Service DNS。 |
| R3, R4, AC3 | D3：fides-bff config 保持 OTEL enabled，并通过 Consul 私密运行时配置保留 endpoint / headers。 | 真实 Sentry 配置不进入 Git。 |
| R5, AC4 | D4：验证 applicant-api、quote-api、origination-api 现有 OTEL / trace bootstrap，不做无关代码修改。 | quote/origination 已有保留 endpoint / headers 模式。 |
| R6, AC5, AC6 | D5：用 kustomize 渲染和 live kubectl/Consul 检查证明 Argo 不回退。 | GitOps 为配置真相源。 |
| R7, AC7 | D6：保留旧公网 BFF 域名作为临时 smoke/debug 入口，验收以同源代理 trace 为准。 | 不在本票删除 Caddy route。 |

## Summary

方案只改 GitOps runtime 配置。fides-web 浏览器继续读取 public runtime config，
但得到的 BFF base URL 固定为 `/api/v1`。fides-web 服务端 route handler 再通过
`FIDES_BFF_BASE_URL` 访问同 namespace 的 fides-bff Service。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| fides | 更新 dev-1 / sta-1 Deployment env 和 Consul runtime-config bootstrap | 切换到同源代理 + 内网 BFF URL |
| fides-bff | 更新 dev-1 / sta-1 OTEL bootstrap | 保持跨服务 trace export |
| applicant-api | 验证现有 OTEL bootstrap | 下游 trace context 接收 |
| quote-api | 验证现有 OTEL bootstrap | 下游 trace context 接收 |
| origination-api | 验证现有 OTEL bootstrap | 下游 trace context 接收 |

## API / Contract Design

- Protobuf IDL required: no.
- Proto files: none.
- Buf module: not changed.
- Buf config version: v2.
- Generated outputs: none.
- Breaking check baseline: not applicable.
- Compatibility strategy: public browser path remains `/api/v1`; BFF HTTP API path remains unchanged.

## Data / Config / Permission

- Data model: no change.
- Config:
  - `apps/fides/overlays/dev-1/runtime-config-consul.yaml` writes `bffBaseUrl: "/api/v1"`。
  - `apps/fides/overlays/sta-1/runtime-config-consul.yaml` writes `bffBaseUrl: "/api/v1"`。
  - fides dev-1 `FIDES_BFF_BASE_URL` becomes
    `http://fides-bff.lendora-dev-1.svc.cluster.local:8000/api/v1`。
  - fides sta-1 `FIDES_BFF_BASE_URL` becomes
    `http://fides-bff.lendora-sta-1.svc.cluster.local:8000/api/v1`。
  - fides-bff reads OTEL endpoint / headers from Consul config when those private values already exist.
- Permission: no RBAC or NetworkPolicy change.

## Observability

- Logs: no log schema change.
- Metrics: no metric schema change.
- Tracing:
  - Browser fetch instrumentation propagates trace headers to `/api/v1` from LEN-156.
  - fides route handler proxies those headers to fides-bff.
  - fides-bff and downstream services keep OTEL exporter enabled where configured.
  - Sentry endpoint / header values remain runtime secret material.
- Events: none.

## Testing Strategy

- Test-first exception: config-only GitOps change. No production code behavior test is edited.
- Render checks:
  - `kubectl kustomize apps/fides/overlays/dev-1`
  - `kubectl kustomize apps/fides/overlays/sta-1`
  - `kubectl kustomize apps/fides-bff/overlays/dev-1`
  - `kubectl kustomize apps/fides-bff/overlays/sta-1`
- Static checks:
  - rendered fides Deployment env contains internal `FIDES_BFF_BASE_URL`。
  - rendered fides runtime config contains `bffBaseUrl=/api/v1`。
  - rendered fides-bff config has OTEL enabled and no committed secret value.
- Live checks:
  - Argo apps are Synced / Healthy.
  - Deployment env and Consul KV match GitOps.
  - Runtime `/api/runtime-config` returns `/api/v1`。
  - Sentry trace contains fides, fides-bff, and touched downstream service spans.

## Rollout And Rollback

- Rollout: merge GitOps PR, sync dev-1, verify, then sync sta-1 and verify。
- Kill switch: revert fides Deployment `FIDES_BFF_BASE_URL` and runtime config to previous public API URL.
- Rollback: revert GitOps commit and resync Argo apps。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Consul private endpoint / headers are absent in an environment | Service starts and OTEL export remains no-op until private values are bootstrapped | forest |
| fides-bff OTEL enabled without endpoint | Setup is no-op without endpoint; live verification records missing endpoint as environment prerequisite | forest |
| Public API route removal breaks smoke | Keep Caddy API route in this ticket | forest |
