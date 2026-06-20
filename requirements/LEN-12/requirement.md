---
requirement_id: "LEN-12"
owner: "Codex"
status: "approved"
created_at: "2026-06-19"
related_branch: "feature/applicant-api/LEN-12"
approved_by: "Forest"
approved_at: "2026-06-19T17:39:21+08:00"
decision: "批准 LEN-12 requirement 与 impact-analysis，允许进入设计阶段。"
---

# [BE] OTP 发送 / 校验 / 会话与限流

## Background

LEN-2 要求访客通过香港手机号接收并校验 OTP，验证成功后获得登录态并进入申请流程。当前 Spark/Lendora 后端还没有独立的 Applicant 身份服务来承载 OTP challenge、会话 token 和 Lendora applicant 身份。

先说不是什么：本需求不是 `fides-bff` 的 REST handler，也不是前端验证屏；BFF 被视为前端职责，不在本需求交付范围。本需求也不接真实短信供应商，不采集 KYC，不创建贷款申请，不实现资源越权防护中间件。

本需求要建立一个新的后端领域服务 `applicant-api`，用 Java 21 + Spring Boot 实现 Applicant 身份、OTP、会话签发和刷新，并通过 protobuf 契约供 BFF 或其他调用方后续接入。

## Goals

- R1：新增后端服务 `applicant-api`，作为 Lendora Applicant 身份服务。
- R2：新增 protobuf 服务契约，覆盖 OTP 发送、OTP 校验和 token 刷新。
- R3：支持 MVP 香港手机号规则：仅接受 `+852`，非香港号码拒绝发码。
- R4：OTP challenge 使用 Redis 存储验证码状态、过期时间、重发冷却、错误次数和临时锁定状态。
- R5：OTP 校验成功后新建或查找 Lendora applicant，并签发 `accessToken` 与 `refreshToken`。
- R6：`accessToken` 与 `refreshToken` TTL 均为 1 小时；refresh token 不允许滚动续期。
- R7：所有写请求必须携带 `Idempotency-Key`，重复请求返回首次结果，不重复发码、验证或刷新。
- R8：MVP 不接真实短信供应商，但必须明确验证码替身策略，并保证冷却、限流、过期、错误次数和幂等真实生效。
- R9：需求、影响分析、设计、任务、门禁、IDL 检查与测试证据可互相追溯。

## Non-Goals

- 不修改 `fides-bff`，不实现 BFF REST handler、BFF client 或前端验证屏。
- 不接真实短信供应商；短信渠道适配为后续需求。
- 不实现 KYC 资料采集、贷款请求、申请提交或申请状态查询。
- 不实现资源归属越权中间件；该能力属于 LEN-22 或后续安全需求。
- 不实现账号密码、第三方登录或多国家手机号支持。
- 不改变现有 `user-api` 语义，不把 Applicant 身份合并进用户域。

## User / Business Scenarios

### Scenario 1：合法香港手机号请求 OTP

Given：访客输入合法 `+852` 香港手机号，并携带新的 `Idempotency-Key`。

When：调用 OTP 发送能力。

Then：服务创建 OTP challenge，返回 `challengeId`、验证码有效期和重发冷却时间；冷却、过期和发送状态写入 Redis。

### Scenario 2：冷却期内重复发码

Given：同一手机号或同一 challenge 仍处于重发冷却期。

When：访客再次请求 OTP。

Then：服务不重复发码，并返回剩余冷却时间或等价可处理错误。

### Scenario 3：正确 OTP 校验

Given：访客持有未过期 challenge，并输入正确验证码。

When：调用 OTP 校验能力。

Then：服务新建或查找 Lendora applicant，签发 `accessToken` 和 `refreshToken`，并返回 `applicantId`。

### Scenario 4：错误或过期 OTP 校验

Given：访客输入错误验证码，或 challenge 已过期。

When：调用 OTP 校验能力。

Then：错误验证码返回明确错误；过期 challenge 返回过期错误；达到错误次数阈值后进入临时锁定。

### Scenario 5：非香港手机号请求 OTP

Given：访客输入非 `+852` 国家码。

When：调用 OTP 发送能力。

Then：服务拒绝请求，不创建 challenge，不发送验证码，并返回不支持国家码的错误。

### Scenario 6：刷新 token

Given：调用方持有未过期 refresh token，并携带新的 `Idempotency-Key`。

When：调用 token 刷新能力。

Then：服务返回新的 `accessToken`；refresh token 本身不滚动续期。

### Scenario 7：所有写请求幂等

Given：调用方使用相同 `Idempotency-Key` 重复提交同一写请求。

When：重复请求到达服务。

Then：服务返回首次结果，不重复发码、验证、创建 applicant 或刷新 token。

## Business Rules

- BR1：MVP 仅支持 `+852` 香港手机号；其他国家码必须拒绝且不发码。
- BR2：OTP challenge 必须有有效期；过期后不可校验，用户可重新获取。
- BR3：同一手机号频繁请求 OTP 必须被限流或冷却，响应应包含调用方可处理的冷却信息。
- BR4：重复请求不能导致重复发码、重复验证、重复创建 applicant 或重复刷新 token。
- BR5：多次错误 OTP 校验后必须进入临时锁定，并提示稍后再试。
- BR6：OTP 校验成功只代表“手机号已验证”，不代表已完成 KYC 或已创建贷款申请。
- BR7：OTP 校验成功后必须新建或查找 Lendora applicant，并返回稳定 `applicantId`。
- BR8：`accessToken` TTL 为 1 小时；`refreshToken` TTL 为 1 小时；refresh token 不允许滚动续期。
- BR9：所有写请求都必须携带 `Idempotency-Key`。
- BR10：Redis 是 OTP、冷却、错误次数、锁定和 token 状态的运行时存储。
- BR11：MVP 验证码替身策略必须在设计中明确；在未接真实短信前，不能让调用方误以为已经发送真实短信。

## Acceptance Criteria

- AC1：合法 `+852` 手机号请求 OTP 时，返回 `challengeId`、`expiresInSec` 和 `resendAfterSec`，并写入 Redis challenge 状态。
- AC2：冷却期内重复请求 OTP 时，不重复发码，并返回剩余冷却或等价可处理错误。
- AC3：正确且未过期 OTP 校验成功后，返回 `accessToken`、`refreshToken` 和 `applicantId`；同一手机号可查找已有 applicant。
- AC4：错误 OTP 返回验证码错误；过期 challenge 返回验证码过期；短时间多次错误后进入临时锁定。
- AC5：非 `+852` 号码请求 OTP 时返回不支持国家码错误，不创建 challenge。
- AC6：`accessToken` 与 `refreshToken` 均按 1 小时 TTL 生效；refresh token 不允许滚动续期。
- AC7：token 刷新使用未过期 refresh token 成功返回新的 `accessToken`；过期或无效 token 被拒绝。
- AC8：OTP 发送、OTP 校验、token 刷新均强制 `Idempotency-Key`；相同 key 的同一请求返回首次结果。
- AC9：新增 protobuf 契约通过 Buf lint、generate 和 breaking 检查；生成契约与业务实现可追溯。
- AC10：`applicant-api` 单元测试和服务级测试覆盖 AC1-AC8。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| MVP 验证码替身策略采用日志输出、测试固定码，还是按环境配置切换 | Backend | 设计阶段 | Open |
| OTP 有效期、重发冷却、错误次数阈值和锁定时长的具体数值 | Product / Backend | 设计阶段 | Open |
| refresh token 刷新后旧 access token 是否继续自然过期，还是需要服务端吊销记录 | Backend | 设计阶段 | Open |
| 生成契约是否只需要 Java，还是需要 Go/其他语言生成物供 BFF 后续消费 | Backend / Frontend | 设计阶段 | Open |

## Notes

- 关联 JIRA 子任务 `LEN-12`（父 Story `LEN-2` / Epic `LEN-1`）。
- 用户在 2026-06-19 会话中批准 Requirement Brief，并明确：选择新建 `applicant-api`；技术栈使用 Java + Spring Boot；不修改 `fides-bff`，BFF 视为前端职责；Redis 直接使用；refreshToken TTL 为 1 小时且不滚动续期；所有写请求都使用 `Idempotency-Key`。
- `requirement.md` 与 `impact-analysis.md` 同属需求定义阶段；`requirement-review` 门禁待二者就绪并获批后生成。
