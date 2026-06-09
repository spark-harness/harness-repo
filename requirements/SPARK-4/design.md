---
requirement_id: "SPARK-4"
owner: "Codex"
status: "approved"
updated_at: "2026-06-09"
approved_by: "Forest"
approved_at: "2026-06-09T00:11:56+08:00"
decision: "设计已获批准，可以进入任务执行阶段。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1 | D1: 新增 `ProfileService/UpdateUsername` gRPC RPC | 修改用户名使用独立资料服务边界 |
| R2, R6 | D2: 请求包含 `user_id`、`username`，响应返回 `user_id`、`username` | 响应只返回本次修改结果 |
| R3, R5 | D3: application 用例统一 trim 并校验 `username` | 非法输入映射为 `INVALID_ARGUMENT` |
| R4 | D4: 用户不存在由 application 用例表达，adapter 映射为 `NOT_FOUND` | 避免把不存在用户当作参数格式错误 |
| R7 | D5: tasks 和 gate JSON 引用需求、设计、IDL 证据和测试证据 | 由 Janus 校验可追溯性 |

## Summary

方案保持最小范围：protobuf 定义 ProfileService 服务边界，`user-api` 使用现有干净架构分层实现修改用户名用例。用户仓储端口扩展为支持按 `user_id` 更新用户名，当前仍使用内存实现。

本设计不是鉴权设计，也不是持久化用户资料设计。它只交付可验证的修改用户名 API，并把安全和持久化边界显式留给后续需求。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| user-api | 新增 Profile gRPC 入口、修改用户名用例、用户仓储更新能力和测试 | 满足 R1-R6 |
| aegis | 仅作为上游影响记录 | 支持服务矩阵影响面 |

## API / Contract Design

- Protobuf IDL required: yes
- Proto files: `{idl-repo}/vesta/spark/user/v1/profile.proto`
- Service: `vesta.spark.user.v1.ProfileService`
- Method: `UpdateUsername`
- Request fields: `user_id`, `username`
- Response fields: `user_id`, `username`
- Buf module: local/spark-user
- Buf config version: v2
- Generated outputs: Java / Go generated outputs follow `buf.gen.yaml`
- Breaking check baseline: `.git#branch=master`
- Compatibility strategy: 只新增 ProfileService 和消息，不修改或删除 PingService、AuthService。

## Application Design

- `UpdateUsernameCommand`: 承载用户 ID 和用户名。
- `UpdateUsernameResult`: 返回用户 ID 和更新后的用户名。
- `UpdateUsernameUseCase`: 负责输入规范化、非空校验、调用仓储更新用户名。
- `UserRepository`: 扩展为支持按 `user_id` 更新用户名。
- `InMemoryUserRepository`: 当前最小实现，同时维护按手机号和按用户 ID 的查询能力。
- `UserAccount`: 增加用户名字段，用户 ID 和手机号保持不变。

## Error Handling

| Case | Application Meaning | gRPC Status |
|---|---|---|
| `user_id` 为空 | 请求缺少目标用户 | `INVALID_ARGUMENT` |
| `username` 为空 | 请求缺少有效用户名 | `INVALID_ARGUMENT` |
| 用户不存在 | 目标用户不存在 | `NOT_FOUND` |

## Data / Config / Permission

- Data model: no database schema in this stage.
- Runtime storage: 内存用户仓储扩展用户名字段，服务重启后数据丢失。
- Config: gRPC server starter controls transport startup.
- Permission: no service-specific permission.
- Sensitive data: 不记录手机号明文和验证码。

## Observability

- Logs: no business log requirement.
- Metrics: reuse gRPC server metrics when available.
- Tracing: reuse gRPC server tracing when available.
- Events: no.

## Testing Strategy

- Use case tests cover successful update, blank `user_id`, blank `username`, and missing user.
- gRPC adapter tests cover successful response, `INVALID_ARGUMENT`, and `NOT_FOUND`.
- IDL checks cover `buf lint`, `buf generate`, and `buf breaking --against .git#branch=master`.
- Service verification runs `mvn test` in `business-repo/services/backend/user-api`.

## Rollout And Rollback

- Gray release: deploy to local or test environment first and run grpcurl/list tests.
- Kill switch: not required for this sample endpoint.
- Rollback: revert Harness SPARK-4 artifacts, IDL changes, generated contracts, and `user-api` changes on the same requirement branch.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| 三仓分支不一致导致 CR 难以追溯 | service-repo-check gate includes repo branch policy | Harness Team |
| 当前内存仓储被误认为生产持久化 | Non-Goals、Impact 和 evidence 明确当前边界 | Harness Team |
| 鉴权边界被误解 | Non-Goals 和设计明确本阶段不做真实鉴权 | Harness Team |
| IDL 证据缺失导致契约风险漏过 | Gate JSON must declare `idl_impact` and evidence | Harness Team |
