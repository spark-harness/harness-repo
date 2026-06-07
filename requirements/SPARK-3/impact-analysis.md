---
requirement_id: "SPARK-3"
analyst: "Codex"
status: "Reviewed"
updated_at: "2026-06-07"
---

# Impact Analysis

## Summary

本需求只影响 `user-api` HTTP inbound adapter，新增 `/ready` 只读 readiness endpoint。不涉及 IDL、数据、配置、权限或部署变更。

## Affected Domains

- 用户域

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| user-api | `{business-repo}/services/backend/user-api` | 新增 HTTP readiness endpoint 和测试 | no |

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: no
- Contract repo: N/A
- Proto files: N/A
- Buf module: N/A
- Buf config version: v2
- Required buf checks: N/A
- Breaking baseline: N/A
- Compatibility risk: 低；只新增 HTTP endpoint，不修改现有接口。

## Data Impact

- Database schema: no
- Data migration: no
- Backfill: no
- Cache: no

## Config / Permission / Observability Impact

- Config: no
- Permission: no service-specific permission.
- Metrics: no new metrics.
- Logs: no new business log.
- Tracing: no new tracing.
- Events: no

## Rollout And Rollback

- Gray release: 可先在本地或测试环境调用 `/ready`。
- Kill switch: 不需要。
- Rollback steps: 回滚 `HealthHttpAdapter` 和对应测试改动。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| readiness 语义被误认为包含外部依赖检查 | 运维预期不一致 | 在需求和设计中明确本阶段只代表应用本身 ready | Codex |
