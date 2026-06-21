# LEN-13 T2 Evidence: mobile-verification domain/application baseline

## Scope

- Task: T2
- Service: `fides`
- Worktree: `/Users/forest/Code/spark/.worktrees/LEN-13/business-repo`
- Requirement trace: R1, R3, R6
- Design trace: D1, D3, D5, D6

## Test-first result

Before production code was added, `pnpm test` failed because the expected modules did not exist:

- `src/domain/mobile-verification/phone-number`
- `src/domain/mobile-verification/otp-code`
- `src/application/mobile-verification/idempotency-key`

This established executable expectations for Hong Kong phone validation, OTP code validation, and user-intent idempotency key reuse.

## Implemented behavior

- `parseHongKongPhoneNumber` accepts valid `+852` mobile numbers, normalizes digits, and returns a masked display string.
- `parseHongKongPhoneNumber` rejects non-`+852` country codes and invalid Hong Kong mobile numbers.
- `parseOtpCode` accepts exactly six digits and normalizes pasted codes with spaces.
- `UserIntentIdempotencyKeys` reuses one key for retries of the same user intent and rotates for a new user intent.

## Verification

```text
pnpm test
Test Files  3 passed (3)
Tests  8 passed (8)
```

```text
pnpm lint:deps
no dependency violations found (11 modules, 8 dependencies cruised)
```

```text
pnpm build
Compiled successfully
Route (app)
┌ ○ /
└ ○ /_not-found
```
