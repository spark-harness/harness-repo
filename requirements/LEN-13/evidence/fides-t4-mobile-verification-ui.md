# Fides T4 Mobile Verification UI Evidence

## Scope

- Requirement: LEN-13
- Task: T4 手机验证 presentation 与 OTP 输入体验
- Service: `fides`
- Business repo path: `/Users/forest/Code/spark/.worktrees/LEN-13/business-repo/services/frontend/fides`
- UI source of truth: `/Users/forest/Code/spark/hk_loan_ui/1._mobile_verification/code.html`

## Implementation Summary

- `MobileVerificationScreen` now follows the `hk_loan_ui/1._mobile_verification/code.html` structure:
  - fixed top app bar with Back, `Lendora`, More options
  - step progress bar with Step 1 of 7 semantics
  - sms icon plus `Verify your mobile`
  - copy `We'll text a one-time code to confirm it's really you.`
  - `Mobile Number` label, `+852` selector, phone input, and in-field `Send`
  - OTP section with 6 digit inputs and resend cooldown after send
  - fixed bottom `Continue` button
- Material Symbols dependency was removed from runtime rendering for this screen; equivalent inline SVG icons are used so icons do not degrade into ligature text in verification browsers.
- Existing controller behavior remains wired through the adapter boundary; no prototype `setTimeout` success path is used for verification.

## Verification Commands

Run from `/Users/forest/Code/spark/.worktrees/LEN-13/business-repo/services/frontend/fides`.

```bash
pnpm lint
```

Result: PASS. ESLint completed with 0 errors and 0 warnings.

```bash
pnpm test
```

Result: PASS. Vitest reported 7 test files passed and 20 tests passed.

```bash
pnpm lint:deps
```

Result: PASS. Dependency Cruiser reported no dependency violations across 25 modules and 33 dependencies.

```bash
pnpm build
```

Result: PASS. Next.js 16.2.6 production build compiled successfully, completed TypeScript, and prerendered `/`.

## Browser Verification

- Dev server: `http://localhost:30213/?fresh=wide-window`
- Screenshot: `/Users/forest/Downloads/下载 (14).png`
- Observed structure:
  - Back button, `Lendora` link, More options button
  - `Application progress` progressbar
  - `Verify your mobile`
  - `We'll text a one-time code to confirm it's really you.`
  - `Mobile Number`, `+852`, `9123 4567`, `Send`
  - fixed bottom `Continue`
- Visual correction verified: icons render as icons instead of `arrow_back`, `sms`, `expand_more`, `arrow_forward` ligature text.

## Remaining Work

- T5 remains open for `SessionStore` and `FlowControllerPort` integration.
- T6 remains open for broader behavior coverage across AC1-AC10.
- T7 remains open for review report and merge-readiness gate work.
