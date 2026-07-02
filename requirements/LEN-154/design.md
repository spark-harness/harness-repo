---
requirement_id: "LEN-154"
owner: "forest"
status: "approved"
updated_at: "2026-07-02"
approved_by: "forest"
approved_at: "2026-07-02T16:13:19Z"
decision: "用户授权 Agent 批准所有需要的文件；批准 LEN-154 设计，允许进入任务拆分和 BFF 实现。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, AC1 | D1：HTTP server 注册统一使用 `idl-go-repo v0.2.5` 生成的 auth、identity-profile、pricing、loan-application registration。 | `v0.2.5` 包含 LEN-153 pricing / loan application Go binding。 |
| R2, AC2 | D2：删除 pricing、loan-application、identity-profile 的手工 Kratos route 注册，只保留 health 和 session probe 手工路由。 | 不修改 URL、HTTP method 或前端可见 path。 |
| R3, AC3 | D3：`internal/service` 中的入站 service 实现 generated interface，完成 proto request/response 与 biz command/result 的映射。 | proto 类型只停留在入站适配层，不进入 biz 层。 |
| R4, BR3, BR4, BR5 | D4：继续从 request context/header 提取 principal、`Idempotency-Key`、`traceparent`、`tracestate`，并传给现有下游 client/usecase。 | principal 不从 body 接收 applicantId。 |
| R5 | D5：`/api/v1/health` 和 `/api/v1/protected/session:probe` 不纳入 generated binding。 | 保持运行时探针和 session 检查兼容。 |
| R6, AC4, AC5 | D6：在 `internal/server/http_test.go` 和 service 相关测试中覆盖 generated binding 下的成功、鉴权、idempotency/trace 和错误映射。 | 先运行 characterization / failing tests，再改生产代码。 |

## Summary

LEN-154 把 `fides-bff` 已入 IDL 的业务 HTTP 入口从手写 Kratos route 切到 generated HTTP binding。核心业务用例、下游 HTTP/gRPC client、错误码语义、鉴权中间件、trace 传播和运行时探针保持不变。

实现边界是入站适配层和 server registration：generated proto request/response 只在 `internal/service` 和 `internal/server` 出现，biz 层继续使用现有 command/result 类型。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| fides-bff | 更新 Go contract dependency，替换 HTTP route registration，改造入站 service adapter 和测试。 | 主体变更服务。 |
| applicant-api | 不改代码；identity-profile 下游调用保持现状。 | 验证 BFF adapter 不破坏 principal、idempotency 和 trace 传递。 |
| quote-api | 不改代码；pricing 下游调用保持现状。 | 验证报价请求仍到达 quote facade。 |
| origination-api | 不改代码；loan application 下游调用保持现状。 | 验证 application ID、幂等和 trace 仍传递。 |

## API / Contract Design

- Protobuf IDL required: no new IDL; consume LEN-153 output.
- Proto files:
  - `{idl-repo}/vesta/lendora/fides-bff/v1/auth.proto`
  - `{idl-repo}/vesta/lendora/fides-bff/v1/identity_profile.proto`
  - `{idl-repo}/vesta/lendora/fides-bff/v1/pricing.proto`
  - `{idl-repo}/vesta/lendora/fides-bff/v1/loan_application.proto`
- Buf config version: v2
- Buf module: `local/lendora-fides-bff`
- Generated outputs: `github.com/spark-harness/idl-go-repo v0.2.5`
- Formal tag trace:
  - `idl-repo v0.2.5` -> `34c4f17456d5032bf4aecc765b641094d7ab0b5e`
  - `idl-go-repo v0.2.5` -> `e519b232cbaa043b38a7138e926f8641be6b7a11`
- Breaking check baseline: not applicable in LEN-154 because proto is unchanged; LEN-153 owns Buf evidence.
- Compatibility strategy: keep existing HTTP path, method, JSON field names, status mapping and error envelope behavior. Tests must exercise generated route paths instead of service methods only.

## Data / Config / Permission

- Data model: no schema, migration, cache, backfill or persistence change.
- Config: update `business-repo/apps/fides-bff/go.mod` to formal `github.com/spark-harness/idl-go-repo v0.2.5` if required by generated pricing / loan application symbols.
- Permission: existing protected-path filter remains responsible for `/api/v1/pricing/*`, `/api/v1/loan-applications`, `/api/v1/loan-applications/*`, `/api/v1/me/identity-profile` and `/api/v1/protected/session:probe`.

## Observability

- Logs: no new log fields; errors continue through existing error handler.
- Metrics: no new metrics.
- Tracing: generated binding must not strip incoming request context. Existing downstream clients must continue propagating `traceparent` and `tracestate`.
- Events: none.

## Rollout And Rollback

- Gray release: deploy a new `fides-bff` image after tests and gates pass.
- Kill switch: no runtime flag; rollback by reverting the BFF image to the previous version.
- Rollback: keep `idl-repo` and generated repo formal tags because they are additive; revert only the `business-repo` implementation commit if generated binding causes regression.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Generated binding request decoding differs from hand-written handler. | Characterization tests hit the same HTTP endpoints before and after adapter change. | forest |
| `application_id` path variable mapping breaks GET/PATCH loan application. | Tests call `/api/v1/loan-applications/{id}` and assert the usecase receives the expected ID. | forest |
| Proto enum JSON output differs from current string output. | Tests assert identity-profile and loan-application response JSON compatibility for user-visible fields. | forest |
| Contract dependency accidentally uses pseudo-version. | `go.mod` must use formal `idl-go-repo v0.2.5`; evidence records tag resolution. | forest |
