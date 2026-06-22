---
requirement_id: "LEN-44"
owner: "Codex"
status: "draft"
created_at: "2026-06-23"
related_branch: "feature/LEN-44-applicant-api-local-runtime"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - business-repo
---

# applicant-api 本地真实运行时接入

## Background

LEN-12 和 LEN-41 已经建立 `applicant-api` 与 Lendora applicant 契约主线，但服务仍需要更接近真实环境的本地运行路径，才能验证 PostgreSQL、Redis、Consul、迁移、健康检查和 trace 配置在同一条链路中协同工作。

先说不是什么：本需求不是新增手机号验证业务语义，不修改 applicant protobuf 契约，也不处理已识别的 Redis 并发、Consul 生命周期或架构分层技术债。

它是什么：一次面向 `applicant-api` 的本地真实运行时接入，让业务仓 PR 能通过 CI/CD 的 delivery-readiness 链路，并把剩余技术债显式留给后续 Ticket。

## Goals

- R1：`applicant-api` 提供本地 PostgreSQL、Redis 和 Consul 运行依赖。
- R2：服务启动时能执行 applicant 表结构迁移，并在本地 runtime profile 下使用 Redis/JDBC runtime store。
- R3：`/ready` 能反映关键运行依赖状态，便于本地和 CI 排查。
- R4：gRPC auth adapter 保留现有 OTP RPC 行为，并补充 trace 传播覆盖。
- R5：提供本地 smoke 和 reset 脚本，reset 脚本必须防止误删非本地数据。
- R6：业务仓 PR 能通过 contract dependency scan 和 delivery-readiness CI。

## Non-Goals

- 不修改 IDL、generated Java contract 或 generated Go contract。
- 不修改 `fides`、`fides-bff` 或前端行为。
- 不接入真实短信供应商。
- 不在本票完成 Redis 幂等原子性、手机号 cooldown 原子预留、Consul 注销/重试策略或 bootstrap/infrastructure 分层整理。
- 不把已有 not-ready code review 结论改写为通过。

## User / Business Scenarios

### Scenario 1：本地启动真实依赖

Given：工程师需要在本地验证 applicant-api runtime。

When：启动本地 PostgreSQL、Redis、Consul 和 applicant-api。

Then：服务能完成迁移、连接 runtime store，并暴露可检查的 readiness 状态。

### Scenario 2：执行本地 smoke

Given：本地 runtime 已启动。

When：执行 applicant-api smoke 脚本。

Then：脚本通过 gRPC 调用 OTP 流程，并验证 PostgreSQL applicant 记录和 Redis runtime key。

### Scenario 3：防止误删共享数据

Given：工程师运行本地 reset 脚本。

When：未显式声明本地 reset 或 URL 不指向默认本地依赖。

Then：脚本拒绝执行 destructive reset。

### Scenario 4：业务 PR 进入 delivery-readiness

Given：`business-repo` 创建 LEN-44 PR。

When：CI 运行 contract dependency scan 和 delivery-readiness。

Then：CI 能读取 LEN-44 requirement front matter，并验证本次业务仓交付状态。

## Business Rules

- BR1：本地 runtime 只能作为开发和验证入口，不能改变生产契约语义。
- BR2：master-bound 业务 PR 不能引入 SNAPSHOT、RC 或 local replacement contract dependency。
- BR3：reset 脚本必须要求显式确认，并限制目标为默认本地 PostgreSQL/Redis。
- BR4：已识别但不属于 CI/CD 闭环的技术债必须在 PR 风险和后续 Ticket 中跟踪。
- BR5：delivery-readiness 的事实源是 Harness requirement front matter，不由 PR 文案替代。

## Acceptance Criteria

- AC1：`business-repo/services/backend/applicant-api` 包含本地 Docker Compose runtime 配置。
- AC2：`applicant-api` 包含 Flyway applicant 表迁移，并在测试中验证迁移可执行。
- AC3：`applicant-api` 包含 Redis/JDBC runtime wiring 和 readiness dependency probes。
- AC4：本地 reset 脚本未设置 `ALLOW_LOCAL_RUNTIME_RESET=true` 时拒绝 destructive reset。
- AC5：`mvn test` 在 `services/backend/applicant-api` 通过。
- AC6：`python3 scripts/contract_dependency_scan.py --mode master --path services/backend/applicant-api/pom.xml` 通过。
- AC7：`business-repo` PR 的 delivery-readiness 能读取 `requirements/LEN-44/requirement.md`。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| Redis 幂等与 cooldown 原子性是否作为单独后续 Ticket 处理 | Backend | 后续技术债票 | Deferred |
| Consul 注册超时、重试和注销策略是否作为单独后续 Ticket 处理 | Backend | 后续技术债票 | Deferred |
| `/ready` 对外兼容策略是否需要拆出内部 readiness endpoint | Backend / Platform | 后续技术债票 | Deferred |

## Notes

- 关联 JIRA 子任务：LEN-44。
- 用户明确要求先完成 CI/CD 闭环，技术债后续专门开 Ticket 处理。
