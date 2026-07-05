---
requirement_id: "LEN-192"
analyst: "forest"
status: "approved"
updated_at: "2026-07-05"
idl_impact: "no"
idl_impact_reason: "origination-api gRPC 服务端和 Go SDK 已由 LEN-180 完成；本需求只消费既有 origination gRPC 契约。"
approved_by: "forest"
approved_at: "2026-07-05T05:41:18+08:00"
decision: "用户本轮明确授权批准 LEN-192 impact-analysis 和服务仓库检查，确认 fides-bff、origination-api、business-repo、gitops-repo 和 idl-repo 拓扑。"
---

# Impact Analysis

## Summary

本需求把 `fides-bff` 到 `origination-api` 的申请创建、查询、更新和步骤推进从内部 HTTP 加部分 gRPC 统一改为 gRPC。影响集中在 BFF origination client、配置模型、GitOps 环境变量、Go contract 版本和 trace 验证。

## Affected Domains

| Domain | Impact |
|---|---|
| frontend | BFF 对外 HTTP API 保持不变，内部出站链路切换 |
| applicant | `origination-api` 既有 gRPC server 被调用 |

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides-bff | `{business-repo}/apps/fides-bff` | 替换 origination 出站 client 和配置 | Yes, consume only |
| origination-api | `{business-repo}/apps/origination-api` | 既有 gRPC server 被调用，本需求不修改 | Yes, no change |
| fides-bff GitOps | `{gitops-repo}/apps/fides-bff` | 删除 origination HTTP config，保留 origination gRPC config | No |

## Upstream / Downstream

- Upstream: `fides-web` 仍通过 BFF HTTP API 调用申请流程，本需求不修改。
- Downstream: `fides-bff -> origination-api` 从 HTTP/部分 gRPC 混用改为全量 gRPC。
- Dependent chain: `origination-api -> quote-api` 的 gRPC 硬切由 `LEN-184` 完成后，完整申请流程才具备端到端 gRPC 后端链路。

## API / Contract Impact

- IDL change: none.
- Go module: consume existing `github.com/spark-harness/idl-go-repo` origination package from formal version.
- RPC coverage: create application, get application, patch/update application, advance application step.
- Compatibility risk: no protobuf change；runtime risk is Consul `grpc_port` metadata, NetworkPolicy reachability, and BFF error mapping compatibility.

## Generated Contract Impact

- 不修改 `idl-repo` 或 generated contract 仓库。
- `business-repo/apps/fides-bff/go.mod` 只能使用 formal contract 版本。
- `spark/contract-dependency-scan` 必须通过 release-bound formal-only 检查。

## Data / Storage

- 不修改数据库 schema。
- 不新增 migration。
- 不改变缓存、Redis、Postgres 或业务状态持久化语义。

## Config / Permission / Observability

- Removed config: `ORIGINATION_HTTP_BASE_URL` 和 origination HTTP timeout。
- Retained/required config: origination service discovery target, gRPC timeout, plaintext/TLS mode。
- Permission: BFF namespace must be allowed to call origination-api TCP 9090.
- Tracing: BFF 出站 span 应为 gRPC client span，目标 RPC 指向 origination service；不得再出现 BFF 到 origination 的业务 HTTP span。
- Logs: 不记录 applicant PII、请求体或 metadata token；依赖错误日志只记录错误码、dependency、grpc status 和 latency。

## Error Mapping

| origination gRPC result | BFF boundary | Frontend compatibility |
|---|---|---|
| not found | application not found | 保持现有 404 语义 |
| permission denied | forbidden | 保持现有权限错误 |
| invalid argument / failed precondition | validation or step error | 保持现有 4xx 语义 |
| unavailable / deadline / unknown | origination unavailable | 保持现有 5xx 依赖错误 |

## Rollout And Rollback

- Rollout: after `LEN-180` server capability, `LEN-184` backend quote chain, and `LEN-188` quote BFF chain are merged and deployable.
- Dev-first: dev-1 smoke must pass before sta-1.
- Rollback: revert BFF image and GitOps config together.
- No partial fallback: rollback may restore previous image/config, but this requirement implementation must not keep HTTP fallback in the new code path.

## Risks And Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| origination gRPC method coverage differs from HTTP DTO behavior | BFF response compatibility regression | adapter tests cover create/get/patch/advance response and error mapping |
| Consul metadata lacks `grpc_port` | BFF may fail to dial origination | resolver and GitOps config checks; live Consul evidence before closeout |
| old HTTP config remains in GitOps | hard-cut violated | code and kustomize rendered search evidence |
| trace backend unavailable | live AC delayed | record local/config evidence and live blocker explicitly |
