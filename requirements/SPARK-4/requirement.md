---
requirement_id: "SPARK-4"
owner: "Codex"
status: "approved"
created_at: "2026-06-09"
related_branch: "feature/SPARK-4-update-username"
approved_by: "Forest"
approved_at: "2026-06-09T00:01:10+08:00"
decision: "Requirement Brief 已在会话中批准，可以创建需求文档进入下一阶段。"
---

# User API Update Username Requirement

## Background

`user-api` 已提供手机号验证码注册/登录能力，但当前用户资料只包含用户 ID 和手机号。客户端需要一个明确的服务端 API 来修改用户展示名。

本需求不是认证体系升级，也不是用户资料持久化改造。它只定义修改用户名的最小可验证能力，并保持需求、契约、实现、测试证据和门禁可追溯。

## Goals

- R1: `user-api` 暴露修改用户名的 gRPC API。
- R2: 客户端可以通过 `user_id` 和新的 `username` 请求修改用户名。
- R3: `username` 去除首尾空白后不能为空。
- R4: 用户不存在时，接口返回 gRPC `NOT_FOUND`。
- R5: `username` 非法时，接口返回 gRPC `INVALID_ARGUMENT`。
- R6: 修改成功后，接口返回 `user_id` 和更新后的 `username`。
- R7: 需求产物、影响分析、设计决策、任务拆分、门禁报告和证据可以互相追溯。

## Non-Goals

- 不引入 JWT、Session、登录态校验或权限模型。
- 不引入数据库、缓存、消息队列或持久化迁移。
- 不修改手机号验证码注册/登录语义。
- 不实现用户名唯一性校验、敏感词审核或昵称推荐。
- 不实现头像、性别、生日、简介等其他用户资料字段。
- 不修改生产部署流程。

## User / Business Scenarios

### Scenario 1

Given: 用户 `user_123` 已存在。

When: 客户端调用修改用户名 API，并传入 `username = "Alice"`。

Then: 服务将该用户的用户名更新为 `Alice`，并返回 `user_id = "user_123"` 和 `username = "Alice"`。

### Scenario 2

Given: 用户 `user_123` 已存在。

When: 客户端调用修改用户名 API，并传入只包含空白字符的 `username`。

Then: 服务拒绝请求并返回 gRPC `INVALID_ARGUMENT`。

### Scenario 3

Given: 用户 `user_missing` 不存在。

When: 客户端调用修改用户名 API。

Then: 服务返回 gRPC `NOT_FOUND`。

## Business Rules

- BR1: `user_id` 必须去除首尾空白后校验。
- BR2: `user_id` 为空时必须拒绝。
- BR3: `username` 必须去除首尾空白后校验。
- BR4: `username` 为空时必须拒绝。
- BR5: 修改用户名只影响目标用户的用户名，不改变手机号、用户 ID 或注册状态。
- BR6: 本阶段不校验用户名唯一性。
- BR7: 本阶段不要求用户名持久化到数据库，运行时存储边界必须在影响分析和设计中说明。
- BR8: 本需求涉及 protobuf IDL，必须保留 Buf v2 配置和契约检查证据。

## Acceptance Criteria

- AC1: protobuf IDL 新增修改用户名 RPC 和请求/响应消息。
- AC2: `buf lint` 在 `idl-repo` 通过。
- AC3: `buf generate` 同步生成契约输出。
- AC4: `UpdateUsernameUseCaseTest` 覆盖成功修改用户名。
- AC5: `UpdateUsernameUseCaseTest` 覆盖空用户名拒绝。
- AC6: `UpdateUsernameUseCaseTest` 覆盖用户不存在。
- AC7: gRPC adapter 测试覆盖成功响应。
- AC8: gRPC adapter 测试覆盖 `INVALID_ARGUMENT` 和 `NOT_FOUND` 映射。
- AC9: `mvn test` 在 `business-repo/services/backend/user-api` 通过。
- AC10: Janus lifecycle gate JSON 记录当前输入文件 hash 和 IDL 证据。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 是否本阶段做真实鉴权？ | Codex | 2026-06-09 | Closed: 不做，API 直接接收 `user_id`。 |
| 是否本阶段要求用户名唯一？ | Codex | 2026-06-09 | Closed: 不要求，留给后续需求。 |
| 是否本阶段接入数据库持久化？ | Codex | 2026-06-09 | Closed: 不接入，沿用当前最小运行时存储边界。 |

## Notes

本需求优先交付修改用户名的最小闭环。鉴权、持久化、用户名唯一性和内容审核都属于后续独立需求。

