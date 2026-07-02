---
requirement_id: "LEN-155"
owner: "forest"
status: "approved"
updated_at: "2026-07-02"
approved_by: "forest"
approved_at: "2026-07-02T17:05:12Z"
decision: "用户授权 Agent 批准所有需要的文件；批准 LEN-155 design，允许进入任务拆分和 fides-web 实现。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, AC1 | D1：`apps/fides-web` 升级 `@spark-harness/idl-ts-client` 到 `v0.2.5`。 | `v0.2.5` 指向 `idl-ts-repo af09e09`，包含 pricing / loan-application。 |
| R2, AC2 | D2：`RestLoanRequestGateway` 构造 `FidesBffPricingServiceApi` 与 `FidesBffLoanApplicationServiceApi`，用 generated methods 替代手写 endpoint fetch。 | gateway port 与 controller 不变。 |
| R3, BR1, BR2 | D3：generated client 和 DTO 只停留在 infrastructure 层；domain/application/adapters/presentation 继续使用现有类型。 | 由 `pnpm lint:deps` 和 import scan 验证。 |
| R4, BR6, AC3, AC4 | D4：删除 mobile verification、identity profile、loan request gateway 内的手写 trace span/header 逻辑。 | 保留 `Idempotency-Key`、Authorization、timeout、错误映射。 |
| R5, BR3, BR4, BR5 | D5：抽出 infrastructure 内部 SDK helper，统一 basePath、timeout fetch、headers middleware 和 BFF error envelope 读取。 | helper 不进入 application/adapters 层。 |
| R6, AC5, AC6 | D6：更新 gateway tests，覆盖 generated client 请求路径、鉴权短路、幂等键、超时和错误映射。 | 先用测试暴露 loan-request 仍手写 fetch 的差异。 |

## Summary

LEN-155 把 `fides-web` 的 BFF infrastructure gateway 收敛到 generated TS SDK 浅适配层。浅适配层只负责技术边界：构造 generated client、注入 Authorization / Idempotency-Key、设置超时、读取 BFF error envelope、把 generated DTO 映射回 application/domain 类型。

业务层不感知 generated SDK。页面、controller、application port 和 domain model 不因 SDK 升级改变。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| fides | 更新 TS SDK 依赖、gateway implementation、gateway tests。 | 本票主体。 |
| fides-bff | 不改代码；作为 generated HTTP contract provider。 | 已由 LEN-154 合并。 |

## API / Contract Design

- Protobuf IDL required: no new IDL; consume LEN-153 output.
- Generated TS package: `@spark-harness/idl-ts-client v0.2.5`.
- Formal tag trace: `idl-ts-repo v0.2.5` -> `af09e09be8328d15ca9f026f65cbc980f90425d3`.
- SDK APIs:
  - `FidesBffAuthServiceApi`
  - `FidesBffIdentityProfileServiceApi`
  - `FidesBffPricingServiceApi`
  - `FidesBffLoanApplicationServiceApi`
- Base URL rule: existing runtime `bffBaseUrl` may include `/api/v1`; generated client `basePath` must strip trailing `/api/v1` because generated operations include `/api/v1/...`.
- Compatibility: HTTP path, method, request JSON, response JSON and error envelope remain controlled by generated OpenAPI output from LEN-153.

## Application Design

### Shared SDK Helper

Create an infrastructure-only helper for generated SDK usage:

- `generatedClientBasePath(baseUrl)` strips `/api/v1`.
- `timeoutFetch(fetcher, timeoutMs)` preserves current AbortController behavior.
- `requestInitWithHeaders(init, headers)` merges generated client init with gateway headers.
- `readBffErrorEnvelope(response)` preserves BFF error parsing.

The helper must not import React or application/adapters modules.

### Mobile Verification Gateway

Keep `RestOtpAuthGateway` implementing `OtpAuthGateway`. It continues to use `FidesBffAuthServiceApi`, but its middleware only injects `Idempotency-Key`. It no longer starts spans or manually writes trace headers.

### Identity Profile Gateway

Keep `RestIdentityProfileGateway` implementing `IdentityProfileGateway`. It continues to use `FidesBffIdentityProfileServiceApi`, but its middleware only injects Authorization and optional `Idempotency-Key`.

### Loan Request Gateway

Refactor `RestLoanRequestGateway` to own two generated clients:

- `FidesBffPricingServiceApi` for `createQuote`.
- `FidesBffLoanApplicationServiceApi` for create/get/patch draft.

Gateway mapping remains:

- `LoanRequestInput` -> generated loan input.
- generated quote response -> `QuoteResult`.
- generated loan application response -> `DraftResult` / `DraftDetail`.

## Data / Config / Permission

- Data model: no schema, migration or browser storage format change.
- Config: package dependency and lockfile update only.
- Permission: gateway checks access token before protected calls and injects bearer token.
- Idempotency: write requests continue to send `Idempotency-Key`.

## Observability

- Gateway-local trace span/header creation is removed.
- Browser tracing bootstrap remains untouched.
- LEN-156 owns `/api/v1` app proxy and fetch auto tracing, including trace context propagation.

## Testing Strategy

- Test-first target: `apps/fides-web/src/infrastructure/loan-request/rest-loan-request-gateway.test.ts`.
- Expected pre-implementation failure: tests that expect generated client configuration or SDK methods fail because the gateway still calls hand-written fetch URLs directly.
- Regression tests:
  - auth gateway sends idempotency and maps BFF errors without trace header expectation.
  - identity-profile gateway uses generated client and keeps auth/idempotency behavior.
  - loan-request gateway uses generated pricing and loan-application clients.
  - missing token short-circuits before network call.
  - timeout maps to `network_timeout`.
- Final commands: `pnpm test`, `pnpm lint`, `pnpm lint:deps`, `pnpm build`.

## Rollout And Rollback

- Rollout: merge fides-web once generated SDK dependency resolves and tests pass.
- Rollback: revert fides-web business commit; keep `idl-ts-repo v0.2.5` tag because it is additive.
- Release order: LEN-155 follows LEN-154 and precedes LEN-156 / LEN-157.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Generated SDK path base is misconfigured. | Tests assert generated request URL remains `/api/v1/...`. | forest |
| Removing manual trace causes temporary trace visibility gap. | Scope accepted; LEN-156 owns unified automatic tracing. | forest |
| DTO mapping misses optional generated fields. | Gateway tests cover quote, draft create/get/patch response mapping. | forest |
| Dependency cruiser blocks shared helper placement. | Place helper under `src/infrastructure/bff/` and keep dependencies inward-safe. | forest |
