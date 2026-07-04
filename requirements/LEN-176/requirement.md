---
requirement_id: "LEN-176"
owner: "forest"
status: "approved"
created_at: "2026-07-05"
related_branch: "feature/LEN-176-quote-api-grpc-hard-cut"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - idl-repo
  - business-repo
  - gitops-repo
approved_by: "forest"
approved_at: "2026-07-05T00:35:00+08:00"
decision: "用户在 /goal 中授权处理下列任务中的任何事项，包括批准文件；批准 LEN-176 requirement 与 impact-analysis。"
---

# quote-api 提供 gRPC 报价服务端能力

## Background

当前 `quote-api` 通过 HTTP 暴露报价创建和内部报价读取能力。后续 `origination-api` 和 `fides-bff` 都要切到 quote gRPC，如果 quote 服务端能力不存在，调用方无法硬切。

它不是什么：本需求不是新增报价规则，不改变报价计算、金额单位、期限或有效期语义。

它是什么：本需求建立 quote protobuf/gRPC 服务端能力、Java SDK 生成物和运行时 9090 入口。业务 HTTP 删除必须等 `LEN-184`、`LEN-188` 调用方硬切完成，并在 `LEN-196` 最终清理阶段执行。

## Goals

- R1：在 `idl-repo` 新增 quote gRPC 契约，作为 quote 内部业务能力唯一源。
- R2：生成 Java 契约，供 quote-api 服务端实现绑定。
- R3：quote-api 新增 gRPC 入站 adapter，覆盖 CreateQuote 和 GetQuote。
- R4：保留现有业务 HTTP controller 直到调用方完成 gRPC 硬切，防止先删服务端 HTTP 导致现有链路断开。
- R5：GitOps 暴露 quote-api gRPC 端口、Consul `grpc_port` 和必要 NetworkPolicy。
- R6：保留 `/health` 和 `/ready` HTTP 健康检查。

## Non-Goals

- 不修改 fides-bff 到 quote-api 的调用方式；该调用方硬切属于 `LEN-188`。
- 不修改 origination-api 到 quote-api 的调用方式；该调用方硬切属于 `LEN-184`。
- 不删除 `lendora-shared-consul`。
- 不改变报价计算公式、数据库 schema 或对外 BFF HTTP 接口。
- 不在调用方硬切完成前删除 quote-api 业务 HTTP；最终不保留业务 HTTP fallback。

## User / Business Scenarios

### Scenario 1：内部服务创建报价

Given：调用方携带申请人身份 metadata。

When：调用 quote-api `QuoteService.CreateQuote`。

Then：quote-api 返回报价 ID、月供、APR、总利息、总应还和有效期，并持久化报价。

### Scenario 2：内部服务读取报价

Given：调用方携带报价所属申请人身份 metadata。

When：调用 quote-api `QuoteService.GetQuote`。

Then：quote-api 返回完整报价明细，用于后续申请链路校验。

### Scenario 3：旧业务 HTTP 入口等待最终清理

Given：quote-api 已完成 gRPC 服务端改造，但 fides-bff 和 origination-api 仍未完成调用方切换。

When：检查 quote-api 代码和 GitOps。

Then：gRPC 服务端和 9090 运行时入口已经存在；业务 HTTP 暂时保留，最终删除交给 `LEN-196`。

## Business Rules

- BR1：quote-api 的内部业务能力只通过 gRPC 暴露。
- BR2：protobuf 契约以 `idl-repo/vesta/lendora/quote/v1` 为唯一源。
- BR3：金额字段继续使用 decimal string，避免精度和单位语义变化。
- BR4：Java 入站 adapter 位于 `adapter/inbound/grpc`。
- BR5：业务规则继续位于 application/domain，不迁移到 adapter。
- BR6：Consul 注册必须包含 `grpc_port` metadata。
- BR7：Kubernetes Service 和 NetworkPolicy 必须允许 gRPC 9090。
- BR8：Java health/readiness HTTP 可以保留。
- BR9：`LEN-196` 之前不能做最终 HTTP 清理。

## Acceptance Criteria

- AC1：`buf lint`、`buf generate`、`buf breaking --against '.git#branch=master'` 通过。
- AC2：`idl-java-repo` 生成 quote Java message 和 `QuoteServiceGrpc`。
- AC3：quote-api gRPC adapter 测试覆盖 CreateQuote、GetQuote 和错误映射。
- AC4：quote-api 包含 gRPC adapter，同时业务 HTTP adapter 保留到 `LEN-196`，避免调用方未切换时断链。
- AC5：quote-api Consul 注册包含 `grpc_port=9090`。
- AC6：dev-1 和 sta-1 GitOps 渲染包含 gRPC container port、Service port 和 NetworkPolicy 端口。
- AC7：`/health` 和 `/ready` HTTP 健康检查保留。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| Java SDK 正式版本号由哪次 IDL CI 发布 | forest | business-repo PR 合并前 | Resolved：`idl-repo` formal tag `v0.2.6` 已发布 `spark-idl-java:0.2.6`。 |

## Notes

- 依赖后续 Story：`LEN-184`、`LEN-188`。
- 本需求不删除 fides-bff 中的 `QUOTE_HTTP_*`，也不删除 quote-api 业务 HTTP adapter；这些清理属于调用方硬切完成后的最终清理。
