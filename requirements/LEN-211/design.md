---
requirement_id: "LEN-211"
owner: "codex"
status: "approved"
updated_at: "2026-07-05T17:54:44+08:00"
approved_by: "forest"
approved_at: "2026-07-05T17:54:44+08:00"
decision: "用户明确授权批准中间需要的文件；批准 LEN-211 design，采用共享 starter 统一日志接入并硬切 quote trace_id 业务字段。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, R6 | D1：更新团队规范和 Java quality gate，只允许 SLF4J 业务日志 API | Checkstyle `IllegalImport` 阻断非 SLF4J 日志入口 |
| R2, R3 | D2：spring-starter 提供统一 `logback-spring.xml` 和 OTel Logback appender 安装 | 服务不各自维护重复 Logback 配置 |
| R4 | D3：applicant、quote、origination 主验收 API 输出低基数字段日志 | applicant 已有 SendOtp telemetry，quote/origination 补主路径日志 |
| R5 | D4：quote trace_id 硬切 | proto reserved、domain/command/repository/migration/BFF 调用同步清理 |
| R7 | D5：保留 W3C TraceContext gRPC 传播 | origination-api `GrpcQuoteGateway` 传播逻辑不改变 |

## Summary

本设计把日志实现收敛到共享 starter：业务服务继续只写 SLF4J 日志；starter 提供 Logback 输出、OpenTelemetry MDC 注入和 OTel Logs appender。quote-api 的历史 `trace_id` 业务字段删除，trace/log 关联仅来自 OpenTelemetry Context。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| spring-starter | 新增 Logback / OTel Logs appender 配置和安装器 | 避免每个服务重复配置 |
| applicant-api | 启用 logs exporter 配置路径 | SendOtp 已有 trace/log 关联日志 |
| quote-api | 删除业务 trace_id，补 CreateQuote/GetQuote 日志 | 满足 quote 主验收和硬切要求 |
| origination-api | 启用 logs exporter 配置路径，补 CreateLoanApplication 日志 | 满足跨服务链路验收 |
| fides-bff | 不再发送 quote trace_id request 字段 | 业务 trace_id 不再属于 quote 契约 |

## API / Contract Design

- Protobuf IDL required: yes.
- Proto files: `vesta/lendora/quote/v1/quote.proto`.
- Buf module: `local/lendora-quote`.
- Buf config version: v2.
- Generated outputs: 本仓只改 IDL；业务仓当前消费发布契约，调用代码先兼容删除字段。
- Breaking check baseline: `master`.
- Compatibility strategy: `CreateQuoteRequest.trace_id` 字段号和字段名 reserved；调用方改用 W3C TraceContext。

## Data / Config / Permission

- Data model: `quotes.trace_id` 删除，新增 `V2__remove_quote_trace_id.sql`。
- Config: `OTEL_LOGS_EXPORTER` 默认跟随 `OTEL_TRACES_EXPORTER`；logs endpoint/header 可独立配置，也可继承通用 OTLP 配置。
- Permission: 无。

## Observability

- Logs: SLF4J 业务日志；Logback 运行时；日志包含 `service`、`operation`、`trace_id`、`span_id`，失败日志包含 `error_code`。
- Metrics: 不新增。
- Tracing: 保留 OpenTelemetry server/client span 和 W3C TraceContext。
- Events: 无。

## Testing Strategy

- IDL：`buf lint`、`buf breaking --against .git#branch=master`。
- Java：spring-starter、applicant-api、quote-api、origination-api Maven test。
- Go：fides-bff `go test ./internal/data`。
- Quality：`python tooling/java-quality/tests/test_java_quality.py`。
- Evidence：记录本地测试和已知 Maven 缓存修复步骤。

## Rollout And Rollback

- Gray release: IDL PR 先合并，业务 PR 再合并；运行环境逐服务启用 logs exporter。
- Kill switch: `OTEL_LOGS_EXPORTER=none`。
- Rollback: 回滚 PR；DB migration 不恢复历史 `trace_id`。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| 删除 proto 字段为 breaking change | Buf breaking 记录风险，业务调用同步迁移 | codex |
| OTel appender 在无 SDK 时提前启动 | appender 安装器在 ApplicationReadyEvent 安装 OpenTelemetry | codex |
| 日志字段泄露敏感信息 | 只记录 service/operation/result/error_code/trace/span，不记录请求体 | codex |
