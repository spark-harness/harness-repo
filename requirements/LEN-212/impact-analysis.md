---
requirement_id: "LEN-212"
analyst: "forest"
status: "approved"
updated_at: "2026-07-06"
approved_by: "forest"
approved_at: "2026-07-06T00:18:58+08:00"
decision: "用户授权 Agent 批准中间文件；确认 LEN-212 影响 harness-repo、idl-repo、business-repo，服务为 fides-bff 与 bffkit，三仓同名分支已隔离。"
idl_impact: "yes"
idl_impact_reason: "需要升级 buf.gen.go.yaml 中 Kratos HTTP 生成插件，产出 Kratos v3 Go HTTP binding；不修改 .proto 业务契约。"
---

# LEN-212 Impact Analysis

## Summary

LEN-212 是 fides-bff 框架运行时升级，影响 Harness 生命周期材料、IDL Go 生成配置、已发布 Go 契约版本消费、`fides-bff` 服务和共享 `bffkit` 横切包。它不改变 protobuf 业务字段、HTTP 路由语义、数据模型或前端页面流程。

## Affected Domains

- frontend：`fides-bff` 作为前端体验模块的 BFF，承载 OTP、报价、贷款申请和身份资料 facade。
- shared：`packages/go/bffkit` 提供 BFF 横切能力。
- contract：`idl-repo` 的 Go HTTP binding 生成链路需要从 Kratos v2 切到 v3。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides-bff | `business-repo/apps/fides-bff` | 升级 Kratos runtime、HTTP server、配置、注册发现和正式 Go 契约依赖 | Yes, reuse existing proto only |
| fides-bff shared package | `business-repo/packages/go/bffkit` | 横切 HTTP filters 和 error binding 使用 Kratos transport API，需要随 fides-bff 同步 v3；它不是服务矩阵中的独立 service | No |
| fides-bff proto generation | `idl-repo/buf.gen.go.yaml` | Go HTTP binding 生成插件从 v2 切到 v3，避免发布契约继续导入 Kratos v2 | Yes, config-only |

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: Yes, generated Go HTTP binding changes framework import path only.
- Contract repo: `idl-repo`
- Proto files: `vesta/lendora/fides-bff/v1/*.proto` reused without business field changes.
- Buf module: `local/lendora-fides-bff`
- Buf config version: v2
- Required buf checks: `buf lint`, `buf generate`, `buf breaking --against .git#branch=master`
- Breaking baseline: `origin/master`
- Compatibility risk: protobuf wire and HTTP route semantics should remain compatible; generated Go HTTP code changes compile-time dependency from Kratos v2 to v3 and requires a formal `idl-go-repo` module tag before release-bound business consumption.

## Data Impact

- Database schema: none.
- Data migration: none.
- Backfill: none.
- Cache: none.

## Config / Permission / Observability Impact

- Config: existing config files and env keys remain compatible; implementation must verify Kratos v3 config loader behavior.
- Permission: no permission boundary changes.
- Metrics: `bffkit` HTTP request counter and duration histogram continue with stable names and low-cardinality labels.
- Logs: access logs continue to include `operation`, `trace_id`, `request_id`, `status_code`, `latency_ms`, and `error_code` when present.
- Tracing: W3C `traceparent` / `tracestate` extraction and downstream propagation remain required.
- Events: none.

## Rollout And Rollback

- Gray release: build upgraded fides-bff image, deploy to dev first, run health and BFF smoke, then promote to sta.
- Kill switch: no runtime feature flag; rollback uses previous stable image digest.
- Rollback steps: revert fides-bff image digest to previous known-good version, sync Argo app, verify health and smoke paths; IDL formal tag remains additive at generation-runtime level and does not require frontend/downstream rollback.

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| Kratos v3 API differs from v2 | Compile or runtime startup failure | Characterization tests before production edits, then `go test`, `go vet`, `make lint`, `make build`, local smoke | forest |
| Published Go contract still imports Kratos v2 | AC4 cannot pass, v2 remains in dependency graph | Upgrade `buf.gen.go.yaml`, generate output, publish/consume formal `idl-go-repo` version | forest |
| Consul registry contrib v3 behavior changes | Service discovery or registration fails in dev/sta | Keep existing config keys, run registry unit tests and runtime smoke against dev/sta | forest |
| Trace/error behavior regresses | Observability AC fails | Preserve `bffkit` tests for error envelope, trace headers, request IDs and metrics | forest |
| Release-bound contract version not formal | Master merge violates contract-versioning policy | Do not merge business dependency on RC/pseudo/local generated contract; record formal module tag evidence | forest |
