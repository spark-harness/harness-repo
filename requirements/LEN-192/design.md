---
requirement_id: "LEN-192"
owner: "forest"
status: "approved"
updated_at: "2026-07-05"
approved_by: "forest"
approved_at: "2026-07-05T05:41:18+08:00"
decision: "用户本轮明确授权批准 LEN-192 design，允许进入任务拆分和实现准备。"
---

# Design

## Requirement Traceability

| Requirement | Design Decision |
|---|---|
| R1, AC1 | D1：BFF 创建申请通过统一 origination gRPC client 调用 `origination-api`。 |
| R2, AC2 | D1：查询申请复用同一个 gRPC client，不保留 HTTP 查询路径。 |
| R3, AC3 | D1：更新申请复用同一个 gRPC client，不保留 HTTP patch 路径。 |
| R4, AC4 | D1：步骤推进复用同一个 gRPC client，不再维护单独 draft client。 |
| R5, AC5, AC6 | D2：删除 origination HTTP client、DTO、fallback 和 HTTP 配置入口。 |
| R7, AC7 | D3：GitOps 删除 HTTP base URL，保留 gRPC target/timeout/plaintext 配置。 |
| R8, AC8 | D4：验证 trace 只出现 BFF 到 origination 的 gRPC span。 |

## Summary

`fides-bff` 保持对前端的 HTTP API 不变。内部将 origination 出站调用收口到一个 gRPC adapter，由该 adapter 负责 service discovery、metadata、错误映射和响应转换。

## Affected Services

| Service | Change |
|---|---|
| fides-bff | 替换 origination HTTP client 和部分 draft gRPC client。 |
| origination-api | 被调用方，使用既有 gRPC server，不修改。 |
| fides-bff GitOps | 删除 origination HTTP env，保留 gRPC env。 |

## API / Contract Design

- 不修改 protobuf。
- BFF 消费 `LEN-180` 已发布的 origination Go SDK formal 版本。
- BFF 对外 HTTP request/response 保持兼容。
- gRPC metadata 必须携带 applicant identity，语义对齐现有 HTTP 鉴权边界。

## Application Design

### D1：统一 origination gRPC client

新增或收口一个 BFF 出站 adapter，覆盖：

- create application
- get application
- patch/update application
- advance application step

旧 HTTP client、HTTP DTO 和部分 gRPC draft client 不再作为业务路径存在。

### D2：硬切删除 HTTP 包袱

删除 BFF 内部 origination HTTP base URL、timeout、HTTP trace header 注入和 fallback。外部 BFF HTTP API 不受影响。

### D3：运行时配置

GitOps 只提供 origination gRPC 发现和调用配置：

- service name / target
- timeout
- plaintext/TLS mode

不得继续注入 `ORIGINATION_HTTP_BASE_URL`。

### D4：错误和可观测性

gRPC status 映射到现有 BFF 错误边界。依赖失败日志只记录 error code、dependency、grpc status 和 latency，不记录 payload 或 token。

Trace 应显示 `fides-bff` gRPC client span 到 `origination-api` server span。

## Data / Config / Permission

- Data: no schema or migration.
- Config: remove origination HTTP config; retain origination gRPC config.
- Permission: BFF namespace must reach origination-api gRPC port 9090.
- Consul: retain `lendora-shared-consul`; gRPC discovery still depends on service metadata.

## Testing Strategy

- Add BFF adapter tests for create/get/patch/advance request conversion, applicant metadata and error mapping.
- Run `go test ./...` in `apps/fides-bff`.
- Run contract dependency scan for `apps/fides-bff/go.mod`.
- Render GitOps dev-1 and sta-1 overlays after GitOps branch is based on merged LEN-184/LEN-188 config.
- Run Janus gate validation and `janus requirement verify --target merge`.

## Rollout And Rollback

- Roll out after LEN-184 and LEN-188 images/config are deployable.
- dev-1 first, then sta-1.
- Rollback reverts BFF image and GitOps config together.
- The new implementation does not include HTTP fallback.

## Risks

| Risk | Mitigation |
|---|---|
| gRPC adapter misses one old HTTP behavior | Adapter tests cover create/get/patch/advance and error mapping. |
| GitOps still carries HTTP env | Rendered search must prove `ORIGINATION_HTTP_BASE_URL` is gone. |
| live environment cannot be queried | Record cluster or trace backend blocker and do not claim live smoke. |
