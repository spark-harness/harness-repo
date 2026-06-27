---
requirement_id: "LEN-11"
evidence_type: "local-verification"
created_at: "2026-06-28T07:34:59+08:00"
status: "pass"
repos:
  - business-repo
  - harness-repo
---

# LEN-11 Local Verification

## Scope

本证据覆盖 `fides-web` 贷款请求屏实现、BFF HTTP gateway、draft pointer store、手机号验证后切屏、同一草稿回填，以及前端分层门禁。

## Test-First Evidence

生产代码补齐前，新增测试先执行以下命令：

```bash
pnpm test -- src/infrastructure/loan-request/rest-loan-request-gateway.test.ts src/infrastructure/loan-request/browser-draft-store.test.ts src/adapters/loan-request/loan-request-controller.test.ts src/presentation/loan-request/loan-request-screen.test.tsx src/api/fides-application.test.tsx
```

结果：5 个测试套件失败，原因是目标模块尚不存在：

- `./fides-application`
- `./loan-request-controller`
- `./browser-draft-store`
- `./rest-loan-request-gateway`
- `./loan-request-screen`

该失败用于证明 LEN-11 行为测试先于生产实现存在。

## Final Commands

在 `/Users/forest/Code/spark/.worktrees/LEN-11/business-repo/apps/fides-web` 执行：

```bash
pnpm test -- src/infrastructure/loan-request/rest-loan-request-gateway.test.ts src/infrastructure/loan-request/browser-draft-store.test.ts src/adapters/loan-request/loan-request-controller.test.ts src/presentation/loan-request/loan-request-screen.test.tsx src/api/fides-application.test.tsx
```

结果：

```text
Test Files  18 passed | 1 skipped (19)
Tests       69 passed | 1 skipped (70)
```

```bash
pnpm test
```

结果：

```text
Test Files  18 passed | 1 skipped (19)
Tests       69 passed | 1 skipped (70)
```

```bash
pnpm lint
```

结果：退出码 0。存在既有 warning：

```text
src/infrastructure/mobile-verification/mock-otp-auth-gateway.ts
37:22  warning  '_command' is defined but never used
```

```bash
pnpm lint:deps
```

结果：

```text
✔ no dependency violations found (59 modules, 122 dependencies cruised)
```

```bash
pnpm build
```

结果：

```text
✓ Compiled successfully
✓ Generating static pages using 5 workers (2/2)
Route (app)
┌ ƒ /
├ ○ /_not-found
└ ƒ /api/runtime-config
```

## Behavior Covered

- `RestLoanRequestGateway` 只调用 BFF `/api/v1/pricing/quotes`、`/api/v1/loan-applications`、`/api/v1/loan-applications/{applicationId}`。
- pricing 请求携带 `Authorization`、`Idempotency-Key`、`X-Trace-Id` 和 W3C `traceparent`。
- draft create/patch 通过 BFF 完成，不直连 Java 服务。
- `BrowserDraftStore` 只保存 `applicationId`、`applicantId`、`currentStep`，不保存 access token。
- `LoanRequestController` 覆盖 pricing、first Continue create、existing Continue patch、same draft load/refill。
- `LoanRequestScreen` 覆盖 code.html 结构、Step 2 progress、真实 quote summary、Continue 停留当前页且无 toast/status、同一草稿回填。
- `FidesApplication` 覆盖手机号验证成功后进入贷款请求屏。

## Result

本地实现、测试、lint、依赖方向和 production build 均通过。
