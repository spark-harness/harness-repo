---
requirement_id: "LEN-155"
analyst: "forest"
status: "approved"
updated_at: "2026-07-02"
idl_impact: "no"
idl_impact_reason: "复用 LEN-153 已合并并发布的 fides-bff OpenAPI / TS SDK 输出，不修改 proto。"
approved_by: "forest"
approved_at: "2026-07-02T17:05:12Z"
decision: "用户授权 Agent 批准所有需要的文件；批准 LEN-155 impact-analysis，确认本票只修改 fides-web 与 TS SDK 依赖，不产生新的 IDL、数据或 GitOps 影响。"
---

# Impact Analysis

## Summary

LEN-155 修改 `business-repo/apps/fides-web` 的 infrastructure gateway 和测试，使前端所有 BFF 调用通过 generated TS SDK 浅适配层完成。它不修改 protobuf、BFF runtime、数据库、Next proxy 或 GitOps 配置。

## Affected Domains

- 前端体验：申请流程调用路径保持不变。
- 前端基础设施：BFF gateway 从手写 fetch endpoint 切换为 generated API client。
- 可观测性：移除 gateway 手写 trace 注入，为 LEN-156 的统一 fetch 自动追踪留出单一入口。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides | `{business-repo}/apps/fides-web` | 升级 TS SDK 依赖，调整 infrastructure gateway 和 tests | No |
| fides-bff | `{business-repo}/apps/fides-bff` | 作为已合并 BFF HTTP contract provider，本票不改代码 | Yes |

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: no.
- Contract source: `idl-repo v0.2.5` already merged by LEN-153.
- OpenAPI / TS generated source: `idl-ts-repo v0.2.5` -> `af09e09be8328d15ca9f026f65cbc980f90425d3`.
- Compatibility risk: frontend must preserve existing request base URL, auth header, idempotency key, timeout and error envelope mapping.
- Required checks: fides-web tests, dependency cruiser, lint and build; no new Buf change.

## Generated Contract Impact

| Artifact | Version | Commit | Usage |
|---|---|---|---|
| `@spark-harness/idl-ts-client` | `v0.2.5` | `af09e09be8328d15ca9f026f65cbc980f90425d3` | fides-web generated API client dependency |

Generated SDK classes used by this ticket:

- `FidesBffAuthServiceApi`
- `FidesBffIdentityProfileServiceApi`
- `FidesBffPricingServiceApi`
- `FidesBffLoanApplicationServiceApi`

## Data Impact

- Database schema: none.
- Data migration: none.
- Browser storage: no schema change; existing session and draft storage remain.
- Cache: none.

## Config / Permission / Observability Impact

- Config: `apps/fides-web/package.json` and lockfile move `@spark-harness/idl-ts-client` to `v0.2.5`.
- Permission: existing bearer-token injection remains in gateway; missing token still fails before network call.
- Metrics: none.
- Logs: none.
- Tracing: gateway-local manual trace header/span creation is removed; unified fetch tracing is deferred to LEN-156.
- Events: none.

## Rollout And Rollback

- Rollout: deploy fides-web after tests and gates pass.
- Rollback: revert fides-web LEN-155 business commit. The TS SDK tag is additive and can remain.
- Release ordering: LEN-153 and LEN-154 are already merged; LEN-155 can merge independently before LEN-156 proxy and LEN-157 GitOps.

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| generated SDK method signatures differ from hand-written request shape | FE build or runtime failure | Test-first coverage for pricing and loan application gateway calls | forest |
| generated SDK basePath double-includes `/api/v1` | Requests hit wrong path | Preserve existing `generatedClientBasePath` behavior and assert requested URL in tests | forest |
| removing manual trace headers breaks short-term trace propagation before LEN-156 | Temporary trace gap for FE -> BFF | Scope is explicit in LEN-155; LEN-156 owns unified fetch tracing | forest |
| generated DTO leaks into application or presentation layers | Architecture boundary regression | `pnpm lint:deps` and import scan | forest |
