---
requirement_id: "LEN-5"
owner: "core"
status: "approved"
updated_at: "2026-06-28"
approved_by: "forest"
approved_at: "2026-06-28T07:58:10+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-5 design，采用前序交付物矩阵和 live Story smoke 证明 AC1-AC5。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| AC1 | D1: 用 BFF pricing API 和 quote DB 证据证明服务端试算 | 不接受前端本地计算作为证据 |
| AC2 | D2: 覆盖前端就地校验和后端越界响应 | 验证不会产生可继续 quote |
| AC3 | D3: 覆盖 quote stale 状态和修改后重新试算 | Continue 必须绑定当前 loan terms 的 quoteId |
| AC4 | D4: 用 BFF create/patch、application DB 和 UI 状态证明静默保存 | 保存后仍停留贷款请求页 |
| AC5 | D5: 用 BFF get 或前端回填测试证明同一草稿可回填 | 验证 amount、term、purpose |
| BR2, BR3, BR4 | D6: Story smoke 走 BFF 受保护接口 | 传播 applicant 和 tracing |

## Summary

LEN-5 的工程设计是“验收编排”，不是新实现。它把前序 ticket 的交付边界串成一个 Story 验收包：

- 文档层：记录 LEN-5 requirement、impact、design、tasks。
- 证据层：收集前序 merge-readiness 和新的 live Story smoke。
- 门禁层：用 requirement-review、design-review、dev-entry、service-repo-check 和 merge-readiness 表达是否可交付。

## Affected Services

| Service | Role In Acceptance | Change |
|---|---|---|
| fides | 用户可见贷款请求屏、就地提示、Continue 不跳转、同草稿回填 | no code change |
| fides-bff | 受保护 pricing 和 loan application facade | no code change |
| quote-api | quote 计算、持久化、内部校验边界 | no code change |
| origination-api | 草稿创建、PATCH、GET、幂等、quote 归属和有效期校验 | no code change |

## Acceptance Design

### D1: 服务端试算

通过受保护 BFF pricing 请求创建 quote，验证响应包含 `quoteId`、`monthly`、`apr`、`totalInterest`、`totalPayable` 和 `validUntil`。如可访问 DB，同时验证 quote row 中的 applicant、amount、term、purpose 和 trace id。

### D2: 越界输入

验证前端测试覆盖金额/期限越界就地提示。运行时通过 BFF pricing 或 Continue 请求验证越界不会生成可继续 quote 或 draft。

### D3: 旧报价失效

验证前端在 loan terms 变化后清除当前 quote，并阻止 Continue。运行时通过使用不匹配 quote/loan terms 的 create 或 patch 请求确认后端仍拒绝不一致草稿。

### D4: Continue 静默保存

验证有效 quote 后 create draft 返回 `applicationId`、`status=draft`、`currentStep=loan_request`。如已有 applicationId，PATCH 同一 draft 后仍返回 draft。前端证据必须证明保存成功后不跳转、不 toast。

### D5: 同一草稿回填

验证 GET 同一 applicationId 返回已保存 loan terms 和 acceptedQuote。前端测试或浏览器 evidence 必须证明同一草稿回填 amount、term、purpose。

## Data / Config / Permission

- Data:
  - 使用 `len5_` 前缀 applicant 和 idempotency key。
  - 不记录 token secret 和 Authorization header。
- Config:
  - 使用当前 lendora-sta runtime 配置和 service discovery。
- Permission:
  - 公网 OTP verify 签发的 access token 用于验证受保护 BFF API。
  - 不信任外部请求体 applicantId。

## Observability

- 记录 trace id、HTTP status、服务 readiness 和 DB row 摘要。
- 不记录敏感 token、真实手机号或 PII。
- 若公网 OTP 或受保护业务接口回退，保留现有 trace/error 作为 BLOCKED 或 WARN，不把它伪装成 PASS。

## Testing Strategy

- Reuse前序本地证据：
  - LEN-11 frontend tests/build/UI smoke。
  - LEN-132/LEN-133 BFF facade tests。
  - LEN-10/LEN-9 Java service tests。
- Run live Story smoke:
  - readiness for fides-bff、quote-api、origination-api。
  - protected pricing quote。
  - out-of-range rejection。
  - stale quote rejection or mismatch validation。
  - draft create/patch/get。
  - DB write/read evidence where available.
- Run Harness verification:
  - `janus gate validate` for all LEN-5 gates。
  - `janus requirement verify --requirement LEN-5 --target merge --ticket-id LEN-5`。

## Rollout And Rollback

- LEN-5 does not roll out runtime resources.
- If smoke finds a defect, LEN-5 records BLOCKED and the fix must go to the owning implementation ticket or a new bug ticket.
- Reverting LEN-5 only removes Story acceptance documents and gates.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Runtime environment lacks Argo CD | Record WARN with exact missing component and use runtime functional evidence | core |
| Public login or protected API token validation regresses | Re-run OTP and protected BFF smoke with trace evidence and block if business flow cannot complete | core |
| Frontend UI cannot be visually screenshotted | Use LEN-11 component/build evidence and DOM/accessibility evidence | frontend |
