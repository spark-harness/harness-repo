---
requirement_id: "LEN-5"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-28"
idl_impact: "no"
idl_impact_reason: "LEN-5 只做 Story 验收收口和 evidence/gate 归档，不修改 protobuf IDL、generated contracts 或 Buf 配置。"
approved_by: "forest"
approved_at: "2026-06-28T07:58:30+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-5 service-repo-check，本票只新增 Harness 验收材料，服务实现和部署复用前序已交付 ticket。"
---

# Impact Analysis

## Summary

LEN-5 验证贷款请求 Story 的端到端业务结果。它不新增运行时代码，只读取前序 ticket 交付物并补充 Story 级 evidence。

## Affected Domains

- Frontend user journey：手机号验证后的贷款请求页。
- Pricing：服务端 quote 生成、越界校验和 quote 有效性。
- Origination：草稿创建、PATCH、GET 回填和 applicant 归属。
- BFF security boundary：受保护接口鉴权、principal 和 tracing 传播。
- Harness lifecycle：新增 LEN-5 Story 验收材料和门禁。

## Affected Services

| Service | Repo | Reason | Change |
|---|---|---|---|
| fides | business-repo | Story 用户入口和 UI 行为验收对象 | no code change |
| fides-bff | business-repo | pricing/origination facade 和鉴权边界验收对象 | no code change |
| quote-api | business-repo | 服务端试算和 quote 持久化验收对象 | no code change |
| origination-api | business-repo | draft 保存和回填验收对象 | no code change |
| Harness LEN-5 lifecycle | harness-repo | 保存 Story 验收证据和 gate | docs/evidence only |

## Upstream / Downstream

- Upstream user：已认证访客。
- Runtime path：
  - `fides-web -> fides-bff POST /api/v1/pricing/quotes`
  - `fides-web -> fides-bff POST /api/v1/loan-applications`
  - `fides-web -> fides-bff PATCH /api/v1/loan-applications/{applicationId}`
  - `fides-web -> fides-bff GET /api/v1/loan-applications/{applicationId}`
  - `fides-bff -> quote-api`
  - `fides-bff -> origination-api -> quote-api`

## API / Contract Impact

- External API: no new API.
- BFF REST facade: reused.
- Java HTTP endpoints: reused.
- Protobuf IDL: no changes.
- Generated contracts: no changes.
- Error contract: existing BFF and Java error envelopes are validated through runtime evidence.

## Data Impact

- Quote DB: runtime evidence may create test quote rows.
- Application DB: runtime evidence may create draft application and idempotency rows.
- Browser storage: runtime evidence may create non-sensitive session draft pointer.
- No schema, migration, retention or backfill changes.

## Config / Permission / Observability Impact

- Config:
  - Reuses LEN-135 fides-bff downstream quote/origination config.
  - Reuses current lendora-sta service discovery.
- Permission:
  - Requires valid BFF token and applicant principal.
  - Verifies applicant ownership through BFF/origination boundary.
- Logs:
  - Evidence must not print token secret, Authorization header value or real PII.
- Tracing:
  - Verifies trace propagation using non-sensitive trace id evidence.
- Metrics:
  - No new metrics.
- Events:
  - No new events.

## Rollout And Rollback

- Rollout:
  - No runtime rollout is required for LEN-5 itself.
  - Run live Story smoke against the currently deployed lendora-sta services.
  - Record evidence and gate status.
- Rollback:
  - Reverting LEN-5 only removes Harness evidence and gates.
  - Runtime rollback remains owned by the implementing tickets if a defect is found.

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| OTP verify runtime path regresses | Full public login-through-browser E2E cannot be claimed | Re-run public OTP send/verify and block Story acceptance if protected loan-request APIs cannot be reached with the issued token | core |
| Existing deployed image drifts from merged source | Story evidence may not reflect master | Capture deployment image digests and service readiness during evidence collection | core |
| Test data pollutes STA DB | Later smoke may see extra drafts/quotes | Use LEN-5 prefixed idempotency keys and record exact quote/application IDs | core |
| Browser visual evidence tool unavailable | UI proof incomplete | Use component/build evidence plus accessible DOM or alternate browser tooling | frontend |
