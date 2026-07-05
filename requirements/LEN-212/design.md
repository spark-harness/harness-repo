---
requirement_id: "LEN-212"
owner: "forest"
status: "approved"
updated_at: "2026-07-06"
approved_by: "forest"
approved_at: "2026-07-06T00:18:06+08:00"
decision: "用户授权 Agent 批准中间文件；批准 LEN-212 design，采用先升级 Kratos v3 Go HTTP 生成链路并发布 formal 契约，再升级 bffkit 与 fides-bff 的最小迁移方案。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, AC2 | D1: 将 fides-bff 进程依赖从 Kratos v2 切到 Kratos v3，并保留现有 bootstrap、config、HTTP server、health 和 Consul wiring | 不改变配置 key 或健康检查语义 |
| R2, BR1, BR2 | D2: `bffkit` 只做 Kratos v3 import/API 迁移，保持错误信封、CORS、幂等、trace header 和指标行为 | 用现有单元测试和新增依赖检查证明行为不退化 |
| R3, AC4 | D3: `idl-repo` Go HTTP 生成插件升级到 Kratos v3，业务仓只消费 formal `idl-go-repo` 版本 | release-bound 不允许 local replace、RC 或 pseudo-version |
| R4, AC1 | D4: 不新增业务能力；通过现有 API/adapter 测试和本地 smoke 覆盖 OTP、pricing、loan application、identity profile 入口 | 业务语义归既有测试保护 |
| R5, AC3 | D5: 保持 W3C TraceContext、`X-Trace-Id`、`X-Correlation-Id`、错误码和 access log 字段 | dev/sta smoke 继续验证跨服务链路 |
| R6, AC5 | D6: 本地先过质量门禁，合并后按 dev -> sta 顺序发布，失败回滚上一版镜像 digest | 无运行时开关 |

## Summary

LEN-212 采用最小框架迁移：先让 IDL Go HTTP binding 生成 Kratos v3 代码，再升级 `bffkit` 和 `fides-bff` 的 Kratos imports、模块依赖和必要 API 适配。业务层、proto 字段、HTTP 路由、错误码、配置 key 和前端流程保持不变。

最容易错的假设是“只改业务仓依赖即可”。实际 `idl-go-repo@v0.2.7` 的 HTTP binding 仍导入 Kratos v2，如果不先升级生成链路并发布 formal 契约版本，业务仓即使升级主模块也会把 v2 带回依赖图，AC4 不能成立。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| fides-bff | Kratos runtime、HTTP server、config、registry、generated HTTP service imports 升级到 v3 | 主交付服务 |
| fides-bff shared package | Kratos HTTP filter、binding、error adapter 升级到 v3 | `packages/go/bffkit` 被 fides-bff 直接消费，不作为独立服务登记 |
| fides-bff Go contract generation | `buf.gen.go.yaml` 使用 Kratos v3 HTTP 插件生成 binding | 避免正式 Go 契约继续依赖 v2 |

## API / Contract Design

- Protobuf IDL required: no `.proto` business field change; yes for generated Go HTTP binding refresh.
- Proto files: `vesta/lendora/fides-bff/v1/auth.proto`, `pricing.proto`, `loan_application.proto`, `identity_profile.proto` remain semantically unchanged.
- Buf module: `local/lendora-fides-bff`
- Buf config version: v2
- Generated outputs: `../.generated/idl-go` should contain Kratos v3 HTTP binding imports under `github.com/go-kratos/kratos/v3/...`.
- Breaking check baseline: `.git#branch=master`
- Compatibility strategy: config-only generation change; protobuf wire compatibility unchanged. Business release consumes a formal `github.com/spark-harness/idl-go-repo` version that can be resolved by Go tooling and whose generated fides-bff files no longer import Kratos v2.

## Data / Config / Permission

- Data model: no database, cache, migration or backfill changes.
- Config: keep existing fides-bff config files, env names, Consul KV paths and local `.env` behavior. Do not commit local env files.
- Permission: no auth or permission boundary change.

## Observability

- Logs: preserve `operation`, `trace_id`, `request_id`, `status_code`, `latency_ms`, `error_code` fields in access logging.
- Metrics: preserve `http.server.requests` and `http.server.duration` names and labels used by `bffkit`.
- Tracing: preserve W3C TraceContext extraction/injection and downstream `traceparent` / `tracestate` propagation.
- Events: none.

## Rollout And Rollback

- Gray release: merge IDL generation config and publish formal Go contract tag, then merge business upgrade, build image, deploy dev, run health and smoke, promote sta after dev passes.
- Kill switch: none; framework upgrade is binary-level. Runtime rollback uses image digest.
- Rollback: revert fides-bff deployment image to the previous stable digest and sync Argo. Since proto semantics and frontend contract do not change, frontend and downstream services do not need coordinated rollback.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Kratos v3 import path compiles but generated binding version is still v2 | Dependency scan blocks any `github.com/go-kratos/kratos/v2` in fides-bff, bffkit and generated fides-bff contract files | forest |
| Formal Go contract version is unavailable before business PR | Stop before business merge; release-bound master cannot consume RC/pseudo/local module | forest |
| Kratos v3 registry or config API differs at runtime | Keep registry/config tests, run local start and dev/sta smoke | forest |
| Observability headers or error envelope changes accidentally | Preserve `bffkit` tests and fides-bff HTTP tests; add narrow regression coverage if compile migration changes behavior | forest |
