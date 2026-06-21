---
requirement_id: "LEN-13"
owner: "Frontend / Harness"
status: "approved"
updated_at: "2026-06-21"
approved_by: "Forest"
approved_at: "2026-06-21T14:37:14+08:00"
decision: "批准 LEN-13 design，可以进入任务拆分。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, R7, AC7 | D1: 在 `fides` 手机验证功能内建立本地表单规则，只允许 `+852` 国家码和香港手机号格式；非 `+852` 不发起发码请求 | UI 规则只做体验校验，后端仍为权威 |
| R2, AC1, AC2, AC10 | D2: 通过 `OtpAuthGateway.sendOtp` 消费 `auth/otp:send`，成功后保存 `challengeId` 并按响应冷却秒数驱动倒计时 | 冷却以服务端响应或限流响应为准 |
| R3, AC4, AC5, AC6 | D3: 用 OTP 输入视图模型承载 6 位输入、粘贴、退格、焦点、错误态和 `aria` 反馈 | 优先使用现有 UI 控件；没有时在 presentation 层实现 |
| R4, R5, AC3, AC9 | D4: 通过 `OtpAuthGateway.verifyOtp` 消费 `auth/otp:verify`；成功后由会话端口保存结果，并调用 FlowController 前进到步骤 2 | 禁止以 `setTimeout` 或纯本地状态作为成功路径 |
| R6, AC4, AC5, AC6, AC8 | D5: 建立 OTP 错误映射器，把 `code_invalid`、`code_expired`、`too_many_attempts`、`401` 等转换为就地错误、冷却状态或重验流程 | 错误信封 traceId 可用于排障，不展示或记录 PII |
| BR2, AC1, AC2 | D6: 发码操作生成用户意图级 `Idempotency-Key`，pending 期间按钮禁用；超时重试沿用同一 key | 防连点和网络重试重复发码 |
| BR6, BR7, AC8 | D7: access token 优先内存，必要时只在 `sessionStorage` 保存短期会话定位；refresh token 优先 httpOnly cookie；不记录手机号、验证码或 token | 登录态 1 小时过期后回到手机验证范围 |
| BR8, AC3, AC9 | D8: 手机验证屏只上报本屏完成结果；步骤推进、401 回跳和草稿续填由 FlowController / API 客户端端口承接 | 流程不写进屏幕组件 |
| R7 | D9: Harness 产物、设计、后续任务和证据按 `LEN-13` 互相追溯；实现前必须隔离 `business-repo` 同名分支 | 当前设计阶段只修改 harness-repo |

## Summary

本设计把 `fides` 的第 1 步手机验证屏从静态原型行为改成可消费 OTP 契约的前端功能：本地校验 `+852` 手机号，调用 BFF REST 发码和验码，按真实请求状态驱动 loading、冷却倒计时、错误恢复、会话保存和 FlowController 前进。

先说不是什么：本设计不实现 `applicant-api`、不修改 protobuf、不过问真实短信供应商、不实现完整 BFF 业务 handler，也不把贷款请求、KYC 或提交流程塞进手机验证屏。它只定义 `fides` 前端如何在干净架构边界内消费既定 OTP 能力。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| fides | 修改手机验证屏、OTP 输入、接口适配、会话保存端口、错误映射和 FlowController 接入 | 实现 LEN-13 前端验收 |
| fides-bff | 不改代码；作为 REST `/api/v1` OTP 契约提供方被消费 | 前端通过 BFF 访问后端能力 |
| applicant-api | 不改代码；其 OTP/session 能力经 BFF 暴露后被前端间接消费 | LEN-12 前置能力 |
| harness-repo | 新增 LEN-13 设计、后续任务、门禁和证据 | 生命周期追溯 |

## API / Contract Design

- Protobuf IDL required: No。
- Proto files: N/A。
- Buf module: N/A。
- Buf config version: v2（不涉及变更）。
- Generated outputs: N/A。
- Breaking check baseline: N/A。
- Compatibility strategy: 本需求消费 BFF REST 契约，不新增或修改 protobuf；前端通过 infrastructure adapter 隔离请求字段、响应字段和错误码变化。

前端面向应用层定义端口，基础设施层实现 BFF REST 调用：

| Port | Operation | Request | Result |
|---|---|---|---|
| `OtpAuthGateway` | `sendOtp` | `countryCode`, `phone`, `idempotencyKey` | `challengeId`, `expiresInSec`, `resendAfterSec` |
| `OtpAuthGateway` | `verifyOtp` | `challengeId`, `code`, `idempotencyKey` | `accessToken`, `refreshToken?`, `applicantId`, `expiresInSec`, `refreshExpiresInSec?` |
| `SessionStore` | `saveVerifiedSession` | verified session result | no user-visible output |
| `FlowControllerPort` | `advanceAfterMobileVerified` | applicant/session context | next route or step result |

BFF REST 目标：

| Action | Method / endpoint | Headers | Notes |
|---|---|---|---|
| 发码 | `POST /api/v1/auth/otp:send` | `Idempotency-Key` | 成功后进入 OTP 输入和冷却倒计时 |
| 验码 | `POST /api/v1/auth/otp:verify` | `Idempotency-Key` | 成功后保存会话并前进 |

错误映射：

| BFF error | UI mapping |
|---|---|
| `unsupported_country` or local non-`+852` validation | 手机号字段就地提示 MVP 暂仅支持香港 +852，不发码 |
| `code_invalid` | OTP 区就地提示验证码不正确，焦点留在 OTP 输入 |
| `code_expired` | OTP 区提示验证码已过期，并提供重新获取路径 |
| `too_many_attempts` / `otp_cooldown_active` / HTTP 429 | 按返回冷却秒数禁用按钮并展示稍后再试 |
| HTTP 401 after prior verification | 清理短期会话，提示重新验证，并交给 FlowController 回到步骤 1 |
| 5xx / network | 保持当前输入，恢复按钮，展示可重试错误；写操作重试沿用同一 idempotency key |

## Application Design

`fides` 已有 Clean Architecture 分层骨架。LEN-13 的实现按功能切片进入现有层，避免让 React 组件直接调用 API 或解释后端错误。

```text
services/frontend/fides/src/
├── domain/mobile-verification/
│   ├── phone-number
│   ├── otp-code
│   └── otp-error
├── application/mobile-verification/
│   ├── command
│   ├── result
│   ├── usecase
│   └── port
├── adapters/mobile-verification/
│   ├── controller
│   ├── presenter
│   └── mapper
├── infrastructure/mobile-verification/
│   ├── api
│   ├── session
│   └── idempotency
└── presentation/mobile-verification/
    ├── page
    ├── components
    ├── hooks
    └── state
```

裁剪规则：

- `domain` 只保存手机号、OTP code、冷却和错误分类等不依赖 UI / HTTP 的规则。
- `application` 编排 `sendOtp`、`verifyOtp`、`resumeWhenSessionExpired` 等用例，并定义 `OtpAuthGateway`、`SessionStore`、`FlowControllerPort`。
- `adapters` 提供 controller 和 presenter：把按钮点击、粘贴、提交等 UI 动作转换为 command，把 use case result 转成 view model。
- `infrastructure` 包装 BFF REST、session 存储、idempotency key 生成和错误信封解析。
- `presentation` 实现 React 页面、OTP 输入、按钮 loading、倒计时和字段错误展示；只调用 adapter controller。

核心状态：

| State | Owner | Persistence |
|---|---|---|
| `countryCode` / `phone` / `otpCode` | presentation form state，提交时转 command | 不持久化完整手机号 |
| `challengeId` | application result / presentation state | 可在当前会话内保存；不进日志 |
| resend cooldown | presentation state from use case result | 以后端秒数初始化，前端只做倒计时 |
| request pending / error | presentation state from presenter | 随屏幕生命周期 |
| verified session | `SessionStore` | access token 优先内存；refresh token 优先 httpOnly cookie |

FlowController 边界：

- 手机验证屏不决定步骤 2 的路由细节，只调用 `advanceAfterMobileVerified`。
- 会话过期后，API 客户端或 FlowController 触发回到手机验证范围，同时保留允许保留的非敏感草稿定位。
- 原型中的假 `setTimeout` 只可作为删除对象，不得保留在成功路径。

## Data / Config / Permission

Data model:

- 不新增数据库或 protobuf 数据结构。
- 前端不持久化验证码、完整手机号、access token、refresh token 或 BFF 响应原文。
- `challengeId`、`applicantId`、非敏感步骤定位仅在必要范围内保存。

Config:

- API base URL：沿用 `fides` / BFF 的环境配置。
- adapter mode：允许 `mock` / `real` 切换，mock 仅用于 AC1-AC8 演示和前端测试。
- 默认冷却秒数只作为兜底显示；真实冷却以 `sendOtp` 成功或限流响应为准。

Permission:

- 验证成功只代表“手机号已验证的 applicant 身份”，不代表 KYC 完成、贷款申请创建或资源授权。
- 前端不拼接他人的 applicant id；后续资源访问由 BFF / 后端校验。

## Observability

Logs:

- 前端本地日志、错误上报和调试信息不得包含完整手机号、验证码、token、refresh token 或 BFF 原始敏感响应。
- 允许记录非敏感事件名、错误码、traceId、阶段和是否 mock/real adapter。

Metrics / product events:

- 可选记录 `otp_send_clicked`、`otp_send_succeeded`、`otp_send_failed`、`otp_verify_succeeded`、`otp_verify_failed`。
- 标签必须低基数：`result`、`error_code`、`adapter_mode`；禁止手机号、验证码、token、challengeId。

Tracing:

- 前端应保留并透传 BFF 错误信封中的 `traceId`，供排障复制或上报。
- 本需求不新增后端 tracing。

Events:

- 不发布业务事件。

## Testing Strategy

测试证明用户可见行为和边界转换，不锁死内部调用次数。

Unit tests:

- `PhoneNumber` 只接受 `+852` 和香港手机号格式。
- `OtpCode` 只接受 6 位输入，并覆盖粘贴、删除、未满 6 位提交。
- 错误映射器把 `code_invalid`、`code_expired`、`too_many_attempts`、`401` 映射到稳定 UI 状态。
- idempotency key manager 在同一用户意图重试时复用 key，新用户意图生成新 key。

Adapter / application tests:

- `sendOtp` 成功后返回 OTP 输入可见、倒计时开始、按钮禁用。
- 冷却未结束时不触发第二次发码。
- `verifyOtp` 成功后调用 `SessionStore` 和 `FlowControllerPort`。
- `verifyOtp` 失败后不前进，并保留输入上下文。

Presentation / component tests:

- 非 `+852` 号码请求验证码时就地提示且不发请求。
- OTP 输入支持自动跳格、粘贴和退格。
- pending 状态禁用按钮，settled 后按结果恢复或前进。
- `aria-invalid`、错误区域和焦点移动满足现有表单模式。

E2E / mock contract tests:

- 用 mock adapter 演示 AC1-AC8：合法发码、冷却、正确验码、错误码、过期、限流、非 `+852`、登录态过期回验证。
- 真实 BFF 就绪后补充 real adapter smoke：发码和验码字段兼容、错误信封可解析。

Required commands, to be confirmed in task planning from `fides/package.json`:

- `pnpm lint:deps`
- `pnpm test` or project-equivalent component/unit test command
- `pnpm build`

## Rollout And Rollback

Gray release:

- 先以 mock adapter 在 `fides` 演示 AC1-AC8。
- BFF / applicant-api 可用后，通过环境配置切换到 real adapter。
- 若需要灰度真实 OTP，可按环境或 feature flag 控制 real adapter 可见范围。

Kill switch:

- 通过配置把 OTP adapter 切回 mock 或禁用继续操作。
- 真实 OTP 不可用时，不允许恢复假成功跳转作为验收路径。

Rollback:

- 回滚 `fides` 中 mobile verification feature、adapter 配置和相关测试。
- Harness 产物随分支回滚。
- 无数据库、IDL 或生成契约回滚。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| `LEN-12` / BFF REST 字段尚未冻结 | 通过 `OtpAuthGateway` 和 mapper 隔离 DTO；mock adapter 先固定前端行为，real adapter 单点替换 | Frontend / Backend |
| `LEN-4` FlowController 未完全就绪 | `FlowControllerPort` 先定义最小前进和会话过期回跳接口；实现任务中对接或提供临时 adapter | Frontend |
| token 存储策略不清导致安全风险 | access token 优先内存、refresh token 优先 httpOnly cookie；禁止 localStorage 保存 token | Frontend / Security |
| 冷却倒计时与服务端限流不一致 | 每次发码成功或 429 响应都用服务端返回冷却秒数重置本地倒计时 | Frontend |
| 为了演示保留假跳转 | AC9 和 D4 明确禁止；测试必须断言成功路径来自 verify 响应和 FlowController | Harness |
| `business-repo` 尚未隔离到 LEN-13 分支 | 进入任务拆分或实现前先为 `business-repo` 建立同名隔离 worktree / 分支 | Harness |
| 前端项目上下文缺失 | 记录为非阻塞上下文缺口；交付后建议新增 `context/project/spark/frontend/fides/INDEX.md` | Harness Team |
