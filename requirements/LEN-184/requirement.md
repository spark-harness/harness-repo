---
requirement_id: "LEN-184"
owner: "forest"
status: "approved"
created_at: "2026-07-05"
related_branch: "feature/LEN-184-origination-quote-grpc-hard-cut"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
  - gitops-repo
approved_by: "forest"
approved_at: "2026-07-05T03:32:39+08:00"
decision: "用户本轮明确授权处理 LEN-184 的任何事项，包括批准 requirement 与 impact-analysis。"
---

# origination-api 调 quote-api 硬切 gRPC

## Background

`quote-api` gRPC 服务端和 Java SDK 已由 `LEN-176` 完成，`origination-api` 服务端 gRPC 能力已由 `LEN-180` 完成。当前 `origination-api` 创建和更新贷款申请时仍通过内部 HTTP client 读取报价。

它不是什么：本需求不是修改 quote protobuf，不是删除 `lendora-shared-consul`，也不是执行 `LEN-196` 的最终 HTTP 清理。

它是什么：本需求只把 `origination-api -> quote-api` 内部业务调用从 HTTP 硬切到 gRPC，并删除该调用路径上的 HTTP fallback、HTTP base URL 和旧 HTTP client 配置。

## Goals

- R1：新增 `GrpcQuoteGateway`，通过 `QuoteService.GetQuote` 读取报价。
- R2：创建和更新贷款申请时只使用 gRPC quote gateway。
- R3：删除 `origination-api -> quote-api` 内部业务 HTTP client、fallback 和 base URL 配置。
- R4：保留 `origination-api` 对外或旧业务 HTTP controller，以及 Java health/readiness HTTP。
- R5：GitOps 不再向 `origination-api` 注入 quote HTTP base URL 或 timeout。
- R6：NetworkPolicy 允许 `origination-api` 到 `quote-api` gRPC 9090 的业务访问。
- R7：trace 验证能看到 `origination-api` gRPC client 到 `quote-api` gRPC server，且没有业务 HTTP span。

## Non-Goals

- 不修改 IDL、Buf 配置或生成契约。
- 不删除 `lendora-shared-consul`。
- 不删除 `origination-api` 自身 HTTP controller。
- 不删除 Java `/health`、`/ready` HTTP。
- 不删除 `quote-api` 业务 HTTP controller；最终清理属于 `LEN-196`。
- 不为 quote 调用保留 HTTP fallback。
- 不改变贷款申请状态机、报价匹配规则、数据库 schema 或金额语义。

## User / Business Scenarios

### Scenario 1：创建贷款申请读取报价

Given：申请人提交贷款申请，携带 quote ID。

When：`origination-api` 创建贷款申请。

Then：`origination-api` 通过 gRPC 调用 `quote-api` 读取报价，并基于返回报价创建 draft 申请。

### Scenario 2：更新贷款申请读取报价

Given：申请人已有 draft 申请，并提交新的贷款条件和 quote ID。

When：`origination-api` 更新贷款申请。

Then：`origination-api` 通过 gRPC 读取 quote，并更新申请中的贷款条件和报价快照。

### Scenario 3：内部业务 HTTP 配置清理

Given：GitOps 搜索 quote HTTP base URL。

When：检查 `origination-api` 配置和渲染结果。

Then：不再出现 `ORIGINATION_QUOTE_API_BASE_URL` 或 quote HTTP base URL；`origination-api` 自身 HTTP readiness 仍保留。

### Scenario 4：链路追踪

Given：创建或更新申请成功。

When：检查对应 trace。

Then：trace 包含 `origination-api` gRPC client 到 `quote-api` gRPC server；不存在 `origination-api -> quote-api` 业务 HTTP span。

## Business Rules

- BR1：`origination-api -> quote-api` 业务调用只允许 gRPC。
- BR2：不允许 HTTP fallback。
- BR3：`GrpcQuoteGateway` 必须透传申请人身份 metadata。
- BR4：quote gRPC `NOT_FOUND` 映射为 `QuoteNotFoundException`。
- BR5：quote gRPC `FAILED_PRECONDITION` 映射为 `QuoteExpiredException`。
- BR6：quote gRPC `PERMISSION_DENIED` 映射为 `ForbiddenException`。
- BR7：quote gRPC `UNAVAILABLE`、`UNKNOWN` 或调用异常映射为 `QuoteUnavailableException`。
- BR8：金额字段继续按 decimal string 转为 `BigDecimal`，不改变单位或舍入。
- BR9：NetworkPolicy 必须允许 gRPC 9090；不再依赖 quote 业务 HTTP 端口作为内部业务调用。

## Acceptance Criteria

- AC1：创建贷款申请通过 gRPC 读取 quote 成功。
- AC2：更新贷款申请通过 gRPC 读取 quote 成功。
- AC3：`origination-api` 不再引用或装配 `HttpQuoteGateway`。
- AC4：`origination-api` 配置不再包含 `ORIGINATION_QUOTE_API_BASE_URL`、`quote-api-base-url` 或 quote HTTP fallback。
- AC5：GitOps 搜索 quote HTTP base URL 时，`origination-api` 不再包含内部 quote HTTP 配置。
- AC6：GitOps 渲染显示 `origination-api` 与 `quote-api` 的 gRPC 9090 端口和 NetworkPolicy 可达。
- AC7：trace 证据显示 gRPC client/server span，且不存在 `origination-api -> quote-api` 业务 HTTP span。
- AC8：相关 Maven 测试、格式/静态检查、kustomize 渲染和 Janus requirement verify 有执行结果或明确失败根因。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| trace 证据是否需要 live dev-1 环境验证 | forest | 合并前 | Open：本地可验证代码和配置；live trace 需要环境可用、镜像部署和 trace backend 查询权限。 |

## Notes

- Java contract 使用 `com.spark.contract:spark-idl-java:0.2.7`。
- `LEN-184` 只删除 `origination-api -> quote-api` 内部业务 HTTP client/fallback/config，不执行 `LEN-196` 最终 HTTP 清理。
