---
requirement_id: "LEN-13"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-19"
approved_by: "Forest"
approved_at: "2026-06-21T15:10:48+08:00"
decision: "批准 LEN-13 service-repo-check，可以进入编码循环。"
idl_impact: "no"
idl_impact_reason: "本需求只修改前端 fides 的手机验证屏，消费 BFF REST OTP 契约；不新增或修改 protobuf IDL、Buf 配置或生成契约。"
---

# Impact Analysis

## Summary

`LEN-13` 影响 `fides` 前端第 1 步手机验证屏：接入 OTP 发码 / 验码接口、真实倒计时、OTP 输入、错误态、会话保存和 FlowController 前进；不修改后端服务、protobuf 契约或数据库。

## Affected Domains

- `frontend`：前端申请漏斗第 1 步，从静态原型行为演进为可接 OTP 契约的真实界面。
- `frontend / edge`：消费 `fides-bff` 暴露的 REST `/api/v1` 约定；本需求不修改 BFF。
- `user / auth`：作为 OTP 业务能力的契约依赖记录；本需求不实现领域服务。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides | `{business-repo}/services/frontend/fides` | 修改手机验证屏、表单状态、OTP 输入、接口消费、会话保存和流程前进 | No |
| fides-bff | `{business-repo}/services/backend/fides-bff` | 上游前端消费其 REST / 错误 / 幂等 / 可观测约定；本需求不改代码 | No |
| —（harness-repo） | `harness-repo` | 新增 `LEN-13` 需求生命周期产物 | No |

## Upstream / Downstream Consumers

- 上游用户：Lendora 申请漏斗访客。该屏是进入贷款请求步骤的前置验证门。
- 下游流程：验证成功后进入步骤 2 贷款请求；验证失败、过期或限流时停留在步骤 1。
- 下游依赖：`LEN-12` 提供 OTP 契约；`LEN-4` 提供 FlowController / API 客户端；`LEN-21` 提供 BFF REST 入口与横切约定。
- 不影响 `aegis`、`user-api` 当前 gRPC 契约、IDL 仓或生成契约仓。

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: 不涉及 protobuf；消费既定或待定的 BFF REST OTP 契约。
- Contract repo: 无 protobuf 契约仓变更。
- Proto files: 无。
- Buf module: 不适用。
- Buf config version: v2（不涉及变更）。
- Required buf checks: 不适用。
- Breaking baseline: 不适用。
- Compatibility risk: 前端依赖 `auth/otp:send` 和 `auth/otp:verify` 字段、错误码、冷却时间、token 返回结构；若 `LEN-12` 契约未冻结，设计阶段必须以 mock adapter 隔离字段变化。

## Data Impact

- Database schema: 无。
- Data migration: 无。
- Backfill: 无。
- Cache / runtime storage: 前端需要保存短期请求状态、倒计时和会话结果。验证码、完整手机号、token 不得进入日志或持久化草稿；登录态 1 小时过期后应触发重验流程。

## Config / Permission / Observability Impact

- Config: 可能需要前端 API base URL、mock/real adapter 切换、OTP 冷却默认值；具体放置点在设计阶段确认。
- Permission: 本需求不新增权限模型；验证成功后的登录态只代表“手机已验证”。
- Metrics: 前端可选记录发码点击、发码成功/失败、验码成功/失败等不含 PII 的产品事件；若团队未建立前端遥测，本需求不强制新增。
- Logs: 不记录完整手机号、验证码、token；错误上报仅允许 traceId / 错误码 / 非敏感状态。
- Tracing: 前端需透传 / 展示 BFF 错误信封中的 traceId 以便排障；不新增后端 tracing。
- Events: 无业务事件生产。

## Rollout And Rollback

- Gray release: 可先以 mock adapter 演示 AC1-AC8，再切到真实 BFF；真实接口切换可按环境配置控制。
- Kill switch: 如真实 OTP 接口不可用，可回退到 mock adapter 或临时关闭入口，但不应恢复假成功跳转作为验收路径。
- Rollback steps: 回滚 `fides` 中手机验证屏相关改动与对应 Harness 生命周期产物；不涉及数据迁移、IDL 回滚或后端服务回滚。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| `LEN-12` OTP 契约未冻结 | 前端字段和错误码可能返工 | 设计阶段定义 adapter 边界；先 mock 契约，真实接口就绪后只替换 adapter | Frontend / Backend |
| `LEN-4` FlowController / API 客户端未就绪 | 验证成功后无法按目标方式进入步骤 2 | 设计阶段明确最小接口；必要时本需求只实现步骤 1 局部 adapter，并把跨步前进接入点留清楚 | Frontend |
| token 存储策略不清 | XSS 或会话续期风险 | 设计阶段按安全规则确定 accessToken / refreshToken / applicantId 存放边界 | Frontend / Security |
| 冷却倒计时只按前端本地计时 | 刷新或多标签页时与服务端限流不一致 | 以服务端返回冷却时间和 429 错误为准，本地倒计时仅作体验状态 | Frontend |
| 为了演示保留假跳转 | 验收误判，没有真正接入流程 | AC9 明确禁止假 `setTimeout` 作为成功路径；测试 / 演示必须走接口响应和 FlowController | Harness |
