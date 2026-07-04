---
requirement_id: "LEN-188"
owner: "forest"
status: "approved"
created_at: "2026-07-05"
related_branch: "feature/LEN-188-fides-bff-quote-grpc-hard-cut"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
  - gitops-repo
approved_by: "forest"
approved_at: "2026-07-05T04:01:22+08:00"
decision: "用户本轮明确授权处理 LEN-188 的任何事项，包括批准 requirement 与 impact-analysis。"
---

# fides-bff 调 quote-api 硬切 gRPC

## Background

`quote-api` gRPC 服务端和 Go SDK 已由 `LEN-176` 完成。当前 `fides-bff` 报价流程仍通过内部 HTTP client 调用 `quote-api`。

它不是什么：本需求不是改变用户从 `fides-web` 进入 BFF 的 HTTP 入口，不是修改 quote protobuf，也不是执行最终内部 HTTP 清理。

它是什么：本需求只把 `fides-bff -> quote-api` 内部业务调用从 HTTP 硬切到 gRPC，并删除 quote HTTP fallback、HTTP DTO、手写 trace header 覆盖和 `QUOTE_HTTP_BASE_URL` 配置。

## Goals

- R1：`fides-bff` 报价业务调用只使用 `QuoteService.CreateQuote` gRPC。
- R2：删除 quote HTTP client、HTTP DTO、HTTP fallback 和 `QUOTE_HTTP_BASE_URL`。
- R3：通过 Consul service metadata 的 `grpc_port` 发现 quote gRPC 端口。
- R4：BFF 对外 HTTP API、鉴权、响应 shape 和前端入口保持不变。
- R5：GitOps 不再注入 `QUOTE_HTTP_BASE_URL` 或 `QUOTE_HTTP_TIMEOUT`。
- R6：trace 验证能看到 BFF 到 quote-api 的 gRPC client/server span，且没有业务 HTTP span。

## Non-Goals

- 不修改 IDL、Buf 配置或生成契约。
- 不删除 `lendora-shared-consul`。
- 不改变 `fides-web -> fides-bff` 外部 HTTP 入口。
- 不切 `fides-bff -> origination-api`；该范围属于 `LEN-192`。
- 不删除 `quote-api` 业务 HTTP controller；最终清理属于 `LEN-196`。
- 不保留 quote HTTP fallback。

## User / Business Scenarios

### Scenario 1：页面报价入口不变

Given：用户在页面发起报价。

When：`fides-bff` 处理报价请求。

Then：BFF 通过 gRPC 调用 `quote-api`，并返回原有报价响应。

### Scenario 2：内部 HTTP 配置清理

Given：检查 BFF 配置和 GitOps 渲染结果。

When：搜索 `QUOTE_HTTP_BASE_URL`。

Then：`fides-bff` 不再包含该配置；只保留 quote Consul 和 gRPC timeout/plaintext 配置。

### Scenario 3：链路追踪

Given：报价请求成功。

When：检查对应 trace。

Then：trace 包含 `fides-bff` gRPC client 到 `quote-api` gRPC server；不存在 BFF 到 quote 的业务 HTTP span。

## Business Rules

- BR1：`fides-bff -> quote-api` 业务调用只允许 gRPC。
- BR2：不允许 HTTP fallback 或 `QUOTE_HTTP_BASE_URL`。
- BR3：BFF 必须把认证后的 applicant ID 作为 gRPC metadata 传给 quote-api。
- BR4：`QUOTE-PARAM-0002` 映射为 `amount_out_of_range`。
- BR5：`QUOTE-PARAM-0001` 映射为 `validation_error`。
- BR6：`UNAVAILABLE`、`DEADLINE_EXCEEDED` 和未知错误映射为 `quote_unavailable`。
- BR7：BFF 对外响应字段保持兼容。

## Acceptance Criteria

- AC1：报价 HTTP 入口返回成功，内部调用为 gRPC。
- AC2：BFF quote client 测试覆盖 gRPC request、metadata、trace ID 和错误映射。
- AC3：`fides-bff` 代码中不再有 quote HTTP client/fallback/DTO。
- AC4：`fides-bff` 配置不再包含 `QUOTE_HTTP_BASE_URL` 或 `QUOTE_HTTP_TIMEOUT`。
- AC5：GitOps 渲染结果不再包含 `QUOTE_HTTP_BASE_URL`。
- AC6：dev-1/sta-1 渲染保留 quote Consul service name 和 gRPC timeout/plaintext。
- AC7：trace 证据显示 gRPC client/server span，且不存在 BFF 到 quote 的业务 HTTP span。
- AC8：Go 测试、GitOps 渲染和 Janus requirement verify 有执行结果或明确失败根因。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| trace 证据是否需要 live dev-1 环境验证 | forest | 合并前 | Open：代码和配置已可本地验证；live trace 依赖镜像部署和 trace backend 查询权限。 |
