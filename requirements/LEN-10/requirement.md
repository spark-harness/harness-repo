---
requirement_id: "LEN-10"
owner: "core"
status: "approved"
created_at: "2026-06-28"
related_branch: "feature/LEN-10-quote-api-pricing-service"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
  - gitops-repo
approved_by: "forest"
approved_at: "2026-06-28T01:39:43+08:00"
decision: "用户授权 Agent 批准 LEN-10 requirement.md 与 impact-analysis.md，并按 Jira 范围新建 quote-api。"
---

# quote-api Java Spring 试算服务

## Background

贷款申请第二页需要真实试算结果。当前系统尚无 Pricing 子域服务，也没有可供草稿保存引用的持久化 quoteId。

这条需求不是什么：它不是部署 quote-api，不是实现 BFF facade，也不是前端接真实 API。

它是什么：它创建独立 `quote-api` Java Spring 服务，完成 PIL 试算、Quote 持久化和内部 Quote 校验边界，供 LEN-132、LEN-9 和 LEN-11 后续复用。

## Goals

- 新建 `business-repo/apps/quote-api` Java Spring 服务。
- 对 `POST /api/v1/pricing/quotes` 的金额、期限、purpose 和产品配置做校验。
- 每次成功试算都创建并持久化一条 Quote，返回稳定 `quoteId`。
- 返回 `monthly`、`apr`、`totalInterest`、`totalPayable`、`validUntil`。
- 提供内部 Quote 读取/校验边界，校验 quoteId 存在、属于当前 applicant 且未过期。
- 使用 LEN-22 的 `RequestPrincipalContext` 获取 applicantId，不接受前端传 applicantId。
- quote-api ready 检查能反映 quote DB 不可用。

## Non-Goals

- 不修改 protobuf IDL 或生成契约。
- 不创建 Kubernetes/GitOps 部署清单；LEN-131 负责部署 quote-api 和 quote DB。
- 不修改 `fides-bff` pricing facade；LEN-132 负责 BFF 对外转发。
- 不实现 loan application 草稿保存；LEN-9 负责 origination 草稿。
- 不实现前端第二页真实 API 接入；LEN-11 负责。
- 不引入产品目录服务；本 ticket 使用固定 PIL MVP 产品配置。

## User / Business Scenarios

### Scenario 1: 区间内试算成功

Given: 已认证 applicant 请求 PIL 试算，金额和期限在允许范围内。

When: quote-api 创建 Quote。

Then: 返回 quoteId、月供、APR、总息、总还款额和 validUntil，并在 quote DB 写入一条记录。

### Scenario 2: 金额或期限越界

Given: 请求金额或期限超出 PIL 产品配置。

When: quote-api 校验请求。

Then: 返回 422 `amount_out_of_range`，且不写入 Quote。

### Scenario 3: 输入变化产生新 Quote

Given: 同一 applicant 修改金额、期限或 purpose 后重新试算。

When: quote-api 成功计算。

Then: 创建新的 Quote 和 validUntil，不写草稿、不改变申请状态。

### Scenario 4: 内部读取本人 Quote

Given: origination-api 后续携带 principal applicantId 和 quoteId 校验 Quote。

When: quoteId 属于当前 applicant 且未过期。

Then: quote-api 返回完整 Quote 信息供草稿保存快照。

### Scenario 5: 内部读取非本人或过期 Quote

Given: quoteId 不存在、不属于当前 applicant 或已过期。

When: 内部校验边界读取 Quote。

Then: 分别返回 `quote_not_found`、`forbidden` 或 `quote_expired`。

## Business Rules

- BR1: PIL MVP 金额区间为 5,000 到 500,000。
- BR2: PIL MVP 期限只允许 3、6、9、12、24 个月。
- BR3: 每一次成功报价计算必须持久化 Quote，并返回 quoteId。
- BR4: Quote 的 applicantId 必须来自 LEN-22 principal context，不接受请求体传入。
- BR5: 金额计算必须使用 BigDecimal，禁止 double/float 参与金额、APR、总息和总还款额计算。
- BR6: Quote 默认有效期为创建后 30 分钟。
- BR7: 内部 Quote 校验必须同时检查存在性、applicantId 归属和 validUntil。
- BR8: quote-api 不写草稿、不创建申请状态、不调用 origination。

## Acceptance Criteria

- AC1: 区间内金额/期限返回 quoteId、monthly、apr、totalInterest、totalPayable、validUntil，并持久化 Quote。
- AC2: 金额或期限越界返回 422 `amount_out_of_range`，且不写入 Quote。
- AC3: 输入变化产生新的 Quote/validUntil，且不写草稿、不产生申请状态变化。
- AC4: Repository/integration 测试覆盖 quote migration、Quote 写入、按 quoteId 读取和 applicantId 归属校验。
- AC5: 内部 Quote 校验覆盖 quote 不存在、quote 不属于当前 applicant、quote 过期三类失败。
- AC6: quote-api health、ready、Maven test、格式/静态质量门通过；ready 能反映 quote DB 不可用。
- AC7: 代码结构符合 backend-clean-architecture 与 team/java，不复制 applicant/auth 业务代码。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| LEN-10 是否先定义 protobuf/gRPC 契约？ | core | 2026-06-28 | resolved: 本 ticket 先做 HTTP/JDBC 服务边界，不改 IDL；BFF facade 后续用 HTTP 调用或再单独补 contract |
| 是否需要 Idempotency-Key 防双击重复 Quote？ | core | 2026-06-28 | resolved: 当前 Jira 明确每次成功试算落一条 Quote，幂等策略不在本 ticket |

## Notes

- LEN-10 依赖 LEN-22 已合并的 principal context 能力。
- LEN-131 才负责部署、quote DB runtime 和 Consul/k8s 可发现性。
- 本 ticket 包含 `gitops-repo` 中 Java CI DAG 的最小支撑变更，只用于让 LEN-10 的 `quote-api` 被 PR Java gate 调度；不包含运行时部署。
