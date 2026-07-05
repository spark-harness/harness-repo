---
requirement_id: "LEN-192"
owner: "forest"
status: "approved"
created_at: "2026-07-05"
related_branch: "feature/LEN-192-fides-bff-origination-grpc-hard-cut"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
  - gitops-repo
approved_by: "forest"
approved_at: "2026-07-05T05:38:09+08:00"
decision: "用户本轮明确授权处理 LEN-192 的任何事项，包括批准 requirement 与 impact-analysis。"
---

# fides-bff 调 origination-api 全量硬切 gRPC

## Background

`origination-api` gRPC 服务端和 Go SDK 已由 `LEN-180` 完成。当前 `fides-bff` 到 `origination-api` 的申请链路仍存在 HTTP client 和部分 gRPC draft client 混用。

它不是什么：本需求不是改变 `fides-web -> fides-bff` 的用户入口，不是修改 origination protobuf，也不是执行 `LEN-196` 的最终内部 HTTP 清理。

它是什么：本需求只把 `fides-bff -> origination-api` 的 Create、Get、Patch、Advance 申请能力统一硬切到 gRPC，并删除 BFF 侧 origination HTTP client、HTTP DTO、HTTP base URL 和 HTTP fallback。

## Goals

- R1：`fides-bff` 创建贷款申请只调用 `origination-api` gRPC。
- R2：`fides-bff` 查询贷款申请只调用 `origination-api` gRPC。
- R3：`fides-bff` 更新贷款申请只调用 `origination-api` gRPC。
- R4：`fides-bff` 推进申请步骤只调用 `origination-api` gRPC。
- R5：删除 BFF 侧 origination HTTP client、HTTP DTO、HTTP fallback、手写 HTTP trace header 覆盖和 `ORIGINATION_HTTP_BASE_URL` 配置。
- R6：保留 `fides-web -> fides-bff` 外部 HTTP API、鉴权、响应 shape 和页面流程。
- R7：GitOps 不再向 `fides-bff` 注入 origination HTTP base URL。
- R8：trace 验证能看到 BFF 到 origination-api 的 gRPC client/server span，且没有业务 HTTP span。

## Non-Goals

- 不修改 IDL、Buf 配置或生成契约。
- 不删除 `lendora-shared-consul`。
- 不改变 `fides-web -> fides-bff` 外部 HTTP 入口。
- 不改变贷款申请业务流程、页面字段、状态机或数据库 schema。
- 不删除 `origination-api` 自身 HTTP controller 或 Java health/readiness HTTP。
- 不保留 origination HTTP fallback。
- 不执行 `LEN-196` 的最终内部 HTTP 配置和端口清理。

## User / Business Scenarios

### Scenario 1：创建申请入口不变

Given：用户在页面提交报价后创建贷款申请。

When：`fides-bff` 处理创建申请请求。

Then：BFF 通过 gRPC 调用 `origination-api` 创建申请，并保持对前端的响应兼容。

### Scenario 2：查询或更新申请

Given：用户已有 draft 申请。

When：用户查询申请详情或更新贷款条件。

Then：BFF 通过 gRPC 调用 `origination-api` 查询或更新申请，不再走内部 HTTP。

### Scenario 3：推进申请步骤

Given：用户保存身份资料并推进申请步骤。

When：BFF 调用 origination 推进能力。

Then：步骤推进通过 gRPC 完成，错误响应保持前端兼容。

### Scenario 4：内部 HTTP 配置清理

Given：检查 BFF 配置和 GitOps 渲染结果。

When：搜索 `ORIGINATION_HTTP_BASE_URL`。

Then：`fides-bff` 不再包含该配置；只保留 origination Consul 和 gRPC timeout/plaintext 配置。

### Scenario 5：链路追踪

Given：申请流程请求成功。

When：检查对应 trace。

Then：trace 包含 `fides-bff` gRPC client 到 `origination-api` gRPC server；不存在 BFF 到 origination 的业务 HTTP span。

## Business Rules

- BR1：`fides-bff -> origination-api` 业务调用只允许 gRPC。
- BR2：不允许 HTTP fallback 或 `ORIGINATION_HTTP_BASE_URL`。
- BR3：现有部分 gRPC draft client 必须收口到统一 origination gRPC client。
- BR4：BFF 必须把认证后的 applicant ID 作为 gRPC metadata 传给 origination-api。
- BR5：BFF 对外 HTTP 响应字段和错误语义保持兼容。
- BR6：origination gRPC 的 not found、forbidden、validation 和 unavailable 类错误必须映射到现有 BFF 错误边界。
- BR7：GitOps 渲染不得再出现 BFF 到 origination 的业务 HTTP base URL。

## Acceptance Criteria

- AC1：用户创建贷款申请成功，内部调用为 gRPC。
- AC2：用户查询贷款申请成功，内部调用为 gRPC。
- AC3：用户更新贷款申请成功，内部调用为 gRPC。
- AC4：用户保存身份资料并推进步骤成功，内部调用为 gRPC。
- AC5：`fides-bff` 代码中不再有 origination HTTP client、HTTP DTO、HTTP fallback 或手写 HTTP trace header 覆盖。
- AC6：`fides-bff` 配置不再包含 `ORIGINATION_HTTP_BASE_URL` 或 origination HTTP timeout。
- AC7：GitOps dev-1/sta-1 渲染不再包含 origination HTTP base URL，并保留 origination gRPC target/timeout/plaintext 配置。
- AC8：trace 证据显示 gRPC client/server span，且不存在 BFF 到 origination 的业务 HTTP span。
- AC9：Go 测试、contract dependency scan、GitOps 渲染和 Janus requirement verify 有执行结果或明确失败根因。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| live trace 证据是否需要在 dev-1 镜像部署后补齐 | forest | 合并前 | Open：本地可验证代码和配置；live trace 依赖镜像发布、GitOps 同步和 trace backend 查询权限。 |

## Notes

- Go contract 使用 `LEN-180` 已发布的 origination gRPC SDK。
- `LEN-192` 只删除 `fides-bff -> origination-api` 内部业务 HTTP client/fallback/config，不执行 `LEN-196` 最终 HTTP 清理。
