---
requirement_id: "LEN-137"
owner: "core"
status: "approved"
updated_at: "2026-06-28"
approved_by: "forest"
approved_at: "2026-06-28T22:32:07+08:00"
decision: "批准 LEN-137 design.md；方案按 IDL-first 实现 applicant-api 身份信息保存回填、origination-api identity_information 步骤推进、fides-bff HTTP facade、fides-web Step 3 页面和 local 网页真实链路验证。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| BR1, AC2 | D4 BFF 从 principal 获取 applicantId，Step 3 保存必须携带 `applicationId`，origination-api 校验 application 归属 | 不信任前端 applicantId |
| BR2, BR6, AC1, AC7, AC8 | D1 新增 identity profile 契约和 profile 数据模型 | HKID 主体与校验位分字段 |
| BR3, BR4, BR5, BR7, AC4, AC5, AC6 | D2 前端做即时校验，applicant-api 做权威校验 | DOB 使用 Asia/Hong_Kong 自然日期 |
| BR8, AC3 | D6 前端 Continue 成功后停留 Step 3，不 toast、不跳转 | Controller 返回保存成功状态 |
| BR9, AC7, AC8 | D3 applicant-api GET 未保存返回 empty profile，BFF 映射为空对象 | 不抛 not_found |
| BR10 | D3 applicant-api 明文持久化 HKID 字段；日志和证据仍不得输出敏感原文 | 区分存储要求和日志安全 |
| BR11, AC9 | D5 BFF 保存 profile 成功后调用 origination-api 推进 `identity_information` | 需要处理部分成功风险 |
| BR12 | D1 所有新增服务边界先落 IDL，fides-web 只调用 BFF HTTP，BFF 调内部 gRPC | additive contract change |
| BR13, AC10 | D7 本地网页真实链路作为完成证据 | 单元测试和接口直调不能单独完成 Story |

## Summary

本方案新增 Step 3 身份信息链路。IDL 先定义 applicant-api profile gRPC、origination-api step gRPC 和 fides-bff HTTP facade；业务仓再按契约实现保存、回填、步骤推进和前端页面。

这不是 dev-1 发布方案。交付证据以 local 网页真实链路为准。

## Design Decisions

### D1: 契约先行

在 `idl-repo` 中新增 additive proto：

- applicant-api: `ApplicantProfileService.UpsertIdentityProfile` 和 `GetIdentityProfile`。
- origination-api: `OriginationDraftService.AdvanceApplicationStep`。
- fides-bff: `FidesBffIdentityProfileService`，HTTP annotation 暴露 `PUT /api/v1/me/identity-profile` 和 `GET /api/v1/me/identity-profile`。

Nationality 使用契约枚举，前端选项从同一枚举映射，避免手写漂移。

### D2: applicant-api 是身份字段校验权威

前端执行即时校验用于体验，applicant-api 负责权威校验：

- HKID 格式为单字母前缀、6 位数字、单独校验位。
- HKID check digit 按香港身份证规则计算。
- First Name / Last Name 必填且仅允许英文字母。
- Chinese Name 必填。
- DOB 按 Asia/Hong_Kong 当前自然日期计算年龄，范围为 18 到 60 周岁。
- Nationality 必须是契约枚举。

非法输入返回稳定错误码：`validation_error`、`hkid_invalid`、`age_out_of_range`。

### D3: identity profile 独立于 OTP applicant 认证资料

applicant-api 现有 applicant 认证模型服务 OTP 和 token。本需求新增 identity profile 模型，不把 Step 3 字段混入 OTP challenge 或 token 记录。

存储策略：

- 以 `applicantId` 为唯一归属键。
- 明文保存 HKID body、HKID check digit、姓名、Nationality、DOB。
- GET 未保存时返回 `empty=true` 或等价空 profile 语义，不返回 not_found。
- Upsert 同一 applicant 的 profile 时覆盖当前身份信息并更新 `updated_at`。

父 Story 要求 HKID 明文保存；这不等于允许日志、trace、门禁证据输出 HKID 原文。日志和证据仍遵守团队安全规范，不记录身份证号原文、token、手机号或 Authorization header。

### D4: BFF 是前端唯一服务边界

fides-web 只调用 fides-bff HTTP：

- `GET /api/v1/me/identity-profile?applicationId={applicationId}` 用于回填。
- `PUT /api/v1/me/identity-profile` 用于保存，body 包含 identity profile 和 `applicationId`。

BFF 只从 token principal 读取 applicantId，不接受或转发前端传入的 applicantId。

BFF 保存顺序：

1. 校验登录态和 `applicationId` 是否存在。
2. 调用 applicant-api `UpsertIdentityProfile` 保存身份资料。
3. 调用 origination-api `AdvanceApplicationStep` 推进 `currentStep`。
4. 返回保存后的 identity profile 和 `currentStep`。

GET 回填不推进步骤，只读取 profile；没有保存过时返回空对象。

### D5: origination-api 只推进到 identity_information

origination-api 新增 `IDENTITY_INFORMATION("identity_information")` application step。

`AdvanceApplicationStep` 仅允许当前需求需要的目标步骤：

- 必须有 `applicationId`。
- application 必须属于当前 principal applicantId。
- 目标步骤必须是 `identity_information`。
- 成功后持久化 `current_step` 并返回 applicationId/currentStep。

现有 JDBC 读路径必须从 `current_step` 字段映射 ApplicationStep，不能继续固定映射 `LOAN_REQUEST`。否则保存成功后查询会错误回到 `loan_request`。

### D6: 前端 Step 3 保持现有分层

fides-web 按现有 `domain / application / adapters / infrastructure / presentation` 边界实现：

- domain：身份字段值对象和 HKID、姓名、DOB 校验。
- application：identity profile gateway port、save/load use case。
- adapters：controller 把 UI 动作转换为 use case command，把结果转换为 view model。
- infrastructure：BFF HTTP gateway、browser draft pointer 读取。
- presentation：Step 3 表单、字段错误、loading/saved 状态。

没有登录态或没有 Step 2 `applicationId` 时，不展示可保存表单，进入可恢复的前置流程。

Continue 保存成功后保持在 Step 3，不 toast，不跳转第 4 步。

### D7: 本地网页真实链路验收

完成证据必须包含 local 网页真实链路：

```text
OTP -> Step 2 保存 -> Step 3 保存 -> 刷新回填 -> currentStep 验证
```

证据记录：

- local 网页 URL。
- BFF 请求结果，不包含 token 或敏感原文。
- Step 3 保存和刷新回填结果。
- currentStep 为 `identity_information` 的验证范围。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| applicant-api | 新增 profile gRPC adapter、use case、domain model、repository 和 migration | 保存与回填身份信息 |
| origination-api | 新增 step gRPC adapter、use case、step 枚举、repository 映射更新 | 推进 `identity_information` |
| fides-bff | 新增 identity HTTP facade、applicant/origination gRPC clients、路由和错误映射 | 前端唯一服务边界 |
| fides | 新增 Step 3 表单、校验、gateway、controller 和回填 | 用户填写身份信息 |
| idl-repo | 新增 applicant、origination、fides-bff 契约 | 满足 IDL-first |
| harness-repo | 保存生命周期材料、门禁、审查和 local 证据 | 可追溯交付 |

## API / Contract Design

- Protobuf IDL required: yes.
- Proto files:
  - `vesta/lendora/applicant/v1/profile.proto`
  - `vesta/lendora/origination/v1/draft.proto`
  - `vesta/lendora/fides-bff/v1/identity_profile.proto`
- Buf module: current `idl-repo/buf.yaml` module path `.`.
- Buf config version: v2.
- Generated outputs:
  - Go generated contracts for fides-bff.
  - Java generated contracts for applicant-api and origination-api.
- Breaking check baseline: `origin/master` / `master`.
- Compatibility strategy: additive change. Do not change existing `auth.proto`, existing loan request HTTP paths, existing field numbers, or existing response semantics.

### Contract Sketch

Identity profile fields:

- `hkid_body`
- `hkid_check_digit`
- `first_name`
- `last_name`
- `chinese_name`
- `nationality`
- `date_of_birth`

Date of birth is a date string in `YYYY-MM-DD` semantic form. It is not a timestamp.

Fides BFF save response includes identity profile and `current_step`. This lets frontend verify AC9 without coupling to origination internals.

### Error Mapping

| Source | Error Code | BFF HTTP |
|---|---|---:|
| Missing or invalid token | `unauthorized` | 401 |
| Missing `applicationId` | `application_required` | 400 |
| Application not owned by applicant | `forbidden` | 403 |
| Field validation | `validation_error` | 422 |
| HKID invalid | `hkid_invalid` | 422 |
| DOB age out of range | `age_out_of_range` | 422 |
| Applicant API unavailable | `applicant_unavailable` | 502 |
| Origination API unavailable | `origination_unavailable` | 502 |

## Data / Config / Permission

### Data Model

applicant-api:

- Add identity profile storage keyed by applicantId.
- Store HKID body/check digit and profile fields in clear text per Story BR10.
- Add created/updated timestamps.
- Enforce one current identity profile per applicant.

origination-api:

- Add `identity_information` step value.
- Persist currentStep updates.
- Read `current_step` from DB instead of hard-coding `LOAN_REQUEST`.

No data backfill is required.

### Config

- fides-bff needs applicant profile gRPC downstream configuration.
- fides-bff needs origination step gRPC downstream configuration.
- Local runtime must start fides-web, fides-bff, applicant-api, origination-api and their storage dependencies.

### Permission

- BFF protected route middleware must cover `/api/v1/me/identity-profile`.
- applicant-api writes by applicantId from trusted BFF principal propagation.
- origination-api verifies application ownership before step update.
- Frontend never sends applicantId for this operation.

## Observability

- Logs:
  - Record operation name, trace/request id, applicant resource id only if existing policy allows safe identifier logging.
  - Do not log HKID, phone number, token, Authorization header, request body, or response body.
- Metrics:
  - Reuse existing HTTP/gRPC request metrics if generic middleware is present.
  - No new business metric required for MVP.
- Tracing:
  - Preserve `traceparent`/`tracestate` through BFF to downstream calls.
- Events:
  - No event publication required.

## Testing Strategy

### IDL

- `buf lint`
- `buf generate`
- `buf breaking --against '.git#branch=master'` or repo-standard equivalent.

### applicant-api

- Unit tests for HKID check digit, name validation, nationality validation and DOB age boundary.
- Use case tests for upsert, overwrite and get-empty behavior.
- Repository integration tests for clear-text field persistence and applicantId uniqueness.
- gRPC adapter tests for request/response mapping and error mapping.

### origination-api

- Unit/use case tests for missing applicationId, forbidden applicant, invalid target step and successful `identity_information` advancement.
- Repository tests proving `current_step` is written and read back correctly.
- gRPC adapter tests for generated contract mapping.

### fides-bff

- HTTP server tests for auth required, application required, successful save order, GET empty object, downstream validation mapping and 502 mapping.
- Client tests for applicant-api and origination-api gRPC calls.
- Ensure protected path matcher covers `/api/v1/me/identity-profile`.

### fides-web

- Domain tests for HKID, DOB and name validation.
- Controller tests for missing session/draft pointer, save success without navigation, validation failures and load empty profile.
- Infrastructure gateway tests for BFF GET/PUT mapping.
- Presentation tests for field layout, errors, empty profile and refill.
- `pnpm lint:deps` must pass.

### Local E2E

- Use browser against local fides-web.
- Execute OTP, Step 2 save, Step 3 save and refresh/refill.
- Verify currentStep through BFF response or current draft query.

## Rollout And Rollback

- Gray release:
  - Not in scope for LEN-137. This ticket completes through local validation.
- Kill switch:
  - No new kill switch required.
  - If Step 3 route exposure needs temporary control, use existing frontend route/config pattern rather than adding a one-off switch.
- Rollback:
  - Revert fides-web Step 3 UI and BFF facade.
  - Revert applicant-api profile use case/storage and origination step advancement.
  - Revert additive proto before publishing consumers; after publication, deprecate rather than delete consumed fields.
  - Drop local-only test data when resetting local runtime.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| applicant profile saved but currentStep update fails | BFF returns failure after origination error; local evidence must inspect both profile and currentStep. Follow-up retry/idempotency can be added if product needs eventual completion semantics. | bff/origination |
| frontend and backend HKID/DOB validation drift | Put shared examples in tests on both sides; backend remains authority. | applicant/frontend |
| generated contract path blocks implementation | Resolve buf generation and Java/Go consumption before business implementation. | idl |
| existing origination DB reader ignores current_step | Update mapper and add repository test for `identity_information`. | origination |
| sensitive data leaks into logs or evidence | Store HKID as required, but never print raw HKID/token/phone in logs, tests, screenshots or gate evidence. | all |
| LEN-143 Jira description still mentions dev-1 | Keep Harness scope tied to parent Story local requirement and record non-goal; update Jira separately if needed. | core |
