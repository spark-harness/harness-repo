---
requirement_id: "LEN-213"
analyst: "forest"
status: "approved"
updated_at: "2026-07-06"
approved_by: "forest"
approved_at: "2026-07-06T00:00:00+08:00"
decision: "用户明确授权批准中间的文件；批准 LEN-213 impact-analysis，允许进入设计和实现。"
idl_impact: "no"
idl_impact_reason: "本需求只修改 fides-web 服务端日志与 lint/CI 防漂移，不新增或修改 protobuf IDL、HTTP 外部契约或生成契约。"
---

# Impact Analysis

## Summary

LEN-213 影响 `fides-web` 服务端日志、server-side OTLP Logs exporter、GitOps runtime env 注入、测试和 lint 防漂移规则，并补齐 Harness 生命周期证据；不影响 IDL、数据库、用户界面或 `fides-bff` 服务实现。

## Affected Domains

- 前端体验：`fides-web` Next.js server/runtime、runtime config、BFF proxy、route handler。
- 运行质量：服务端 JSON 日志、trace/request 关联、安全字段边界和 lint 防漂移。
- 部署配置：`fides` GitOps ConfigMap 与 VaultStaticSecret raw env passthrough。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides | `business-repo/apps/fides-web` | 增加服务端统一 logger、server-side OTLP Logs exporter、接入 runtime config 与 BFF proxy 日志、更新 lint/test/build 验证 | No |
| fides GitOps | `gitops-repo/apps/fides` | 打开 `OTEL_LOGS_EXPORTER`，通过 Vault raw env -> Secret -> envFrom 注入 server-only OTEL logs endpoint/header | No |
| Harness lifecycle | `harness-repo/requirements/LEN-213` | 记录需求、影响、设计、任务、门禁和验收证据 | No |

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: No.
- Contract repo: N/A.
- Proto files: N/A.
- Buf module: N/A.
- Buf config version: v2 not touched.
- Required buf checks: N/A.
- Breaking baseline: N/A.
- Compatibility risk: Low; `fides-web` 对浏览器暴露的 runtime config 形状不变化，对 BFF 请求契约不变化。

## Data Impact

- Database schema: No change.
- Data migration: No change.
- Backfill: No change.
- Cache: No change.
- Runtime storage: No change.

## Config / Permission / Observability Impact

- Config: 继续使用现有 `FIDES_RUNTIME_ENV`、`FIDES_BFF_BASE_URL`、`FIDES_BROWSER_TRACING_*` 等 raw env；新增 server-only `OTEL_LOGS_EXPORTER`、`OTEL_EXPORTER_OTLP_LOGS_ENDPOINT`、`OTEL_EXPORTER_OTLP_LOGS_HEADERS`、`OTEL_SERVICE_NAME`；不新增 VaultStaticSecret key template allowlist。
- Permission: No change.
- Metrics: No change.
- Logs: 新增 `fides-web` 服务端 stdout JSON/KV 日志，并在 `OTEL_LOGS_EXPORTER=otlp` 时通过 server-side OTLP Logs exporter 双写，覆盖 runtime config 与 BFF proxy 的成功、失败和异常路径。
- Tracing: 从 OpenTelemetry active span 提取 `trace_id` / `span_id`；没有 active span 时只从 W3C `traceparent` 提取 `trace_id`，无有效 trace 时使用 `request_id` 关联同一请求。
- Secrets: `OTEL_EXPORTER_OTLP_LOGS_HEADERS` 只从 Vault/Kubernetes Secret 注入到服务端环境，不进入 `/api/runtime-config` 或浏览器 bundle。
- Events: No change.

## Rollout And Rollback

- Gray release: 随 `fides-web` 镜像发布和 GitOps 配置同步；stdout JSON 继续写容器日志，OTLP Logs exporter 由 server-only env 开启。
- Kill switch: 将 `OTEL_LOGS_EXPORTER` 改为 `none` 或回滚 GitOps ConfigMap 可关闭 OTLP logs exporter；stdout JSON 保留。
- Rollback steps: revert `business-repo` 和 `gitops-repo` PR 后重新部署 `fides-web`，Harness 文件保留交付记录或随回滚 PR 更新状态。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| 日志字段误带敏感 header 或 body | 造成凭证或 PII 暴露 | 统一 logger 只接受 allowlist 字段，并用测试覆盖拒绝敏感字段 | forest |
| 直接使用 `console.*` 绕过统一 logger | JSON 格式和安全边界漂移 | ESLint 增加 `console.*` 禁止规则，仅允许 logger 实现文件输出 | forest |
| route path 记录高基数 URL | 日志聚合困难 | 记录 route pattern 和受控 operation，不记录完整 URL 路径参数 | forest |
| 无 active span 时无法关联 trace | 部分本地路径只能 request 级关联 | 从 `traceparent` 提取 trace id；没有 trace context 时生成 `request_id` | forest |
| Vault 缺少 OTLP logs endpoint/header | OTLP Logs exporter 无法投递 | env cross-field 校验要求 `OTEL_LOGS_EXPORTER=otlp` 时必须有 endpoint；失败时 stdout 写一次安全诊断 `FIDES-OBSERVABILITY-0001` | forest |
| OTLP headers 泄露到浏览器 | Sentry/Vault secret 暴露 | public runtime config allowlist 不包含 server OTEL logs env；测试断言不暴露 `OTEL_EXPORTER_OTLP_LOGS_HEADERS` | forest |
