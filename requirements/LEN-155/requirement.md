---
requirement_id: "LEN-155"
owner: "forest"
status: "approved"
created_at: "2026-07-02"
related_branch: "feature/LEN-155-fides-web-generated-sdk-adapter"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
approved_by: "forest"
approved_at: "2026-07-02T17:05:12Z"
decision: "用户授权 Agent 批准所有需要的文件；批准 LEN-155 impact-analysis，确认本票只修改 fides-web 与 TS SDK 依赖，不产生新的 IDL、数据或 GitOps 影响。"
---

# [FE] fides-web 全面使用生成 TS SDK 浅适配层

## Background

`LEN-153` 已生成 fides-bff pricing 与 loan-application 的 OpenAPI / TypeScript SDK 输出，`LEN-154` 已让 BFF 运行时使用 generated HTTP binding。当前 `fides-web` 已对 auth 和 identity-profile 使用 generated TS client，但 loan request gateway 仍手写 `/pricing/quotes`、`/loan-applications` 请求、trace header 注入和响应解析。

它不是什么：本需求不是新增页面流程，不实现 `/api/v1` 应用内代理，不修改 GitOps 内网 BFF 地址。

它是什么：让 `fides-web` 所有 BFF 调用都通过 `@spark-harness/idl-ts-client v0.2.5` 的浅适配层完成，保留 application / presentation 对 gateway port 的依赖边界，并移除各 gateway 内重复的手写 trace 逻辑。

## Goals

- R1：`fides-web` 消费包含 auth、identity-profile、pricing、loan-application 的 generated TS SDK formal tag。
- R2：mobile verification、identity profile、loan quote、loan application draft 都通过 infrastructure gateway 包装 generated API client。
- R3：application、adapters、presentation 层不直接 import generated client 或 generated DTO。
- R4：删除各 gateway 内手写 `traceparent`、`tracestate`、`startSpan`、`span.end` 等 trace 逻辑。
- R5：保留鉴权、幂等键、超时、错误映射和响应归一化在 gateway 层。
- R6：单测覆盖 auth、identity-profile、pricing、loan-application 四类 adapter 行为。

## Non-Goals

- 不新增或修改 protobuf IDL；LEN-153 已完成。
- 不修改 fides-bff Go runtime；LEN-154 已完成。
- 不新增 Next.js `/api/v1` 应用内代理；LEN-156 负责。
- 不修改 dev / sta GitOps 配置或跨服务 trace 环境；LEN-157 负责。
- 不改变页面视觉、路由或业务步骤。

## User / Business Scenarios

### Scenario 1：手机验证码继续通过 generated auth client

Given：用户打开申请流程并输入手机号。

When：前端发送 OTP、验证 OTP 或刷新 token。

Then：请求通过 auth generated client 发往 BFF，gateway 继续处理幂等键、超时和错误映射。

### Scenario 2：身份资料继续通过 generated identity profile client

Given：用户进入身份资料步骤。

When：前端读取或保存 identity profile。

Then：请求通过 identity-profile generated client 发往 BFF，domain / presentation 不接触 generated DTO。

### Scenario 3：报价请求切换到 generated pricing client

Given：用户填写贷款金额、期限和用途。

When：前端创建 quote。

Then：请求通过 pricing generated client 发往 BFF，响应被 gateway 映射为现有 `QuoteResult`。

### Scenario 4：贷款申请草稿切换到 generated loan application client

Given：用户接受 quote 并保存申请草稿。

When：前端 create、get 或 patch loan application。

Then：请求通过 loan-application generated client 发往 BFF，现有 `DraftResult` / `DraftDetail` 语义保持不变。

## Business Rules

- BR1：生成 API client 只能出现在 infrastructure 层或同层共享 helper 中。
- BR2：application、adapters、presentation 层只能依赖现有 gateway port 和 domain 类型。
- BR3：`Idempotency-Key` 继续由 gateway 在写请求中注入。
- BR4：Authorization header 继续由 gateway 从 session token 注入，缺 token 时不得发起 BFF 请求。
- BR5：超时和 BFF error envelope 必须继续映射为现有前端错误语义。
- BR6：前端 gateway 不再手动创建 span 或拼装 trace context；浏览器 tracing 统一交给 shared fetch / SDK middleware 或后续 LEN-156 自动追踪处理。

## Acceptance Criteria

- AC1：`@spark-harness/idl-ts-client` 升级到包含 pricing 和 loan-application API 的 formal tag `v0.2.5`。
- AC2：loan request gateway 使用 `FidesBffPricingServiceApi` 和 `FidesBffLoanApplicationServiceApi`。
- AC3：mobile verification 和 identity-profile gateway 保持 generated client 包装，并移除本地手写 trace span/header 逻辑。
- AC4：`rg 'traceparent|tracestate|startSpan|span\\.end' apps/fides-web/src/infrastructure` 不再命中 gateway 手写 trace。
- AC5：adapter / gateway tests 覆盖 auth、identity-profile、pricing、loan-application 的成功、鉴权、幂等、超时或错误映射关键行为。
- AC6：`pnpm test`、`pnpm lint`、`pnpm lint:deps`、`pnpm build` 通过。
- AC7：父 Story AC1-AC4、AC6 的前端行为有验证证据。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 是否存在可消费的 TS SDK formal tag | forest | 实现前 | Resolved：`idl-ts-repo v0.2.5` 已指向 `af09e09be8328d15ca9f026f65cbc980f90425d3`，包含 pricing 和 loan-application API。 |

## Notes

- 用户已授权 Agent 批准所有需要的文件；本需求按授权推进生命周期文件和门禁。
- `LEN-155` 只能在 `LEN-154` 已合并并清理 worktree 后开始；该条件已满足。
- `idl-ts-repo` 只作为已发布生成契约的证据来源，不作为 LEN-155 affected repository。
