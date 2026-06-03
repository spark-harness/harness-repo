# Spark User Current State

## Source Of Truth

- Code: `{business-repo}/services/backend/user-api`
- Protobuf IDL: `{idl-repo}/vesta/spark/user/v1/ping.proto`
- Database Schema: none
- Tests: `PingUseCaseTest`, `PingGrpcAdapterTest`
- Runtime Config: gRPC server starter defaults

## Business Meaning

`user-api` 当前承担 Spark 示例用户域的最小后端能力。`PingService` 只用于验证 gRPC 契约、干净架构分层和 Harness 生命周期闭环。

## Current States / Concepts

| Name | Meaning | User Visible | Notes |
|---|---|---:|---|
| Ping request name | 调用方传入的示例名称 | yes | 空白值必须拒绝 |
| Ping response message | 固定格式响应 | yes | `pong, {name}` |

## Allowed Transitions / Rules

| From | To | Trigger | Owner Service |
|---|---|---|---|
| request received | response returned | valid name | user-api |
| request received | INVALID_ARGUMENT | blank name | user-api |

## Invariants

- `name` 为空白时不能返回成功响应。
- gRPC 契约变更必须通过 Buf v2 配置检查。

## Downstream Consumers

| Consumer | Dependency | Compatibility Notes |
|---|---|---|
| aegis | potential gRPC/HTTP client | 目前只记录影响，不在 SPARK-1 修改 |

## Recent Decisions

| Date | Requirement | Decision |
|---|---|---|
| 2026-06-03 | SPARK-1 | 使用 Ping gRPC 需求跑通 Harness 最小闭环 |
