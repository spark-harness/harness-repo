---
requirement_id: "LEN-214"
analyst: "forest"
status: "approved"
updated_at: "2026-07-06"
approved_by: "forest"
approved_at: "2026-07-06T00:00:00+08:00"
decision: "用户明确授权批准中间文件；批准 LEN-214 service repo readiness，harness-repo、business-repo、idl-repo、gitops-repo 同名分支状态有效。"
idl_impact: "no"
idl_impact_reason: "本需求只修改 fides-bff 日志、运行配置、GitOps Secret 注入方式和 lint/CI 防漂移，不新增或修改 protobuf IDL、HTTP 外部契约或生成契约。"
---

# Impact Analysis

## Summary

LEN-214 影响 `fides-bff` Kratos v3 日志、`bffkit` 请求 trace middleware、标准 `OTEL_*` 配置、GitOps fides-bff runtime Secret 注入和 fides-bff CI/lint 防漂移规则；不影响 IDL、数据库、用户界面、Java 服务或业务/API 语义。

## Affected Domains

- 前端体验：`fides-bff` 是 `fides-web` 到后端服务的 BFF，但本票只改 BFF 服务端运行质量。
- 运行质量：stdout JSON 日志、trace/request 关联、安全字段边界、标准 OpenTelemetry 配置和 lint 防漂移。
- 部署配置：`gitops-repo/apps/fides-bff` 的 ConfigMap、VaultStaticSecret 和 Deployment `envFrom` 注入链路。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides-bff | `business-repo/apps/fides-bff` | 收口 Kratos v3 logger、标准 `OTEL_*` 配置、测试和 lint 规则 | No |
| bffkit | `business-repo/packages/go/bffkit` | `TraceFilter` 是 fides-bff 请求 trace、request id、access log 和 HTTP metrics 的实际入口，需要补齐 span_id、deployment environment、低基数 operation 和敏感字段测试 | No |
| fides-bff IDL baseline | `idl-repo/vesta/lendora/fides-bff/v1` | 服务矩阵声明 fides-bff `idl_required: true`；本票只读取现有契约作为门禁基线，不修改 proto | No |
| fides-bff GitOps | `gitops-repo/apps/fides-bff` | 将 fides-bff runtime 配置从 `OBSERVABILITY_OTEL_*` 切到标准 `OTEL_*`，并把 VaultStaticSecret 改为 raw env passthrough | No |
| Harness lifecycle | `harness-repo/requirements/LEN-214` | 记录需求、影响、设计、任务、门禁、审查和验收证据 | No |

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: No.
- Contract repo: N/A.
- Proto files: N/A.
- Buf module: `local/lendora-fides-bff` not touched.
- Buf config version: v2 not touched.
- Required buf checks: N/A.
- Breaking baseline: N/A.
- Compatibility risk: Low; HTTP routes, response envelopes, downstream gRPC contracts and generated clients are unchanged.

## Data Impact

- Database schema: No change.
- Data migration: No change.
- Backfill: No change.
- Cache: No change.
- Runtime storage: Kubernetes Secret content shape changes only by environment variable names; secret values remain platform-managed and are not committed.

## Config / Permission / Observability Impact

- Config: Replace `OBSERVABILITY_OTEL_ENABLED`, `OBSERVABILITY_OTEL_ENDPOINT`, `OBSERVABILITY_OTEL_PROTOCOL`, `OBSERVABILITY_OTEL_X_SENTRY_AUTH`, `OBSERVABILITY_OTEL_ENVIRONMENT` and `OBSERVABILITY_OTEL_RELEASE` with standard `OTEL_SDK_DISABLED`, `OTEL_TRACES_EXPORTER`, `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`, `OTEL_EXPORTER_OTLP_TRACES_PROTOCOL`, `OTEL_EXPORTER_OTLP_TRACES_HEADERS`, `OTEL_RESOURCE_ATTRIBUTES` and `OTEL_SERVICE_NAME` where applicable. GitOps owns non-secret `OTEL_TRACES_EXPORTER=otlp`; Vault raw Secret owns endpoint/header. If endpoint is absent during migration, the app keeps stdout JSON and treats trace export as no-op instead of failing startup.
- Permission: No change.
- Metrics: Keep existing `bffkit` HTTP request count and duration metrics; ensure labels stay low cardinality.
- Logs: stdout JSON remains the primary log path. Access logs include stable `operation`, route pattern, `trace_id`, `request_id`, `span_id` when available, status, latency, error code and deployment environment. Logs do not record raw query, body, response body or sensitive headers.
- Tracing: OTel trace provider remains optional and configured by standard env vars. `trace_id` is runtime correlation metadata, not a business contract field.
- Secrets: GitOps/Vault must preserve raw Vault KV -> Kubernetes Secret -> Deployment `envFrom`; no real secret value enters repo, Jira, evidence or PR text.
- Events: No change.

## Rollout And Rollback

- Gray release: Merge business and GitOps changes, then promote image and sync `fides-bff` dev-1 before sta-1.
- Kill switch: Set `OTEL_SDK_DISABLED=true` or `OTEL_TRACES_EXPORTER=none` in runtime env to disable trace export; stdout JSON logging remains on.
- Rollback steps: Revert business and GitOps PRs, redeploy previous `fides-bff` image/config, and confirm health endpoint plus existing OTP/session paths still work.

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| `OBSERVABILITY_OTEL_*` 到 `OTEL_*` 硬切后 Vault key 未同步 | Trace exporter 不启动或启动失败 | GitOps ConfigMap 拥有 `OTEL_TRACES_EXPORTER=otlp`；Vault raw Secret 提供 endpoint/header；endpoint 缺失时应用降级为 no-op trace exporter，stdout JSON 和基础功能继续可用 | forest |
| 日志误带敏感 header、body、手机号或 OTP | 凭证或 PII 泄漏 | 统一 access log 只记录 allowlist 字段；测试覆盖 Authorization/Cookie/body 不进入日志；lint 禁止裸输出 | forest |
| operation 使用 raw path 导致高基数 | 日志和 metrics 难以聚合 | `TraceFilter` 使用 route pattern 作为 operation，不记录 raw query | forest |
| lint 规则过宽阻止必要入口 stdout JSON logger | CI 阻塞正常实现 | 只允许 `cmd/fides-bff` 初始化 Kratos stdout JSON handler，禁止业务层和 middleware 裸输出 | forest |
| GitOps VSO raw passthrough 行为误配 | Secret 缺 key 或 rollout 不触发 | 使用现有 VSO raw destination 模式，保留 rolloutRestartTargets，kustomize 渲染验证 dev-1/sta-1 overlays | forest |
