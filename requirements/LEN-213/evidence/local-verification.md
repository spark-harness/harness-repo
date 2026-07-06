# Local Verification

Requirement: LEN-213

Workspace:

- `harness-repo`: `/Users/forest/Code/spark/.worktrees/LEN-213/harness-repo`
- `business-repo`: `/Users/forest/Code/spark/.worktrees/LEN-213/business-repo`
- `gitops-repo`: `/Users/forest/Code/spark/.worktrees/LEN-213/gitops-repo`

## Test-First Evidence

Initial targeted tests failed before implementation because:

- `src/infrastructure/observability/server-logger.ts` did not exist.
- BFF proxy did not record request or error logs.
- Runtime config route did not record server request/error logs.

After implementation and review fixes, the targeted tests passed.

Follow-up scope on 2026-07-06:

- Added server-side OTLP Logs exporter configuration to `fides-web`.
- Kept stdout JSON logging as the first sink.
- Kept browser runtime config free of server OTEL endpoint/header values.
- Updated GitOps so `fides-runtime` VaultStaticSecret uses raw env passthrough instead of per-key templates.

## Commands

Run from `business-repo/apps/fides-web`.

| Command | Result | Notes |
|---|---|---|
| `pnpm test src/infrastructure/observability/server-logger.test.ts src/api/bff-proxy/bff-proxy-route.test.ts` | PASS | 9 tests passed |
| `pnpm test src/api/bff-proxy/bff-proxy-route.test.ts src/api/runtime-config/runtime-config-route.test.ts` | PASS | 4 tests passed after governed error-code update |
| `pnpm test src/infrastructure/observability/server-logger.test.ts src/infrastructure/observability/server-otel-logs.test.ts src/config/env.test.ts src/infrastructure/runtime-config/runtime-config.test.ts` | PASS | 22 tests passed |
| `pnpm lint` | PASS | 0 errors, 1 pre-existing warning in `mock-otp-auth-gateway.ts` |
| `pnpm lint:deps` | PASS | no dependency violations, 89 modules / 182 dependencies |
| `pnpm test` | PASS | 28 passed, 1 skipped; 111 passed, 1 skipped |
| `pnpm build` | PASS | Next.js build compiled, TypeScript passed, routes generated |
| `kubectl kustomize apps/fides/overlays/dev-1` | PASS | Rendered 112 lines; config includes `OTEL_LOGS_EXPORTER` and VSS has no transformation template |
| `kubectl kustomize apps/fides/overlays/sta-1` | PASS | Rendered 112 lines; config includes `OTEL_LOGS_EXPORTER` and VSS has no transformation template |

## Scope Notes

- No protobuf IDL changes.
- No generated contract changes.
- GitOps changes are limited to fides ConfigMap and fides VaultStaticSecret overlays.
- VaultStaticSecret per-key transformation templates were removed so raw env keys can pass through from Vault to `fides-runtime`.
- `.next` build output was removed after verification.

## Acceptance Mapping

| AC | Evidence |
|---|---|
| AC1 | Server logger tests assert JSON fields `service`, `operation`, `level`, `timestamp`, `request_id` / `trace_id`; `server-otel-logs.test.ts` asserts enabled OTLP exporter emits a log record with the same safe fields. |
| AC2 | `createRequestLogContext` tests cover W3C `traceparent`; active span support is implemented through OpenTelemetry API. Header fallback logs `trace_id` only, not a fake current `span_id`; OTLP log record uses span context only when both `trace_id` and `span_id` are valid. |
| AC3 | BFF proxy and runtime config route failure tests assert governed error codes and no sensitive fields. |
| AC4 | `pnpm lint` runs with `console.*` restrictions outside `server-logger.ts`. |
| AC5 | Server logger tests reject unapproved and sensitive fields; unsafe `x-request-id` values are replaced with generated request IDs. |
| AC6 | GitOps render proves `fides-runtime` still uses Deployment `envFrom`; VaultStaticSecret no longer requires per-key templates and can pass Vault raw env keys into the Secret. |
| AC7 | `pnpm lint`, `pnpm lint:deps`, `pnpm test`, and `pnpm build` all passed locally. |
