---
requirement_id: "LEN-43"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-21"
approved_by: "Forest"
approved_at: "2026-06-23T00:03:21+08:00"
decision: "批准 LEN-43 impact-analysis 与服务仓库检查，允许进入合并准备。"
idl_impact: "yes"
idl_impact_reason: "本需求新增 fides-bff BFF-facing protobuf，RPC 带 google.api.http 注解并生成 Go contract 供 BFF 消费。"
---

# Impact Analysis

## Summary

LEN-43 将 `fides` 手机验证前端、`fides-bff` REST / gRPC 映射、BFF-facing protobuf 和 applicant-api Consul 调用串成可验证的端到端接入路径。

## Affected Domains

- `frontend`：Lendora 申请漏斗第 1 步手机验证体验、REST adapter、页面状态和错误展示。
- `fides-bff`：前端 BFF 的手机验证业务入口、协议映射、下游服务发现和横切约定。
- `applicant`：作为下游 OTP / 会话能力提供方被调用；本需求不修改 applicant-api 业务规则。
- `contract publishing`：新增 BFF-facing protobuf 与 Go generated contract 验证 / 发布路径。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides | business-repo (`services/frontend/fides`) | 前端真实接入 BFF，覆盖发码、冷却、验码和错误态 | No |
| fides-bff | business-repo (`services/backend/fides-bff`) | 新增手机验证 REST 入口、BFF protocol mapper、applicant gRPC client、Consul resolver | Yes |
| fides-bff proto | idl-repo (`vesta/lendora/fides-bff/v1`) | 新增 BFF-facing auth proto，RPC 带 HTTP 注解 | Yes |
| applicant-api | business-repo (`services/backend/applicant-api`) | 下游运行时依赖；本需求只消费其现有 OTP / token 契约 | Yes |
| harness lifecycle | harness-repo (`requirements/LEN-43`) | 记录需求、影响、设计、任务、证据和门禁 | No |

## Upstream / Downstream Consumers

- Upstream user: `fides` 手机验证页面和 API adapter。
- BFF provider: `fides-bff` 对前端暴露 `/api/v1/auth/*`。
- Downstream service: `applicant-api` 通过 Consul service discovery 被 `fides-bff` 调用。
- Generated contract consumer: `fides-bff` 消费 generated Go contract；master-bound 合并前必须切到 formal 可追溯版本。
- Future consumers: 其他前端或 BFF auth flows 可复用 BFF-facing contract，但本需求不扩展到其他流程。

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: **Yes**。
- Contract repo: `idl-repo`。
- New proto file: `{idl-repo}/vesta/lendora/fides-bff/v1/auth.proto`。
- Proposed proto package: `vesta.lendora.fides_bff.v1`。
- Proposed Go package path: `github.com/spark-harness/idl-go-repo/vesta/lendora/fides-bff/v1`。
- Buf module: 当前 `idl-repo/buf.yaml` 为 v2 单模块；服务矩阵需登记 BFF proto path 和 buf module，建议 `local/lendora-fides-bff`。
- Buf config version: v2。
- Required imports: `google/api/annotations.proto` for `google.api.http`。
- Lint exception: `PACKAGE_DIRECTORY_MATCH` is ignored only for `vesta/lendora/fides-bff/v1/auth.proto` because the approved path uses `fides-bff` while protobuf package syntax requires `fides_bff`.
- Required REST mappings:
  - `SendOtp` -> `POST /api/v1/auth/otp:send`
  - `VerifyOtp` -> `POST /api/v1/auth/otp:verify`
  - `RefreshToken` -> `POST /api/v1/auth/token:refresh`
- Required buf checks:
  - `buf lint`
  - `buf generate`
  - `buf breaking --against .git#branch=master`
- Breaking baseline: `master` has no `vesta/lendora/fides-bff/v1/auth.proto`; change type is additive new service/RPC/message.
- Compatibility risk: Low for existing consumers because this is a new proto path and service. Medium for BFF delivery because generated Go contract publication / consumption must be formal before master-bound merge.

## Generated Contract Impact

- Go generated contracts:
  - New generated package under `vesta/lendora/fides-bff/v1`.
  - `fides-bff` should consume generated Go package from `github.com/spark-harness/idl-go-repo` with a formal tag before release-bound merge.
  - RC or same-branch generated output may be used only for branch validation and must not remain as local replacement in master-bound code.
- Java generated contracts:
  - Not expected for runtime consumers in this requirement.
  - `buf.gen.yaml` may still generate Java if global generation is invoked; do not manually edit `idl-java-repo`.
- Applicant contract:
  - `fides-bff` also consumes existing applicant generated Go contract for downstream gRPC calls.
  - No applicant protobuf field, RPC or package changes are in this requirement.

## Data Impact

- Database schema: No direct schema change.
- Data migration: None.
- Backfill: None.
- Cache: No new Redis persistence in BFF; OTP state remains applicant-api responsibility.
- Runtime storage:
  - `fides-bff` idempotency behavior uses existing BFF idempotency abstraction; if current in-memory store is insufficient for integration, design must classify runtime persistence explicitly.
  - `fides` may retain only allowed short-lived non-sensitive session positioning; no OTP code, full phone, access token, refresh token or raw BFF sensitive response persistence.

## Config / Permission / Observability Impact

- Config:
  - `fides` needs environment/config value for BFF base URL or adapter mode.
  - `fides-bff` needs Consul address, applicant-api service name, gRPC timeout, optional TLS / plaintext mode for local dev, and generated contract version.
  - `fides-bff` needs vendor-neutral OpenTelemetry config: enabled flag, OTLP endpoint, OTLP protocol, optional OTLP headers, environment, and release / commit. Endpoint and headers must come from deployment config or local untracked config, not committed files.
  - Deployment can route OTLP to an OpenTelemetry Collector, and configure the Collector to export to Sentry without changing application code.
  - Local environment can use PostgreSQL `postgresql://forest:forest_dev_password@localhost:5432/app`, Redis `redis://:forest_dev_password@localhost:6379`, and Consul `http://localhost:8500` when applicant-api runtime requires them.
- Permission:
  - No new user permission model.
  - CI / contract publication may need existing generated Go repo token or release credentials.
- Metrics:
  - BFF should expose low-cardinality counters / durations for send, verify, refresh, downstream errors and Consul resolution failures.
  - Labels must avoid phone, OTP, token, challengeId and applicantId.
- Logs:
  - Logs must not include full phone, OTP, token, refresh token or raw downstream sensitive payload.
  - Error logs should include stable error code and traceId.
- Tracing:
  - BFF should use OpenTelemetry tracing with `service.name=fides-bff`.
  - Application code should use only the official OpenTelemetry SDK and official OTLP exporter, avoiding Sentry SDK, Sentry exporter, or Sentry-specific span processors.
  - OpenTelemetry traces should export to a configurable OTLP endpoint, preferably an OpenTelemetry Collector.
  - The deployment-level Collector can export traces to Sentry; switching to another OTLP backend must not require application code changes.
  - OTLP endpoint, headers, environment, and release / commit should be configurable per environment.
  - HTTP auth requests should create or continue server spans with low-cardinality route names.
  - Applicant gRPC calls should create client spans and inject W3C TraceContext.
  - Consul resolution failures and downstream gRPC failures should be trace-correlatable through `trace_id` / `span_id`.
  - Error spans should record stable `error_code` aligned with the BFF error envelope and logs.
  - Redaction must happen before export through OpenTelemetry attribute construction and Collector processors, not through Sentry-specific hooks.
  - Span attributes must not include phone, OTP, token, refresh token, challengeId, raw request body, or raw response body.
- Events:
  - No business event publication in this requirement.

## Rollout And Rollback

- Gray release:
  - First validate BFF-facing proto and generated Go contract on the LEN-43 branch.
  - Run `fides-bff` against local/dev Consul-discovered applicant-api using test provider.
  - Enable `fides` real adapter by environment config while retaining mock adapter for rollback/testing.
- Kill switch:
  - Frontend can switch adapter/base URL back to mock or disable progress to the real BFF path by environment config.
  - BFF can disable applicant auth route registration only if design adds an explicit config; otherwise rollback is via deployment version.
- Rollback steps:
  - Revert `fides` adapter config to mock or prior BFF base.
  - Roll back `fides-bff` auth route/client changes.
  - Revert service matrix `fides-bff` proto registration.
  - Revert `idl-repo` BFF-facing proto if not yet formally published; if published, do not move formal tags, publish a follow-up correction instead.

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| generated Go contract is unavailable as a formal version before business merge | `fides-bff` cannot pass master-bound contract gate | Split IDL publication and BFF consumption; record formal tag / module evidence before merge | Platform / BFF |
| Consul local discovery differs from dev/prod naming | Local smoke passes but deployed BFF cannot find applicant-api | Make Consul address and service name config-driven; test Consul resolution failure explicitly | BFF |
| BFF HTTP annotation and hand-written REST route diverge | Contract and runtime behavior drift | Generate or test route consistency against proto annotations where feasible; document mapping in design | BFF |
| applicant-api local runtime dependency is unavailable | End-to-end smoke blocked | Use BE subtask runtime as dependency; if unavailable, run BFF integration with applicant gRPC test server and record smoke blocker | Backend / BFF |
| frontend stores sensitive session or OTP data | Security and privacy risk | Keep tokens out of durable storage; tests and review check no OTP/token/full phone persistence | FE |
| error code mismatch between applicant-api, BFF and fides | User-facing error states fail LEN-2 AC4-AC6 | Define explicit mapping table in design and cover invalid, expired, cooldown, locked and unavailable cases in tests | FE / BFF |
| current project context lacks Lendora frontend/BFF service entries | Agents may infer from paths instead of source-of-truth context | Record context gap and consider adding minimal `context/project/lendora/frontend/*/INDEX.md` in a separate or scoped task | Harness |

## Context Gaps

- `harness-repo/context/project/` currently has no project-level `lendora/frontend/fides/INDEX.md` or `lendora/frontend/fides-bff/INDEX.md` entry.
- The service matrix does identify `fides`, `fides-bff` and `applicant-api`; implementation should rely on service matrix for paths until project context is added.
