---
requirement_id: "LEN-33"
owner: "Codex"
status: "approved"
created_at: "2026-06-17"
related_branch: "feature/LEN-33"
approved_by: "Forest"
approved_at: "2026-06-17T21:08:22+08:00"
decision: "批准 LEN-33 requirement 与 impact-analysis，允许进入设计阶段。"
---

# [BE] Java + Spring 业务代码骨架

## Background

LEN-3 要求后端具备可运行、可联调、可承载后续业务接口的一致服务骨架。当前 `business-repo/services/backend/user-api` 只有 README 与 POM，缺少 Java 源码、Spring Boot 启动入口、分层目录、最小健康检查和服务级质量入口；后续 LEN-9 申请单聚合如果直接进入业务实现，会先被工程骨架决策阻塞。

先说不是什么：本票不是 fides-bff，不暴露前端 BFF REST 入口；也不实现 LoanApplication、Pricing、OTP、KYC、提交等业务规则。它只提供后续业务票可落地的 Java 21 + Spring Boot 后端业务服务骨架。

## Goals

- R0: `user-api` 使用 Java 21 + Spring Boot 承载后端业务服务骨架，保留为业务领域服务入口。
- R1: 在 `user-api` 建立团队后端 Clean Architecture 分层：`domain / application / adapter/inbound / infrastructure / bootstrap`。
- R2: 服务具备最小本地启动能力，并提供可自动验证的健康检查或 smoke test。
- R3: 复用或对齐 `packages/spring-starter` 的分层 stereotype、事务执行和 gRPC server 基线；如 starter 能力不足，只补最小可用扩展。
- R4: 建立单元测试、Spring 启动测试和架构边界测试，能阻止 `domain` 依赖 Spring、Web、数据库、消息或外部 SDK。
- R5: 新增或更新 CI 入口，一键执行 `user-api` 的构建与测试。
- R6: README 说明后续业务票如何在该骨架中添加 domain/application/adapter/infrastructure 代码。
- R7: 需求、影响、设计、任务、门禁与实现证据可互相追溯。

## Non-Goals

- 不新增 `.proto`，不修改 `idl-repo` 或生成契约。
- 不定义 LoanApplication API，不实现申请单创建、草稿读写、试算、OTP、KYC、提交或状态查询。
- 不实现数据库表、迁移、仓储持久化或真实第三方集成。
- 不改变 LEN-21 / LEN-22 承接的 API 横切约定。
- 不新增独立服务矩阵条目；本票落在现有 `user-api` 服务骨架上。

## User / Business Scenarios

### Scenario 1：新同学可启动后端业务服务骨架

Given: 开发者 clone `business-repo` 并进入 `services/backend/user-api`。

When: 按 README 执行本地构建、测试和启动命令。

Then: 服务可启动；健康检查或 smoke test 通过；后续业务票可在明确分层下继续开发。

### Scenario 2：业务代码有明确落点

Given: 后续 LEN-9 需要添加申请单聚合、用例和适配器。

When: 开发者按 README 指引新增代码。

Then: 领域对象进入 `domain`，用例进入 `application`，入站协议进入 `adapter/inbound`，技术实现进入 `infrastructure`，启动装配进入 `bootstrap`。

### Scenario 3：架构边界被自动拦截

Given: 有代码让 `domain` 直接依赖 Spring、Web、数据库、消息或外部 SDK。

When: 开发者运行服务测试或 CI。

Then: 架构边界测试失败，指出违规包或类，不能作为合并就绪证据。

## Business Rules

- `user-api` 是 Lendora 后端业务服务骨架，不是前端 BFF。
- 领域层不得依赖 Spring、HTTP、ORM、消息、缓存、DI 框架或外部 SDK。
- 应用层可依赖领域层和应用端口，不依赖 controller、数据库实现类、消息实现类或第三方 SDK。
- 入站适配层只做协议转换、参数校验和错误转换，不承载核心业务规则。
- 基础设施层实现技术细节，并实现应用层或领域层定义的端口。
- `bootstrap` 负责 Spring Boot 启动和装配，不放业务规则。
- 本票只建立骨架和最小验证；业务规则必须由后续业务票定义和测试。

## Acceptance Criteria

- AC1（承接 LEN-3 AC5）：`user-api` 可本地构建，最小启动验证或健康检查通过。
- AC2：`user-api` 具备 `domain / application / adapter/inbound / infrastructure / bootstrap` 分层骨架，README 说明各层职责和后续业务票落点。
- AC3：测试入口包含 Spring 启动测试和架构边界测试；架构边界测试能阻止 `domain` 依赖 Spring、Web、数据库、消息或外部 SDK。
- AC4：CI 或等价一键命令可执行 `user-api` 构建与测试。
- AC5：不新增或修改 protobuf IDL、生成契约、业务 API、持久化表结构或业务规则。
- AC6：完成后解除 LEN-9 的 Java + Spring 工程骨架前置阻塞。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 是否需要将 `services/backend/user-api` 加入根 Maven 聚合构建 | Codex | 设计阶段 | 待设计决策 |
| 是否将 Java 21 统一回写到 `packages/spring-starter` / `packages/money` | Codex | 设计阶段 | 默认不扩大范围 |

## Notes

- Jira LEN-33 为 Subtask，父票 LEN-3；描述要求 Java 21 + Spring Boot、Clean Architecture 分层、统一测试入口、配置基线与 CI。
- 用户在 2026-06-17 批准 Requirement Brief，并将分支名从建议值调整为 `feature/LEN-33`；机器批准字段需由 `janus requirement approve` 写入。
