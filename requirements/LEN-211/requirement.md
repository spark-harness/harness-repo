---
requirement_id: "LEN-211"
owner: "forest"
status: "approved"
created_at: "2026-07-05"
related_branch: "feature/LEN-211-java-otel-logs"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - idl-repo
  - business-repo
approved_by: "forest"
approved_at: "2026-07-05T17:54:44+08:00"
decision: "用户明确授权批准中间需要的文件；批准 LEN-211 requirement 与 impact-analysis，允许进入设计和实现。"
---

# Java 服务统一日志规范与 OpenTelemetry trace/log 关联

## Background

当前 Java 服务已经具备 OpenTelemetry tracing 基础，但日志链路仍不统一：服务配置默认关闭 `otel.logs.exporter`，quote-api 还把 `trace_id` 当作业务契约、领域字段和存储字段使用。

它不是什么：本需求不是给每个 Java 服务各写一套私有 logback 配置，也不是在业务代码中直接接入 Sentry SDK。

它是什么：本需求硬切 Java 服务日志链路，统一使用 SLF4J API、Spring Boot 默认 Logback、共享 starter 的 OTel Logs 接入和 OpenTelemetry Context 进行 trace/log 关联。

## Goals

- R1：Harness 团队规范明确 Java 服务只使用 SLF4J API，运行时日志实现使用 Logback，并通过 OTel Logs 与 trace 关联。
- R2：`business-repo/packages/java/spring-starter` 提供统一 logback 和 OTel Logs appender 接入。
- R3：applicant-api、quote-api、origination-api 都能通过环境变量启用 OTLP traces 和 logs 导出。
- R4：三个 Java 服务的主验收 API 都记录包含 `service`、`operation`、`trace_id`、`span_id` 的日志。
- R5：quote-api 不再把 `trace_id` 当作业务契约字段、领域字段、command 字段或数据库字段。
- R6：Java quality gate 禁止业务代码导入 Log4j2、JUL、Commons Logging 或 Logback concrete logger 作为业务日志入口。
- R7：origination-api -> quote-api 的 gRPC 链路继续通过 W3C TraceContext 传播 trace。

## Non-Goals

- 不引入 Sentry Java SDK 作为业务日志入口。
- 不新增贷款申请、报价或 OTP 业务规则。
- 不删除健康检查 HTTP 端点。
- 不把 Sentry endpoint、token 或 header 写入代码或文档真实值。
- 不把日志作为业务状态或审计存储。

## User / Business Scenarios

### Scenario 1：统一日志导出配置

Given：Java 服务配置了 OTLP endpoint 和 headers。

When：服务启动并处理主验收 API。

Then：服务可导出 traces 和 logs，且日志可按 OpenTelemetry trace 关联。

### Scenario 2：quote trace_id 业务字段硬切

Given：quote proto、domain、repository 中存在历史 `trace_id` 业务字段。

When：实现 LEN-211。

Then：`trace_id` 从业务契约、领域模型和数据库 schema 中移除，只由 OpenTelemetry Context 表达。

### Scenario 3：跨服务链路验证

Given：origination-api 通过 gRPC 调用 quote-api。

When：执行 CreateLoanApplication 路径。

Then：origination-api 和 quote-api 通过同一 trace 关联，两个服务日志都包含当前 `trace_id` 和 `span_id`。

## Business Rules

- BR1：Java 业务代码只能使用 `org.slf4j.Logger` 和 `org.slf4j.LoggerFactory` 记录日志。
- BR2：Java 服务不得把 Log4j2、JUL、Commons Logging、Logback concrete logger 或厂商 SDK 作为业务日志入口。
- BR3：日志导出通过标准 OpenTelemetry 环境变量启用，不在代码中硬编码供应商配置。
- BR4：日志必须包含可检索的 `service`、`operation`、`trace_id`、`span_id`；失败日志必须包含稳定 `error_code` 或错误类型。
- BR5：敏感信息、token、secret、PII 和大体积请求/响应体不得进入日志、trace attribute 或门禁证据。
- BR6：发现冲突、过期、多余或重复的日志/trace 关联实现时必须硬切清理，不保留 fallback 或双轨兼容。
- BR7：`trace_id` 不属于业务契约字段；服务间关联必须来自 OpenTelemetry Context。

## Acceptance Criteria

| AC | Given | When | Then |
|---|---|---|---|
| AC1 | 团队查看 Harness Java/日志/Tracing 规范 | 实现 LEN-211 | 规范明确 SLF4J、Logback、OTel Logs 和 trace/log 关联边界 |
| AC2 | Java 服务使用共享 starter | 服务启动 | 统一 Logback 配置和 OTel appender 生效 |
| AC3 | applicant-api 配置 OTLP traces/logs | 调用 SendOtp | 日志包含 service、operation、trace_id、span_id 并可关联 trace |
| AC4 | quote-api 配置 OTLP traces/logs | 调用 CreateQuote | 日志包含 service、operation、trace_id、span_id 并可关联 trace |
| AC5 | origination-api 配置 OTLP traces/logs | 调用 CreateLoanApplication | 日志包含 service、operation、trace_id、span_id 并可关联 trace |
| AC6 | origination-api 调用 quote-api | 执行跨服务路径 | 同一个 trace 覆盖 origination-api -> quote-api，两个服务日志可按同一 trace_id 查询 |
| AC7 | quote-api 存在历史 trace_id 业务字段 | 实现 LEN-211 | proto、domain、command、repository、migration 和 BFF 请求都不再使用业务 trace_id |
| AC8 | Java quality gate 运行 | 检查业务代码导入 | 非 SLF4J 日志 API 被阻断 |

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 本地或 dev 环境是否具备可用 Sentry OTLP endpoint 和 headers | forest | 合并后运行验证前 | 不阻塞本地代码测试 |

## Notes

- Jira 来源：LEN-211 `[OBS] Java 服务统一日志规范与 OpenTelemetry trace/log 关联`。
- 用户已授权批准中间生命周期文件，本需求可以直接进入实现和本地验证。
