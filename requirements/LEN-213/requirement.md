---
requirement_id: "LEN-213"
owner: "forest"
status: "approved"
created_at: "2026-07-06"
related_branch: "feature/LEN-213-fides-web-server-logs"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
approved_by: "forest"
approved_at: "2026-07-06T00:00:00+08:00"
decision: "用户明确授权批准中间的文件；批准 LEN-213 requirement 与 impact-analysis，允许进入设计和实现。"
---

# [OBS] fides-web 服务端 JSON logs 与 trace 关联计划

## Background

当前 `fides-web` 已完成浏览器 tracing 和服务端 runtime config 硬切，但 Next.js 服务端运行路径的日志仍缺少统一结构、字段边界和 trace/request 关联规则。

它不是什么：本需求不是浏览器端日志采集，不是 `fides-bff` 或 Java 服务日志治理，也不是业务审计日志。

它是什么：本需求只补齐 `fides-web` 服务端运行日志，让 runtime config、BFF proxy、route handler 等服务端路径能输出安全、低基数、可关联 trace 或 request 的 JSON 日志。

## Goals

- R1：`fides-web` 服务端日志以 JSON/KV 方式输出到 stdout，并在启用 `OTEL_LOGS_EXPORTER=otlp` 时通过 server-side OTLP Logs exporter 双写。
- R2：服务端日志字段包含 `service`、`operation`、`level`、`timestamp`，并尽量包含 `trace_id`、`span_id` 或 `request_id`。
- R3：runtime config、BFF proxy、route handler 等服务端路径在成功、可诊断失败和异常路径输出稳定日志。
- R4：日志字段保持低基数，只记录 route pattern、operation、status、latency、error_code 或 error_type、deployment environment 等排障字段。
- R5：日志不得包含手机号、OTP、token、Cookie、Authorization header、完整请求体、完整响应体或 runtime secret 原文。
- R6：lint / CI 阻止 fides-web 业务代码直接使用 `console.*` 或绕过统一服务端 logger。
- R7：浏览器 public runtime config 继续只暴露明确允许的 tracing 配置，不暴露 server secret、OTEL headers 或内部 endpoint。
- R8：继续保留 Vault raw env -> Kubernetes Secret -> Deployment `envFrom` 标准，不新增 VaultStaticSecret key template allowlist。

## Non-Goals

- 不做浏览器端日志上报。
- 不改造 `fides-bff` 日志。
- 不改造 Java 服务日志。
- 不改用户界面或业务流程。
- 不引入业务审计日志。
- 不替换日志后端平台。
- 不做浏览器端日志上报；server-side OTEL Logs exporter 只在 Next.js 服务端运行路径启用。

## User / Business Scenarios

### Scenario 1：服务端请求日志可关联

Given：请求经过 `fides-web` Next.js 服务端 runtime。

When：服务端处理 runtime config 或 BFF proxy 路径。

Then：stdout 输出合法 JSON 日志，包含服务名、操作名、级别、时间戳和可关联的 trace 或 request 标识；启用 server-side OTLP logs exporter 时同一安全字段日志可进入日志后端。

### Scenario 2：可诊断失败不泄露敏感信息

Given：runtime config 或 BFF proxy 出现配置错误、下游失败或异常。

When：`fides-web` 记录 WARN 或 ERROR 日志。

Then：日志包含稳定 `error_code` 或 `error_type`，不包含 Authorization、Cookie、token、OTP、手机号、请求体或响应体原文。

### Scenario 3：日志规则防漂移

Given：开发者在 fides-web 业务代码中新增 `console.*` 输出或绕过统一 logger。

When：执行 lint / CI。

Then：检查失败，并提示应使用统一服务端 logger。

## Business Rules

- BR1：服务端日志必须通过统一 logger 记录，业务代码不得直接拼接字符串承载用户输入。
- BR2：日志中能取得当前 OpenTelemetry span 时必须写入 `trace_id` 和 `span_id`。
- BR3：没有有效 trace context 时必须生成或复用 `request_id`，确保同一服务端处理路径可串联。
- BR4：日志字段必须是安全字段；未知字段、敏感字段名和高风险原文必须被拒绝或脱敏。
- BR5：服务端 logger 可以使用 Node 侧 `console.*` 输出最终 JSON，但应用代码不得直接调用 `console.*`。
- BR6：`FIDES_BROWSER_TRACING_*` 等 public runtime config 只服务浏览器 tracing，不得暴露内部 OTEL header、server secret 或内部 BFF URL。
- BR7：运行时配置继续通过 Vault raw env -> Secret -> `envFrom` 注入，不新增逐 key template allowlist。

## Acceptance Criteria

| AC | Given | When | Then |
|---|---|---|---|
| AC1 | `fides-web` 在本地或集群以服务端模式运行 | 请求经过 Next.js server/runtime 路径 | stdout 输出合法 JSON 日志，并包含 `service`、`operation`、`level`、`timestamp`、`request_id` 或 `trace_id`；启用 `OTEL_LOGS_EXPORTER=otlp` 时同一日志进入 server-side OTLP Logs exporter |
| AC2 | 请求带有 trace context 或服务端创建了 trace context | `fides-web` 记录服务端访问或错误日志 | stdout JSON 和 OTLP log record 使用同一个 `trace_id`；能取得当前 span 时包含 `span_id` |
| AC3 | runtime config 或 BFF proxy 发生可诊断失败 | `fides-web` 记录 WARN 或 ERROR 日志 | 日志包含稳定 `error_code` 或 `error_type`，且不包含敏感原文 |
| AC4 | 开发者在 fides-web 业务代码中新增 `console.*` 或绕过统一 logger | 执行 lint / CI | 检查失败并指出应使用统一服务端 logger |
| AC5 | 开发者新增服务端日志字段 | 执行测试和 lint | 字段通过低基数、安全字段校验，不能记录手机号、OTP、token、Cookie、Authorization header 或请求/响应体 |
| AC6 | dev-1 或 sta-1 需要调整日志/OTEL runtime 配置 | 配置通过 GitOps/Vault 注入 | `fides-runtime` 继续使用 `envFrom` 注入，VaultStaticSecret 不需要逐 key 模板维护 |
| AC7 | 实现完成后执行 fides-web CI | 运行 lint、dependency gate、test、build | 全部通过，且 PR 描述记录实际命令与验证范围 |

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 服务端 logs 是否需要在后续版本直接导出到 OTEL Logs backend | 工程 | 2026-07-06 | 已明确：本次 follow-up 增加 server-side OTLP Logs exporter，不做浏览器端日志上报 |

## Notes

- Jira 来源：LEN-213 `[OBS] fides-web 服务端 JSON logs 与 trace 关联计划`。
- 用户已限定范围：只做 `fides-web` 服务端运行日志，不做浏览器端日志上报，不做 `fides-bff`。
- 用户已授权批准中间文件，最终验收要求本地测试、开 PR 并合并到 `master`。
