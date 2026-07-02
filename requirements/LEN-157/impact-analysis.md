---
requirement_id: "LEN-157"
analyst: "forest"
status: "approved"
updated_at: "2026-07-02"
approved_by: "forest"
approved_at: "2026-07-03T02:17:53+08:00"
decision: "用户授权 Agent 批准所有需要的文件；批准 LEN-157 service repo readiness；本票只改 GitOps，不纳入业务/IDL 仓 peer。"
idl_impact: "no"
idl_impact_reason: "只修改 GitOps runtime 配置和 Harness 生命周期文件，不修改 protobuf。"
---

# Impact Analysis

## Summary

LEN-157 调整 dev-1 / sta-1 GitOps runtime 配置，让 fides-web 使用同源
`/api/v1`，服务端代理访问集群内 fides-bff，并补齐跨服务 trace bootstrap。

## Affected Domains

- 前端体验：浏览器 runtime config 不再依赖旧公网 BFF API 域名。
- 前端 BFF：fides-web 服务端代理固定访问内网 fides-bff Service。
- 可观测性：fides-bff 和下游服务需要保持 OTEL exporter 与 trace context。
- GitOps 交付：dev-1 / sta-1 overlays 和 Consul bootstrap 是配置真相源。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides | `{gitops-repo}/apps/fides` | 更新 Deployment env 和 Consul runtime config bootstrap | No |
| fides-bff | `{gitops-repo}/apps/fides-bff` | 开启 OTEL bootstrap，保留私密 exporter 配置 | Yes |
| applicant-api | `{gitops-repo}/apps/applicant-api` | 验证 OTEL 与 trace context 接收配置 | Yes |
| quote-api | `{gitops-repo}/apps/quote-api` | 验证 OTEL 与 trace context 接收配置 | No |
| origination-api | `{gitops-repo}/apps/origination-api` | 验证 OTEL 与 trace context 接收配置 | No |

## API / Contract Impact

- Protobuf: none.
- HTTP: none. fides-web 仍通过 LEN-156 的 `/api/v1/*` 代理访问 fides-bff。
- Contract repo: not changed.
- Proto files: none.
- Buf module: not changed.
- Buf config version: v2.
- Required buf checks: not required for this config-only change.
- Breaking baseline: not applicable.
- Compatibility risk: low; runtime URL source changes, API path remains `/api/v1`。

## Data Impact

- Database schema: none.
- Data migration: none.
- Backfill: none.
- Cache: none.
- Runtime storage: Consul KV bootstrap updates fides-web runtime config and fides-bff config.

## Config / Permission / Observability Impact

- Config: fides Deployment `FIDES_BFF_BASE_URL` points to internal Kubernetes Service URL.
- Config: fides public runtime config `bffBaseUrl` becomes `/api/v1` in dev-1 / sta-1.
- Config: fides-bff OTEL enabled remains true in GitOps and Consul bootstrap.
- Secret: Sentry / OTLP endpoint and headers are not committed; fides-bff reads them from Consul private runtime config.
- Permission: no RBAC change.
- Metrics: no metric name change.
- Logs: no log field change.
- Tracing: W3C trace context flows browser -> fides proxy -> fides-bff -> downstream services.
- Events: none.

## Rollout And Rollback

- Rollout: merge GitOps PR to master, sync Argo apps for fides and fides-bff in dev-1 / sta-1,
  then verify Deployment env, Consul KV, runtime-config response, and trace evidence.
- Rollback: revert GitOps commit and sync Argo apps; fides can fall back to previous public
  BFF API URL while Caddy route remains present.

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| Missing internal BFF URL | fides `/api/v1` proxy fails | Render Deployment env and live check before smoke | forest |
| Bootstrap overwrites Sentry headers | trace export fails | Preserve existing endpoint / headers from Consul, never commit values | forest |
| OTEL endpoint absent in live env | trace not visible in Sentry | Record as live prerequisite and verify current Consul/secret state | forest |
| Old public BFF route remains reachable | Confusing debug surface | Document as temporary smoke/debug route, remove in separate ticket if desired | forest |
