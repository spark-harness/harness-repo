---
requirement_id: "LEN-43"
owner: "Codex"
status: "approved"
created_at: "2026-06-21"
related_branch: "feature/LEN-43-fides-bff-mobile-verification"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - idl-repo
  - business-repo
approved_by: "Forest"
approved_at: "2026-06-21T22:30:36+08:00"
decision: "批准 LEN-43 requirement 与 impact-analysis，允许进入设计阶段。"
---

# [FE+BFF] 手机验证端到端接入 fides-bff

## Background

父 Story LEN-2 定义了 Lendora 申请漏斗第 1 步：访客用手机号收验证码并通过验证，获得“手机已验证”的登录态后进入下一步。现有工作已分别沉淀出 `applicant-api` OTP 能力、`fides-bff` BFF 骨架和 `fides` 手机验证前端体验，但端到端真实接入仍未完成。

当前 `fides` 已有手机验证页面、mock OTP gateway 和 REST gateway 基础；`fides-bff` 仍以健康检查和横切约定为主，尚未暴露手机验证业务入口。本需求把前端体验、BFF REST 入口、BFF-facing protobuf 协议、Consul 服务发现和 applicant-api 调用串成可验证的端到端路径。

先说不是什么：本需求不是 `applicant-api` 的 OTP 业务规则实现，不定义 Redis / PostgreSQL 持久化细节，不接真实短信供应商，也不把“手机已验证”解释为 KYC 完成或已创建贷款申请。

## Goals

- R1：新增 `idl-repo/vesta/lendora/fides-bff/v1/auth.proto`，定义 `fides-bff` 对前端暴露的手机验证 BFF 协议。
- R2：BFF protobuf 的 `SendOtp`、`VerifyOtp`、`RefreshToken` RPC 必须带 `google.api.http` 注解，并映射到 `/api/v1/auth/*` REST 路径。
- R3：更新服务矩阵，将 `fides-bff` 标记为需要 protobuf，并登记 BFF proto path 与 buf module。
- R4：`fides-bff` 暴露 `POST /api/v1/auth/otp:send`、`POST /api/v1/auth/otp:verify`、`POST /api/v1/auth/token:refresh`。
- R5：`fides-bff` 通过 Consul service discovery 发现 `applicant-api`，不得硬编码 applicant-api 地址；本地可通过配置指定 Consul 地址和服务名。
- R6：`fides-bff` 将前端 REST / BFF 协议映射到 applicant-api gRPC client，并处理错误映射、统一错误信封、Idempotency-Key 和 trace metadata 透传。
- R7：`fides` 通过环境配置指向本地或目标环境 `fides-bff`，完成发码、冷却、验码、错误展示和成功进入下一步。
- R8：补充本地联调说明，覆盖 PostgreSQL、Redis、Consul、applicant-api、fides-bff 和 fides 的连接方式。
- R9：提供测试和 smoke 证据，证明 LEN-2 AC1-AC6 在 `fides + fides-bff` 路径上可验证。

## Non-Goals

- 不实现 `applicant-api` 的 OTP 发送、校验、过期、锁定、token 或 applicant 持久化业务规则。
- 不修改 PostgreSQL schema、Redis key 设计或真实短信供应商接入。
- 不实现 KYC、贷款申请创建、金额期限录入或资料填写。
- 不改变 LEN-2 对登录态语义的定义：验证通过只代表“手机已验证”。
- 不在 master-bound 代码中依赖临时本地 generated Go contract、RC、SNAPSHOT 或 branch replacement。
- 不修改 `idl-java-repo`，除非后续设计明确 BFF-facing contract 需要 Java 生成物并获得阶段批准。

## User / Business Scenarios

### Scenario 1：合法手机号请求验证码

Given：访客在 `fides` 手机验证页输入合法 `+852` 手机号。

When：点击获取验证码。

Then：前端调用 `fides-bff`，BFF 经 Consul 发现并调用 `applicant-api`，页面进入冷却倒计时。

### Scenario 2：冷却期内重复发码

Given：访客已经成功请求验证码，冷却倒计时未结束。

When：再次尝试获取验证码。

Then：前端按钮不可用或展示剩余时间；如请求到达 BFF，BFF 以统一错误信封返回可映射的冷却错误。

### Scenario 3：正确验证码进入下一步

Given：访客已获得未过期验证码。

When：输入正确验证码并提交。

Then：`fides-bff` 返回会话结果，`fides` 保存允许保存的短期会话定位并进入下一步。

### Scenario 4：错误验证码停留当前页

Given：访客已获得验证码。

When：输入错误验证码并提交。

Then：页面提示“验证码不正确”，焦点回到 OTP 输入，不进入下一步。

### Scenario 5：验证码过期

Given：验证码已过期。

When：访客提交该验证码。

Then：页面提示验证码已过期，并提供重新获取路径。

### Scenario 6：多次错误后暂时锁定

Given：同一手机号短时间内多次输入错误验证码。

When：再次提交验证码。

Then：页面提示稍后再试；BFF 保留 retry-after / 锁定信息用于前端倒计时或禁用。

## Business Rules

- BR1：MVP 仍仅支持 `+852` 香港手机号；前端可先做体验校验，后端仍是权威。
- BR2：发码、验码、刷新 token 都属于写请求，必须携带或稳定生成 `Idempotency-Key`。
- BR3：BFF REST 错误必须使用统一错误信封，并保留稳定错误码和 traceId。
- BR4：BFF 不得硬编码 applicant-api 地址；本地/dev 通过 Consul 地址、服务名和超时配置装配。
- BR5：BFF-facing protobuf 是 `fides-bff` 对前端 REST 语义的事实来源，RPC 必须带对应 HTTP 注解。
- BR6：BFF 到 applicant-api 的错误映射必须覆盖验证码错误、过期、冷却、锁定、未授权、下游不可用和 Consul 解析失败。
- BR7：前端不得记录或持久化验证码、完整手机号、access token、refresh token 或 BFF 原始敏感响应。
- BR8：master-bound `fides-bff` 只能消费 formal generated Go contract；RC 或同分支生成物只能用于合并前验证。
- BR9：trace metadata 应从前端/BFF 传递到下游调用，日志和指标禁止使用手机号、验证码、token、challengeId 等高敏或高基数字段。

## Acceptance Criteria

- AC1：合法 `+852` 手机号请求验证码时，`fides` 通过 `fides-bff` 完成发码并展示冷却倒计时。
- AC2：冷却未结束时再次请求验证码，页面不可重复发码，并显示剩余秒数或友好提示。
- AC3：输入正确且未过期验证码后，`fides-bff` 返回会话结果，`fides` 进入下一步。
- AC4：输入错误验证码后，页面提示“验证码不正确”，停留当前页。
- AC5：验证码过期后提交，页面提示已过期，并允许重新获取。
- AC6：短时间内多次错误尝试后，页面提示暂时锁定或稍后再试。
- AC7：`idl-repo/vesta/lendora/fides-bff/v1/auth.proto` 存在，RPC 带 `google.api.http` 注解并映射到目标 REST 路径。
- AC8：服务矩阵中 `fides-bff` 声明 `idl_required: true`，并登记 `{idl-repo}/vesta/lendora/fides-bff/v1`。
- AC9：IDL 变更有 `buf lint`、`buf generate`、`buf breaking --against .git#branch=master` 结果记录，并有 Go contract 生成或发布验证证据。
- AC10：`fides-bff` 测试覆盖 REST -> BFF protocol -> applicant gRPC client 映射、错误映射、Consul 解析失败和下游不可用。
- AC11：`fides` 测试覆盖 API adapter、页面交互、冷却、错误码、过期和锁定状态；`pnpm lint:deps` 与 build 通过。
- AC12：端到端 smoke 通过浏览器或等价脚本经 `fides-bff` 完成发码和验码。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| BFF-facing Go contract 在 master-bound 前应使用哪个 formal tag / module 版本消费 | Platform / BFF | 设计阶段 | Open |
| 本地 smoke 是否使用 applicant-api test provider 固定验证码，还是通过测试替身模拟 applicant gRPC | Backend / BFF | 设计阶段 | Open |
| `RefreshToken` REST 响应是否由本需求接入前端自动刷新，还是只完成 BFF 入口和 adapter 能力 | Product / FE | 设计阶段 | Open |

## Notes

- JIRA：`LEN-43`，父 Story `LEN-2`，标签包含 `frontend`、`bff`、`idl`、`consul`。
- 用户已明确 BFF proto 路径使用 `vesta/lendora/fides-bff/v1/auth.proto`，不是 `vesta/lendora/fides/bff/v1/auth.proto`。
- 用户已明确 BFF gRPC 路由应有对应 `google.api.http` 注解。
- 当前项目上下文缺少 `lendora/frontend/fides` 和 `lendora/frontend/fides-bff` 的 `context/project` 入口；本需求需要在影响分析中记录该上下文缺口。
