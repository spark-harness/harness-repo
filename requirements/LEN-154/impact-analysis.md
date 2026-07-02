---
requirement_id: "LEN-154"
analyst: "forest"
status: "approved"
updated_at: "2026-07-02"
approved_by: "forest"
approved_at: "2026-07-02T16:13:19Z"
decision: "用户授权 Agent 批准所有需要的文件；批准 LEN-154 impact-analysis，确认本票只消费 formal Go 生成契约并修改 fides-bff 入站适配层，不产生新的 IDL、数据或 GitOps 影响。"
idl_impact: "no"
idl_impact_reason: "复用 LEN-153 已合并的 fides-bff protobuf 和生成 Go binding，不修改 proto。"
---

# Impact Analysis

## Summary

LEN-154 修改 `business-repo/apps/fides-bff` 的 HTTP 注册和 service adapter，把已入 IDL 的业务路由切到 generated Kratos HTTP binding。它不修改 protobuf、数据库、GitOps 或前端。

## Affected Domains

- 前端体验：保持现有 fides 申请流程 HTTP 行为。
- BFF 边界：统一 route registration 和 service interface。
- 报价与申请：pricing 和 loan-application 继续向下游服务透传。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides-bff | `{business-repo}/apps/fides-bff` | 切换 generated HTTP binding 注册与 service 实现 | Yes |
| applicant-api | `{business-repo}/apps/applicant-api` | auth / identity-profile 下游保持不变 | No |
| quote-api | `{business-repo}/apps/quote-api` | pricing 下游保持不变 | No |
| origination-api | `{business-repo}/apps/origination-api` | loan application 下游保持不变 | No |

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: no.
- Contract repo: `idl-repo` already merged LEN-153.
- Proto files: read-only consumption of `vesta/lendora/fides-bff/v1/*.proto`.
- Required checks: BFF Go tests and build; no new Buf change.
- Compatibility risk: route behavior must remain compatible with current JSON paths and error envelope.

## Data Impact

- Database schema: none.
- Data migration: none.
- Backfill: none.
- Cache: none.

## Config / Permission / Observability Impact

- Config: `business-repo/apps/fides-bff/go.mod` 必须消费 formal `github.com/spark-harness/idl-go-repo v0.2.5`，不能使用 pseudo-version、branch dependency 或 local `replace`。
- Permission: protected-path auth filter must continue to guard pricing, loan-application, identity-profile and session probe paths.
- Metrics: none.
- Logs: no new log fields.
- Tracing: traceparent/tracestate must continue to pass from BFF request to downstream clients.
- Events: none.

## Rollout And Rollback

- Gray release: BFF can roll forward independently after generated contracts are available.
- Kill switch: rollback BFF deployment to previous image if generated binding behavior regresses.
- Rollback steps: revert business-repo LEN-154 commit; proto/generated contracts can remain additive.

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| generated binding changes request decoding details | FE behavior regression | Characterization tests on current endpoints before switching | forest |
| idl-go dependency version not published as formal tag | build failure | 已发布 formal tag：`idl-repo v0.2.5` 和 `idl-go-repo v0.2.5`；实现和 evidence 记录 tag 与 commit | forest |
| path variable name changes from `applicationId` to `application_id` internally | GET/PATCH application lookup fails | Tests must hit generated HTTP route and assert application ID reaches usecase | forest |
