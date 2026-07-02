---
requirement_id: "LEN-151"
analyst: "Codex"
status: "approved"
updated_at: "2026-07-02T22:16:13+08:00"
approved_by: "forest"
approved_at: "2026-07-02T22:20:50+08:00"
decision: "用户已授权 Codex 批准中间文件；批准 LEN-151 服务仓库检查，确认只影响 harness-repo 与 business-repo，同名分支已隔离，不涉及 IDL。"
idl_impact: "no"
idl_impact_reason: "本需求只调整 Java 服务健康检查配置和 readiness probe 装配，不修改 protobuf IDL、HTTP 契约或生成契约。"
---

# Impact Analysis

## Summary

LEN-151 影响 `business-repo` 中三个 Java 服务的健康检查配置和 runtime dependency probe 装配，并新增 Harness 需求证据；不影响 IDL、数据库 schema 或业务接口。

## Affected Domains

- 申请人域：`applicant-api`
- 报价与试算：`quote-api`
- 申请人域 / 进件：`origination-api`
- Harness 需求治理：`harness-repo/requirements/LEN-151`

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| `applicant-api` | `business-repo/apps/applicant-api` | 移除 JDBC readiness probe，禁用 actuator DB health。 | No |
| `quote-api` | `business-repo/apps/quote-api` | 移除 JDBC readiness probe，禁用 actuator DB health。 | No |
| `origination-api` | `business-repo/apps/origination-api` | 移除 JDBC readiness probe，禁用 actuator DB health。 | No |

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: No.
- Contract repo: N/A.
- Proto files: N/A.
- Buf module: N/A.
- Buf config version: v2 unchanged.
- Required buf checks: N/A.
- Breaking baseline: N/A.
- Compatibility risk: Low; no request / response schema or generated contract changes.

## Data Impact

- Database schema: No change.
- Data migration: No change.
- Backfill: No.
- Cache: No change.
- Runtime storage: Existing JDBC repositories and migrations remain in place.

## Config / Permission / Observability Impact

- Config: Disable Spring Boot actuator DB health indicator for affected Java services.
- Permission: No change.
- Metrics: No new metric.
- Logs: No logging contract change.
- Tracing: Health checks stop producing DB spans; real business JDBC spans remain enabled because JDBC dependencies and OTel instrumentation remain unchanged.
- Events: No event impact.

## Rollout And Rollback

- Gray release: Can be deployed service by service because the change is local to each Java service.
- Kill switch: Roll back the service image or revert the config/probe removal.
- Rollback steps: Revert `business-repo` branch for LEN-151 and redeploy affected service image.

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| 健康检查不再覆盖数据库连通性后，数据库故障可能不再通过 readiness 反映。 | DB 故障可能只在业务路径暴露。 | 保留业务 JDBC tracing；本需求明确不把 DB 当作通用 readiness 依赖。 | 服务 owner |
| 删除 DB probe 后某服务没有任何 dependency probe。 | `/ready` 只反映进程和非 DB probe 状态。 | 测试允许 0..N probe，并保留 `/health`、`/ready` 入口。 | Codex |
