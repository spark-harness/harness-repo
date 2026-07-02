---
requirement_id: "LEN-151"
owner: "Codex"
status: "approved"
updated_at: "2026-07-02T22:16:13+08:00"
approved_by: "forest"
approved_at: "2026-07-02T22:19:57+08:00"
decision: "用户已授权 Codex 批准中间文件；批准 LEN-151 设计，采用禁用 actuator DB health 与删除 JDBC readiness probe 的最小方案。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| BR1, AC2 | 保留既有 `/health` 和 `/ready` 健康检查入口。 | 不改变 Kubernetes / Consul 调用方式。 |
| BR2, AC1, AC4 | 禁用 actuator DB health indicator，并移除自定义 JDBC runtime dependency probe。 | 覆盖三个 Java 服务。 |
| BR3, AC3 | 不修改 repository、migration、JDBC dependency、OTel dependency 或业务请求路径。 | 用完整模块测试证明业务 JDBC 路径仍可运行。 |

## Summary

本设计把健康检查从数据库主动查询中解耦。实现只处理两类噪音来源：Spring Boot actuator DB health indicator 和自定义 `RuntimeDependencyProbe` 中的 JDBC 探活。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| `applicant-api` | 禁用 DB health；删除 JDBC runtime dependency probe；保留 Redis / Consul probe。 | 健康检查不再执行 `select 1`。 |
| `quote-api` | 禁用 DB health；删除 JDBC runtime dependency probe。 | 健康检查不再执行 `select 1`。 |
| `origination-api` | 禁用 DB health；删除 JDBC runtime dependency probe。 | 健康检查不再执行 `select 1`。 |

## API / Contract Design

- Protobuf IDL required: No.
- Proto files: N/A.
- Buf module: N/A.
- Buf config version: v2 unchanged.
- Generated outputs: N/A.
- Breaking check baseline: N/A.
- Compatibility strategy: No API or contract surface changes.

## Data / Config / Permission

- Data model: No change.
- Config: Set `management.health.db.enabled=false` in affected service configuration.
- Permission: No change.

## Observability

- Logs: No logging field change.
- Metrics: No metric change.
- Tracing: Health checks stop generating database spans. Business JDBC spans remain enabled because tracing dependencies and business data paths are unchanged.
- Events: No change.

## Testing Strategy

- Add / update configuration model tests to assert DB health is disabled.
- Add / update application wiring tests to assert JDBC health probe is not registered.
- Keep readiness tests focused on non-DB dependency status.
- Run full Maven tests for `applicant-api`, `quote-api`, and `origination-api`.

## Rollout And Rollback

- Gray release: Deploy each Java service independently.
- Kill switch: Revert image or branch.
- Rollback: Restore deleted JDBC runtime dependency probes and previous DB health config if the team decides DB readiness is required again.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| DB outage no longer fails generic readiness. | Treat DB availability as business-path observability, not process readiness; retain business JDBC tests and tracing. | 服务 owner |
| Future service reintroduces DB probe. | Regression tests assert DB health disabled and JDBC probe absent. | Codex |
