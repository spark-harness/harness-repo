# LEN-206 Local Verification

## Go

在 `/Users/forest/Code/spark/.worktrees/LEN-206/business-repo/apps/fides-bff`：

```bash
go test ./...
```

结果：PASS。

在 `/Users/forest/Code/spark/.worktrees/LEN-206/business-repo/packages/go/bffkit`：

```bash
go test ./...
```

结果：PASS。

## Java

在 `/Users/forest/Code/spark/.worktrees/LEN-206/business-repo/packages/java/spring-starter`：

```bash
mvn -q -Dtest=GrpcServerAutoConfigurationTest,GrpcServerLifecycleTest,RequestPrincipalGrpcClientInterceptorTest,RequestPrincipalGrpcServerInterceptorTest test
```

结果：PASS。

安装当前 starter 到本地 Maven 仓：

```bash
mvn -q -DskipTests install
```

结果：PASS。

在 `/Users/forest/Code/spark/.worktrees/LEN-206/business-repo/apps/origination-api`：

```bash
mvn -q -Dtest=GrpcQuoteGatewayTest test
```

结果：PASS。该测试使用前一步安装的当前 starter 版本。

## Residual Runtime Evidence

LEN-210 仍需部署后用真实 Sentry trace 验证：

```text
fides http.client -> fides-bff http.server -> fides-bff rpc -> origination-api CreateLoanApplication -> origination-api rpc -> quote-api GetQuote
```
