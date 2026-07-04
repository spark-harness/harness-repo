---
requirement_id: "LEN-180"
analyst: "forest"
status: "approved"
updated_at: "2026-07-05"
approved_by: "forest"
approved_at: "2026-07-05T02:30:00+08:00"
decision: "用户本轮明确要求完成 LEN-180 实现和证据。"
idl_impact: "yes"
idl_impact_reason: "使用 origination protobuf gRPC 契约并生成 Java contract。"
---

# Impact Analysis

## Summary

本需求让 origination-api 具备服务端 gRPC loan application 能力，并补齐 9090 运行时入口。业务 HTTP 保留到 `LEN-196`。

## Affected Domains

- 申请人域：origination-api 对内提供贷款申请创建、读取、更新和步骤推进 gRPC。
- 契约治理：使用 `vesta.lendora.origination.v1` protobuf 并生成 Java SDK。
- GitOps：origination-api dev-1/sta-1 暴露 9090。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| origination-api | `{business-repo}/apps/origination-api` | 新增 loan application gRPC 入站 adapter，保留业务 HTTP | Yes |
| origination-api GitOps | `{gitops-repo}/apps/origination-api` | 暴露 gRPC 端口、Consul metadata、NetworkPolicy | Yes |
| origination contract | `{idl-repo}/vesta/lendora/origination/v1` | 提供 origination loan application service 契约 | Yes |

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: yes.
- Contract source repo: `idl-repo`。
- Proto files: `vesta/lendora/origination/v1/loan_application.proto`。
- Generated Java artifact: `com.spark.contract:spark-idl-java:0.2.7`。
- Buf module: `local/lendora-origination`。
- Buf config version: v2。
- Required checks: `buf lint`、`buf generate --template buf.gen.java.yaml`、`buf breaking --against '.git#branch=master'`。
- Compatibility risk: additive server capability on origination package; no deletion or field-number reuse.

## Data Impact

- Database schema: none.
- Data migration: none.
- Backfill: none.
- Cache: none.
- Runtime storage: existing origination JDBC repository and idempotency repository remain.

## Config / Permission / Observability Impact

- Config: `SPARK_GRPC_SERVER_PORT=9090` and `SPARK_ORIGINATION_CONSUL_GRPC_PORT=9090`。
- Permission: NetworkPolicy allows 9090 from same-environment namespace and Consul namespace.
- Logs: no new sensitive logs.
- Metrics: uses existing Spring/gRPC starter behavior.
- Tracing: uses existing OpenTelemetry starter and gRPC metadata propagation.
- Events: none.

## Error Codes

| Error Code | gRPC Mapping | Meaning | Retryable | User Visible | Owner | Status |
|---|---|---|---:|---:|---|---|
| `ORIGINATION-PARAM-0001` | `INVALID_ARGUMENT` | 请求字段缺失、金额/期限/步骤非法或幂等键缺失 | No | Yes | applicant | Active |
| `ORIGINATION-AUTH-0001` | `UNAUTHENTICATED` | 请求缺少有效申请人身份 | No | Yes | applicant | Active |
| `ORIGINATION-PERMISSION-0001` | `PERMISSION_DENIED` | 申请人无权访问该申请或报价 | No | Yes | applicant | Active |
| `ORIGINATION-STATE-0001` | `NOT_FOUND` | 申请不存在 | No | Yes | applicant | Active |
| `ORIGINATION-STATE-0002` | `ALREADY_EXISTS` | 幂等键与不同请求冲突 | No | Yes | applicant | Active |
| `ORIGINATION-QUOTE-0001` | `NOT_FOUND` | 引用报价不存在 | No | Yes | applicant | Active |
| `ORIGINATION-QUOTE-0002` | `FAILED_PRECONDITION` | 引用报价已过期或与贷款条款不匹配 | No | Yes | applicant | Active |
| `ORIGINATION-QUOTE-0003` | `UNAVAILABLE` | quote 依赖不可用 | Yes | No | applicant | Active |
| `ORIGINATION-SYSTEM-0001` | `UNKNOWN` | origination-api 未分类系统错误 | Yes | No | applicant | Active |

## Rollout And Rollback

- Gray release: 先合并/发布 IDL Java artifact，再合并 origination-api 服务端实现，最后应用 GitOps。
- Kill switch: 回滚 origination-api 镜像或 GitOps overlay。
- Rollback: 因业务 HTTP 保留，服务端 gRPC 回滚不要求调用方同步回滚。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| Java contract 未发布 | business-repo CI 无法解析 `0.2.7` | 先发布 idl-java-repo artifact，再合并 business-repo | forest |
| NetworkPolicy 漏 9090 | fides-bff 后续无法拨通 gRPC | dev-1/sta-1 kustomize 渲染检查 9090 | forest |
| 过早删除 HTTP | 调用方未切换时断链 | 本需求保留 HTTP，`LEN-196` 再清理 | forest |
