# Design

## Metadata

- Requirement ID: SPARK-1
- Owner: Harness Team
- Status: Reviewed
- Updated At: 2026-06-03

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1 | D1: `PingGrpcAdapter` 暴露 `PingService/Ping` | gRPC 是唯一入口 |
| R2 | D2: `PingUseCase` 生成 `pong, {name}` | 业务规则留在 application 层 |
| R3 | D3: adapter 把空白名称映射为 `INVALID_ARGUMENT` | 协议错误在 inbound adapter 转换 |
| R4 | D4: Gate JSON 引用需求、设计、任务和证据 hash | 由 Janus 校验 |

## Summary

方案保持最小范围：protobuf 定义服务边界，`user-api` 使用干净架构分层实现 Ping 用例，Harness 通过门禁 JSON 和证据文件验证过程可追溯。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| user-api | 新增/验证 gRPC Ping 入口、用例和测试 | 满足 R1-R3 |
| aegis | 仅作为上游影响记录 | 支持服务矩阵影响面 |

## API / Contract Design

- Protobuf IDL required: yes
- Proto files: `{idl-repo}/vesta/spark/user/v1/ping.proto`
- Buf module: local/spark-user
- Buf config version: v2
- Generated outputs: Java / Go generated outputs follow `buf.gen.yaml`
- Breaking check baseline: `.git#branch=master`
- Compatibility strategy: 只新增 Ping 示例契约，不删除字段，不复用不兼容字段号。

## Data / Config / Permission

- Data model: no database state
- Config: gRPC server starter controls transport startup
- Permission: no service-specific permission

## Observability

- Logs: no business log requirement
- Metrics: reuse gRPC server metrics when available
- Tracing: reuse gRPC server tracing when available
- Events: no

## Rollout And Rollback

- Gray release: deploy to local or test environment first and run grpcurl/list tests.
- Kill switch: not required for this sample endpoint.
- Rollback: revert Harness requirement artifacts, business service changes, and IDL changes on the same requirement branch.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| 三仓分支不一致导致 CR 难以追溯 | 4.3 gate includes repo branch policy | Harness Team |
| IDL 证据缺失导致契约风险漏过 | Gate JSON must declare `idl_impact` and evidence | Harness Team |
