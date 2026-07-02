---
requirement_id: "LEN-153"
owner: "forest"
status: "approved"
updated_at: "2026-07-02"
approved_by: "forest"
approved_at: "2026-07-02T00:01:00+08:00"
decision: "批准 LEN-153 design：新增 additive fides-bff pricing 与 loan-application 契约，使用 Buf v2 生成 Go HTTP binding 和 OpenAPI，不实现运行时代码。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, R2, AC4 | D1：保持 auth 与 identity-profile 现有 RPC/字段不做 incompatible change | 本票只新增契约，不重写已有契约 |
| R3, AC2 | D2：新增 `FidesBffPricingService`，HTTP path 使用现有 BFF 路径 `POST /api/v1/pricing/quotes` | 路径对齐当前 BFF/FE 手写调用面 |
| R4, AC3 | D3：新增 `FidesBffLoanApplicationService`，覆盖 create/get/patch draft | path 对齐 `/api/v1/loan-applications` |
| R5, AC5, AC8 | D4：使用 Buf v2 lint/generate/breaking 验证 additive 兼容性 | 不手工编辑生成物 |
| R6, AC6, AC7 | D5：以 `buf.gen.go.yaml` 和 `buf.gen.openapi.yaml` 证明 Go HTTP binding 与 OpenAPI 输入面 | TS SDK 若非本仓直接输出，记录为管线事实 |
| R7, AC9 | D6：在证据中映射父 Story AC1-AC4、AC6 到四类 BFF-facing 契约 | 后续子票消费该映射 |

## Summary

LEN-153 在 `idl-repo` 中补齐 fides-bff 的 BFF-facing pricing 与 loan-application proto。设计目标是把后续 FE/BFF 调用面的事实源收敛到 protobuf + HTTP annotation，而不是继续依赖手写 endpoint 常量。

本设计不实现 runtime handler，不改数据库，不改部署配置。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| fides-bff | 新增 pricing 与 loan-application BFF-facing service 契约 | 后续 LEN-154 注册生成 HTTP binding |
| fides | 无本票代码变更 | 后续 LEN-155 使用生成 TS SDK |
| quote-api | 无本票代码变更 | pricing 契约语义对应其报价能力 |
| origination-api | 无本票代码变更 | loan-application 契约语义对应其草稿能力 |
| applicant-api | 无本票代码变更 | identity-profile 已有契约继续覆盖资料能力 |

## API / Contract Design

- Protobuf IDL required: yes.
- Proto files:
  - `vesta/lendora/fides-bff/v1/pricing.proto`
  - `vesta/lendora/fides-bff/v1/loan_application.proto`
- Existing files preserved:
  - `vesta/lendora/fides-bff/v1/auth.proto`
  - `vesta/lendora/fides-bff/v1/identity_profile.proto`
- Buf module: `local/lendora-fides-bff`.
- Buf config version: v2.
- Generated outputs:
  - Go protobuf/gRPC/Kratos HTTP staged under `../.generated/idl-go`, then synced to `idl-go-repo`.
  - OpenAPI staged under `../.generated/openapi`, then synced to `idl-openapi-repo`.
  - TS SDK generated in `idl-ts-repo` from `idl-openapi-repo/vesta/lendora/fides-bff/v1/openapi.yaml`.
- Breaking check baseline: `.git#branch=master`.
- Compatibility strategy: additive new service/RPC/message only.

### Pricing Contract

新增 `FidesBffPricingService.CreateQuote`。

HTTP:

```text
POST /api/v1/pricing/quotes
```

Request 表达贷款金额、期限、用途和产品码。金额使用 decimal string。

Response 表达 quoteId、monthly payment、APR、total interest、total payable、validUntil。字段保持 BFF-facing DTO，不承诺下游内部模型。

### Loan Application Contract

新增 `FidesBffLoanApplicationService`。

HTTP:

```text
POST /api/v1/loan-applications
GET /api/v1/loan-applications/{application_id}
PATCH /api/v1/loan-applications/{application_id}
```

Request 不包含 applicantId。BFF 后续从 session/principal context 解析申请人身份。

Create/Patch 使用 loan terms 和 quoteId。幂等键继续通过 header 传递，不进入业务请求体。

Response 表达 applicationId、status、currentStep、loan terms 和 accepted quote 快照，满足前端回填和下一步跳转需要。

`currentStep` 在 loan-application BFF-facing 契约中保持 string。它不是下游内部枚举外泄；它是现有前端/BFF JSON 行为的一部分，后续 generated SDK 迁移不能改变页面状态值。

## Data / Config / Permission

- Data model: none.
- Config: none.
- Permission: no new permission source; authenticated endpoints later由 BFF middleware 校验。

## Observability

- Logs: no runtime log change.
- Metrics: no runtime metric change.
- Tracing: HTTP path 保持低基数，为后续 automatic fetch instrumentation 和 BFF server span 聚合提供稳定 route。
- Events: none.

## Testing Strategy

- Run `buf lint`.
- Run `buf generate`.
- Run `buf breaking --against .git#branch=master`.
- Inspect generated Go HTTP binding for pricing and loan-application registration symbols.
- Inspect generated OpenAPI for pricing and loan-application paths.
- Run `pnpm generate` and `pnpm build` in `idl-ts-repo`.
- Run `go test ./...` in `idl-go-repo`.
- Record commands and results in `requirements/LEN-153/evidence/buf-checks.md`.

## Rollout And Rollback

- Rollout:
  1. Merge LEN-153 IDL changes.
  2. Publish or expose generated outputs according to current IDL pipeline.
  3. Start LEN-154 BFF implementation only after LEN-153 merges to `master` and worktree is cleaned.
- Rollback:
  - Before downstream adoption, revert LEN-153 IDL commit.
  - After downstream adoption, roll back BFF/FE consumers first, then revert contract if still needed.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| 契约字段过度绑定下游内部模型 | 只表达 BFF-facing DTO 和父 Story AC 需要的字段 | forest |
| 当前生成链路没有本地 TS 输出 | 把 OpenAPI 作为 TS SDK 输入面证据，并记录后续生成仓事实 | forest |
| breaking 检查因历史基线失败 | 记录准确失败，不把失败伪装成通过 | forest |
