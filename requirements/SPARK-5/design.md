---
requirement_id: "SPARK-5"
owner: "Codex"
status: "approved"
updated_at: "2026-06-10"
approved_by: "Forest"
approved_at: "2026-06-10T08:27:45+08:00"
decision: "设计已获批准，可以进入任务拆分阶段。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1 | D1: 在 `ProfileService` 增加 `DisableUser` RPC | 用户状态属于用户资料/管理边界，不修改 `AuthService` 契约 |
| R2 | D2: 在 `ProfileService` 增加 `RestoreUser` RPC | 恢复与禁用保持同一服务边界 |
| R3, R7 | D3: `RegisterOrLoginUseCase` 获取用户后检查用户是否可登录 | 禁用用户映射为 `PERMISSION_DENIED` |
| R4 | D4: 恢复用户后保留原手机号和用户 ID | 再次登录返回既有用户，`new_user = false` |
| R5 | D5: 新建 `UserAccount` 默认 enabled | 不改变 SPARK-2 的首次注册语义 |
| R6, R7 | D6: 用户状态用例校验 `user_id` 并区分非法输入和不存在用户 | 非法输入映射为 `INVALID_ARGUMENT`，不存在用户映射为 `NOT_FOUND` |
| R8 | D7: tasks 和 gate JSON 引用需求、影响分析、设计、IDL 证据和测试证据 | 由 Janus 校验可追溯性 |

## Summary

方案保持最小范围：protobuf 在现有 `ProfileService` 下新增禁用和恢复用户 RPC，`user-api` 使用现有干净架构分层实现用户状态管理。登录用例继续处理手机号验证码注册/登录，但在返回用户前检查用户是否 enabled。

本设计不是权限系统，也不是会话治理方案。它只交付可验证的“禁用后不能登录、恢复后可以登录”能力；资料修改、管理员鉴权、审计、持久化和已登录会话踢出都不在本阶段内。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| user-api | 新增 Profile gRPC 用户状态入口、用户状态用例、用户仓储状态更新能力和登录拦截测试 | 满足 R1-R7 |
| aegis | 仅作为上游影响记录 | 支持服务矩阵影响面 |

## API / Contract Design

- Protobuf IDL required: yes
- Proto files: `{idl-repo}/vesta/spark/user/v1/profile.proto`
- Service: `vesta.spark.user.v1.ProfileService`
- Methods: `DisableUser`, `RestoreUser`
- Request fields: `user_id`
- Response fields: `user_id`, `enabled`
- Buf module: local/spark-user
- Buf config version: v2
- Generated outputs: Java / Go generated outputs follow `buf.gen.yaml`
- Breaking check baseline: `.git#branch=master`
- Compatibility strategy: 只新增 RPC 和消息，不修改或删除 `PingService`、`AuthService/RegisterOrLoginByMobileCode`、`ProfileService/UpdateUsername`。

## Application Design

- `UserAccount`: 增加 `enabled` 字段；新注册用户默认 `enabled = true`。
- `UserRepository`: 扩展为支持按 `user_id` 更新用户 enabled 状态。
- `InMemoryUserRepository`: 当前最小实现继续维护按手机号和按用户 ID 的索引，状态更新必须更新同一个用户对象。
- `SetUserEnabledCommand`: 承载用户 ID 和目标 enabled 状态。
- `SetUserEnabledResult`: 返回用户 ID 和更新后的 enabled 状态。
- `SetUserEnabledUseCase`: 负责输入规范化、非空校验、调用仓储禁用或恢复用户。
- `RegisterOrLoginUseCase`: 保持手机号和验证码校验逻辑不变；拿到用户后，如果用户 disabled，则拒绝登录。
- `AuthGrpcAdapter`: 将禁用用户登录错误映射为 gRPC `PERMISSION_DENIED`。
- `ProfileGrpcAdapter`: 将禁用/恢复的非法输入映射为 `INVALID_ARGUMENT`，不存在用户映射为 `NOT_FOUND`。

## Error Handling

| Case | Application Meaning | gRPC Status |
|---|---|---|
| 禁用/恢复 `user_id` 为空 | 请求缺少目标用户 | `INVALID_ARGUMENT` |
| 禁用/恢复目标用户不存在 | 目标用户不存在 | `NOT_FOUND` |
| 被禁用用户登录 | 用户存在但不允许登录 | `PERMISSION_DENIED` |
| 登录手机号或验证码非法 | 现有认证请求非法 | `INVALID_ARGUMENT` |

## Data / Config / Permission

- Data model: no database schema in this stage.
- Runtime storage: 内存用户仓储扩展 enabled 状态，服务重启后状态丢失。
- Config: gRPC server starter controls transport startup.
- Permission: no service-specific permission or admin authorization in this stage.
- Sensitive data: 不记录手机号明文和验证码。

## Observability

- Logs: no business log requirement.
- Metrics: reuse gRPC server metrics when available.
- Tracing: reuse gRPC server tracing when available.
- Events: no.

## Testing Strategy

- Use case tests cover successful disable, successful restore, blank `user_id`, missing user, disabled user login denied, and restored user login allowed.
- gRPC adapter tests cover successful disable/restore, `INVALID_ARGUMENT`, `NOT_FOUND`, and login `PERMISSION_DENIED`.
- IDL checks cover `buf lint`, `buf generate`, and `buf breaking --against .git#branch=master`.
- Service verification runs `mvn test` in `business-repo/services/backend/user-api`.

## Rollout And Rollback

- Gray release: 本地或测试环境先通过单元测试、gRPC adapter 测试和 grpcurl 验证。
- Kill switch: 不需要独立开关。
- Rollback: 回滚 Harness SPARK-5 产物、IDL 契约变更、生成契约变更和 `user-api` 用户状态实现。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| 禁用能力被误解为完整权限系统 | Non-Goals、Impact 和 Design 明确本阶段只阻止登录 | Harness Team |
| 当前内存仓储不具备生产持久性 | 影响分析和设计明确运行时存储边界，后续持久化需求替换仓储实现 | Harness Team |
| 不踢出已登录会话造成安全边界误解 | Non-Goals 和设计明确本阶段没有 JWT、Session 或会话踢出能力 | Harness Team |
| IDL 生成物与业务仓依赖不同步 | IDL 任务单独拆分，必须记录 Buf 和 Maven 测试证据 | Harness Team |
