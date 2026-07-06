---
requirement_id: "LEN-214"
owner: "forest"
status: "approved"
created_at: "2026-07-06"
related_branch: "feature/LEN-214-fides-bff-logs"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
  - gitops-repo
approved_by: "forest"
approved_at: "2026-07-06T00:00:00+08:00"
decision: "用户明确授权批准中间文件；批准 LEN-214 requirement 与 impact-analysis，代码审查后修订风险与 rollout 策略并刷新门禁。"
---

# [OBS] fides-bff Kratos v3 日志体系收口

## Background

`fides-bff` 已在 Kratos v3 下运行，并作为 `fides-web` 到 Lendora 后端服务的前端 BFF。当前排查请求经过 BFF、下游调用和运行配置问题时，需要稳定、结构化、可关联 trace/request、且不会泄漏敏感信息的日志证据。

它不是什么：本需求不是 `fides-web` 浏览器日志计划，不是 Java 服务日志改造，不是业务审计日志，也不改变业务/API 语义。

它是什么：本需求只收口 `fides-bff` Kratos v3 下的 stdout JSON 日志、请求上下文关联字段、OpenTelemetry 标准运行配置、GitOps/Vault 注入方式和 lint/CI 防漂移规则。

## Goals

- R1：`fides-bff` 进程启动、访问和错误日志必须以结构化 JSON 输出到 stdout，并包含 `service.name`、`service.version`、`level`、`timestamp` 和 `message`。
- R2：请求经过 `fides-bff` 时，访问日志和错误日志必须能通过 `trace_id` 或 `request_id` 关联到同一次请求；能取得当前 span 时包含 `span_id`。
- R3：请求日志字段必须低基数，记录 operation、route pattern、status、latency、error_code、deployment environment 等排障字段，不记录 raw query、请求体或响应体。
- R4：日志不得记录 token、Cookie、Authorization header、OTP、手机号、密码、secret 或其他敏感原文；敏感 key 必须统一脱敏或拒绝。
- R5：OpenTelemetry 运行配置必须使用标准 `OTEL_*` 环境变量，不继续扩展 `OBSERVABILITY_OTEL_*`。
- R6：GitOps/Vault 继续使用 raw Vault KV 到 Kubernetes Secret，再由 Deployment `envFrom` 注入的标准，不新增逐 key模板白名单。
- R7：lint / CI 必须阻止日志规则漂移，包括 Kratos v2 import、裸输出、业务层依赖 observability 实现和绕过统一 logger。

## Non-Goals

- 不做 `fides-web` 日志、浏览器日志或 Next.js 服务端日志。
- 不改 Java 服务日志。
- 不新增业务审计日志。
- 不改变用户界面、业务流程、HTTP/API 响应语义或 protobuf IDL。
- 不记录请求体、响应体、raw query、Authorization、Cookie、token、OTP、手机号或 secret 原文。
- 不手写 OTLP HTTP 请求；第一版以 stdout JSON 为主，OTLP trace 配置只使用标准环境变量。

## User / Business Scenarios

### Scenario 1：stdout JSON 日志可搜索

Given：`fides-bff` 以 Kratos v3 启动。

When：服务输出启动、请求或错误日志。

Then：stdout 每行日志是合法 JSON，并包含服务名、版本、级别、时间和消息字段。

### Scenario 2：请求日志可关联

Given：请求进入 `fides-bff` 并携带或创建 trace/request context。

When：`fides-bff` 输出访问日志或错误日志。

Then：日志包含 `trace_id` 和 `request_id`；存在当前 span 时包含 `span_id`，并可与同次 trace 或错误响应信封关联。

### Scenario 3：失败路径可诊断且不泄密

Given：请求失败、认证失败、输入无效或下游服务不可用。

When：`fides-bff` 输出 WARN 或 ERROR 日志。

Then：日志包含稳定 `error_code` 或 `error_type`，不包含敏感原文。

### Scenario 4：日志规则防漂移

Given：开发者新增日志调用点、裸输出、Kratos v2 import 或绕过统一 logger。

When：执行 Go test、go vet 或 golangci-lint。

Then：检查失败，并提示应使用 Kratos v3 / slog / 统一 logger 路径。

## Business Rules

- BR1：`fides-bff` 日志必须以结构化 JSON 输出，业务代码和中间件必须以 KV / slog Attr 传字段，不通过字符串拼接承载用户输入。
- BR2：请求经过 `fides-bff` 时，日志必须能用 `trace_id` 或 `request_id` 关联到同一次请求链路；能取得当前 span 时应包含 `span_id`。
- BR3：请求日志字段必须低基数，记录 operation、route pattern、status、latency、error_code、deployment environment 等排障字段，不记录 raw query、请求体或响应体。
- BR4：日志不得记录 token、Cookie、Authorization header、OTP、手机号、密码、secret 或其他敏感原文；敏感 key 必须被统一脱敏或拒绝。
- BR5：OpenTelemetry 配置必须使用标准 `OTEL_*` 环境变量；不继续扩展自造 `OBSERVABILITY_OTEL_*` 变量。
- BR6：GitOps/Vault 继续遵守 raw Vault KV 到 Kubernetes Secret 再由 Deployment `envFrom` 注入的标准，不新增 VaultStaticSecret 逐 key template 白名单。
- BR7：lint / CI 必须阻止日志规则漂移，包括禁止 Kratos v2 import、禁止业务层直接依赖 observability 实现、禁止裸输出和绕过统一 logger。

## Acceptance Criteria

| AC | Given | When | Then |
|---|---|---|---|
| AC1 | `fides-bff` 以 Kratos v3 启动 | 服务输出启动、请求或错误日志 | stdout 为合法 JSON，并包含 `service.name`、`service.version`、`level`、`timestamp` 和 `message` |
| AC2 | 请求进入 `fides-bff` 并携带或创建 trace context | `fides-bff` 输出访问日志或错误日志 | 日志包含 `trace_id` 和 `request_id`，且可与同一次 trace 或响应错误信封关联；能取得当前 span 时包含 `span_id` |
| AC3 | 请求失败、认证失败、输入无效或下游不可用 | `fides-bff` 输出 WARN 或 ERROR 日志 | 日志包含稳定 `error_code` 或 `error_type`，且不包含敏感原文 |
| AC4 | 开发者新增日志字段或调用点 | 执行 go test、go vet、golangci-lint | 检查能阻止裸输出、字符串拼接输入、Kratos v2 import 和绕过统一 logger 的代码进入主干 |
| AC5 | dev-1 或 sta-1 需要配置 traces/logs 导出 | 通过 Vault/GitOps 注入运行时配置 | 使用标准 `OTEL_*` key，`fides-bff-runtime` Secret 由 raw env 同步并通过 `envFrom` 注入，不需要修改 VSO key template |
| AC6 | 实现完成并部署到 dev-1 | 执行一次经过 `fides-bff` 的 smoke 请求 | K8s stdout 能看到 JSON 访问日志，日志中的 `trace_id` 能与同次请求链路对齐 |
| AC7 | 合并前执行 fides-bff 质量门禁 | 运行 `make lint`、`make test`、`make build` | 全部通过，PR 描述记录实际命令和结果 |

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 第一版是否需要启用 Kratos OTel Logs handler 直连 logs backend | 工程 | 2026-07-06 | 暂不作为第一版阻塞项：本次以 stdout JSON 为主，避免手写导出器；如当前依赖自然支持再单独接入 |

## Notes

- Jira 来源：LEN-214 `[OBS] fides-bff Kratos v3 日志体系收口`。
- 用户已明确范围：只做 `fides-bff` Kratos v3 日志体系收口，不做 `fides-web`、浏览器日志、Java 服务日志、业务审计或业务/API 语义变化。
- 用户已授权批准中间文件，最终要求本地测试通过后再开 PR，不破坏业务代码和既有基础能力。
