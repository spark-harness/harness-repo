---
requirement_id: "LEN-132"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-28"
idl_impact: "no"
idl_impact_reason: "本需求在 fides-bff 增加 HTTP facade 和 quote-api HTTP adapter，不修改 protobuf IDL、generated contracts 或 Buf 配置。"
approved_by: "forest"
approved_at: "2026-06-28T03:34:39+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-132 service-repo-check，按 Jira 范围实现 fides-bff pricing facade，不修改 IDL，不交付 GitOps runtime 配置。"
---

# Impact Analysis

## Summary

LEN-132 在 `fides-bff` 新增 pricing facade。BFF 接收前端试算请求，复用 LEN-22 鉴权和 principal context，调用 `quote-api`，并统一响应字段、身份传播、trace 传播和错误映射。

## Affected Domains

- Frontend/BFF：新增前端可调用 pricing facade。
- Pricing：消费 `quote-api` 已有创建 Quote HTTP 能力。
- Security：强化 `x-applicant-id` 只从 token principal 派生。

## Affected Services And Repos

| Service / Module | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides-bff | business-repo | 新增 pricing HTTP handler、usecase、quote-api HTTP client、config 和测试 | no |
| Harness LEN-132 lifecycle | harness-repo | 保存需求、影响分析、设计、任务、门禁和证据 | no |
| quote-api | business-repo | 作为下游依赖被调用；本 ticket 不修改 quote-api | no |

## Upstream / Downstream Consumers

- Upstream:
  - LEN-11 `fides-web` 将调用 `/api/v1/pricing/quotes`。
- Downstream:
  - `quote-api` `POST /api/v1/pricing/quotes`。
  - quote DB 只由 quote-api 写入，BFF 不直接访问。

## API And Contract Impact

- BFF external HTTP contract:
  - `POST /api/v1/pricing/quotes`
  - request: `{ productCode, amount, term, purpose }`
  - response: `{ quoteId, monthly, apr, totalInterest, totalPayable, validUntil }`
- Protobuf IDL: no changes.
- Generated contracts: no changes.
- Error semantics:
  - 401 `unauthorized`
  - 422 `amount_out_of_range`
  - 422 `validation_error`
  - 502 `quote_unavailable`
- Compatibility risk:
  - 新增 endpoint，无已发布 BFF pricing facade 兼容负担。
  - 字段名必须与 Jira 和后续前端 adapter 保持一致。

## Data / Storage Impact

- BFF 不新增数据库、migration、cache 或持久化表。
- Quote 写入由 quote-api 执行。
- BFF 不保存请求体、响应体或金额快照。

## Config Impact

- `fides-bff` 增加 quote-api client 配置面：
  - direct base URL，用于本地测试和 smoke。
  - Consul service name/address/scheme，用于后续 LEN-135 运行时服务发现配置。
  - HTTP timeout。
- LEN-132 只交付代码配置能力和默认值；Kubernetes/GitOps 运行时注入由 LEN-135 交付。

## Permission / Security Impact

- `/api/v1/pricing/quotes` 使用 LEN-22 AuthFilter。
- applicantId 从 principal context 获取。
- 外部传入 `x-applicant-id` 必须被忽略。
- 不记录 Authorization、token 或完整请求体。
- quote-api 不可用时只返回稳定错误码，不暴露内部地址或异常堆栈。

## Observability / Logs / Tracing

- 入口请求继续使用 BFF 既有 TraceFilter。
- 下游 HTTP request 必须传播 `traceparent` 和 `tracestate`。
- 下游调用应使用 context timeout。
- 失败路径返回稳定错误码，便于日志和 trace 关联。

## Rollout And Rollback

- Rollout:
  1. 合入 BFF pricing facade 代码和测试。
  2. 本地/CI 验证通过。
  3. LEN-135 后续配置运行时 quote-api 下游地址并 smoke。
- Rollback:
  - 回滚 BFF branch 中 pricing facade 代码和 config 面。
  - 不涉及 DB 回滚。
  - 未修改 quote-api 或 GitOps runtime，回滚半径只在 BFF。

## Risks And Mitigations

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| BFF 信任外部 `x-applicant-id` | applicant 可越权创建他人 Quote | 测试覆盖攻击者 header 被忽略，只传播 principal applicantId | core |
| BFF 用 float 解析金额 | 金额精度或格式漂移 | 用 `json.RawMessage` / `json.Number` 保持 decimal 语义，不计算不格式化 | core |
| quote-api 地址配置与 LEN-135 冲突 | 部署态 smoke 失败 | LEN-132 只提供 config surface；LEN-135 管理 runtime 注入和服务发现 | core |
| 下游错误泄露内部细节 | 前端或日志暴露内部地址/堆栈 | 统一映射为稳定错误码和 BFF error envelope | core |
