---
requirement_id: "LEN-13"
owner: "Frontend / Harness"
status: "approved"
created_at: "2026-06-19"
related_branch: "feature/LEN-13-fe-otp-verification"
approved_by: "Forest"
approved_at: "2026-06-19T19:12:35+08:00"
decision: "批准 LEN-13 requirement.md 与 impact-analysis.md，可以进入 requirement-review 门禁。"
---

# [FE] 验证屏接 OTP

## Background

Lendora 申请漏斗第 1 步需要让访客通过香港手机号获取验证码并完成验证，获得仅代表“手机已验证”的登录态，然后进入贷款请求步骤。当前 `hk_loan_ui` 中已有手机验证原型，但它仍是静态 HTML 行为：数据不来自 BFF，按钮只做假异步，继续操作不会真正交给流程编排。

先说不是什么：本需求不是完整认证体系，不实现真实短信渠道，不实现后端 OTP 契约，也不采集 KYC、贷款金额、期限或申请资料。它只把 `fides` 的第 1 步验证屏变成可消费 OTP 契约、可承接 `LEN-2` AC1-AC8 的前端体验。

## Goals

- R1：在 `fides` 的手机验证屏实现 +852 香港手机号输入与本地格式校验。
- R2：消费 `auth/otp:send`，获取验证码后进入真实冷却倒计时，冷却期间不可重复发码。
- R3：使用 OTP 输入组件承载 6 位验证码输入、粘贴、删除、错误态和可达性反馈。
- R4：消费 `auth/otp:verify`，校验成功后保存会话结果，并通过 FlowController 前进到步骤 2 贷款请求。
- R5：移除原型中的 `setTimeout` 假跳转；按钮 loading、禁用和错误恢复必须由真实请求状态驱动。
- R6：覆盖验证码错误、验证码过期、限流锁定、非 +852 号码、登录态 1 小时过期后的前端表现。
- R7：本需求产物、影响分析、后续设计、任务和验收证据可互相追溯。

## Non-Goals

- 不实现 `auth/otp:send` 或 `auth/otp:verify` 后端契约；契约属于 `LEN-12`。
- 不接真实短信供应商；MVP 可先对 mock。
- 不实现完整会话与越权中间件；本需求只消费验证成功后的会话结果。
- 不实现贷款请求、KYC 资料、住宅地址、工作收入、银行账户或提交复核。
- 不修改 `aegis`；目标前端应用为 `fides`。
- 不涉及 protobuf IDL、生成契约或后端业务代码。

## User / Business Scenarios

### Scenario 1：合法手机号获取验证码

Given：访客停留在手机验证屏，并输入合法 +852 香港手机号。

When：访客点击“获取验证码”。

Then：前端调用发码接口；成功后展示 OTP 输入区，并让获取按钮进入冷却倒计时。

### Scenario 2：冷却期内重复发码

Given：验证码冷却倒计时尚未结束。

When：访客再次尝试点击“获取验证码”。

Then：按钮保持不可用，并显示剩余秒数，不发起重复发码请求。

### Scenario 3：验证码正确

Given：访客已收到验证码，验证码未过期。

When：访客输入正确验证码并提交。

Then：前端调用校验接口；成功后保存会话结果，并由 FlowController 前进到步骤 2。

### Scenario 4：验证码错误

Given：访客已进入 OTP 输入区。

When：访客输入错误验证码并提交。

Then：OTP 区展示“验证码不正确”类错误，焦点和用户停留在当前屏。

### Scenario 5：验证码过期

Given：验证码已超过有效期。

When：访客提交该验证码。

Then：OTP 区展示过期提示，并提供重新获取验证码的路径。

### Scenario 6：错误次数过多或被限流

Given：同一手机号短时间内多次错误尝试，或发码/验码接口返回限流。

When：访客继续发码或提交验证码。

Then：界面展示锁定或稍后再试提示；相关按钮按后端返回的冷却时间禁用。

### Scenario 7：非香港手机号

Given：访客输入非 +852 号码，或尝试选择非香港区号。

When：访客请求验证码。

Then：界面提示 MVP 暂仅支持香港 +852 手机号，不发起发码请求。

### Scenario 8：登录态过期

Given：访客此前已完成手机验证，但登录态超过 1 小时。

When：访客继续操作申请流程。

Then：前端提示需要重新验证，保留可保留的非敏感草稿定位，并引导回到手机验证屏。

## Business Rules

- BR1：MVP 仅支持 +852 香港手机号；非 +852 号码不发码。
- BR2：`auth/otp:send` 属非幂等用户意图，前端必须防连点；接口需要时应携带幂等键。
- BR3：冷却倒计时以发码成功或后端限流响应为准；冷却期间按钮不可用。
- BR4：验证码错误、过期、限流和锁定必须映射成就地错误，不用全页失败替代字段反馈。
- BR5：验证码校验成功后得到的登录态只代表“手机已验证”，不代表已创建贷款申请或已完成 KYC。
- BR6：登录态有效期按 `LEN-2` 为 1 小时；过期后重新验证，不应静默继续流程。
- BR7：前端不记录完整手机号、验证码或 token 到日志、埋点和错误上报。
- BR8：本屏只负责本屏输入和请求状态；下一步、会话过期回跳和草稿续填由 FlowController / API 客户端承担。

## Acceptance Criteria

- AC1：输入合法 +852 手机号并请求验证码后，界面展示 OTP 输入区，获取按钮进入冷却倒计时。
- AC2：冷却未结束时，获取按钮不可点击，并显示剩余秒数。
- AC3：输入正确且未过期的验证码后，前端保存会话结果，并进入步骤 2 贷款请求。
- AC4：输入错误验证码后，OTP 区就地提示“验证码不正确”类错误，停留当前页。
- AC5：验证码过期后提交，界面提示已过期，并允许重新获取验证码。
- AC6：短时间内多次错误尝试或接口返回限流时，界面展示锁定 / 稍后再试状态，并按冷却时间禁用相关操作。
- AC7：非 +852 号码请求验证码时，就地提示暂仅支持香港 +852 手机号，且不发码。
- AC8：登录态超过 1 小时后继续操作，前端提示重新验证并回到手机验证范围。
- AC9：原型中的假 `setTimeout` 前进逻辑不再作为成功路径；成功路径必须来自接口响应和 FlowController。
- AC10：AC1-AC8 可在 mock 接口下演示；真实后端就绪后可切换到 BFF 契约。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| `LEN-12` 的 `auth/otp:send` 和 `auth/otp:verify` 请求/响应字段是否已冻结，包括 `challengeId`、冷却秒数、错误码和 token 字段 | Backend / Frontend | 设计阶段 | Open |
| `LEN-4` 的 FlowController / API 客户端是否已提供会话保存、401 过期回跳和步骤前进接口 | Frontend | 设计阶段 | Open |
| accessToken、refreshToken 与 applicantId 在 MVP 中的前端存放策略是否以内存 + sessionStorage + httpOnly cookie 组合落地 | Frontend / Security | 设计阶段 | Open |
| mock 接口放在前端本地 handler、MSW，还是 fides-bff 缺省桩 | Frontend / Backend | 设计阶段 | Open |

## Notes

- 用户最初写作 `LNE-13` / `LNE-2`；当前 JIRA 可访问 key 为 `LEN-13` / `LEN-2`。
- `LEN-13` 是 `LEN-2` 的前端子任务，承接 `LEN-2` AC1-AC8 的界面表现。
- 参考 UI 操作和原型位于 `hk_loan_ui/1._mobile_verification/`；生产目标应用为 `business-repo/services/frontend/fides`。
- `LEN-21` 已提供 `fides-bff` REST 入口与错误 / 幂等 / 可观测约定，本需求消费该方向的前端契约，不新增 protobuf。
