---
requirement_id: "LEN-22"
owner: "core"
status: "approved"
updated_at: "2026-06-28"
approved_by: "forest"
approved_at: "2026-06-28T01:12:46+08:00"
decision: "用户授权 Agent 批准 LEN-22 design.md，并以 token 校验、principal context、x-applicant-id、traceparent 为实现边界。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| BR1, AC1 | 在 Go `bffkit` 提供 AuthFilter 和 TokenValidator 端口 | BFF 统一处理外部 Bearer token |
| BR2, AC3 | AuthFilter 在进入下游 handler 前清洗外部 `x-applicant-id` | 不允许浏览器注入权威身份 |
| BR3, AC2 | `bffkit.Principal` 写入 Go context | 后续 facade/use case 通过 context 读取 |
| BR4, BR8, AC4 | `OutgoingGRPCContext` 注入 `x-applicant-id`，并保留 W3C trace propagation | 身份传播和 tracing 独立 |
| BR5, AC5 | Java starter 提供 gRPC ServerInterceptor 与 RequestPrincipalContext | Java use case 读取可信 BFF principal |
| BR6, BR7, AC6 | `RequireResourceOwner` 返回统一 forbidden 错误 | 不泄露非本人资源细节 |
| AC7 | Go/Java 单测覆盖中间件、metadata 和 principal context | 作为后续 ticket 的前置证据 |

## Summary

LEN-22 在 BFF 和 Java 内部服务之间建立最小可信身份链路。

它不是什么：不是服务网格级别的调用方身份认证，也不是把 applicantId 放进前端请求体。

它是什么：BFF 校验 access token 并建立 Principal；BFF 向内部服务注入 `x-applicant-id`；Java 服务只从受信 metadata 建立 `RequestPrincipalContext`。

## Affected Services

| Service / Module | Change | Reason |
|---|---|---|
| `packages/go/bffkit` | 增加 Principal、TokenValidator、AuthFilter、ownership guard、gRPC metadata 传播 | BFF 横切认证能力 |
| `apps/fides-bff` | 在受保护路由组可接入 AuthFilter，保留 auth 路由匿名 | 后续 pricing/origination facade 复用 |
| `packages/java/spring-starter` | 增加 RequestPrincipalContext 和 gRPC ServerInterceptor | Java 服务统一读取 principal |
| `apps/applicant-api` | 保持 token 签发兼容，OTP/auth 路由匿名 | 登录链路不受保护 |

## API / Contract Design

- External HTTP: 不新增本 ticket 对外业务接口。
- Error envelope: 复用 `bffkit.ErrorEncoder`，401 使用 `BFF-AUTH-0001`，403 使用 `BFF-PERMISSION-0001`。
- Internal gRPC metadata:
  - `x-applicant-id`: BFF 从 Principal 注入。
  - `traceparent`: 由 OpenTelemetry W3C propagation 注入。
  - `tracestate`: 如存在则继续传播。
- Protobuf IDL: no changes.

## Application Design

### Go BFF Principal

`bffkit.Principal` 只包含当前已认证主体需要的低风险字段：

```text
ApplicantID
TokenID
ExpiresAt
```

`TokenValidator` 是端口接口，BFF 可先使用与 applicant-api 兼容的 validator，后续替换为 introspection 或 JWKS 时不影响 handler。

`AuthFilter` 行为：

1. 从 Authorization 读取 Bearer token。
2. 缺失或格式错误时返回 401。
3. 调用 TokenValidator 校验 token type、签名、过期时间。
4. 清洗外部 `x-applicant-id`。
5. 把 Principal 写入 request context。

### Ownership Guard

受保护 use case 在读取资源后调用 owner guard：

```text
RequireResourceOwner(ctx, resourceApplicantID)
```

principal 不存在返回 401；归属不一致返回 403；一致则继续处理。

### gRPC Metadata Propagation

`OutgoingGRPCContext` 继续注入 trace metadata，并在 Principal 存在时追加 `x-applicant-id`。如果调用方声明该下游受保护但 context 中没有 Principal，业务 client 必须在调用前返回明确错误。

### Java RequestPrincipalContext

Java starter 提供：

- `RequestPrincipal`：不可变 applicantId 值对象。
- `RequestPrincipalContext`：ThreadLocal 生命周期上下文，提供 `current()` 和 `required()`。
- `RequestPrincipalGrpcServerInterceptor`：从 incoming metadata 读取 `x-applicant-id`，缺失时返回 `UNAUTHENTICATED`，请求结束后清理 context。

## Data / Config / Permission

- Data: 不新增表、migration 或缓存 key。
- Config: BFF validator 使用与 applicant-api token 签发一致的 secret/mode；不提交真实 secret。
- Permission: 本 ticket 建立 applicant 级资源归属守卫；服务调用方身份由后续平台能力补强。

## Observability

- Logs:
  - 401/403 记录稳定 error code、operation、trace_id。
  - 不记录 token、Authorization header 或资源敏感细节。
- Tracing:
  - BFF server span 从外部 traceparent 提取。
  - BFF client span 向 Java gRPC 注入新的 traceparent。
  - Java server interceptor 不使用 traceparent 做鉴权。
- Metrics:
  - 复用 BFF HTTP metrics 的 status_code 和 error_code。

## Testing Strategy

- Go `bffkit`:
  - AuthFilter 缺失/错误 token 返回 401。
  - AuthFilter 成功后 context 有 Principal。
  - 外部 `x-applicant-id` 被清洗且不能覆盖 Principal。
  - `RequireResourceOwner` 对非本人资源返回 403。
  - `OutgoingGRPCContext` 同时传播 `x-applicant-id` 和 `traceparent`。
- Go `fides-bff`:
  - 匿名 auth 路由不被 AuthFilter 阻断。
  - 测试路由证明受保护 filter 行为。
- Java starter:
  - interceptor 从 metadata 建立 `RequestPrincipalContext`。
  - 缺失 `x-applicant-id` 返回 `UNAUTHENTICATED`。
  - 请求完成后 context 被清理。

## Rollout And Rollback

- Rollout:
  - 先合入公共包和 BFF 中间件。
  - LEN-132/LEN-133 接 BFF facade 时直接使用 AuthFilter。
  - LEN-10/LEN-9 Java 服务读取 RequestPrincipalContext。
- Rollback:
  - 回滚公共包和 BFF 接入。
  - 不涉及数据或 IDL 回滚。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Token validator 与签发实现漂移 | 测试覆盖现有 token 格式，后续抽换 validator 端口 | core |
| 中间件只在部分受保护路由启用 | 后续 facade ticket 在 tasks 中显式引用 AuthFilter | core |
| ThreadLocal 泄漏 principal | interceptor 使用 try/finally 清理并测试覆盖 | core |
| 错误响应泄露资源存在性 | forbidden 使用统一 message，不返回资源信息 | core |
