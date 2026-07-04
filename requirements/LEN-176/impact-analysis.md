---
requirement_id: "LEN-176"
analyst: "forest"
status: "approved"
updated_at: "2026-07-05"
approved_by: "forest"
approved_at: "2026-07-05T00:35:00+08:00"
decision: "用户在 /goal 中授权处理下列任务中的任何事项，包括批准文件；批准 LEN-176 service repo readiness 与 impact-analysis。"
idl_impact: "yes"
idl_impact_reason: "新增 quote-api protobuf gRPC 服务和 Java/Go 生成物。"
---

# Impact Analysis

## Summary

本需求新增 quote-api gRPC 契约和服务端实现，并在 GitOps 中补齐 gRPC 端口和 Consul metadata。业务 HTTP 删除不在本 Story 执行，避免调用方未切换时断链。

## Affected Domains

- 报价与试算：quote-api 新增 gRPC 服务端边界，后续调用方完成硬切后再清理业务 HTTP。
- 契约治理：新增 quote protobuf、生成 Java/Go SDK。
- GitOps：quote-api 暴露 9090 gRPC 并保留 HTTP health/readiness。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| quote-api | `{business-repo}/apps/quote-api` | 新增 gRPC 入站 adapter，保留业务 HTTP 到最终清理阶段 | Yes |
| quote-api GitOps | `{gitops-repo}/apps/quote-api` | 暴露 gRPC 端口、Consul metadata、NetworkPolicy | Yes |
| quote contract | `{idl-repo}/vesta/lendora/quote/v1` | 新增 QuoteService，并通过 formal SDK 发布 Java 生成物 | Yes |

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: yes.
- Contract source repo: `idl-repo`。
- Generated Java artifact: `com.spark.contract:spark-idl-java:0.2.6`。
- Proto files: `vesta/lendora/quote/v1/quote.proto`。
- Buf module: `local/lendora-quote`。
- Buf config version: v2。
- Required buf checks: lint / generate / breaking。
- Breaking baseline: `.git#branch=master`。
- Compatibility risk: additive new service，当前 master 无 quote proto，不破坏既有 protobuf 消费方。

## Data Impact

- Database schema: none.
- Data migration: none.
- Backfill: none.
- Cache: none.
- Runtime storage: quote repository 继续使用现有 JDBC/H2 配置。

## Config / Permission / Observability Impact

- Config: 新增 `SPARK_QUOTE_CONSUL_GRPC_PORT` 和 `SPARK_GRPC_SERVER_PORT`。
- Permission: NetworkPolicy 允许业务命名空间访问 quote-api 9090。
- Metrics: 无新增指标要求。
- Logs: 错误通过 gRPC status 和 description 返回，不新增敏感日志。
- Tracing: proto 包含 `trace_id` 字段保留现有 trace 透传能力；后续调用方会在 `LEN-184/LEN-188` 接入。
- Events: none.

## Error Codes

| Error Code | HTTP / gRPC Mapping | Meaning | Retryable | User Visible | Owner | Status |
|---|---|---|---:|---:|---|---|
| `QUOTE-PARAM-0001` | `INVALID_ARGUMENT` | quote 请求字段缺失或格式非法 | No | Yes | pricing | Active |
| `QUOTE-PARAM-0002` | `INVALID_ARGUMENT` | quote 金额超出报价范围 | No | Yes | pricing | Active |
| `QUOTE-AUTH-0001` | `UNAUTHENTICATED` | quote 请求缺少有效申请人身份 | No | Yes | pricing | Active |
| `QUOTE-PERMISSION-0001` | `PERMISSION_DENIED` | 申请人无权读取该报价 | No | Yes | pricing | Active |
| `QUOTE-STATE-0001` | `NOT_FOUND` | 报价不存在 | No | Yes | pricing | Active |
| `QUOTE-STATE-0002` | `FAILED_PRECONDITION` | 报价已过期 | No | Yes | pricing | Active |
| `QUOTE-SYSTEM-0001` | `UNKNOWN` | quote-api 未分类系统错误 | Yes | No | pricing | Active |

## Rollout And Rollback

- Gray release: 先合并 IDL 并发布 formal SDK，等 SDK CI 产物，再合并 quote-api 和 GitOps。
- Kill switch: 回滚 quote-api 镜像和 GitOps 端口配置；调用方尚未切换前回滚不影响现有调用。
- Rollback steps: revert quote-api business PR 和 GitOps PR；业务 HTTP 和健康 HTTP 均保留。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| business-repo 先于 SDK 合并 | CI 无法解析新 Java contract | 严格先合并 IDL 并等待 formal SDK CI 产物 | forest |
| 删除业务 HTTP 过早影响现有调用方 | fides-bff/origination 仍 HTTP 时调用失败 | LEN-176 不删除业务 HTTP；`LEN-196` 最终清理前必须证明调用方已硬切 | forest |
| Consul metadata 缺失 | gRPC client 无法发现 9090 | 单元测试和 GitOps 渲染检查 `grpc_port` | forest |
