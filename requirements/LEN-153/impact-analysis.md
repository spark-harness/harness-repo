---
requirement_id: "LEN-153"
analyst: "forest"
status: "approved"
updated_at: "2026-07-02"
approved_by: "forest"
approved_at: "2026-07-02T00:04:00+08:00"
decision: "批准 LEN-153 service-repo-check：已创建同名 harness-repo、idl-repo、business-repo peer worktree，并克隆 idl-go-repo、idl-openapi-repo、idl-ts-repo 生成仓；fides-bff 在服务矩阵中声明 idl_required=true，proto_path 指向 vesta/lendora/fides-bff/v1。"
idl_impact: "yes"
idl_impact_reason: "新增 fides-bff pricing 与 loan-application protobuf RPC，并要求 Go HTTP binding、OpenAPI 与 TS SDK 输入面可生成。"
---

# Impact Analysis

## Summary

LEN-153 影响 fides-bff BFF-facing protobuf 契约、Go 生成物、OpenAPI 生成物和 TypeScript SDK。它不改变运行时业务行为，但为后续 BFF、FE 和 GitOps 子任务提供统一生成契约源。

## Affected Domains

- 前端体验：`fides` 后续通过生成 TS SDK 浅适配层访问 BFF。
- BFF 边界：`fides-bff` 后续通过生成 Kratos HTTP binding 注册业务路由。
- 报价与试算：pricing 契约覆盖创建报价入口。
- 申请人域：loan application 与 identity profile 契约覆盖申请草稿和身份资料入口。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides-bff | `idl-repo` / `{business-repo}/apps/fides-bff` | 新增 BFF-facing pricing 与 loan-application proto；后续 BFF 消费生成 Go binding | Yes |
| fides | `{business-repo}/apps/fides-web` | 后续消费 OpenAPI 派生的 TS SDK；本票只提供契约输入 | No |
| quote-api | `{business-repo}/apps/quote-api` | pricing BFF 契约语义对应下游报价能力；本票不修改下游 | No |
| origination-api | `{business-repo}/apps/origination-api` | loan-application BFF 契约语义对应下游草稿能力；本票不修改下游 | No |
| applicant-api | `{business-repo}/apps/applicant-api` | identity-profile 既有契约仍覆盖资料读写；本票不修改下游 | No |

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: yes.
- Contract repo: `idl-repo`.
- Proto files:
  - Existing: `vesta/lendora/fides-bff/v1/auth.proto`
  - Existing: `vesta/lendora/fides-bff/v1/identity_profile.proto`
  - New: `vesta/lendora/fides-bff/v1/pricing.proto`
  - New: `vesta/lendora/fides-bff/v1/loan_application.proto`
- Buf module: `local/lendora-fides-bff` from service matrix.
- Buf config version: v2.
- Required buf checks: `buf lint`, `buf generate`, `buf breaking --against .git#branch=master`.
- Breaking baseline: `origin/master` / `.git#branch=master`.
- Compatibility risk: low if additive; existing auth and identity-profile messages must not change incompatible fields.

## Generated Contract Impact

- Go: `buf.gen.go.yaml` should generate protobuf, gRPC and Kratos HTTP files under `../.generated/idl-go`.
- OpenAPI: `buf.gen.openapi.yaml` should generate OpenAPI under `../.generated/openapi`.
- TypeScript: `idl-ts-repo` generates `typescript-fetch` SDK from `idl-openapi-repo/vesta/lendora/fides-bff/v1/openapi.yaml`.
- Java: not required for BFF-facing FE contract unless the existing Buf Java pipeline is explicitly invoked by release workflow.

## Data Impact

- Database schema: none.
- Data migration: none.
- Backfill: none.
- Cache: none.

## Config / Permission / Observability Impact

- Config: none in this ticket.
- Permission: no permission model change; authenticated BFF endpoints still derive principal from session context.
- Metrics: no runtime metrics change in this ticket.
- Logs: no runtime log change in this ticket.
- Tracing: contract names and HTTP paths must remain stable so later trace spans can aggregate by low-cardinality route.
- Events: none.

## Rollout And Rollback

- Gray release: contract change should merge before BFF and FE implementation tickets consume it.
- Kill switch: not applicable at IDL-only stage.
- Rollback steps:
  1. Revert IDL commit if downstream consumers have not adopted it.
  2. If downstream has consumed generated output, roll back consumers before reverting the contract source.
  3. Keep auth and identity-profile generated outputs available throughout rollback.

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| 新增字段类型与下游真实语义不一致 | 后续 BFF/FE 适配返工 | 从现有 BFF 手写 HTTP 路径和 Jira AC 反推最小字段；只表达 BFF-facing DTO | forest |
| TS SDK 不在 `idl-repo` 本地直接生成 | DoD 证据可能不完整 | 记录当前生成管线事实：本票验证 OpenAPI 输入面，TS SDK 由后续或外部管线生成 | forest |
| `buf breaking` 基线受历史标签或仓库结构影响失败 | merge-readiness 被阻塞 | 记录准确命令、输出和兼容性判断；不绕过失败 | forest |
| 新增 HTTP annotation 与已有手写 BFF 路径不一致 | 后续 LEN-154/155 无法无缝迁移 | 使用当前 BFF/FE 已存在路径作为契约路径 | forest |
