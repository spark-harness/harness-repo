---
requirement_id: "LEN-156"
evidence_type: "implementation"
updated_at: "2026-07-02T17:36:50Z"
repos:
  - business-repo
  - harness-repo
---

# LEN-156 Implementation Evidence

## Implementation

- Added `/api/v1/[...path]` Next route handler.
- Added server-only BFF proxy base URL lookup.
- Public runtime config returns browser `bffBaseUrl: "/api/v1"`.
- Registered OpenTelemetry fetch instrumentation with propagation limited to `/api/v1`.

## Verification

```text
pnpm exec vitest run src/api/bff-proxy/bff-proxy-route.test.ts src/infrastructure/runtime-config/runtime-config.test.ts src/infrastructure/observability/browser-tracing.test.ts
3 passed
```

```text
pnpm test
23 passed | 1 skipped
```

```text
pnpm lint
0 errors, 1 existing warning in mock-otp-auth-gateway.ts
```

```text
pnpm lint:deps
no dependency violations found
```

```text
pnpm build
Compiled successfully; route list includes /api/v1/[...path].
```
