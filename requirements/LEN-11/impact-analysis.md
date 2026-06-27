---
requirement_id: "LEN-11"
analyst: "Codex"
status: "draft"
updated_at: "2026-06-28"
idl_impact: "no"
idl_impact_reason: "本需求只修改 fides-web 前端实现和 Harness 证据，复用已交付 BFF REST facade，不修改 protobuf IDL、generated contracts 或 Buf 配置。"
---

# Impact Analysis

## Summary

LEN-11 将 `fides-web` 从手机号验证屏扩展到贷款请求屏，并让该屏调用真实 BFF pricing 和 loan application draft facade。

## Affected Domains

- Frontend application flow：手机号验证成功后进入第二页。
- Frontend API integration：新增 pricing 和 origination BFF HTTP gateway。
- Frontend state：保存当前会话 access token、application pointer、quote snapshot。
- Harness lifecycle：新增 LEN-11 需求、设计、任务、证据和门禁。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides | business-repo | 新增贷款请求屏、controller、gateway、session flow 和测试 | no |
| fides-bff | business-repo | 下游依赖，只消费已交付 REST facade，不改代码 | existing only |
| Harness LEN-11 lifecycle | harness-repo | 保存需求、设计、任务、门禁和证据 | no |

## Upstream / Downstream

- Upstream user: `fides-web` browser user。
- Downstream runtime:
  - `fides-web -> fides-bff POST /api/v1/pricing/quotes`
  - `fides-web -> fides-bff POST /api/v1/loan-applications`
  - `fides-web -> fides-bff GET /api/v1/loan-applications/{applicationId}`
  - `fides-web -> fides-bff PATCH /api/v1/loan-applications/{applicationId}`
- `fides-web` 不调用 Java 服务。

## API / Contract Impact

- External API: no new public backend API.
- Protobuf IDL: no changes.
- Generated contracts: no changes.
- Frontend HTTP adapter:
  - 直接调用 BFF REST endpoints。
  - 统一注入 Authorization、Idempotency-Key 和 trace headers。
  - 读取 BFF error envelope 并映射成 UI error。

## Data Impact

- Browser:
  - access token only in memory.
  - sessionStorage may store applicationId/applicantId/current step pointer.
- Backend data:
  - pricing 请求会创建 quote。
  - Continue create/patch 会写 application draft 和 idempotency record。
- No DB schema or migration changes.

## Config / Permission / Observability Impact

- Config:
  - 复用 `PublicRuntimeConfig.bffBaseUrl`。
  - 复用 OTP adapter config。
- Permission:
  - 受保护请求依赖 LEN-22 access token。
  - BFF 负责 applicant principal 和越权防护。
- Logs:
  - 前端不记录 token、Authorization、手机号或完整申请 PII。
- Tracing:
  - 复用 browser tracing helper 注入 W3C trace headers。
- Metrics:
  - 不新增指标。
- Events:
  - 不新增事件。

## Rollout And Rollback

- Rollout:
  - 合并 `fides-web` 前端改动。
  - 运行 frontend tests、lint、dependency cruiser。
  - 部署/刷新 fides image 后执行浏览器 smoke。
- Rollback:
  - 回滚 `fides-web` commit。
  - 如 runtime 已发布，回滚 fides image digest。
  - 后端 API 不需要回滚。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| access token 无法从手机号验证传给第二页 | 第二页全部 401 | 用 session store 保持内存 token，并用组件测试覆盖 verified flow | core |
| pricing 防抖或竞态导致旧 quote 覆盖新输入 | Continue 保存错误 quote | 只接受最新请求结果，测试覆盖快速输入 | core |
| Continue 成功后误跳转或 toast | 违反用户要求和 AC7 | 组件测试断言仍停留当前页且不调用导航/toast | core |
| purpose code 映射错误 | quote/create/patch 返回校验错误 | 明确 UI option 到后端 code 映射并测试 | core |
| Runtime BFF token secret/manual STA drift | 浏览器 smoke 无法登录或保存 | 复用 LEN-135 runtime smoke 结果，失败时记录环境 WARN | core |

