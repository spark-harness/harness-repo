---
requirement_id: "SPARK-3"
owner: "Codex"
status: "approved"
created_at: "2026-06-07"
related_branch: "feature/SPARK-3-user-api-readiness"
approved_by: "Codex"
approved_at: "2026-06-07T23:30:00+08:00"
decision: "需求定义通过，可以进入设计阶段。"
---

# User API Readiness Endpoint

## Background

`user-api` 目前只有 `/health` HTTP 探活入口。服务需要一个更明确的 readiness 入口，用于区分“进程存活”和“服务已准备好承接流量”的语义。

本需求保持最小范围，只增加一个只读 HTTP endpoint，不引入数据库、缓存、IDL 或部署系统变更。

## Goals

- R1: `user-api` 提供 `GET /ready` HTTP endpoint。
- R2: endpoint 返回 HTTP 200。
- R3: response body 包含 `status = "READY"` 和 `service = "user-api"`。
- R4: endpoint 不依赖外部系统，不触发写操作。
- R5: 需求、设计、任务、门禁和测试证据可以互相追溯。

## Non-Goals

- 不修改 gRPC 契约。
- 不修改 protobuf IDL。
- 不接入 Kubernetes readinessProbe 配置。
- 不增加数据库、缓存、消息队列或外部健康检查。
- 不改变现有 `/health` 行为。

## User / Business Scenarios

### Scenario 1

Given: `user-api` Spring 应用已启动。

When: 运维或上游系统请求 `GET /ready`。

Then: 服务返回 HTTP 200，body 中 `status` 为 `READY`，`service` 为 `user-api`。

## Business Rules

- BR1: `/ready` 必须是只读接口。
- BR2: `/ready` 不能依赖外部服务。
- BR3: `/ready` 不能改变现有 `/health` 响应。
- BR4: 本需求不涉及 protobuf IDL。

## Acceptance Criteria

- AC1: `GET /ready` 返回 HTTP 200。
- AC2: `GET /ready` 返回 JSON 字段 `status = "READY"`。
- AC3: `GET /ready` 返回 JSON 字段 `service = "user-api"`。
- AC4: 现有 `/health` 测试继续通过。
- AC5: `mvn test` 在 `business-repo/services/backend/user-api` 通过。
- AC6: Janus lifecycle gate JSON 记录当前输入文件 hash。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 是否接入 Kubernetes readinessProbe 配置？ | Codex | 2026-06-07 | Closed: 本需求不涉及部署配置。 |

## Notes

本需求用于完整演练 Harness 生命周期：需求定义、影响面、设计、任务拆分、门禁、实现、测试证据和提交。
