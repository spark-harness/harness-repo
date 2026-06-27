# LEN-22 Local Verification Evidence

## Scope

本证据覆盖 LEN-22 的本地实现验证：

- Go `bffkit` principal、AuthFilter、owner guard、gRPC metadata 传播。
- Go `fides-bff` 受保护 probe 路由、token validator、匿名 auth 路由不受阻断。
- Java `spring-starter` RequestPrincipalContext 和 gRPC interceptor。

## Test-First Evidence

生产代码实现前新增测试并运行：

```text
cd business-repo/packages/go/bffkit && go test ./...
```

结果：失败，原因是缺少 `AuthFilter`、`Principal`、`ContextWithPrincipal`、`HeaderApplicantID` 等符号。

```text
cd business-repo/packages/java/spring-starter && mvn test
```

结果：失败，原因是缺少 `RequestPrincipalGrpcServerInterceptor`、`RequestPrincipal`、`RequestPrincipalContext`。

## Final Verification

```text
cd business-repo/packages/go/bffkit && go test ./...
```

结果：PASS。

```text
cd business-repo/apps/fides-bff && go test ./...
```

结果：PASS。

```text
cd business-repo/packages/java/spring-starter && mvn test
```

结果：PASS，10 tests, 0 failures, 0 errors.

## Behavior Covered

- 缺失 Bearer token 访问受保护 BFF probe 返回 401。
- 有效 token 建立 Principal 并返回 applicantId。
- 外部 `x-applicant-id` 被清洗，不能覆盖 token 派生身份。
- BFF protected path matcher 覆盖后续 `/api/v1/pricing/` 与 `/api/v1/loan-applications` facade 路径，并保持 `/api/v1/auth/*` 匿名入口不受阻断。
- `RequireResourceOwner` 对非本人资源返回 403。
- BFF outgoing gRPC context 传播 `x-applicant-id` 与 `traceparent`。
- Java interceptor 从 metadata 建立 RequestPrincipalContext。
- Java interceptor 在缺失 `x-applicant-id` 时返回 UNAUTHENTICATED。
- Java RequestPrincipalContext 在请求完成后清理。

## IDL Impact

无 IDL 修改。`idl-repo` 仅创建同名 helper worktree 用于 Janus service-repo-check 解析现有 proto path，不产生文件变更。
