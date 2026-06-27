---
requirement_id: "LEN-11"
owner: "core"
status: "approved"
updated_at: "2026-06-28"
approved_by: "forest"
approved_at: "2026-06-28T07:12:32+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-11 design，采用 fides-web clean architecture 分层新增 loan request feature。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| AC1 | D1: `LoanRequestScreen` 按 `code.html` 结构实现 | Step 2 progress、TopAppBar、form、summary、BottomNavBar |
| AC2 | D2: `FidesApplication` 管理 mobile-verification -> loan-request flow | 手机号验证成功后在同页切屏 |
| AC3, AC4 | D3: `LoanRequestController` 调 pricing gateway | 不再用本地 recalc 作为权威结果 |
| AC5, AC6, AC7 | D4: Continue 调 create/patch 并停留当前页 | 成功后只更新本地 draft pointer |
| AC8 | D5: sessionStorage 保存非敏感 application pointer，并支持 get 回填 | token 仍只在内存 |
| BR1, BR2, BR3 | D6: infrastructure HTTP gateway 只调 BFF 并注入 headers | 不直连 Java 服务 |
| BR9, BR10 | D7: 扩展 session/flow store，不持久化 access token | 401 映射到重新验证 |

## Summary

新增一个 `loan-request` 前端功能切片，按现有 clean architecture 边界分层：

- `application/loan-request`：定义 pricing/draft gateway 端口、用例输入输出和 idempotency key。
- `adapters/loan-request`：提供 controller，把 UI 操作转换成 application 命令，映射 UI error。
- `infrastructure/loan-request`：实现 BFF HTTP gateway 和 browser draft pointer store。
- `presentation/loan-request`：React screen，复刻 `code.html` 的 UI 和状态。
- `api/loan-request`：组合默认 controller。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| fides | 新增第二页 UI、controller、gateway、tests | 接真实 pricing 和 draft API |
| fides-bff | no code changes | 已提供 pricing/origination facade |

## API / Contract Design

### Pricing

```text
POST /api/v1/pricing/quotes
Authorization: Bearer <accessToken>
Idempotency-Key: <key>
traceparent: <w3c>

{ "productCode": "PIL", "amount": "50000.00", "term": 9, "purpose": "debt_consolidation" }
```

### Draft Create

```text
POST /api/v1/loan-applications
Authorization: Bearer <accessToken>
Idempotency-Key: <key>

{
  "productCode": "PIL",
  "loan": { "amount": "50000.00", "term": 9, "purpose": "debt_consolidation" },
  "quoteId": "quote_..."
}
```

### Draft Get / Patch

```text
GET /api/v1/loan-applications/{applicationId}
PATCH /api/v1/loan-applications/{applicationId}
```

No protobuf changes.

## Application Design

- `LoanRequestController.load()`:
  - reads current draft pointer.
  - if applicationId exists, calls get and maps loan + acceptedQuote to screen model.
- `LoanRequestController.price(input)`:
  - validates amount/term/purpose.
  - calls pricing gateway.
  - only latest request result is accepted by screen.
- `LoanRequestController.continue(input)`:
  - requires current quoteId.
  - if no applicationId, calls create and saves pointer.
  - if applicationId exists, calls patch and keeps pointer.
  - returns success summary without navigation instruction.

## UI Design

The UI follows `.docs/hk_loan_ui/2._loan_request_input_field/code.html`:

- fixed translucent TopAppBar.
- Step 2 of 7 progress at 28.57%.
- title `How much do you need?`.
- amount input with HKD `$` prefix.
- term select with 3/6/9/12/24 months.
- purpose select.
- estimated summary card.
- fixed bottom Continue button.

Implementation uses existing `globals.css` Tailwind tokens and local SVG icons, not external CDN icons.

## Data / Config / Permission

- Data:
  - token: memory only through `BrowserSessionStore`.
  - application pointer: sessionStorage only, no token or phone number.
  - quote snapshot: component state and draft response.
- Config:
  - uses `PublicRuntimeConfig.bffBaseUrl`.
- Permission:
  - BFF enforces applicant principal.
  - frontend sends bearer token only to configured BFF base URL.

## Observability

- Reuse browser trace header generation from existing OTP gateway pattern.
- Do not log Authorization, token, phone, or full request payload.
- UI displays stable user-safe error messages.

## Testing Strategy

- Test-first:
  - component test: verified mobile flow enters loan request screen.
  - component test: pricing success updates summary from BFF quote.
  - component test: Continue create saves draft and stays on screen.
  - component test: Continue patch existing draft and stays on screen.
  - infrastructure test: gateway sends Authorization, Idempotency-Key and trace headers.
  - store test: application pointer does not persist token.
- Verification:
  - `pnpm test`
  - `pnpm lint`
  - `pnpm lint:deps`
  - Playwright/browser smoke against local or deployed frontend when runtime is available.

## Rollout And Rollback

- Rollout:
  - merge business and Harness PRs.
  - deploy fides image through existing GitOps/image release path.
  - smoke on lendora-sta.
- Rollback:
  - revert fides-web commit and redeploy previous image.
  - no backend rollback needed.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Screen diverges from `code.html` | Compare DOM/text/layout and Playwright screenshot | core |
| stale pricing result | Track latest request sequence in screen/controller | core |
| accidental navigation on Continue | Tests assert current screen remains visible | core |
| session token persistence | Store tests assert token absent from sessionStorage | core |

