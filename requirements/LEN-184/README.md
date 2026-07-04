# LEN-184 origination-api 调 quote-api gRPC 硬切

本目录记录 `LEN-184` 的需求、影响分析、设计、任务和验证证据。

目标是让 `origination-api` 在创建和更新贷款申请时只通过 gRPC 读取 `quote-api` 报价。`origination-api` 自身 HTTP 入站、Java health/readiness HTTP 和 `lendora-shared-consul` 继续保留。

## 文件

- `requirement.md`：需求语义、业务规则和验收标准。
- `impact-analysis.md`：服务、配置、NetworkPolicy、Tracing 和回滚影响。
- `design.md`：GrpcQuoteGateway、配置替换、GitOps 和验证方案。
- `tasks.json`：可验证任务切片。
- `evidence/`：Maven、GitOps 渲染、trace 搜索和配置清理证据。
- `gates/`：Janus gate JSON。
