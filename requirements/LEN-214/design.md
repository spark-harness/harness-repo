---
requirement_id: "LEN-214"
owner: "forest"
status: "approved"
updated_at: "2026-07-06"
approved_by: "forest"
approved_at: "2026-07-06T00:00:00+08:00"
decision: "用户明确授权批准中间文件；批准 LEN-214 design，代码审查后补齐安全 header 校验、OTEL header decode、logger schema 和显式配置注入。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, AC1 | D1：保留 Kratos v3 stdout JSON logger 作为唯一进程日志出口，并补测试验证字段 schema | 不引入 Kratos v2 log.Helper 兼容层 |
| R2, R3, AC2, AC3 | D2：在 `bffkit.TraceFilter` 中统一生成/传播 trace/request context，并让 access log 自动带 `trace_id`、`request_id`、`span_id`、route pattern、status、latency 和 error_code | 低基数 operation，不记录 raw query/body |
| R4, AC3, AC4 | D3：日志只输出 allowlist 字段；lint 禁止裸输出和绕过统一 logger | 防止敏感字段漂移 |
| R5, AC5 | D4：将 fides-bff OTel runtime 配置硬切到标准 `OTEL_*` env，并兼容 OTel SDK 常见开关语义 | 不继续扩展 `OBSERVABILITY_OTEL_*` |
| R6, AC5 | D5：GitOps fides-bff VaultStaticSecret 使用 raw passthrough，Deployment 继续 `envFrom` | 不维护逐 key template |
| R7, AC4, AC7 | D6：强化 `.golangci.yml` depguard 和 custom checks，阻止 Kratos v2 import、裸输出、业务层 observability 依赖和 logger 绕过 | CI 复用 `make lint` |
| AC6, AC7 | D7：本地测试和 PR 证据覆盖 Go unit tests、vet、lint、build、GitOps kustomize 和 Harness gate | dev-1 smoke 需要合并部署后执行 |

## Summary

本方案不改变 `fides-bff` 的业务路由、HTTP 响应、protobuf 契约或下游调用语义。实现集中在三个层面：

- `business-repo/apps/fides-bff`：Kratos v3 JSON logger、标准 OTel 配置和 fides-bff lint/test。
- `business-repo/packages/go/bffkit`：请求 trace middleware 的 access log 字段、低基数 operation、span_id、deployment environment 和测试。
- `gitops-repo/apps/fides-bff`：标准 `OTEL_*` runtime env 与 Vault raw env passthrough。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| fides-bff | 更新 OTel config loader、README、`.env.example`、logger tests 和 lint 防漂移规则 | 覆盖 LEN-214 Kratos v3 日志收口 |
| bffkit | 强化 `TraceFilter` access log 字段、trace/span/request context 和测试 | fides-bff 访问日志的实际中间件入口 |
| idl-repo | 只作为 fides-bff 现有 proto path 的 no-change gate baseline | 服务矩阵要求 idl_required 服务具备契约仓，不修改 IDL |
| GitOps fides-bff | ConfigMap 改为标准 `OTEL_*`；dev-1/sta-1 VaultStaticSecret 改为 raw passthrough | 保持 raw Vault KV -> Secret -> `envFrom` |
| Harness lifecycle | 补齐 requirement、impact、design、tasks、gates、review 和 evidence | 支持 PR 和合并追溯 |

## API / Contract Design

- Protobuf IDL required: No.
- Proto files: N/A.
- Buf module: `local/lendora-fides-bff` not touched.
- Buf config version: v2 not touched.
- Generated outputs: N/A.
- Breaking check baseline: N/A.
- Compatibility strategy: HTTP routes, response JSON and generated protobuf clients remain unchanged. `trace_id` stays runtime correlation metadata and does not become a business contract field.

## Application Design

### D1：Kratos v3 JSON Logger

`cmd/fides-bff/main.go` continues to create a Kratos v3 logger with `log.NewHandler(...log.FormatJSON)` and static `service.name` / `service.version` fields. The implementation must add focused tests or executable checks proving stdout JSON contains the required fields and must not introduce Kratos v2 `log.Helper`.

### D2：TraceFilter Access Log

`packages/go/bffkit/trace.go` remains the single HTTP request observability middleware:

- Extract W3C `traceparent` / `tracestate` before starting the server span.
- Prefer inbound `X-Trace-Id` as request correlation id when present; otherwise use current span trace id; otherwise create a random trace id.
- Set response `X-Trace-Id` and `X-Correlation-Id`.
- Put `trace_id`, `request_id`, and HTTP request into context for service/data layers.
- Write access log with stable `operation` based on route pattern, not raw path.
- Include `span_id` when the current span context is valid.
- Include `deployment.environment` when configured through resource/env.
- Include `error_code` when `bffkit.SetErrorCode` was used.
- Keep existing HTTP metrics on low-cardinality route pattern labels.

### D3：Sensitive Field Boundary

Access logs must not include Authorization, Cookie, token, OTP, phone, raw query, request body or response body. The middleware does not accept arbitrary request maps; it emits only a fixed key list. Tests must cover that sensitive request input is not reflected in log key/value pairs.

### D4：Standard OTel Config

`configs/config.yaml` and config loader tests switch from custom `OBSERVABILITY_OTEL_*` vars to standard OTel vars:

| Old | New |
|---|---|
| `OBSERVABILITY_OTEL_ENABLED` | `OTEL_SDK_DISABLED=false` plus `OTEL_TRACES_EXPORTER=otlp` |
| `OBSERVABILITY_OTEL_ENDPOINT` | `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` |
| `OBSERVABILITY_OTEL_PROTOCOL` | `OTEL_EXPORTER_OTLP_TRACES_PROTOCOL` |
| `OBSERVABILITY_OTEL_X_SENTRY_AUTH` | `OTEL_EXPORTER_OTLP_TRACES_HEADERS` |
| `OBSERVABILITY_OTEL_ENVIRONMENT` | `OTEL_RESOURCE_ATTRIBUTES=deployment.environment=...` |
| `OBSERVABILITY_OTEL_RELEASE` | `OTEL_SERVICE_VERSION` or build version fallback |

`internal/observability.Setup` should treat disabled SDK or `OTEL_TRACES_EXPORTER=none` as no-op. When traces export is configured as `otlp` but endpoint is missing, it must also no-op rather than crash so Vault key migration timing cannot break BFF startup.

### D5：GitOps Raw Secret Passthrough

`gitops-repo/apps/fides-bff/base/env-configmap.yaml` uses standard `OTEL_*` non-secret keys and owns `OTEL_TRACES_EXPORTER=otlp`. `overlays/{dev-1,sta-1}/vault-static-secret.yaml` keeps `destination.name: fides-bff-runtime`, `create`, `overwrite` and rollout restart target, but removes per-key transformation templates so raw Vault keys sync to the Kubernetes Secret. Vault raw KV owns `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` and `OTEL_EXPORTER_OTLP_TRACES_HEADERS`; if those keys are absent during migration, the app starts with stdout JSON and no-op trace export. Deployment keeps:

```yaml
envFrom:
  - configMapRef:
      name: fides-bff-env
  - secretRef:
      name: fides-bff-runtime
```

### D6：Lint / CI 防漂移

`.golangci.yml` remains the primary fides-bff lint surface. Add depguard or local custom checks so CI fails on:

- `github.com/go-kratos/kratos/v2` imports anywhere in `apps/fides-bff`.
- business/service/data layers importing `internal/observability`.
- `fmt.Print*`, standard `log.Print*`, direct `os.Stdout` / `os.Stderr` writes outside the Kratos logger bootstrap.
- application layers bypassing `slog` / Kratos logger for request logs.

If golangci-lint cannot express a rule precisely, add a small repo-local script called by `make lint` before `golangci-lint run`.

## Data / Config / Permission

- Data model: No change.
- Config: Standard `OTEL_*` env replaces custom `OBSERVABILITY_OTEL_*`. `.env.example`, README, config loader tests and GitOps ConfigMap/VaultStaticSecret stay aligned.
- Permission: No change.
- Secret: No secret values are committed. `OTEL_EXPORTER_OTLP_TRACES_HEADERS` remains server-side runtime secret from Vault/Kubernetes Secret only.

## Observability

- Logs: stdout JSON access logs include stable schema and request correlation fields. No OTel Logs direct exporter is introduced in this first slice.
- Metrics: Existing `http.server.requests` and `http.server.duration` stay on route pattern/status/error_code labels.
- Tracing: Existing OTel trace provider remains optional; config moves to standard env names and W3C trace propagation remains unchanged.
- Events: No change.

## Testing Strategy

- Add/adjust `bffkit` unit tests for `TraceFilter` access log key/value fields, `span_id`, low-cardinality operation, error_code and sensitive input exclusion.
- Add/adjust `fides-bff` config loader tests for standard `OTEL_*` env and legacy `OBSERVABILITY_OTEL_*` absence.
- Add/adjust observability tests for disabled SDK, traces exporter `none`, missing endpoint no-op, escaped OTLP headers parsing and resource attributes.
- Add lint/check tests or scripts for forbidden Kratos v2 import and direct output patterns.
- Run `go test ./... -count=1`, `go vet ./...`, `make lint`, `make build` for `apps/fides-bff`; run relevant `go test` for `packages/go/bffkit`.
- Run `kubectl kustomize` or `kustomize build` for `gitops-repo/apps/fides-bff/overlays/dev-1` and `sta-1`.

## Rollout And Rollback

- Gray release: Merge business-repo PR, publish/promote image, merge GitOps config, sync dev-1 first, run smoke through `fides-bff`, then promote to sta-1.
- Kill switch: Set `OTEL_SDK_DISABLED=true` or `OTEL_TRACES_EXPORTER=none`; stdout JSON remains on for operational evidence.
- Rollback: Revert business and GitOps changes, redeploy previous image/config and confirm `/api/v1/health` plus existing auth/pricing/origination paths are unchanged.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Standard OTel env hard cut breaks runtime if Vault still has old keys | Update GitOps expected keys and evidence; call out Vault key migration in PR and deployment notes | forest |
| Tests overfit private implementation | Test public middleware/config behavior and emitted log fields, not private call order | forest |
| Direct logs from future code bypass access middleware | Add lint/script guard and keep `make lint` in CI | forest |
| Raw Vault passthrough syncs unexpected key names | Vault path is service-scoped, secret values are still not committed; app only reads known `OTEL_*` and auth keys | forest |
