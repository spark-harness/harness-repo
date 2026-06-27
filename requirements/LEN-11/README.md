# LEN-11 贷款请求屏接试算与 Continue 静默保存

- Ticket: `LEN-11`
- Title: `[FE] 贷款请求屏接试算与 Continue 静默保存`
- Branch: `feature/LEN-11-loan-request-real-pricing-draft`
- Status: `draft`
- Owner: `core`

## Scope

本需求让 `fides-web` 第二页贷款请求屏接入真实 `fides-bff` pricing 和 loan application draft API。UI 必须参照 `.docs/hk_loan_ui/2._loan_request_input_field/code.html`。

## Delivery Boundary

- 修改仓库：`business-repo`、`harness-repo`
- 不修改仓库：`idl-repo`、`gitops-repo`
- 前置依赖：LEN-22、LEN-132、LEN-133、LEN-135 已合并并在 lendora-sta 可用。

