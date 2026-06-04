---
requirement_id: "SPARK-2"
owner: "Harness Team"
status: "Reviewed"
updated_at: "2026-06-03"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1 | D1: 新增 `AuthGrpcAdapter` 暴露 `AuthService/RegisterOrLoginByMobileCode` | gRPC 是唯一入口 |
| R2 | D2: `RegisterOrLoginUseCase` 在手机号不存在时创建用户 | 用户创建在 application 层编排 |
| R3 | D3: `UserRepository` 按手机号复用已有用户 | 防止重复创建 |
| R4 | D4: protobuf 请求只包含 `mobile` 和 `verification_code` | 不提供密码相关字段 |
| R5 | D5: adapter 将输入错误和验证码错误映射为 `INVALID_ARGUMENT` | 协议错误在 inbound adapter 转换 |
| R6 | D6: Gate JSON 引用需求、设计、任务和证据 hash | 由 Janus 校验 |

## Summary

方案保持最小范围：protobuf 定义 AuthService 服务边界，`user-api` 使用干净架构分层实现手机号验证码注册/登录用例。验证码校验和用户存储通过端口隔离，当前使用测试友好的内存实现，后续可以替换为短信供应商和数据库仓储。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| user-api | 新增 Auth gRPC 入口、注册/登录用例、内存用户仓储和测试验证码校验 | 满足 R1-R5 |
| aegis | 仅作为上游影响记录 | 支持服务矩阵影响面 |

## API / Contract Design

- Protobuf IDL required: yes
- Proto files: `{idl-repo}/vesta/spark/user/v1/auth.proto`
- Service: `vesta.spark.user.v1.AuthService`
- Method: `RegisterOrLoginByMobileCode`
- Request fields: `mobile`, `verification_code`
- Response fields: `user_id`, `new_user`
- Buf module: local/spark-user
- Buf config version: v2
- Generated outputs: Java / Go generated outputs follow `buf.gen.yaml`
- Breaking check baseline: `.git#branch=master`
- Compatibility strategy: 只新增 AuthService，不修改或删除 PingService。

## Application Design

- `RegisterOrLoginCommand`: 承载手机号和验证码。
- `RegisterOrLoginResult`: 返回用户 ID 和是否新用户。
- `RegisterOrLoginUseCase`: 负责输入校验、验证码校验、查找或创建用户。
- `VerificationCodeVerifier`: 验证码校验端口。
- `UserRepository`: 用户仓储端口。
- `InMemoryUserRepository`: 当前最小实现，按手机号保存用户。
- `FixedVerificationCodeVerifier`: 当前最小实现，只接受固定验证码 `123456`。

## Data / Config / Permission

- Data model: no database state in this stage.
- Config: gRPC server starter controls transport startup.
- Permission: no service-specific permission.
- Sensitive data: 不记录手机号明文和验证码。

## Observability

- Logs: no business log requirement.
- Metrics: reuse gRPC server metrics when available.
- Tracing: reuse gRPC server tracing when available.
- Events: no.

## Rollout And Rollback

- Gray release: deploy to local or test environment first and run grpcurl/list tests.
- Kill switch: not required for this sample endpoint.
- Rollback: revert Harness requirement artifacts, business service changes, and IDL changes on the same requirement branch.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| 三仓分支不一致导致 CR 难以追溯 | 4.3 gate includes repo branch policy | Harness Team |
| IDL 证据缺失导致契约风险漏过 | Gate JSON must declare `idl_impact` and evidence | Harness Team |
| 当前内存仓储被误认为生产持久化 | Non-Goals、Impact 和 evidence 明确当前边界 | Harness Team |
