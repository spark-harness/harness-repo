# LEN-132 fides-bff pricing facade

本目录保存 `LEN-132` 的需求、影响分析、设计、任务、门禁、审查和验证证据。

## Ticket

- Jira: `LEN-132`
- Title: `[BE] fides-bff pricing facade`
- Branch: `feature/LEN-132-fides-bff-pricing-facade`

## Scope

`fides-bff` 对前端暴露 `POST /api/v1/pricing/quotes`，在 LEN-22 会话上下文下调用 `quote-api`，传播 `x-applicant-id`、`traceparent` 和 `tracestate`，并把 quote-api 的结果和错误映射为 BFF 对外契约。

不在本 ticket 实现报价算法、访问 quote DB、部署 quote/origination 下游配置或修改前端。
