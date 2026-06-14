# Sub-task 示例：[BE] OTP 发送/校验/会话与限流

> 真实票：LEN-12，属于 Story LEN-2。Sub-task 讲技术实现；契约用表格；不重复业务动机（回指 Story）。

## 技术范围

实现 OTP 后端：发送、校验、会话签发。承接 LEN-2 的 BR1-BR5、AC1-AC6。

## 接口 / 契约

| 端点 | 请求 | 响应 |
|------|------|------|
| POST /api/v1/auth/otp:send | { countryCode, phone } | { challengeId, expiresInSec, resendAfterSec } |
| POST /api/v1/auth/otp:verify | { challengeId, code } | { accessToken, refreshToken, applicantId } |
| POST /api/v1/auth/token:refresh | { refreshToken } | { accessToken } |

| HTTP | code | 触发 |
|------|------|------|
| 400 | code_invalid | 验证码错误 |
| 410 | code_expired | 验证码过期 |
| 429 | too_many_attempts | 超出发送 / 尝试限流 |

## 实现要点

- Redis 存 challenge（验证码 + 过期 + 尝试次数）；冷却 resendAfter + 频率限流（落 BR1/BR2）。
- Idempotency-Key 去重，重复请求返回首次结果（落 BR3）。
- 校验通过签发短期 accessToken + refreshToken，绑定认证身份 applicantId 认证态（落 BR4）。
- MVP 验证码走桩（固定码 / 日志），但冷却 / 限流 / 过期 / 幂等真实生效（落 BR5）。

## DoD

- 单测覆盖父票 AC1-AC6（限流→AC2/AC6、过期→AC5、错误→AC4、成功→AC3）。
- 契约符合 backend/05 §2 Identity & Access；错误码符合 team/error-codes 规范。

## 依赖

依赖 LEN-3（API 约定 / 错误信封 / 幂等中间件）。属于 LEN-2。
