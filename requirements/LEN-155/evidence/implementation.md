---
requirement_id: "LEN-155"
evidence_type: "implementation"
updated_at: "2026-07-02T17:18:30Z"
repos:
  - business-repo
  - harness-repo
---

# LEN-155 Implementation Evidence

## Formal Contract Version

| Artifact | Version | Commit | Verification |
|---|---|---|---|
| `idl-ts-repo` | `v0.2.5` | `af09e09be8328d15ca9f026f65cbc980f90425d3` | `git ls-remote --tags git@github.com:spark-harness/idl-ts-repo.git refs/tags/v0.2.5` |

`business-repo/apps/fides-web/package.json` consumes `@spark-harness/idl-ts-client` with `#semver:v0.2.5`.

## Test-First Evidence

Failing test before implementation:

```text
pnpm exec vitest run src/infrastructure/mobile-verification/rest-otp-auth-gateway.test.ts src/infrastructure/loan-request/rest-loan-request-gateway.test.ts
FAIL src/infrastructure/loan-request/rest-loan-request-gateway.test.ts
FAIL src/infrastructure/mobile-verification/rest-otp-auth-gateway.test.ts
Expected headers without traceparent / X-Trace-Id, but current gateways still sent both headers.
```

## Implementation Evidence

- `src/infrastructure/bff/generated-client.ts` centralizes generated client basePath, timeout fetch, header merge and BFF error envelope parsing.
- `RestOtpAuthGateway` keeps `FidesBffAuthServiceApi` and removes local span / trace header creation.
- `RestIdentityProfileGateway` keeps `FidesBffIdentityProfileServiceApi` and removes local span / trace header creation.
- `RestLoanRequestGateway` uses `FidesBffPricingServiceApi` and `FidesBffLoanApplicationServiceApi`.
- Generated client imports remain inside `src/infrastructure`.

Static checks:

```text
rg -n "traceparent|tracestate|startSpan|span\\.end" apps/fides-web/src/infrastructure -S
no matches

rg -n "@spark-harness/idl-ts-client" apps/fides-web/src/{application,adapters,presentation,app} -S
no matches
```

## Final Verification

```text
pnpm test
Test Files  22 passed | 1 skipped (23)
Tests  86 passed | 1 skipped (87)
```

```text
pnpm lint
0 errors, 1 existing warning in src/infrastructure/mobile-verification/mock-otp-auth-gateway.ts
```

```text
pnpm lint:deps
no dependency violations found (71 modules, 148 dependencies cruised)
```

```text
pnpm build
Compiled successfully.
TypeScript finished successfully.
```
