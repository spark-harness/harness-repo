---
requirement_id: "LEN-12"
owner: "Codex"
status: "approved"
updated_at: "2026-06-19"
approved_by: "Forest"
approved_at: "2026-06-19T18:12:48+08:00"
decision: "批准 LEN-12 design，允许进入任务拆分。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, AC10 | D1: 新增 Java 21 + Spring Boot 服务 `applicant-api`，采用团队后端 Clean Architecture 分层 | 新增服务矩阵条目，独立于 `user-api` |
| R2, AC9 | D2: 在 `vesta/spark/applicant/v1` 新增 protobuf 契约，定义 ApplicantAuthService 的 OTP 发送、校验、刷新 RPC | Additive new service/RPC/message |
| R3, AC5 | D3: 在领域规则中只允许 `+852`，其他国家码返回稳定错误 | 不创建 challenge |
| R4, AC1, AC2, AC4 | D4: Redis 保存 OTP challenge、冷却、错误次数、锁定状态，默认 OTP 5 分钟、冷却 60 秒、5 次错误锁定 15 分钟 | 具体数值可配置 |
| R5, AC3 | D5: 校验成功后通过 ApplicantRepository 新建或查找 applicant，并返回稳定 `applicantId` | 需要持久化 applicant |
| R6, AC6, AC7 | D6: access token 与 refresh token 均 1 小时 TTL；refresh 不滚动续期，只签发新 access token | refresh token 自身到期后必须重新 OTP |
| R7, AC8 | D7: 所有写 RPC 要求 `idempotency_key`，应用层用 Redis 幂等记录回放首次结果 | 覆盖 send / verify / refresh |
| R8 | D8: 验证码发送通过 SmsCodeSender 端口；MVP 使用按环境配置的 test provider，本地/dev 可固定测试码，生产必须禁用 test provider | 不接真实短信 |
| R9 | D9: Harness、IDL、生成契约、服务实现、测试与门禁证据按同一 `LEN-12` 追溯 | 多仓同名分支 |

## Summary

新增 `applicant-api` 作为 Lendora Applicant 身份服务。服务只负责手机号 OTP、Applicant 身份、短期 token 和 Redis 运行时状态；它不实现 BFF REST handler，不做前端验证屏，不接真实短信供应商，也不处理贷款申请或 KYC。

设计重点是把“手机号已验证”建成后端稳定契约：调用方通过 protobuf/gRPC 发送 OTP、校验 OTP、刷新 access token；`applicant-api` 内部使用 Redis 承载 challenge、冷却、错误次数、锁定、token 状态和幂等记录，并用持久化 applicant 存储保证“新建或查找 applicant”不是 Redis TTL 内的临时语义。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| applicant-api | 新增 Java 21 + Spring Boot 服务、Clean Architecture 分层、gRPC 入站、Redis 和 applicant 持久化端口 | 承载 LEN-12 后端身份能力 |
| idl-repo | 新增 `vesta/spark/applicant/v1` protobuf 契约 | 暴露 ApplicantAuthService |
| idl-java-repo | 生成 Java message 与 gRPC stub | 供 `applicant-api` 编译和测试 |
| harness-repo | 新增 LEN-12 生命周期产物、服务矩阵条目和门禁 | 追溯与服务仓库检查 |

`fides-bff` 不在本设计修改范围内。未来前端职责方可消费 `applicant-api` 契约，但本需求不承诺 BFF 接入。

## API / Contract Design

- Protobuf IDL required: Yes。
- Proto files: `idl-repo/vesta/spark/applicant/v1/auth.proto`。
- Buf module: 沿用当前 `idl-repo/buf.yaml` v2 单模块配置。
- Generated outputs: Java message + Java gRPC stub 必需；Go 生成物由现有 `buf.gen.yaml` 生成，但本需求不消费它。
- Breaking check baseline: `buf breaking --against '.git#branch=master'`。
- Compatibility strategy: 纯新增 package/service/rpc/message，不修改现有 user 契约；旧消费者忽略新增契约后行为不变。

建议 protobuf 形状：

```proto
package vesta.spark.applicant.v1;

service ApplicantAuthService {
  rpc SendOtp(SendOtpRequest) returns (SendOtpResponse);
  rpc VerifyOtp(VerifyOtpRequest) returns (VerifyOtpResponse);
  rpc RefreshToken(RefreshTokenRequest) returns (RefreshTokenResponse);
}
```

请求必须携带幂等键。为了让幂等成为服务契约而不是某个 HTTP header 假设，三个写 RPC 的 request 都包含 `idempotency_key` 字段：

| RPC | Request | Response |
|---|---|---|
| `SendOtp` | `country_code`, `phone`, `idempotency_key` | `challenge_id`, `expires_in_sec`, `resend_after_sec` |
| `VerifyOtp` | `challenge_id`, `code`, `idempotency_key` | `access_token`, `refresh_token`, `applicant_id`, `expires_in_sec`, `refresh_expires_in_sec` |
| `RefreshToken` | `refresh_token`, `idempotency_key` | `access_token`, `expires_in_sec` |

错误语义：

| Error | gRPC code | 触发 |
|---|---|---|
| `unsupported_country` | `INVALID_ARGUMENT` | 国家码不是 `+852` |
| `idempotency_key_required` | `INVALID_ARGUMENT` | 写请求未提供幂等键 |
| `otp_cooldown_active` | `FAILED_PRECONDITION` | 冷却未结束 |
| `otp_code_invalid` | `INVALID_ARGUMENT` | 验证码错误 |
| `otp_code_expired` | `NOT_FOUND` 或 `FAILED_PRECONDITION` | challenge 不存在或已过期 |
| `otp_too_many_attempts` | `RESOURCE_EXHAUSTED` | 错误次数超限或临时锁定 |
| `token_invalid` | `UNAUTHENTICATED` | refresh token 无效 |
| `token_expired` | `UNAUTHENTICATED` | refresh token 过期 |

## Application Design

`applicant-api` 包根建议为 `com.spark.applicant`：

```text
services/backend/applicant-api/
├── src/main/java/com/spark/applicant/
│   ├── bootstrap/
│   ├── domain/
│   │   └── applicant/
│   │       ├── model/
│   │       ├── value/
│   │       └── exception/
│   ├── application/
│   │   └── applicant/
│   │       ├── usecase/
│   │       ├── command/
│   │       ├── result/
│   │       └── port/
│   ├── adapter/inbound/grpc/
│   └── infrastructure/
│       ├── persistence/
│       ├── redis/
│       ├── token/
│       └── sms/
└── src/test/java/com/spark/applicant/
```

用例：

- `SendOtpUseCase`：校验国家码和手机号格式；检查冷却/限流；生成 challenge 和 OTP；通过 `OtpChallengeRepository` 写 Redis；调用 `SmsCodeSender`。MVP `SmsCodeSender` 使用 test provider。
- `VerifyOtpUseCase`：读取 challenge；检查过期、锁定和错误次数；校验 code；通过 `ApplicantRepository` 新建或查找 applicant；通过 `TokenService` 签发 access/refresh token；写 token 状态；记录幂等结果。
- `RefreshTokenUseCase`：校验 refresh token 和 Redis token 状态；不延长 refresh token TTL；签发新的 access token。

端口：

| Port | 位置 | 实现 |
|---|---|---|
| `ApplicantRepository` | application/domain port | `infrastructure/persistence` |
| `OtpChallengeRepository` | application port | `infrastructure/redis` |
| `SessionTokenStore` | application port | `infrastructure/redis` |
| `IdempotencyRepository` | application port | `infrastructure/redis` |
| `TokenService` | application port | `infrastructure/token` |
| `SmsCodeSender` | application port | `infrastructure/sms` test provider |
| `Clock` / `IdGenerator` | application port | infrastructure or bootstrap bean |

领域模型：

- `Applicant`：稳定 applicant 身份，至少包含 `applicantId`、手机号、创建时间、更新时间。
- `PhoneNumber`：国家码 + 本地号码；MVP 只允许 `+852`。
- `OtpChallenge`：challenge ID、手机号、验证码摘要、过期时间、冷却时间、错误次数、锁定截止时间。
- `SessionToken`：token ID 或摘要、applicantId、过期时间、token 类型。

验证码存储不得保存明文 code。Redis 中保存验证码摘要或 HMAC。test provider 可以返回固定测试码，但持久状态仍按摘要校验。

## Data / Config / Permission

Data model:

- 需要 applicant 持久化表或等价存储，保证相同手机号可以查找已有 applicant。
- Redis key 使用 `applicant-api` 命名空间，例如：
  - `applicant-api:otp:challenge:{challengeId}`
  - `applicant-api:otp:phone:{countryCode}:{phoneHash}`
  - `applicant-api:token:refresh:{tokenHash}`
  - `applicant-api:idempotency:{operation}:{idempotencyKey}`
- Redis TTL：
  - OTP challenge: 默认 5 分钟。
  - resend cooldown: 默认 60 秒。
  - lock: 默认 15 分钟。
  - refresh token: 1 小时。
  - idempotency record: 至少覆盖对应业务结果可重试窗口，默认 1 小时。

Config:

- 服务端口、gRPC 端口。
- Redis 连接、超时、key prefix。
- token 签名密钥引用、issuer、audience、access TTL、refresh TTL。
- OTP TTL、resend cooldown、max attempts、lock duration。
- OTP provider mode：`test` / `disabled` / future `sms`。
- test provider code：仅允许本地/dev/test；生产环境启动时若启用 test provider 必须失败。

Permission:

- token 只表示“手机号已验证的 applicant 身份”。
- 不实现资源越权中间件，不判断贷款申请资源归属。
- 不在需求、设计、配置样例或门禁报告中保存真实密钥。

## Observability

Logs:

- 关键操作记录：send otp、verify success/failure、lock、refresh success/failure。
- 必带字段：`service=applicant-api`、`operation`、`trace_id`、`span_id`、`request_id`、`error_code`。
- 不记录手机号明文、OTP 明文、access token、refresh token、签名密钥或 Redis key 全量。
- 手机号只允许脱敏或 hash；token 只允许 hash 前缀或 token id。

Metrics:

- `applicant.otp.requests`：按 operation/result/error_code 统计。
- `applicant.otp.duration`：OTP send/verify 延迟。
- `applicant.otp.cooldown_rejections`：冷却拒绝数量。
- `applicant.otp.lockouts`：锁定数量。
- `applicant.token.refresh.requests`：刷新成功/失败。
- `applicant.redis.operations`：Redis 调用量、错误、延迟。
- 标签必须低基数：`operation`、`result`、`error_code`、`country_code` 可控；禁止手机号、applicantId、challengeId。

Tracing:

- gRPC 入站创建 SERVER span。
- Redis、数据库和未来 SMS 调用创建 CLIENT span。
- 错误 span 记录稳定 `error_code`。
- W3C trace context 由上游透传时接入；无上游时创建新 trace。

Events:

- 本需求不发布业务事件。

## Testing Strategy

测试优先验证业务行为，不锁死内部方法调用。

Unit tests:

- `PhoneNumber` 仅接受 `+852`。
- OTP challenge 过期、错误次数、锁定规则。
- token TTL 与 refresh 不滚动续期。
- 幂等 key 缺失、重复 key 回放、同 key 不同请求冲突。
- Applicant 查找已有手机号与新建 applicant。

Integration tests:

- gRPC adapter 到 use case 的请求/响应和错误码映射。
- Redis repository 的 TTL、冷却、锁定和 token 状态。
- Applicant persistence repository 的手机号唯一性和查找语义。
- test provider 模式下 OTP 替身策略可控，生产 profile 禁用 test provider。

Contract checks:

- `buf lint`
- `buf generate`
- `buf breaking --against '.git#branch=master'`

Service checks:

- `mvn test` in `services/backend/applicant-api`。
- Spring context smoke test。
- ArchUnit：`domain` 不依赖 Spring、gRPC、Redis、JPA、SQL、HTTP 或外部 SDK。

## Rollout And Rollback

Gray release:

- 先合并/发布 IDL 和生成契约。
- 再部署 `applicant-api`，默认只在内部环境或无外部流量下验证。
- BFF/前端接入另行排期，不作为本需求交付条件。

Kill switch:

- 通过配置禁用 OTP send/verify 或禁用 test provider。
- Redis 不可用时返回明确服务不可用错误，不降级为无状态 OTP。

Rollback:

- 回滚 `applicant-api` 服务代码和配置。
- 回滚新增 protobuf 和生成契约。
- 回滚服务矩阵新增 `applicant-api`。
- 清理 Redis `applicant-api:*` key。
- 如 applicant 持久化表已创建，设计实现阶段必须给出删除或保留空表的回滚策略。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| applicant 持久化模型过早设计过重 | 只保存手机号 identity 所需最小字段；贷款申请/KYC 不进入 applicant 表 | Backend |
| test provider 被误开到生产 | 启动期校验 profile；生产启用 test provider 直接 fail fast | Backend |
| token 密钥管理不清 | 设计只引用 secret 名称和配置键，不写真实密钥；实现接入环境 secret | Backend |
| Redis 不可用导致认证链路不可用 | 明确超时、错误码、健康检查和告警；不做不安全降级 | Backend |
| Go 生成物是否交付不清 | 本设计声明 Go 生成物不被本需求消费；若前端/BFF 要求，另开接入任务或在任务拆分中单独标注 | Backend / Frontend |
| BFF 不在范围导致端到端流程未闭环 | Requirement Non-Goals 和设计边界明确；本需求验收以后端契约与 applicant-api 行为为准 | Product |

