---
requirement_id: "LEN-22"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-28"
idl_impact: "no"
idl_impact_reason: "本需求只新增 BFF 和 Java 服务内部认证中间件、context 与 metadata 传播，不修改 protobuf IDL、HTTP 对外契约或 generated contracts。"
approved_by: "forest"
approved_at: "2026-06-28T01:12:46+08:00"
decision: "用户授权 Agent 批准 LEN-22 服务仓库检查；本需求影响 harness-repo 与 business-repo，不修改 IDL。"
---

# Impact Analysis

## Summary

LEN-22 影响 `fides-bff` 的受保护路由过滤器、Go `bffkit` 横切能力、Java Spring starter 的请求 Principal 上下文，以及现有 Java 服务读取可信 BFF 注入身份的边界。不修改 IDL，不新增业务服务。

## Affected Domains

- 前端体验域：BFF 负责外部会话校验和身份传播。
- 申请人域：`applicant-api` 继续签发 token，并提供兼容 token 校验所需格式。
- 公共工程能力：Go `bffkit` 和 Java `spring-starter` 承载横切认证和 principal context。

## Affected Services

| Service / Module | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides-bff | business-repo | 新增受保护接口 auth filter、principal context、下游 metadata 传播 | no |
| packages/go/bffkit | business-repo | 提供 Principal、AuthFilter、Forbidden/Unauthorized 错误和 OutgoingGRPCContext 身份传播 | no |
| packages/java/spring-starter | business-repo | 提供 RequestPrincipal、RequestPrincipalContext 和 gRPC interceptor | no |
| applicant-api | business-repo | 作为 token 签发事实源，保持签发格式兼容；如需 Java interceptor 测试可消费 starter | no |
| Harness LEN-22 lifecycle | harness-repo | 保存需求、影响分析、设计、任务、门禁和证据 | no |

## Upstream / Downstream Consumers

- Upstream consumers: 浏览器和 `fides-web` 只继续携带 Bearer access token，不允许提供权威 applicantId。
- Downstream consumers: 后续 `quote-api`、`origination-api` 将从 Java starter 读取 `RequestPrincipalContext`。
- Existing downstream: `applicant-api` 的 OTP gRPC 接口保持匿名入口，不受保护。

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: no.
- Contract repo: `idl-repo` 不需要修改。
- Proto files: no changes.
- Buf module: no changes.
- Generated contract impact: no changes.
- Breaking baseline: not applicable.
- Compatibility risk: 外部 API 路径不变；新增受保护接口时会使用统一 401/403 错误信封。

## Data Impact

- Database schema: 不修改。
- Data migration: 不需要。
- Cache: 不修改 Redis key 或 token storage。
- Runtime storage: 不新增状态存储；token 校验为无状态或读取已有签发策略。

## Config / Permission / Observability Impact

- Config:
  - BFF 需要 token validator secret/mode 与 applicant-api 签发策略保持一致。
  - Java starter 不保存 secret，只读取 gRPC metadata。
- Permission:
  - 新增 Principal 边界和本人资源守卫。
  - 服务身份信任暂以内部网络/BFF 调用约定为前提，后续由 mTLS/Istio 固化。
- Logs:
  - 不记录 token、Authorization、Cookie 或完整个人信息。
  - 401/403 日志只记录稳定 error code、trace_id、operation。
- Tracing:
  - 保持 W3C `traceparent` 传播。
  - 身份传播与 tracing 解耦，traceparent 不参与鉴权。
- Metrics:
  - 可复用现有 HTTP 指标记录 401/403 error_code。
- Events:
  - 不新增事件。

## Rollout And Rollback

- Rollout:
  - 先通过 bffkit 和 spring-starter 单元测试。
  - 再在 `fides-bff` 中接入受保护路由过滤器。
  - 后续 tickets 在新增 quote/origination facade 时复用此中间件。
- Rollback:
  - 回滚 `bffkit` auth/principal 变更和 `fides-bff` 接入。
  - 回滚 Java starter principal interceptor。
  - 由于无 schema/IDL 变更，回滚不涉及数据迁移。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| BFF 与 applicant-api token 格式不一致 | 有效登录 token 被错误拒绝 | 用测试覆盖 HMAC/simple token validator 与现有签发格式 | core |
| 浏览器伪造 x-applicant-id 被误信任 | 越权访问本人以外资源 | AuthFilter 清洗外部 header，只从 token 建 Principal | core |
| Java 下游缺失 principal 时继续执行业务 | 资源归属校验失效 | ServerInterceptor 对受保护调用缺失 metadata 返回 UNAUTHENTICATED | core |
| traceparent 与身份传播耦合 | 调试 header 被误用于鉴权 | 设计和测试明确 traceparent 不参与身份判断 | core |
| 只实现中间件但没有可验证受保护业务路由 | 验收无法证明 403 | 用 bffkit 守卫函数和测试路由证明行为，后续业务 ticket 复用 | core |
