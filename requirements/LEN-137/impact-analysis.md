---
requirement_id: "LEN-137"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-28"
approved_by: "forest"
approved_at: "2026-06-28T22:36:45+08:00"
decision: "批准 LEN-137 service-repo-check；确认 applicant-api、origination-api、fides-bff、fides 服务矩阵路径可解析，harness-repo、idl-repo、business-repo 已在同名分支隔离。"
idl_impact: "yes"
idl_impact_reason: "LEN-137 新增 applicant-api gRPC、origination-api gRPC 和 fides-bff HTTP facade 契约；前端通过 BFF HTTP 调用，BFF 通过 gRPC 调内部服务。"
---

# Impact Analysis

## Summary

LEN-137 新增身份信息 Step 3 的契约、后端保存与回填、申请草稿步骤推进、BFF HTTP facade、前端页面和 local 网页真实链路验证。

## Affected Domains

- Applicant：保存和回填申请人身份信息。
- Origination：推进当前 loan application draft 的申请步骤。
- Frontend BFF：对前端暴露身份信息保存和回填 HTTP facade。
- Frontend Web：呈现 Step 3 表单、校验、保存、回填和前置条件处理。
- Harness lifecycle：保存需求、影响、设计、任务、门禁和本地验证证据。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| applicant-api | business-repo | 新增身份信息保存与回填 gRPC 能力，并新增明文字段持久化 | yes |
| origination-api | business-repo | 新增推进 `identity_information` 步骤的 gRPC 能力 | yes |
| fides-bff | business-repo | 新增 `/api/v1/me/identity-profile` HTTP facade，并调用 applicant-api / origination-api gRPC | yes |
| fides | business-repo | 新增 Step 3 身份信息 UI、校验、保存、回填和 local 链路验证 | no |
| Harness LEN-137 lifecycle | harness-repo | 保存需求生命周期文档、门禁、审查和证据 | no |

## Upstream / Downstream

- User entry: 已通过 OTP 且已保存 Step 2 草稿的申请人。
- Runtime path:
  - `fides-web -> fides-bff GET /api/v1/me/identity-profile`
  - `fides-web -> fides-bff PUT /api/v1/me/identity-profile`
  - `fides-bff -> applicant-api UpsertIdentityProfile`
  - `fides-bff -> applicant-api GetIdentityProfile`
  - `fides-bff -> origination-api AdvanceApplicationStep`
- Service dependencies from matrix:
  - `applicant-api` upstream consumer: `fides-bff`
  - `origination-api` upstream consumer: `fides-bff`
  - `origination-api` downstream dependency: `quote-api`
- This requirement does not change `quote-api`.

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: yes.
- Contract repo: `idl-repo`.
- Proto files:
  - Existing applicant package: `vesta/lendora/applicant/v1`.
  - Existing fides-bff package: `vesta/lendora/fides-bff/v1`.
  - New or existing origination package to be introduced under `vesta/lendora/origination/v1`.
- Planned contract surface:
  - `ApplicantProfileService.UpsertIdentityProfile`
  - `ApplicantProfileService.GetIdentityProfile`
  - `OriginationDraftService.AdvanceApplicationStep`
  - `FidesBffIdentityProfileService` with `PUT /api/v1/me/identity-profile`
  - `FidesBffIdentityProfileService` with `GET /api/v1/me/identity-profile`
  - `Nationality` enum with Chinese, HongKong, British, Indian, Filipino, Indonesian, Pakistani, American, Australian, Canadian, Other.
- Buf module: current `idl-repo/buf.yaml` uses buf v2 with one module at `.`.
- Buf config version: v2.
- Required buf checks: `buf lint`, `buf generate`, `buf breaking --against '.git#branch=master'` or the repo-standard baseline.
- Breaking baseline: `origin/master` / `master`.
- Compatibility risk: expected additive. New services, RPCs, messages and enum are compatible if existing field numbers and packages are not changed.

## Generated Contract Impact

- Go generated contracts are required for `fides-bff` gRPC clients and HTTP annotations.
- Java generated contracts are required for `applicant-api` and `origination-api` gRPC adapters.
- Current `idl-repo/buf.gen.yaml` has an empty `plugins` list, so generation and consumption path must be confirmed during IDL design.
- `idl-java-repo` is not included in the initial affected repositories until the generated Java contract publication path is explicitly required by the design.

## Data Impact

- Database schema:
  - `applicant-api` needs persistent storage for HKID body, HKID check digit, first name, last name, Chinese name, nationality and date of birth.
  - `origination-api` must persist or update the existing loan application `currentStep` to `identity_information`.
- Data migration:
  - applicant identity profile storage requires a migration if the service uses relational storage in the target runtime.
  - origination step value may require enum or column value compatibility if persisted as a constrained value.
- Backfill:
  - No backfill required. Existing applicants without identity information return an empty profile.
- Cache:
  - No cache impact identified.
- Runtime storage:
  - Local validation creates test applicant, loan application and identity profile records.

## Config / Permission / Observability Impact

- Config:
  - `fides-bff` needs downstream gRPC client configuration for applicant-api profile RPCs and origination-api step RPCs if not already configured.
  - Local runtime must start fides-web, fides-bff, applicant-api, origination-api and dependencies.
- Permission:
  - BFF must read `applicantId` from authenticated principal, not from frontend request body.
  - origination-api must verify `applicationId` belongs to the current principal applicant.
- Metrics:
  - No new business metric is required for MVP.
  - Existing HTTP/gRPC request metrics should cover new endpoints if middleware is already generic.
- Logs:
  - Do not log token values, real HKID, phone number or other sensitive values in local evidence.
  - Parent Story explicitly excludes HKID masking/encryption as a product requirement, but engineering logs should still avoid raw sensitive payloads where existing logging policy already requires that.
- Tracing:
  - Existing trace propagation from fides-web/BFF to downstream services should cover new calls.
- Events:
  - No domain event impact identified.

## Rollout And Rollback

- Rollout:
  - Implement and verify in isolated worktrees on `feature/LEN-137-identity-information`.
  - Run IDL checks before service consumption.
  - Run focused service tests, frontend tests, and local browser E2E.
  - No dev-1 rollout or GitOps digest update is in scope.
- Kill switch:
  - No explicit kill switch is required for local-only MVP implementation.
  - If runtime config supports hiding Step 3, design may use existing feature routing rather than adding a new switch.
- Rollback steps:
  - Revert fides-web Step 3 UI and BFF facade changes.
  - Revert applicant-api identity profile storage and origination step advancement changes.
  - Revert additive IDL if not yet consumed; if consumed, use a forward-compatible deprecation path instead of removing published fields.
  - Remove Harness evidence and gates only if the requirement branch is abandoned.

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| LEN-143 Jira description still mentions dev-1 while parent Story says local | Scope creep into GitOps/public verification | Treat parent Story as source of truth for this requirement and record local-only non-goal | core |
| HKID validation differs between frontend and backend | User sees inconsistent validation | Put HKID rules in explicit test cases on both sides; backend remains authority | applicant/frontend |
| DOB age boundary differs by timezone | Underage or overage applicant may be accepted inconsistently | Use Asia/Hong_Kong natural date in requirement, design and tests | applicant/frontend |
| BFF trusts frontend applicantId | Applicant could write another applicant's profile | BFF must derive applicantId from principal and downstream must enforce ownership | bff |
| Identity profile save succeeds but step advancement fails | Profile saved while currentStep remains stale | Design must define save order, error response and retry/idempotency behavior | bff/origination |
| Generated contract publication path is unclear | Service implementation may block after IDL changes | Resolve generation path before implementation and record buf/generation evidence | idl |
