# User API Ping gRPC Requirement

## Metadata

- Requirement ID: SPARK-1
- Owner: Harness Team
- Status: Reviewed
- Created At: 2026-06-03
- Related Branch: feature/SPARK-1-harness-lifecycle

## Background

Spark 需要一个足够小但真实可验证的后端需求，用来验证 Harness 需求、影响面、设计、任务、门禁和证据之间的闭环。

当前业务仓已有 `user-api` 服务，IDL 仓已有 `vesta.spark.user.v1.PingService` 契约。这个需求把它作为最小样例，验证 gRPC 服务、IDL 影响、测试证据和服务矩阵之间能互相追溯。

## Goals

- R1: `user-api` 暴露 `PingService/Ping` gRPC 接口。
- R2: 当请求 `name` 非空时，接口返回 `pong, {name}`。
- R3: 当请求 `name` 缺失或为空白时，接口返回 `INVALID_ARGUMENT`。
- R4: 需求产物、设计决策、任务拆分、门禁报告和证据可以互相追溯。

## Non-Goals

- 不引入数据库、缓存、消息队列或外部服务调用。
- 不设计用户注册、登录或权限模型。
- 不修改生产部署流程。

## User / Business Scenarios

### Scenario 1

Given: 客户端传入 `name = "Spark"`。

When: 客户端调用 `vesta.spark.user.v1.PingService/Ping`。

Then: 服务返回 `message = "pong, Spark"`。

### Scenario 2

Given: 客户端传入空白 `name`。

When: 客户端调用 `vesta.spark.user.v1.PingService/Ping`。

Then: 服务返回 gRPC `INVALID_ARGUMENT`。

## Business Rules

- BR1: `name` 必须先去除首尾空白再判断是否为空。
- BR2: 成功响应必须使用固定格式 `pong, {name}`。
- BR3: 参数错误必须映射为 gRPC `INVALID_ARGUMENT`，不能返回普通成功响应。
- BR4: 本需求涉及 protobuf IDL，必须保留 Buf v2 配置和契约检查证据。

## Acceptance Criteria

- AC1: `PingUseCaseTest` 覆盖成功返回。
- AC2: `PingUseCaseTest` 覆盖空白名称拒绝。
- AC3: `PingGrpcAdapterTest` 覆盖 gRPC 成功响应。
- AC4: `PingGrpcAdapterTest` 覆盖 gRPC `INVALID_ARGUMENT`。
- AC5: IDL 仓 `buf.yaml` 和 `buf.gen.yaml` 均为 v2。
- AC6: 四道门禁都有 Janus 可校验的 `*.gate.json`。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 是否需要把 Ping 暴露为 HTTP 接口 | Harness Team | 2026-06-03 | Closed: 本需求只验证 gRPC |

## Notes

本需求优先服务 Harness 流程跑通，因此功能范围保持最小。
