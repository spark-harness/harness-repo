---
requirement_id: "SPARK-3"
owner: "Codex"
status: "Reviewed"
updated_at: "2026-06-07"
design_review_status: "approved"
approved_by: "Codex"
approved_at: "2026-06-07T23:35:00+08:00"
decision: "设计覆盖服务边界、接口、测试和回滚，可以进入任务拆分。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1 | D1: 在 `HealthHttpAdapter` 中新增 `GET /ready` | 复用现有 HTTP adapter |
| R2, R3 | D2: 返回 `Map.of("status", "READY", "service", "user-api")` | 保持响应结构与 `/health` 相似 |
| R4 | D3: endpoint 不调用 application、domain 或 infrastructure 层 | 只表达应用本身 ready |
| R5 | D4: 用 Janus gate JSON 和 evidence 文件记录追溯与验证 | 支持生命周期审计 |

## Summary

方案保持最小实现：在现有 `HealthHttpAdapter` 中增加 `/ready` 方法，并扩展 `HealthHttpAdapterTest` 验证响应。该 endpoint 是 HTTP inbound adapter 的只读接口，不涉及业务用例、数据访问或 protobuf 契约。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| user-api | 新增 `GET /ready` 和测试 | 满足 readiness endpoint 需求 |

## API / Contract Design

- Protobuf IDL required: no
- Proto files: N/A
- Buf module: N/A
- Buf config version: v2
- Generated outputs: N/A
- Breaking check baseline: N/A
- Compatibility strategy: 只新增 HTTP endpoint，不修改 `/health` 或 gRPC 契约。

## Data / Config / Permission

- Data model: no
- Config: no
- Permission: no

## Observability

- Logs: no new business log.
- Metrics: no new metric.
- Tracing: no new tracing.
- Events: no.

## Rollout And Rollback

- Gray release: 本地或测试环境运行 `GET /ready` 和单元测试。
- Kill switch: not required.
- Rollback: revert `HealthHttpAdapter` and `HealthHttpAdapterTest`.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| `/ready` 被误解为检查所有下游依赖 | 明确本阶段只做应用自身 ready，不检查外部依赖 | Codex |
