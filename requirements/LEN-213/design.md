---
requirement_id: "LEN-213"
owner: "forest"
status: "approved"
updated_at: "2026-07-06"
approved_by: "forest"
approved_at: "2026-07-06T00:00:00+08:00"
decision: "用户明确授权批准中间的文件；批准 LEN-213 design，采用 fides-web 服务端 stdout JSON logger 与 lint 防漂移方案。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, R4, AC1, AC5 | D1：新增 `fides-web` server logger，输出固定 schema 的 JSON/KV 日志 | stdout JSON，字段低基数 |
| R2, AC2 | D2：logger 从 active OTel span 提取 trace/span；无 active span 时从 `traceparent` 提取 trace id，兜底 request id | 不把 trace id 写入业务契约 |
| R3, AC3 | D3：runtime config 与 BFF proxy 在关键成功/失败路径接入日志 | 不改变业务响应契约 |
| R5, AC3, AC5 | D4：日志字段 allowlist + 敏感字段拒绝 | 不记录 header/body/token/OTP/手机号 |
| R6, AC4, AC7 | D5：ESLint 禁止业务代码直接 `console.*`，只允许 logger 实现文件输出 JSON | CI 复用 `pnpm lint` |
| R7, AC6 | D6：public runtime config 输出不变，继续拒绝 legacy `NEXT_PUBLIC_*` | 不把 server secret 暴露到浏览器 |
| R8, AC6 | D7：不修改 GitOps/Vault key template，保留 raw env -> Secret -> envFrom | 如需环境调参另走 GitOps |

## Summary

本方案在 `fides-web` 服务端组合/基础设施层增加统一 logger。业务路径通过 logger 传入受控 KV 字段，logger 负责补齐 timestamp、service、level、operation、trace/request 关联字段，并输出单行 JSON 到 stdout。

第一版不引入新的日志后端 SDK，也不直接实现 OTEL Logs exporter。这样可以满足本票的本地和集群 stdout JSON 验收，同时避免把供应商配置或 secret 绑定进应用代码。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| fides | 新增服务端 logger、请求上下文工具、runtime config 日志、BFF proxy 访问/失败日志、lint 规则和测试 | 覆盖 LEN-213 服务端日志验收 |
| Harness lifecycle | 新增 LEN-213 requirement、impact-analysis、design、tasks、gate/evidence/review | 支持 PR 和合并追溯 |

## API / Contract Design

- Protobuf IDL required: No.
- Proto files: N/A.
- Buf module: N/A.
- Buf config version: v2 not touched.
- Generated outputs: N/A.
- Breaking check baseline: N/A.
- Compatibility strategy: BFF proxy request/response 透传行为保持不变；public runtime config JSON shape 保持不变。

### Error Code Registry

本票新增的错误码只用于 `fides-web` 服务端结构化日志，不进入浏览器响应契约。

| Error Code | HTTP / gRPC Mapping | Meaning | Retryable | User Visible | Owner | Status |
|---|---|---|---:|---:|---|---|
| `FIDES-DEPENDENCY-0001` | N/A, log-only | `fides-web` BFF proxy 调用内部 `fides-bff` 失败或抛出异常 | Yes | No | frontend | Active |
| `FIDES-SYSTEM-0001` | N/A, log-only | `fides-web` 服务端 runtime config 加载或校验失败 | Yes | No | frontend | Active |

## Application Design

### D1：Server Logger

新增 `src/infrastructure/observability/server-logger.ts`：

- 对外提供 `info`、`warn`、`error` 等方法。
- 固定基础字段：`timestamp`、`level`、`service: "fides-web"`、`operation`。
- 仅允许受控字段进入日志，例如 `route`, `status`, `latency_ms`, `error_code`, `error_type`, `deployment_environment`, `trace_id`, `span_id`, `request_id`。
- 输出为单行 JSON，便于容器 stdout 采集。

### D2：Trace / Request 关联

新增或内聚请求上下文工具：

- 优先从 OpenTelemetry active span 读取 `trace_id` 与 `span_id`。
- 如果 active span 不存在，从请求 header `traceparent` 只解析 trace id，不把 upstream parent span 记为当前 `span_id`。
- 如果没有有效 trace context，生成 `request_id`。
- 响应日志、错误日志和下游失败日志复用同一个 request context。

### D3：服务端路径接入

接入点：

- BFF proxy route：记录开始后的最终结果、HTTP status、latency、route pattern、trace/request context；fetch 抛异常时记录 ERROR 并返回原有异常语义。
- BFF proxy route：对内部 BFF fetch 设置单次请求超时边界；超时记录 `FIDES-DEPENDENCY-0001` + `TimeoutError`，不做自动重试。
- Runtime config：成功加载时记录 INFO；配置校验失败时记录 ERROR，包含稳定 `error_code`，不记录 env 值。
- Route handler：复用 api/composition 层，不把 logger 引入 domain/application/presentation。

### D4：安全字段边界

logger 不接受任意对象直出：

- 对字段名做 allowlist 检查。
- 拒绝敏感字段名：`authorization`、`cookie`、`token`、`secret`、`password`、`otp`、`phone`、`body`、`headers`、`request`、`response`。
- 测试覆盖合法字段、敏感字段拒绝、手机号/OTP/token 不进入输出。

### D5：Lint 防漂移

更新 `eslint.config.mjs`：

- 对 `**/*.{ts,tsx}` 禁止 `console.*`。
- 对 logger 实现文件单独豁免最终 stdout 输出。
- 保留现有 `process.env` 只能经 `src/config/env.ts` 读取规则。

## Data / Config / Permission

- Data model: No change.
- Config: 不新增 runtime env；继续使用现有 `FIDES_RUNTIME_ENV` 作为 deployment environment 字段来源。
- Permission: No change.
- Secret: 不记录 secret 原文，不暴露内部 BFF URL 到 public runtime config。

## Observability

- Logs: 新增 `fides-web` 服务端 JSON logs，覆盖 runtime config 与 BFF proxy。
- Metrics: No change.
- Tracing: 不新增 span 创建；仅读取当前 OTel context 或 W3C `traceparent` 作为日志关联字段。
- Events: No change.

## Testing Strategy

- 单元测试 `server-logger` JSON schema、字段 allowlist、敏感字段拒绝、traceparent 解析和 request id 兜底。
- 更新 BFF proxy 测试，断言成功和下游失败路径会记录安全 JSON 日志，不泄露 Authorization/body。
- 更新 runtime config 测试，断言成功/失败路径记录稳定 operation 和 error_code。
- 运行 fides-web `pnpm lint`、`pnpm lint:deps`、`pnpm test`、`pnpm build`。

## Rollout And Rollback

- Rollout: 随 `fides-web` PR 合并和镜像发布生效，平台继续采集 stdout。
- Rollback: 回滚 `business-repo` 变更并重新部署 `fides-web`。
- GitOps/Vault: 本票不新增 GitOps/Vault key template；如果后续需要环境级日志开关，另开票处理。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| 日志量增加影响排查噪音 | 仅记录入口成功/失败和配置加载结果，不在循环或高频内部步骤记录 | forest |
| 误记录敏感信息 | logger allowlist + 敏感字段测试 + ESLint 防绕过 | forest |
| 没有 active OTel span 时缺少 trace id | 从 `traceparent` 提取；仍无 context 时使用 `request_id` | forest |
