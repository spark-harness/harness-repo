---
requirement_id: "LEN-22"
owner: "core"
status: "approved"
created_at: "2026-06-28"
related_branch: "feature/LEN-22-session-principal-guard"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
approved_by: "forest"
approved_at: "2026-06-28T01:12:46+08:00"
decision: "用户授权 Agent 批准 LEN-22 requirement.md 与 impact-analysis.md，并要求先完成会话与越权防护中间件。"
---

# 会话与越权防护中间件

## Background

Lendora 登录链路已经能通过 OTP 返回 access token 和 applicantId。后续 quote、origination 和前端第二页都需要受保护接口，但当前 BFF 与 Java 服务之间还缺少统一的 Principal 上下文、身份传播和越权防护边界。

这条需求不是什么：它不是重新实现 OTP 签发/刷新，也不是让浏览器直接控制 `x-applicant-id`。

它是什么：它把浏览器 Bearer token 校验收敛到 `fides-bff`，把可信 Principal 注入服务上下文，并只由 BFF 向内部 Java 服务传播 `x-applicant-id` 与 W3C `traceparent`。

## Goals

- `fides-bff` 为受保护接口提供 Bearer access token 校验入口。
- token 校验成功后，将 `Principal{applicantId}` 写入 Go context。
- BFF 不信任外部请求传入的 `x-applicant-id`，必须由已校验 token 派生身份。
- BFF 调用内部 Java/gRPC 服务时传播 `x-applicant-id`、`traceparent` 和现有 trace/correlation metadata。
- Java Spring starter 提供 `RequestPrincipal`、`RequestPrincipalContext` 和 gRPC interceptor，供下游 use case 读取可信 applicantId。
- 受保护资源必须按 principal applicantId 做归属检查，非本人资源返回 403 且不泄露资源细节。
- 缺失、格式错误、签名无效、过期或 token type 错误时返回统一 401 错误信封。

## Non-Goals

- 不新增或修改 protobuf IDL。
- 不新增 quote-api、origination-api 或前端页面能力。
- 不改变 OTP send/verify/refresh 的匿名入口。
- 不把 `x-applicant-id` 暴露为浏览器可控制的身份来源。
- 不在本 ticket 引入 mTLS、Istio AuthorizationPolicy 或完整服务网格身份认证。
- 不记录 token、Authorization、Cookie 或其他敏感凭据。

## User / Business Scenarios

### Scenario 1: 无 token 访问受保护接口

Given: 浏览器未携带 `Authorization: Bearer <accessToken>`。

When: 浏览器请求受保护 BFF 接口。

Then: BFF 返回 401 统一错误信封，且不会调用下游 Java 服务。

### Scenario 2: 有效 token 访问本人资源

Given: access token 对应 applicantId 为 `applicant_001`。

When: 用户请求属于 `applicant_001` 的受保护资源。

Then: BFF 在 context 中建立 Principal，并向下游传播 `x-applicant-id=applicant_001` 与 `traceparent`。

### Scenario 3: 外部伪造 x-applicant-id

Given: 浏览器同时携带有效 token 和伪造的 `x-applicant-id`。

When: 请求进入 BFF。

Then: BFF 忽略外部 `x-applicant-id`，只使用 token 校验结果派生的 applicantId。

### Scenario 4: 越权访问非本人资源

Given: principal applicantId 与资源归属 applicantId 不一致。

When: 受保护 use case 校验资源归属。

Then: 请求返回 403，响应不包含非本人资源是否存在或具体内容。

### Scenario 5: Java 下游读取可信 Principal

Given: BFF 调用内部 Java/gRPC 服务并注入 `x-applicant-id`。

When: Java gRPC interceptor 处理请求。

Then: `RequestPrincipalContext` 能在请求生命周期内读取 applicantId，并在请求完成后清理。

## Business Rules

- BR1: 受保护 BFF 接口只接受 `Authorization: Bearer <accessToken>` 作为外部身份凭据。
- BR2: BFF 必须清洗或忽略浏览器传入的 `x-applicant-id`，不得把它当作认证主体。
- BR3: token 校验成功后，BFF 必须把 applicantId 写入 Principal context。
- BR4: BFF 调用内部 Java/gRPC 服务时，必须传播 `x-applicant-id` 与 `traceparent`。
- BR5: Java 下游服务只能把来自受信 BFF 的 `x-applicant-id` 当作 principal，不得从 body/path 获取用户身份作为权威。
- BR6: principal applicantId 与资源归属不一致时必须拒绝访问，并返回稳定 403 错误。
- BR7: 401/403 错误、日志和 trace 不得泄露 token、资源细节或敏感个人信息。
- BR8: traceparent 只用于链路追踪，不参与鉴权决策。

## Acceptance Criteria

- AC1: 无 Authorization、格式错误、无效、过期或 token type 错误的 access token 请求受保护接口时，返回统一 401 错误信封。
- AC2: token 校验成功后，BFF context 中可读取 `Principal.applicantId`。
- AC3: 外部请求传入的 `x-applicant-id` 被清洗或忽略，不能覆盖 token 派生身份。
- AC4: BFF 发起 gRPC 下游调用时，同时传播 `x-applicant-id` 与 `traceparent`。
- AC5: Java starter 能从 gRPC metadata 建立 `RequestPrincipalContext`，缺失 `x-applicant-id` 的受保护调用显式失败。
- AC6: principal applicantId 与资源归属不一致时返回 403，不泄露非本人资源细节。
- AC7: Go 与 Java 自动化测试覆盖上述认证、传播和越权边界。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 当前 access token 校验是否直接复用 applicant-api HMAC 格式？ | core | 2026-06-28 | resolved: 先用与 applicant-api 兼容的本地 token validator，后续可替换为专用 introspection 或 JWKS |
| 下游 Java 是否在本 ticket 强制校验调用方服务身份？ | core | 2026-06-28 | resolved: 本 ticket 只建立 principal metadata 边界，服务身份由后续 mTLS/Istio 固化 |

## Notes

- 本需求是 LEN-10、LEN-9、LEN-11 等受保护接口的前置。
- 服务矩阵当前未包含 quote-api 和 origination-api；本 ticket 只影响已存在的 `fides-bff`、`applicant-api` 和公共 starter。
