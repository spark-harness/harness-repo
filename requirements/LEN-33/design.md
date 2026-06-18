---
requirement_id: "LEN-33"
owner: "Codex"
status: "approved"
updated_at: "2026-06-17"
approved_by: "Forest"
approved_at: "2026-06-17T21:26:36+08:00"
decision: "批准 LEN-33 design，允许进入任务拆分。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R0, AC1 | D0: `user-api` 作为现有后端业务服务骨架，升级/配置为 Java 21 + Spring Boot 可运行模块 | 不新增服务矩阵条目 |
| R1, AC2 | D1: 建立 `domain / application / adapter/inbound / infrastructure / bootstrap` 包结构和职责 README | 后续 LEN-9 直接沿用 |
| R2, AC1 | D2: 新增 Spring Boot 启动入口、Actuator health endpoint 和 Spring 启动 smoke test | 最小可运行，不暴露业务 API |
| R3 | D3: 复用 `spark-spring-clean-architecture-starter` 的 stereotype 与事务/gRPC 基线，不在本票扩展公共 starter | 控制范围 |
| R4, AC3 | D4: 使用 ArchUnit 架构边界测试约束 `domain` 不依赖 Spring/Web/DB/消息/SDK | test-first 红线 |
| R5, AC4 | D5: 新增 `user-api` CI job，执行 Maven test | 只读权限 |
| R6, AC2 | D6: 更新 `user-api` README，说明分层职责、运行、测试和后续业务票落点 | 面向新同学 |
| R7 | D7: Harness 产物、门禁、证据和评审报告互相追溯 | 合并就绪使用证据 hash |

## Summary

在现有 `services/backend/user-api` 中补齐可运行的 Java 21 + Spring Boot 后端业务服务骨架。它交付的是工程地基：分层包、启动入口、健康检查、测试入口、架构边界测试、README 和 CI。

先说不是什么：本设计不新增业务接口，不定义 LoanApplication API，不引入持久化，不修改 IDL，也不把 LEN-3 的错误信封、会话、幂等等横切约定一并实现。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| user-api | 补齐源码骨架、Spring Boot 启动入口、健康检查、测试、架构测试、README、CI | 承载后续后端业务票 |

## API / Contract Design

- Protobuf IDL required: `user-api` 既有服务矩阵为 true；本票不新增或修改 IDL。
- Proto files: 不修改。
- Buf module: `local/spark-user`（既有）。
- Buf config version: v2。
- Generated outputs: 不生成。
- Breaking check baseline: 不适用。
- Compatibility strategy: 只新增工程骨架和健康检查，不改变已有 gRPC ping 契约或外部业务契约。

## Application Design

`user-api` 包根保持 `com.spark.user`：

```text
src/main/java/com/spark/user/
├── bootstrap/
│   └── UserApiApplication
├── domain/
│   └── README.md
├── application/
│   └── README.md
├── adapter/inbound/
│   └── health/
├── infrastructure/
│   └── README.md
└── README.md
```

- `bootstrap`：Spring Boot 主类和组件扫描入口。
- `adapter/inbound/health`：最小健康检查控制器或 Actuator 配置入口，只用于 smoke 验证。
- `domain/application/infrastructure`：本票只放职责 README 或最小占位，不创建业务子域类。
- 后续 LEN-9 在 `domain/loanapplication`、`application/loanapplication`、`adapter/inbound`、`infrastructure` 下补业务代码。

健康检查优先使用 Spring Boot Actuator `/actuator/health`。如需自定义 endpoint，也只能返回服务存活状态，不承载业务语义。

## Data / Config / Permission

- Data model: 无。
- Config: `pom.xml` 使用 Java 21；新增 Actuator、ArchUnit 测试依赖；新增 `src/main/resources/application.yml` 或等价配置。
- Permission: CI `contents: read`。

## Observability

- Logs: 默认 Spring Boot 启动日志即可；不新增业务日志字段。
- Metrics: Actuator health 仅用于 smoke，不定义业务指标。
- Tracing: 不新增；trace/correlation 基线由 LEN-3 横切子任务承接。
- Events: 无。

## Testing Strategy

- Baseline：在生产代码前新增或确认测试入口。
- Spring smoke test：`@SpringBootTest(webEnvironment = RANDOM_PORT)` 调用 `/actuator/health`，证明服务可启动且健康检查返回 UP。
- 架构边界测试：ArchUnit 扫描 `com.spark.user.domain..`，禁止依赖 `org.springframework..`、`jakarta.persistence..`、`javax.persistence..`、`io.grpc..`、`java.sql..` 等外层/技术包。
- 验证命令：`mvn test`（工作目录 `services/backend/user-api`）。如私有包凭据导致依赖解析失败，必须记录原始错误并补充可执行替代证据。

## Rollout And Rollback

- Gray release: 不适用；无生产业务行为变化。
- Kill switch: 可临时关闭新增 CI job 或跳过架构测试，但必须记录原因和恢复计划。
- Rollback: 删除 `user-api` 新增源码/测试/配置/CI 即可回退；无数据或契约残留。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| GitHub Packages 凭据缺失导致 `spark-idl-java` 依赖解析失败 | 不新增契约消费；先运行验证并记录真实失败；必要时拆出不依赖私有包的骨架测试 | Codex |
| Java 21 仅用于 `user-api`，公共包仍为 Java 17 | 在 README/设计中明确范围；公共包升级另开需求 | Codex |
| 健康检查被误用为业务 API | 使用 Actuator `/actuator/health`，README 声明只作 smoke | Codex |
| 架构测试约束过度 | 只锁定 domain 红线，避免要求空接口或过度分层 | Codex |
