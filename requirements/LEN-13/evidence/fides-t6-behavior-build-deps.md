# Fides T6 Behavior, Build, And Dependency Evidence

## Scope

- Requirement: LEN-13
- Task: T6 前端行为测试、构建与依赖边界验证
- Service: `fides`
- Business repo path: `/Users/forest/Code/spark/.worktrees/LEN-13/business-repo/services/frontend/fides`

## Coverage Added

T6 expanded executable coverage across the AC1-AC10 surface:

- AC1 / AC2: valid `+852` send shows OTP inputs, disables resend during cooldown, counts cooldown down, and re-enables resend after expiry.
- AC3 / AC9: successful verify response saves session through `SessionStore` and advances through `FlowControllerPort`; no prototype `setTimeout` success path is used.
- AC4: invalid OTP shows inline `验证码不正确` and keeps focus in OTP input.
- AC5: expired OTP shows `验证码已过期，请重新获取验证码`; resend recovery is executable after cooldown expiry.
- AC6: verification rate limit applies returned retry cooldown and shows `请稍后再试`.
- AC7: non-`+852` request shows unsupported-country error and does not reach successful send behavior.
- AC8: session-expired / unauthorized mapping shows `请重新验证手机号`, clears short-lived session state, and returns through the FlowController mobile verification path.
- AC10: mock gateway supports send, cooldown, valid verify, invalid verify, and non-PII mock identifiers; adapter mode config supports mock, real, and disabled paths.

Files with T6-relevant coverage:

- `src/presentation/mobile-verification/mobile-verification-screen.test.tsx`
- `src/adapters/mobile-verification/mobile-verification-controller.test.ts`
- `src/application/mobile-verification/otp-auth-gateway.test.ts`
- `src/infrastructure/mobile-verification/rest-otp-auth-gateway.test.ts`
- `src/infrastructure/mobile-verification/mock-otp-auth-gateway.test.ts`
- `src/infrastructure/mobile-verification/browser-session-store.test.ts`
- `src/infrastructure/mobile-verification/browser-flow-controller.test.ts`
- `src/api/mobile-verification/create-mobile-verification-controller.test.ts`

## Verification Commands

Run from `/Users/forest/Code/spark/.worktrees/LEN-13/business-repo/services/frontend/fides`.

```bash
pnpm lint
```

Result: PASS. ESLint completed with 0 errors and 0 warnings.

```bash
pnpm test
```

Result: PASS. Vitest reported 11 test files passed and 45 tests passed.

```bash
pnpm lint:deps
```

Result: PASS. Dependency Cruiser reported no dependency violations across 32 modules and 52 dependencies.

```bash
pnpm build
```

Result: PASS. Next.js 16.2.6 production build compiled successfully, completed TypeScript, and prerendered `/`.

```bash
pnpm exec tsc --noEmit
```

Result: PASS. TypeScript completed with no output.

## Cleanup

- Removed generated `.next` output after verification.
- No repository ignore policy changes were added for one-off build artifacts.

## Review Fix Verification

After the T7 code review, the implementation was updated to cover the open P0/P1/P2 findings:

- Session save plus FlowController advance now compensates by clearing the saved session if flow advance fails.
- Session-expired / unauthorized errors now clear short-lived session state and call `returnToMobileVerification`.
- Cooldown now counts down and the OTP section `Resend code` action requests a new code after cooldown expiry.
- Idempotency keys rotate after completed send / verify user intents while preserving the same key during an in-flight intent.
- REST error handling accepts published OTP/auth codes, maps bare `401` / `429` / `5xx` responses, carries trace IDs, and does not expose unknown backend messages to users.
- REST OTP requests have an abort timeout; timeout is mapped to retryable UI failure.
- Mock identifiers are opaque and do not persist full phone numbers through `challengeId` / `applicantId`.
- Adapter mode config supports `mock`, `real`, and `disabled` modes.

## Remaining Work

- Real BFF smoke remains pending until the upstream OTP REST contract is ready.
- T7 still needs gate refresh and merge-readiness work after the updated review state is accepted.
