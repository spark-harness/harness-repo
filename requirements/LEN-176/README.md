# LEN-176 quote-api gRPC 硬切

本目录记录 `LEN-176` 的需求、影响分析、设计、任务和验证证据。

目标是让 `quote-api` 提供内部 gRPC 报价服务，并移除自身业务 HTTP 入口。健康检查 HTTP 继续保留，供 Kubernetes readiness/liveness 和 Consul 健康检查使用。

## 文件

- `requirement.md`：需求语义、业务规则和验收标准。
- `impact-analysis.md`：服务、契约、生成物、配置和运行影响。
- `design.md`：IDL、Java 入站 adapter、GitOps 和验证方案。
- `tasks.json`：可验证任务切片。
- `evidence/`：Buf、Maven、GitOps 渲染和清理检查证据。
- `gates/`：Janus gate JSON。
