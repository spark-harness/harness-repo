---
requirement_id: "LEN-180"
owner: "forest"
status: "approved"
created_at: "2026-07-05"
related_branch: "feature/LEN-180-origination-api-grpc-hard-cut"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - idl-repo
  - business-repo
  - gitops-repo
approved_by: "forest"
approved_at: "2026-07-05T02:30:00+08:00"
decision: "用户本轮明确要求在 LEN-180 worktree 实现 origination-api 服务端 gRPC loan application 能力、9090 运行时和 Harness 证据。"
---

# origination-api 提供 gRPC 贷款申请服务端能力

## Background

`origination-api` 已有贷款申请 HTTP adapter 和 draft step gRPC 能力。后续 `fides-bff` 要硬切到 origination gRPC，如果服务端 loan application RPC 不完整，调用方无法迁移。

它不是什么：本需求不是删除业务 HTTP，也不是修改贷款申请业务规则、报价校验规则或数据库 schema。

它是什么：本需求补齐 origination loan application gRPC 服务端 adapter、Java contract 生成物和 9090 运行时入口。业务 HTTP 最终清理由 `LEN-196` 处理。

## Goals

- R1：确认 `vesta.lendora.origination.v1` loan application protobuf 契约可用于服务端实现。
- R2：生成 Java 契约，包含 `OriginationLoanApplicationServiceGrpc` 和相关 request/response message。
- R3：origination-api 新增 gRPC 入站 adapter，覆盖 Create、Get、Update 和 AdvanceApplicationStep。
- R4：保留现有业务 HTTP adapter 到 `LEN-196`，避免调用方未切换时断链。
- R5：运行时显式暴露 gRPC 9090，Consul 注册包含 `grpc_port=9090`。
- R6：GitOps dev-1 和 sta-1 Service、Deployment、NetworkPolicy、ConfigMap 均包含 9090。

## Non-Goals

- 不修改 fides-bff 到 origination-api 的调用方式；调用方硬切属于后续 Story。
- 不删除 origination-api 业务 HTTP。
- 不修改 quote-api 调用方式。
- 不改变 loan application schema、状态机或报价匹配规则。
- 不新增外部权限模型。

## User / Business Scenarios

### Scenario 1：内部服务创建贷款申请

Given：调用方通过 gRPC metadata 携带申请人身份，并传入产品、贷款条件、报价 ID 和幂等键。

When：调用 `OriginationLoanApplicationService.CreateLoanApplication`。

Then：origination-api 创建 draft 申请并返回 application ID、状态和当前步骤。

### Scenario 2：内部服务读取贷款申请

Given：调用方是申请所属申请人。

When：调用 `OriginationLoanApplicationService.GetLoanApplication`。

Then：origination-api 返回贷款条件、接受的报价、状态和当前步骤。

### Scenario 3：内部服务更新贷款申请

Given：调用方传入同一申请的更新贷款条件、报价 ID 和幂等键。

When：调用 `OriginationLoanApplicationService.UpdateLoanApplication`。

Then：origination-api 更新 draft 贷款条件并返回申请摘要。

### Scenario 4：旧 HTTP 入口等待最终清理

Given：origination-api 已提供 gRPC 服务端能力。

When：检查代码和 GitOps。

Then：业务 HTTP 仍存在，最终删除只在 `LEN-196` 执行。

## Business Rules

- BR1：申请人身份通过 `x-applicant-id` gRPC metadata 进入服务端上下文。
- BR2：幂等键是 Create/Update 的必填 request 字段。
- BR3：金额字段继续使用 decimal string，避免精度和单位变化。
- BR4：gRPC adapter 只做协议转换和错误映射，业务规则继续在 application/domain。
- BR5：Consul metadata 必须包含 `grpc_port=9090`。
- BR6：Kubernetes Service 和 NetworkPolicy 必须允许 9090。
- BR7：HTTP `/health` 和 `/ready` 保留。
- BR8：`LEN-196` 前不能删除 origination-api 业务 HTTP。

## Acceptance Criteria

- AC1：`buf lint` 和 `buf breaking --against '.git#branch=master'` 通过。
- AC2：`idl-java-repo` 包含 origination loan application Java message 和 `OriginationLoanApplicationServiceGrpc`。
- AC3：origination-api gRPC adapter 测试覆盖 Create、Get、Update、AdvanceApplicationStep 和错误映射。
- AC4：origination-api 业务 HTTP adapter 保留。
- AC5：origination-api Consul 注册和配置包含 `grpc_port=9090`。
- AC6：dev-1 和 sta-1 GitOps 渲染包含 gRPC container port、Service port、NetworkPolicy 9090、`SPARK_ORIGINATION_CONSUL_GRPC_PORT` 和 `SPARK_GRPC_SERVER_PORT`。
- AC7：origination-api 全量测试通过。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| Java SDK 正式版本号由哪次 IDL CI 发布 | forest | business-repo PR 合并前 | Resolved：本地按 `0.2.7` 验证，正式发布需由 idl-java-repo workflow 发布同版本。 |

## Notes

- `idl-repo` 当前分支已包含 `vesta/lendora/origination/v1/loan_application.proto`；本轮验证并生成 Java contract。
- 本需求只提供服务端能力，调用方迁移和最终 HTTP 删除不在本 Story。
