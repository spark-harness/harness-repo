---
requirement_id: "LEN-156"
owner: "forest"
status: "approved"
updated_at: "2026-07-02"
approved_by: "forest"
approved_at: "2026-07-02T17:36:50Z"
decision: "用户授权 Agent 批准所有需要的文件；批准 LEN-156 design。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision |
|---|---|
| R1, R2 | D1：新增 `src/app/api/v1/[...path]/route.ts`，统一委托 `proxyBffRequest`。 |
| R3, R4 | D2：runtime public config 始终返回 `/api/v1`，服务端内部读取 `FIDES_BFF_BASE_URL`。 |
| R5, R6 | D3：注册 `FetchInstrumentation`，`propagateTraceHeaderCorsUrls` 只匹配 `/^\\/api\\/v1(?:\\/|$)/`。 |

## Summary

方案把浏览器和 BFF 的跨域/内网细节收敛到 fides-web 服务端。浏览器只访问同源 `/api/v1`，route handler 将请求代理到 `FIDES_BFF_BASE_URL`。

## Affected Services

| Service | Change |
|---|---|
| fides | 新增 proxy route、server-only BFF config、fetch instrumentation。 |

## API / Contract Design

No IDL change. Proxy preserves existing BFF HTTP paths below `/api/v1`.

## Application Design

- `proxyBffRequest` filters hop-by-hop headers and forwards method/body/query.
- `getBffProxyBaseUrl` reads server-only runtime config.
- `initializeBrowserTracing` registers `FetchInstrumentation`.

## Testing Strategy

- Proxy unit test covers path/query/header/body forwarding.
- Runtime config tests cover public `/api/v1` and prod server BFF requirement.
- Browser tracing test covers fetch instrumentation registration.
- Final commands: `pnpm test`, `pnpm lint`, `pnpm lint:deps`, `pnpm build`.

## Rollout And Rollback

LEN-157 must configure dev/sta `FIDES_BFF_BASE_URL`. Rollback reverts fides-web commit.
