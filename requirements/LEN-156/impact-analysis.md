---
requirement_id: "LEN-156"
analyst: "forest"
status: "approved"
updated_at: "2026-07-02"
idl_impact: "no"
idl_impact_reason: "只修改 fides-web app proxy 和 tracing 配置，不修改 proto。"
approved_by: "forest"
approved_at: "2026-07-02T17:36:50Z"
decision: "用户授权 Agent 批准所有需要的文件；批准 LEN-156 impact-analysis，确认只修改 fides-web proxy 和 tracing。"
---

# Impact Analysis

## Summary

LEN-156 修改 `business-repo/apps/fides-web`，新增同源 BFF proxy route 和 browser fetch instrumentation。它不修改 IDL、BFF runtime、数据库或 GitOps。

## Affected Domains

- 前端体验：浏览器 BFF 请求改为同源 `/api/v1`。
- 可观测性：fetch instrumentation 负责 FE client span 和 trace context 传播。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides | `{business-repo}/apps/fides-web` | 新增 app proxy 和 fetch instrumentation | No |
| fides-bff | `{business-repo}/apps/fides-bff` | 代理目标，本票不改代码 | Yes |

## API / Contract Impact

- Protobuf: none.
- HTTP: fides-web 新增同源 `/api/v1/*` proxy；外部 BFF HTTP contract 不变。
- Config: server-side `FIDES_BFF_BASE_URL` must point to fides-bff base URL.

## Data Impact

No database, migration, cache, or browser storage schema change.

## Config / Permission / Observability Impact

- Config: `FIDES_BFF_BASE_URL` becomes server-only proxy target.
- Permission: Authorization header is preserved by proxy.
- Tracing: `@opentelemetry/instrumentation-fetch` propagates trace only for `/api/v1`.
- Sentry / OTLP: exporter endpoint is not part of propagation allow-list.

## Rollout And Rollback

- Rollout: deploy fides-web image with route handler; LEN-157 supplies dev/sta BFF address.
- Rollback: revert fides-web LEN-156 business commit.

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| Missing `FIDES_BFF_BASE_URL` in environment | proxy returns runtime error | LEN-157 config and runtime tests | forest |
| Proxy forwards hop-by-hop headers | protocol errors | header filter test | forest |
| Trace headers propagate to OTLP endpoint | vendor request pollution | regex allow-list only matches `/api/v1` | forest |
