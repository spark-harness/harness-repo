# Local Verification

验证时间：2026-07-05T01:19:21+08:00

## IDL

工作目录：`/Users/forest/Code/spark/.worktrees/LEN-176/idl-repo`

```bash
buf lint
buf generate --template buf.gen.java.yaml
buf generate --template buf.gen.go.yaml
buf breaking --against '.git#branch=master'
```

结果：全部通过。

生成物：

- `../idl-java-repo/src/main/java/com/vesta/lendora/quote/v1/*`
- `../idl-java-repo/src/main/grpc-java/com/vesta/lendora/quote/v1/QuoteServiceGrpc.java`
- `../.generated/idl-go/vesta/lendora/quote/v1/quote.pb.go`
- `../.generated/idl-go/vesta/lendora/quote/v1/quote_grpc.pb.go`

## Formal Contract

- `idl-repo` PR: https://github.com/spark-harness/idl-repo/pull/14
- `idl-repo` merge commit: `042af3374be47e6e2854adab79930260945f2403`
- Formal IDL tag: `v0.2.6`
- Java artifact: `com.spark.contract:spark-idl-java:0.2.6`
- Go generated contract tag: `spark-harness/idl-go-repo` `v0.2.6`

`apps/quote-api/pom.xml` 使用 `spark.contract.version=0.2.6`。

## quote-api

工作目录：`/Users/forest/Code/spark/.worktrees/LEN-176/business-repo`

```bash
mvn -B -f packages/java/spring-starter/pom.xml test install -DskipTests=false
```

结果：BUILD SUCCESS，12 tests，0 failures，0 errors。公共 `RequestPrincipalGrpcServerInterceptor` 保留默认未认证描述，并支持 quote-api 覆盖为 `QUOTE-AUTH-0001`。

```bash
python3 scripts/contract_dependency_scan.py --mode master --path apps/quote-api/pom.xml
```

结果：通过，未发现 contract dependency violations。

```bash
mvn -B -s /tmp/len176-maven-settings.<redacted>.xml -f apps/quote-api/pom.xml test
```

结果：BUILD SUCCESS，28 tests，0 failures，0 errors。测试下载并使用 `spark-idl-java:0.2.6`。

覆盖：

- gRPC CreateQuote 成功路径。
- gRPC GetQuote 成功路径。
- 缺少 applicant metadata 时返回 `UNAUTHENTICATED` / `QUOTE-AUTH-0001`。
- 非法金额映射到 `INVALID_ARGUMENT` / `QUOTE-PARAM-0002`。
- 报价不存在映射到 `NOT_FOUND` / `QUOTE-STATE-0001`。
- 跨申请人读取映射到 `PERMISSION_DENIED` / `QUOTE-PERMISSION-0001`。
- 报价过期映射到 `FAILED_PRECONDITION` / `QUOTE-STATE-0002`。
- HTTP health/readiness 保留。
- Consul 注册包含 `grpc_port=9090`。
- application.yml 保留 env placeholder 并声明 gRPC 端口。

## GitOps

工作目录：`/Users/forest/Code/spark/.worktrees/LEN-176/gitops-repo`

```bash
kubectl kustomize apps/quote-api/overlays/dev-1 >/tmp/len176-quote-dev.yaml
kubectl kustomize apps/quote-api/overlays/sta-1 >/tmp/len176-quote-sta.yaml
rg -n "name: grpc|port: 9090|SPARK_QUOTE_CONSUL_GRPC_PORT|SPARK_GRPC_SERVER_PORT" /tmp/len176-quote-dev.yaml /tmp/len176-quote-sta.yaml
```

结果：渲染通过；dev-1 和 sta-1 都包含 gRPC Service port、container port、NetworkPolicy 9090、`SPARK_QUOTE_CONSUL_GRPC_PORT` 和 `SPARK_GRPC_SERVER_PORT`。

## HTTP Cleanup Boundary

```bash
rg -n "QuoteHttpAdapter|QuoteHttpExceptionHandler|/api/v1/pricing/quotes|/internal/v1/pricing" apps/quote-api
```

结果：quote-api 业务 HTTP adapter 仍存在。该保留是刻意的发布边界：现有 fides-bff 和 origination-api 仍在后续 Story 中迁移到 gRPC，`LEN-196` 前不能做最终 HTTP 清理。
