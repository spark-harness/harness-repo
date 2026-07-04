# LEN-188 fides-bff 调 quote-api gRPC 硬切

本目录记录 `LEN-188` 的需求、影响分析、设计、任务和验证证据。

目标是让 `fides-bff` 的报价流程只通过 gRPC 调用 `quote-api`。`fides-web -> fides-bff` 的外部 HTTP 入口继续保留；`fides-bff -> origination-api` 的硬切属于 `LEN-192`。

## 文件

- `requirement.md`：需求语义、业务规则和验收标准。
- `impact-analysis.md`：BFF、Go SDK、GitOps、Tracing 和回滚影响。
- `design.md`：gRPC QuoteClient、配置替换和验证方案。
- `tasks.json`：可验证任务切片。
- `evidence/`：Go 测试、GitOps 渲染、配置清理和 trace 证据。
- `gates/`：Janus gate JSON。
