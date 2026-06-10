---
requirement_id: "SPARK-5"
owner: "Codex"
status: "approved"
created_at: "2026-06-10"
related_branch: "feature/SPARK-5-user-disable-restore"
approved_by: "Forest"
approved_at: "2026-06-10T08:09:36+08:00"
decision: "Requirement Brief 已在会话中批准，可以创建需求文档进入下一阶段。"
---

# User Disable And Restore Login Control Requirement

## Background

`user-api` 已支持手机号验证码注册/登录。团队需要一个最小的用户状态控制能力，用于禁用存在风险或不应继续访问系统的用户，并在风险解除后恢复其登录能力。

本需求不是完整权限系统，也不是会话管理系统。它只定义用户禁用和恢复的最小可验证能力，并确保被禁用用户不能继续通过现有登录接口登录。

## Goals

- R1: `user-api` 暴露禁用用户的 gRPC API。
- R2: `user-api` 暴露恢复用户的 gRPC API。
- R3: 被禁用用户再次调用 `AuthService/RegisterOrLoginByMobileCode` 时必须被拒绝。
- R4: 被恢复用户再次调用 `AuthService/RegisterOrLoginByMobileCode` 时可以继续登录。
- R5: 新注册用户默认可以登录。
- R6: 禁用或恢复不存在用户时，接口返回 gRPC `NOT_FOUND`。
- R7: 禁用、恢复或登录输入非法时，接口返回可测试的 gRPC 错误。
- R8: 需求产物、影响分析、设计决策、任务拆分、门禁报告和证据可以互相追溯。

## Non-Goals

- 不影响 `ProfileService/UpdateUsername` 或其他资料修改行为。
- 不引入管理员鉴权、角色权限、审计后台或操作人身份模型。
- 不引入数据库、缓存、消息队列或持久化迁移。
- 不实现 JWT、Session、刷新令牌或已登录会话踢出。
- 不修改验证码校验规则、手机号格式规则或注册用户 ID 生成规则。
- 不修改生产部署流程。

## User / Business Scenarios

### Scenario 1

Given: 用户 `user_123` 已存在且当前可以登录。

When: 客户端调用禁用用户 API，并传入 `user_id = "user_123"`。

Then: 服务将该用户标记为禁用，并返回 `user_id = "user_123"` 和禁用状态。

### Scenario 2

Given: 用户 `user_123` 已被禁用，且手机号为 `13800138000`。

When: 客户端使用手机号 `13800138000` 和正确验证码调用 `AuthService/RegisterOrLoginByMobileCode`。

Then: 服务拒绝登录并返回 gRPC `PERMISSION_DENIED`。

### Scenario 3

Given: 用户 `user_123` 已被禁用。

When: 客户端调用恢复用户 API，并传入 `user_id = "user_123"`。

Then: 服务将该用户恢复为可登录状态，并返回 `user_id = "user_123"` 和恢复后的状态。

### Scenario 4

Given: 用户 `user_123` 已恢复，且手机号为 `13800138000`。

When: 客户端使用手机号 `13800138000` 和正确验证码调用 `AuthService/RegisterOrLoginByMobileCode`。

Then: 服务允许登录并返回原有 `user_id`，不创建重复用户。

### Scenario 5

Given: 用户 `user_missing` 不存在。

When: 客户端调用禁用或恢复用户 API。

Then: 服务返回 gRPC `NOT_FOUND`。

## Business Rules

- BR1: 新注册用户默认处于可登录状态。
- BR2: `user_id` 必须去除首尾空白后校验。
- BR3: `user_id` 为空时必须拒绝。
- BR4: 禁用用户只改变该用户是否允许登录，不改变用户 ID、手机号或用户名。
- BR5: 恢复用户只改变该用户是否允许登录，不改变用户 ID、手机号或用户名。
- BR6: 被禁用用户再次使用正确手机号和验证码登录时，必须返回 `PERMISSION_DENIED`。
- BR7: 被恢复用户再次使用正确手机号和验证码登录时，必须返回已有用户 ID，且 `new_user = false`。
- BR8: 禁用已禁用用户或恢复已恢复用户必须保持幂等。
- BR9: 本阶段不要求禁用状态持久化到数据库，运行时存储边界必须在影响分析和设计中说明。
- BR10: 本需求涉及 protobuf IDL，必须保留 Buf v2 配置和契约检查证据。

## Acceptance Criteria

- AC1: protobuf IDL 新增禁用用户 RPC、恢复用户 RPC 和请求/响应消息。
- AC2: protobuf IDL 不修改或删除现有 `AuthService/RegisterOrLoginByMobileCode` 字段和语义。
- AC3: `buf lint` 在 `idl-repo` 通过。
- AC4: `buf generate` 同步生成契约输出。
- AC5: `buf breaking --against .git#branch=master` 在 `idl-repo` 通过。
- AC6: 用户状态管理用例测试覆盖成功禁用用户。
- AC7: 用户状态管理用例测试覆盖成功恢复用户。
- AC8: 用户状态管理用例测试覆盖不存在用户。
- AC9: `RegisterOrLoginUseCaseTest` 覆盖禁用用户登录被拒绝。
- AC10: `RegisterOrLoginUseCaseTest` 覆盖恢复用户后可以重新登录。
- AC11: gRPC adapter 测试覆盖禁用、恢复、`INVALID_ARGUMENT`、`NOT_FOUND` 和登录 `PERMISSION_DENIED` 映射。
- AC12: `mvn test` 在 `business-repo/services/backend/user-api` 通过。
- AC13: Janus lifecycle gate JSON 记录当前输入文件 hash 和 IDL 证据。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 禁用用户是否需要阻止登录以外的操作？ | Codex | 2026-06-10 | Closed: 只阻止登录，其他不用管。 |
| 是否本阶段实现管理员鉴权或操作审计？ | Codex | 2026-06-10 | Closed: 不实现，留给后续独立需求。 |
| 是否本阶段踢出已登录会话？ | Codex | 2026-06-10 | Closed: 不实现，本阶段没有 JWT 或 Session。 |
| 是否本阶段接入数据库持久化？ | Codex | 2026-06-10 | Closed: 不接入，沿用当前最小运行时存储边界。 |

## Notes

本需求优先交付用户禁用和恢复的最小闭环。禁用状态只约束现有手机号验证码登录入口；权限体系、审计、持久化和会话治理属于后续独立需求。
