---
requirement_id: "SPARK-2"
owner: "Harness Team"
status: "Reviewed"
created_at: "2026-06-03"
related_branch: "feature/SPARK-2-mobile-code-register"
---

# Mobile Code Register/Login Requirement

## Background

Spark 需要用户注册能力，但本阶段不引入密码体系。用户只能通过手机号和验证码完成注册或登录。

该需求同时验证 Harness 在真实认证类需求中的闭环：需求定义、影响面、设计、任务、IDL 契约、服务实现、测试证据和门禁报告必须能互相追溯。

## Goals

- R1: `user-api` 暴露 `AuthService/RegisterOrLoginByMobileCode` gRPC 接口。
- R2: 当手机号不存在时，接口创建用户并返回用户 ID。
- R3: 当手机号已存在时，接口返回已有用户 ID，不重复创建用户。
- R4: 接口只接受手机号和验证码，不支持密码、用户名或第三方登录。
- R5: 手机号格式不合法、验证码为空或验证码错误时返回 gRPC `INVALID_ARGUMENT`。
- R6: 需求产物、设计决策、任务拆分、门禁报告和证据可以互相追溯。

## Non-Goals

- 不引入密码登录、用户名登录、邮箱登录或第三方登录。
- 不接入真实短信发送服务。
- 不引入数据库、缓存、消息队列或持久化迁移。
- 不实现登录态、JWT、Session 或刷新令牌。
- 不修改生产部署流程。

## User / Business Scenarios

### Scenario 1

Given: 用户首次使用手机号 `13800138000` 和正确验证码。

When: 客户端调用 `vesta.spark.user.v1.AuthService/RegisterOrLoginByMobileCode`。

Then: 服务创建用户并返回新的 `user_id`，`new_user = true`。

### Scenario 2

Given: 用户已经通过手机号 `13800138000` 注册。

When: 客户端再次使用同一手机号和正确验证码调用注册/登录接口。

Then: 服务返回同一个 `user_id`，`new_user = false`。

### Scenario 3

Given: 客户端传入非法手机号。

When: 客户端调用注册/登录接口。

Then: 服务返回 gRPC `INVALID_ARGUMENT`。

### Scenario 4

Given: 客户端传入错误验证码。

When: 客户端调用注册/登录接口。

Then: 服务返回 gRPC `INVALID_ARGUMENT`。

## Business Rules

- BR1: 手机号必须去除首尾空白后校验。
- BR2: 手机号必须满足中国大陆 11 位手机号格式：以 `1` 开头，第二位为 `3-9`。
- BR3: 验证码必须去除首尾空白后校验。
- BR4: 验证码为空或验证码错误必须拒绝。
- BR5: 已存在手机号不能创建重复用户。
- BR6: 本阶段用户 ID 由服务端生成，格式必须稳定非空。
- BR7: 本需求涉及 protobuf IDL，必须保留 Buf v2 配置和契约检查证据。

## Acceptance Criteria

- AC1: `RegisterOrLoginUseCaseTest` 覆盖首次手机号注册。
- AC2: `RegisterOrLoginUseCaseTest` 覆盖重复手机号返回已有用户。
- AC3: `RegisterOrLoginUseCaseTest` 覆盖非法手机号拒绝。
- AC4: `RegisterOrLoginUseCaseTest` 覆盖错误验证码拒绝。
- AC5: `AuthGrpcAdapterTest` 覆盖 gRPC 成功注册响应。
- AC6: `AuthGrpcAdapterTest` 覆盖 gRPC `INVALID_ARGUMENT`。
- AC7: IDL 仓新增 `AuthService/RegisterOrLoginByMobileCode`，且 `buf lint` 和 `buf generate` 通过。
- AC8: 四道门禁都有 Janus 可校验的 `*.gate.json`。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 是否本阶段接入真实短信供应商 | Harness Team | 2026-06-03 | Closed: 不接入，使用可替换验证码端口和测试实现 |
| 是否本阶段返回 JWT 或 Session | Harness Team | 2026-06-03 | Closed: 不返回，本需求只完成注册/登录身份识别 |

## Notes

本需求优先交付可验证的最小认证能力。真实短信、持久化用户仓储和登录态发放留给后续需求。
