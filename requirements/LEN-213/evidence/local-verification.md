# Local Verification

Requirement: LEN-213

Workspace:

- `harness-repo`: `/Users/forest/Code/spark/.worktrees/LEN-213/harness-repo`
- `business-repo`: `/Users/forest/Code/spark/.worktrees/LEN-213/business-repo`

## Test-First Evidence

Initial targeted tests failed before implementation because:

- `src/infrastructure/observability/server-logger.ts` did not exist.
- BFF proxy did not record request or error logs.
- Runtime config route did not record server request/error logs.

After implementation and review fixes, the targeted tests passed.

## Commands

Run from `business-repo/apps/fides-web`.

| Command | Result | Notes |
|---|---|---|
| `pnpm test src/infrastructure/observability/server-logger.test.ts src/api/bff-proxy/bff-proxy-route.test.ts` | PASS | 9 tests passed |
| `pnpm test src/api/bff-proxy/bff-proxy-route.test.ts src/api/runtime-config/runtime-config-route.test.ts` | PASS | 4 tests passed after governed error-code update |
| `pnpm lint` | PASS | 0 errors, 1 pre-existing warning in `mock-otp-auth-gateway.ts` |
| `pnpm lint:deps` | PASS | no dependency violations, 85 modules / 172 dependencies |
| `pnpm test` | PASS | 27 passed, 1 skipped; 105 passed, 1 skipped |
| `pnpm build` | PASS | Next.js build compiled, TypeScript passed, routes generated |

## Scope Notes

- No protobuf IDL changes.
- No generated contract changes.
- No GitOps or VaultStaticSecret template changes.
- `.next` build output was removed after verification.

## Acceptance Mapping

| AC | Evidence |
|---|---|
| AC1 | Server logger tests assert JSON fields `service`, `operation`, `level`, `timestamp`, `request_id` / `trace_id`; runtime and BFF route tests assert request logs. |
| AC2 | `createRequestLogContext` tests cover W3C `traceparent`; active span support is implemented through OpenTelemetry API. Header fallback logs `trace_id` only, not a fake current `span_id`. |
| AC3 | BFF proxy and runtime config route failure tests assert governed error codes and no sensitive fields. |
| AC4 | `pnpm lint` runs with `console.*` restrictions outside `server-logger.ts`. |
| AC5 | Server logger tests reject unapproved and sensitive fields; unsafe `x-request-id` values are replaced with generated request IDs. |
| AC6 | No GitOps/Vault key template changes were made; existing raw env -> Secret -> envFrom model remains untouched. |
| AC7 | `pnpm lint`, `pnpm lint:deps`, `pnpm test`, and `pnpm build` all passed locally. |
