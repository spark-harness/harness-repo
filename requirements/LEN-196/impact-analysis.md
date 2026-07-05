---
requirement_id: "LEN-196"
analyst: "forest"
status: "approved"
updated_at: "2026-07-05"
idl_impact: "no"
idl_impact_reason: "本需求不修改 protobuf；只删除已被 gRPC 替代的业务 HTTP 暴露面和 GitOps 旧配置。"
approved_by: "forest"
approved_at: "2026-07-05T09:08:32+08:00"
decision: "用户本轮明确授权批准 LEN-196 service repo readiness；确认 harness-repo、business-repo、gitops-repo、idl-repo worktree 已就位且不修改 IDL。"
---

# Impact Analysis

## Summary

本需求是 gRPC 硬切后的最终环境验证和遗留清理。影响集中在 `quote-api`、`origination-api` 的业务 HTTP adapter 删除，以及 `gitops-repo` 中内部业务 HTTP ingress 和旧 Consul KV bootstrap 删除。

## Affected Domains

| Domain | Impact |
|---|---|
| pricing | 删除 quote-api 业务 HTTP controller；保留 gRPC、health/readiness |
| applicant | 删除 origination-api 业务 HTTP controller；检查 applicant-api 内部 HTTP ingress 和旧 KV bootstrap |
| frontend | fides-bff 外部 HTTP 保持不变；BFF 到后端服务继续使用 gRPC |

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| quote-api | `{business-repo}/apps/quote-api` | 删除业务 HTTP adapter；保留 gRPC 和 health/readiness | Yes, no change |
| origination-api | `{business-repo}/apps/origination-api` | 删除业务 HTTP adapter；保留 gRPC 和 health/readiness | Yes, no change |
| applicant-api | `{gitops-repo}/apps/applicant-api` | 清理 client namespace HTTP ingress 和旧 Consul KV bootstrap | Yes, no change |
| fides-bff | `{gitops-repo}/apps/fides-bff` | 验证外部 HTTP 保留、内部后端调用使用 gRPC，并删除旧 runtime-config Consul bootstrap | Yes, no change |

## Upstream / Downstream

- Upstream: `fides-web -> fides-bff` 外部 HTTP 不变。
- Downstream: `fides-bff -> applicant-api`、`fides-bff -> quote-api`、`fides-bff -> origination-api` 使用 gRPC。
- Downstream: `origination-api -> quote-api` 使用 gRPC。
- Consul remains service discovery infrastructure and is not removed.

## API / Contract Impact

- 不修改 protobuf IDL。
- 不修改 BFF 外部 HTTP contract。
- 删除 quote-api/origination-api 内部业务 HTTP controller 后，服务间调用方不能再依赖 HTTP。
- Java `/health`、`/ready` 仍是运行时健康检查接口，不属于业务 contract。

## Generated Contract Impact

- 不更新 `idl-go-repo`、`idl-java-repo` 或 generated contracts。
- Contract dependency scan 仍应证明业务仓未引入 SNAPSHOT 或非 formal 依赖。

## Data / Migration / Runtime Storage

- 不修改数据库 schema、migration、Redis、业务数据或状态机。
- 删除旧 Consul KV bootstrap Job 只影响不再使用的运行时配置写入路径，包括 fides-bff runtime-config bootstrap。
- `lendora-shared-consul` 服务本身继续保留，用于服务注册/发现。

## Config / Permission / Observability

- GitOps NetworkPolicy 删除业务 client namespace 对 quote-api/origination-api/applicant-api HTTP 端口的访问。
- Consul namespace 对 health/readiness HTTP 端口的访问保留。
- Service HTTP port 可保留用于 health/readiness，不作为业务入口。
- OTLP `http/protobuf` exporter 保留。
- Trace evidence 应证明核心业务流程内部服务间 span 是 gRPC。

## Rollout And Rollback

Rollout:

1. dev-1 当前状态先执行 baseline smoke 和扫描。
2. 合并 business-repo 删除业务 HTTP adapter。
3. 发布 quote-api/origination-api 新镜像并先验证 dev-1。
4. 合并 GitOps 清理 client HTTP ingress 和旧 Consul KV bootstrap，先 dev-1 后 sta-1。
5. sta-1 执行同样 smoke、config 和 trace 验证。

Rollback:

- 如果业务 smoke 失败，先回滚对应 GitOps image digest 或 NetworkPolicy commit。
- 如果删除 HTTP adapter 导致编译或测试失败，回滚 business-repo commit 并恢复 adapter。
- 不通过恢复 `lendora-shared-consul` 处理问题，因为它不被删除。

## Risks And Mitigations

| Risk | Mitigation |
|---|---|
| health/readiness HTTP 被误删 | 明确保留 `HealthHttpAdapter`、Service HTTP port 和 Consul health check |
| BFF 外部 HTTP 被误判为遗留 | requirement/design 中列为允许项 |
| Consul API HTTP 被误判为业务 HTTP | 扫描证据中单列允许项 |
| trace 后端不可用 | 用 smoke、live config、logs 和 repo scan 补充证据并记录限制 |
