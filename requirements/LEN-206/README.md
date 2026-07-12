# LEN-206 - gRPC tracing 与 Principal metadata 硬切

本目录追踪 Story `LEN-206` 及子任务 `LEN-207`、`LEN-208`、`LEN-209`、`LEN-210`。

目标 trace 拓扑：

```text
fides http.client
-> fides-bff http.server
-> fides-bff rpc
-> origination-api CreateLoanApplication
-> origination-api rpc
-> quote-api GetQuote
```

当前状态：

- 需求、影响、设计和任务为实现追溯草案，未写人工批准字段。
- 业务实现位于 `business-repo` 同名分支。
- 本地 Go 验证已通过；Java 验证被 Maven Central 403 / GitHub Packages 401 依赖解析阻塞。
