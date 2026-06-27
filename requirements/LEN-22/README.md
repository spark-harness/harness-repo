# LEN-22 会话与越权防护中间件

本目录保存 LEN-22 的需求、影响分析、设计、任务、门禁和验证证据。

## 目标

- 在 `fides-bff` 统一校验 Bearer access token。
- 将 `principal.applicantId` 注入请求上下文。
- 向 Java 下游传播 `x-applicant-id` 与 `traceparent`。
- 为受保护接口提供本人资源访问和越权拒绝边界。

## 验证边界

- Go 单测覆盖 BFF auth filter、principal context、外部 `x-applicant-id` 清洗、gRPC metadata 传播。
- Java 单测覆盖 gRPC server interceptor 读取 `x-applicant-id` 并暴露 `RequestPrincipalContext`。
- 不修改 protobuf IDL，不改变 OTP 登录签发接口。
