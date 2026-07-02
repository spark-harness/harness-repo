---
requirement_id: "LEN-151"
owner: "Codex"
status: "approved"
created_at: "2026-07-02T22:16:13+08:00"
related_branch: "feature/LEN-151-health-db-noise"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - "harness-repo"
  - "business-repo"
approved_by: "forest"
approved_at: "2026-07-02T22:19:57+08:00"
decision: "用户已授权 Codex 批准中间文件；批准 LEN-151 requirement 与 impact-analysis，按 Jira Story 范围移除 Java 健康检查 DB 探活噪音，不修改 IDL 或业务数据库路径。"
---

# 移除 Java 服务健康检查中的数据库探活噪音

## Background

当前 Java 服务的健康检查会触发数据库连通性探测。它在 Sentry / OTel 中表现为周期性的 `select 1` 或等价数据库 span，容易和真实业务数据库访问混在一起。

这不是关闭健康检查，也不是关闭数据库 tracing。它是把健康检查与数据库主动查询解耦，让观测系统中的数据库 span 更接近真实业务访问或真实运行问题。

## Goals

- Java 服务继续提供 Kubernetes 和 Consul 可用的健康检查入口。
- 健康检查不再主动发起数据库查询证明服务可用。
- 真实业务请求产生的数据库访问和 tracing 仍然保留。
- 覆盖 `applicant-api`、`quote-api`、`origination-api` 三个 Java 服务。

## Non-Goals

- 不关闭 Sentry、OTel 或 JDBC tracing。
- 不修改业务 repository、migration、数据库表结构或业务接口行为。
- 不改变 Kubernetes / Consul 调用健康检查入口的整体方式。
- 不把数据库可用性从业务运行观测中移除；数据库问题仍由真实业务路径、日志、指标或专门诊断手段暴露。

## User / Business Scenarios

### Scenario 1

Given: Java 服务开启 tracing 并处于运行中。

When: 平台周期性执行健康检查。

Then: 观测系统中不再出现仅由健康检查触发的数据库查询 span。

### Scenario 2

Given: Java 服务进程正常且健康检查入口可访问。

When: Kubernetes 或 Consul 调用健康检查。

Then: 服务仍能返回健康检查结果。

### Scenario 3

Given: 数据库 tracing 仍处于开启状态。

When: 真实业务请求访问数据库。

Then: 真实业务数据库 span 仍可被观测。

## Business Rules

- BR1: Java 服务仍必须保留可被 Kubernetes 和 Consul 使用的健康检查能力。
- BR2: 健康检查不应主动发起数据库查询来证明服务可用。
- BR3: 真实业务请求产生的数据库访问仍应保留 tracing，不因本变更被关闭或隐藏。
- BR4: 本变更覆盖 `applicant-api`、`quote-api`、`origination-api` 三个 Java 服务。

## Acceptance Criteria

- AC1: 周期性健康检查不会产生数据库查询 span。
- AC2: 三个 Java 服务的健康检查入口仍可返回健康检查结果。
- AC3: 三个 Java 服务的业务 JDBC 路径仍可通过 repository / HTTP / use case 测试。
- AC4: `applicant-api`、`quote-api`、`origination-api` 都不再通过数据库查询完成健康检查。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 是否需要保留 Redis / Consul 等非数据库依赖的 readiness 汇总口径？ | 平台 / 服务 owner | 后续需求 | Open |

## Notes

- Jira Story LEN-151 已明确授权实现，并授权批准中间文件。
- 本需求按窄 bugfix 处理，不引入 IDL、数据结构或业务接口变化。
