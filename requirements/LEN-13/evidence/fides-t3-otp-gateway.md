# LEN-13 T3 Evidence: OTP REST infrastructure and mock adapter

## Scope

- Task: T3
- Service: `fides`
- Worktree: `/Users/forest/Code/spark/.worktrees/LEN-13/business-repo`
- Requirement trace: R2, R4, R6
- Design trace: D2, D4, D5, D6

## Test-first result

Before production code was added, `pnpm test` failed because the expected modules did not exist:

- `src/application/mobile-verification/otp-auth-gateway`
- `src/infrastructure/mobile-verification/mock-otp-auth-gateway`
- `src/infrastructure/mobile-verification/rest-otp-auth-gateway`

This established executable expectations for the OTP gateway port, BFF error mapping, mock adapter behavior, and REST adapter idempotency headers.

## Implemented behavior

- `OtpAuthGateway` defines `sendOtp` and `verifyOtp` commands/results.
- `mapOtpAuthError` maps BFF errors into stable UI error kinds.
- `MockOtpAuthGateway` supports deterministic send/verify behavior for AC1-AC8 demonstrations.
- `RestOtpAuthGateway` posts to `/api/v1/auth/otp:send` and `/api/v1/auth/otp:verify`, carries `Idempotency-Key`, and normalizes BFF error envelopes.

## Verification

```text
pnpm test
Test Files  6 passed (6)
Tests  16 passed (16)
```

```text
pnpm lint:deps
no dependency violations found (17 modules, 16 dependencies cruised)
```

```text
pnpm build
Compiled successfully
Route (app)
┌ ○ /
└ ○ /_not-found
```
