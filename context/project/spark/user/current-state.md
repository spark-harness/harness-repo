# Spark User Current State

## Source Of Truth

- Code: `{business-repo}/services/backend/user-api`
- Protobuf IDL: `{idl-repo}/vesta/spark/user/v1/ping.proto`, `{idl-repo}/vesta/spark/user/v1/auth.proto`
- Database Schema: none
- Tests: `PingUseCaseTest`, `PingGrpcAdapterTest`, `RegisterOrLoginUseCaseTest`, `AuthGrpcAdapterTest`
- Runtime Config: gRPC server starter defaults

## Business Meaning

`user-api` 当前承担 Spark 示例用户域的最小后端能力。`PingService` 用于验证 gRPC 契约、干净架构分层和 Harness 生命周期闭环。`AuthService` 提供手机号加验证码的最小注册/登录能力。

## Current States / Concepts

| Name | Meaning | User Visible | Notes |
|---|---|---:|---|
| Ping request name | 调用方传入的示例名称 | yes | 空白值必须拒绝 |
| Ping response message | 固定格式响应 | yes | `pong, {name}` |
| Mobile auth user | 通过手机号识别的用户 | yes | 当前使用内存仓储 |
| Verification code | 手机号验证码 | yes | 当前测试实现只接受 `123456` |

## Allowed Transitions / Rules

| From | To | Trigger | Owner Service |
|---|---|---|---|
| request received | response returned | valid name | user-api |
| request received | INVALID_ARGUMENT | blank name | user-api |
| unknown mobile | user created | valid mobile and verification code | user-api |
| existing mobile | existing user returned | valid mobile and verification code | user-api |
| auth request received | INVALID_ARGUMENT | invalid mobile or verification code | user-api |

## Invariants

- `name` 为空白时不能返回成功响应。
- 注册/登录只能使用手机号和验证码，不能引入密码入口。
- 同一手机号重复注册/登录必须返回同一个用户 ID。
- 当前内存用户仓储不具备生产持久性。
- gRPC 契约变更必须通过 Buf v2 配置检查。

## Downstream Consumers

| Consumer | Dependency | Compatibility Notes |
|---|---|---|
| aegis | potential gRPC/HTTP client | 目前只记录影响，不在 SPARK-1 修改 |

## Recent Decisions

| Date | Requirement | Decision |
|---|---|---|
| 2026-06-03 | SPARK-1 | 使用 Ping gRPC 需求跑通 Harness 最小闭环 |
| 2026-06-03 | SPARK-2 | 新增手机号验证码注册/登录最小能力，不接入密码、真实短信或登录态 |
