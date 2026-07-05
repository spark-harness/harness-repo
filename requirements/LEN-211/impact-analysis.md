---
requirement_id: "LEN-211"
analyst: "codex"
status: "approved"
updated_at: "2026-07-05T17:54:44+08:00"
approved_by: "forest"
approved_at: "2026-07-05T17:54:44+08:00"
decision: "用户明确授权批准中间需要的文件；确认 LEN-211 影响 harness-repo、idl-repo、business-repo，服务为 fides-bff、applicant-api、quote-api、origination-api。"
idl_impact: "yes"
idl_impact_reason: "quote.proto 删除 CreateQuoteRequest.trace_id，并保留字段号和字段名 reserved。"
---

# Impact Analysis

## Summary

LEN-211 影响 Java 可观测性基线、quote protobuf 契约、quote-api 数据结构、fides-bff quote 调用和 Java quality gate。

## Affected Domains

- `frontend`：fides-bff 不再向 quote-api 传业务 `trace_id` 字段。
- `pricing`：quote-api 删除业务 `trace_id` 字段，并补主路径日志。
- `applicant`：applicant-api 启用 OTel Logs 配置。
- `shared`：spring-starter 提供统一 Logback / OTel Logs 接入。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides-bff | business-repo | 删除 CreateQuoteRequest.trace_id 调用 | yes |
| applicant-api | business-repo | 配置 OTLP logs 并验证日志关联 | yes |
| quote-api | business-repo | 删除业务 trace_id，补日志，更新 migration | yes |
| origination-api | business-repo | 配置 OTLP logs，补跨服务主路径日志 | yes |
| spring-starter | business-repo | 统一 Logback / OTel Logs appender | no |

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: yes.
- Contract repo: `idl-repo`.
- Proto files: `vesta/lendora/quote/v1/quote.proto`.
- Buf module: `local/lendora-quote`.
- Buf config version: v2.
- Required buf checks: lint / generate / breaking.
- Breaking baseline: `master`.
- Compatibility risk: 删除 request 字段属于外部契约变化；使用 `reserved 5` 和 `reserved "trace_id"` 防止复用，调用方必须改为 W3C TraceContext。

## Data Impact

- Database schema: `quote-api` 删除 `quotes.trace_id`，新增 migration `V2__remove_quote_trace_id.sql`。
- Data migration: 删除历史 trace_id 列，不回填。
- Backfill: 无。
- Cache: 无。

## Config / Permission / Observability Impact

- Config: 三个 Java 服务新增 `OTEL_LOGS_EXPORTER`、`OTEL_EXPORTER_OTLP_LOGS_ENDPOINT`、`OTEL_EXPORTER_OTLP_LOGS_HEADERS` 配置路径。
- Permission: 无权限边界变化。
- Metrics: 不新增指标。
- Logs: 统一通过 SLF4J + Logback + OTel appender 输出，主路径日志携带 `service`、`operation`、`trace_id`、`span_id`。
- Tracing: 保持 W3C TraceContext，origination-api -> quote-api gRPC 传播不变。
- Events: 无。

## Rollout And Rollback

- Gray release: 先合并 IDL，再合并 business-repo；环境中配置 logs exporter 后逐服务验证。
- Kill switch: 将 `OTEL_LOGS_EXPORTER=none` 可关闭 logs 导出，不影响业务逻辑。
- Rollback steps: 回滚业务仓和 IDL 变更；如已执行 DB migration，回滚不恢复历史 trace_id 数据。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| 删除 proto 字段影响旧调用方 | fides-bff 或其他调用方编译/运行失败 | 本需求同步删除 fides-bff 字段发送，并用 Buf breaking 记录风险 | codex |
| OTel Logs 配置错误 | Sentry 查不到日志 | 保留 exporter kill switch，并在 evidence 记录本地配置测试 | codex |
| DB rollback 无法恢复历史 trace_id | 历史排障字段消失 | trace_id 不再是业务字段，保留 OpenTelemetry trace/log 作为事实源 | codex |
| Maven 本地缓存失败标记 | 本地测试被依赖解析阻断 | 清理 `.lastUpdated` 后重跑测试，证据记录命令 | codex |
