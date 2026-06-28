---
requirement_id: "LEN-5"
owner: "core"
status: "approved"
created_at: "2026-06-28"
related_branch: "feature/LEN-5-story-acceptance"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
approved_by: "forest"
approved_at: "2026-06-28T07:58:00+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-5 requirement 和 impact-analysis，范围为 Story 验收收口，不新增业务代码、IDL 或部署。"
---

# 发起贷款请求并试算 Story 验收收口

## Background

LEN-5 是贷款申请漏斗第 2 步的 Story：已通过手机验证的访客选择 PIL 产品，填写借款金额、期限和用途，看到指示性试算，并在点击 Continue 时静默保存当前贷款请求草稿。

这条需求不是什么：它不是新增 `quote-api`、`origination-api`、`fides-bff` 或 `fides-web` 业务实现，不是重新定义 UI 原型，也不是补做 KYC、审批或第三页跳转。

它是什么：它是 Story 级验收收口。它用前序 ticket 的交付物和新的端到端 evidence 证明 AC1-AC5 已满足，并明确任何环境缺口是否阻塞 Story 交付。

## Goals

- 验证服务端权威试算结果能在贷款请求页展示为估算。
- 验证金额或期限越界时不产生可继续报价。
- 验证金额、期限或用途变化后旧 quote 失效，必须重新试算。
- 验证 Continue 成功后静默保存草稿，页面停留当前贷款请求页。
- 验证同一草稿重新打开后能回填金额、期限和用途。
- 汇总前序 ticket 的 merge-readiness、runtime smoke 和本次端到端证据。

## Non-Goals

- 不新增或修改 protobuf IDL。
- 不新增后端 API、数据库表、GitOps 部署或前端业务代码。
- 不修改 `.docs/hk_loan_ui/2._loan_request_input_field/code.html`。
- 不把真实 secret、token、手机号或生产数据写入仓库。
- 不把前序 ticket 的实现细节复制进 Harness 文档；只记录验收边界和证据入口。

## User / Business Scenarios

### Scenario 1: 有效贷款请求试算

Given: 用户已登录并在贷款请求页。

When: 用户输入 PIL 允许区间内的金额、期限和用途。

Then: 页面显示服务端返回的月供、年化和总额，并标注为估算。

### Scenario 2: 越界输入

Given: 用户在贷款请求页输入金额或期限。

When: 金额或期限超出 PIL 允许区间后试算或点击 Continue。

Then: 页面就地提示超出允许范围，不产生可继续的报价。

### Scenario 3: 旧报价失效

Given: 用户已获得一次有效试算。

When: 用户修改金额、期限或用途。

Then: 旧 quote 不再允许 Continue，用户必须重新试算。

### Scenario 4: Continue 静默保存

Given: 用户填写完成且试算有效。

When: 用户点击 Continue。

Then: 当前贷款请求保存为草稿，页面停留在贷款请求页，不跳转、不 toast。

### Scenario 5: 同一草稿回填

Given: 用户已有某一笔草稿贷款请求。

When: 用户重新打开同一草稿。

Then: 页面回填该草稿保存的金额、期限和用途。

## Business Rules

- BR1: 试算结果只能来自服务端权威 quote，不接受前端本地计算作为验收依据。
- BR2: `fides-web` 只能通过 `fides-bff` 调用 pricing 和 draft API，不直连 Java 服务。
- BR3: 受保护接口必须依赖 LEN-22 的 token 校验、principal context、`x-applicant-id` 和 `traceparent` 传播。
- BR4: quote 与 draft 必须归属于同一 applicant。
- BR5: Continue 保存成功后不得推进到第三页。
- BR6: 同一 applicant 可有多笔草稿，本次验收只验证“同一草稿”的回填。

## Acceptance Criteria

- AC1: 已登录且在贷款请求页时，输入区间内金额与期限后显示服务端返回的月供、年化和总额，且标注为估算。
- AC2: 输入金额或期限超出 PIL 区间后，试算或 Continue 给出就地提示，不产生可继续报价。
- AC3: 已得到试算后修改金额、期限或用途，旧报价失效，需重新试算后方可 Continue。
- AC4: 填写完成且试算有效时点击 Continue，当前贷款请求静默保存为草稿，页面仍停留在贷款请求页。
- AC5: 已有某一笔草稿贷款请求时，重新打开同一草稿能回填金额、期限和用途。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| PIL 金额区间与期限选项是否沿用 LEN-11/LEN-10 固定 MVP 口径？ | product/core | 2026-06-28 | resolved: 本次验收沿用已交付 MVP 口径，正式产品目录另开需求 |
| 完整 OTP 登录链路是否必须作为 LEN-5 阻塞条件？ | core | 2026-06-28 | resolved: 当前公网 OTP send/verify 已通过；LEN-5 以真实登录后的贷款请求链路作为验收主路径 |

## Notes

- 前序依赖：LEN-22、LEN-10、LEN-131、LEN-132、LEN-9、LEN-134、LEN-133、LEN-135、LEN-11。
- 当前集群为 vincent-k3s。
