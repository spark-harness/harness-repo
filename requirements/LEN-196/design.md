---
requirement_id: "LEN-196"
owner: "forest"
status: "approved"
updated_at: "2026-07-05"
approved_by: "forest"
approved_at: "2026-07-05T09:08:32+08:00"
decision: "用户本轮明确授权批准 LEN-196 design；允许按 dev-1 先行、sta-1 后续、保留 health/readiness 和 lendora-shared-consul 的方案实施。"
---

# Design

## Requirement Traceability

| Requirement | Design Decision |
|---|---|
| R1, AC1 | D1：dev-1 先执行完整业务 smoke 和 live config 扫描。 |
| R2, AC2 | D2：sta-1 只在 dev-1 通过后执行同一验证。 |
| R3, R4, AC3, AC6 | D3：删除 quote-api 和 origination-api 的业务 HTTP adapter、exception handler 和对应 HTTP adapter tests。 |
| R5, AC5 | D4：GitOps NetworkPolicy 对业务 client namespace 只保留 gRPC 端口，Consul health/readiness 端口保留。 |
| R6, AC3 | D5：删除 quote-api、origination-api、applicant-api 和 fides-bff 的旧 Consul KV bootstrap Job。 |
| R7, R8 | D6：保留允许的 HTTP 边界，并在扫描证据中排除 health/readiness、BFF external HTTP、Consul API 和 OTLP HTTP。 |

## Summary

LEN-196 采用“先验证、再删除、再验证”的方式收尾。业务代码层删除已经无调用方的业务 HTTP controller。GitOps 层删除服务间 HTTP 访问面和旧 KV bootstrap。运行层按 dev-1、sta-1 顺序收集 smoke、config、NetworkPolicy 和 trace 证据。

## Affected Services

| Service | Change |
|---|---|
| quote-api | 删除 `QuoteHttpAdapter`、`QuoteHttpExceptionHandler` 和业务 HTTP adapter test；保留 `HealthHttpAdapter` 和 gRPC adapter。 |
| origination-api | 删除 `LoanApplicationHttpAdapter`、`LoanApplicationHttpExceptionHandler` 和业务 HTTP adapter test；保留 `HealthHttpAdapter` 和 gRPC adapter。 |
| applicant-api | 不改业务代码；GitOps 删除业务 client namespace HTTP ingress 和旧 Consul KV bootstrap。 |
| fides-bff | 不改业务代码；验证外部 HTTP 保留、内部后端 gRPC，并删除旧 runtime-config Consul bootstrap。 |

## API / Contract Design

- Protobuf 不变。
- BFF 外部 HTTP 不变。
- quote-api 和 origination-api 不再提供内部业务 HTTP API。
- health/readiness HTTP 保持为运行时接口。

## Application Design

- 删除业务 HTTP adapter 类和只覆盖这些 adapter 的测试。
- 不删除 use case、domain、repository、gRPC adapter。
- 不删除 Java service 的 HTTP server，因为 health/readiness 仍需要。
- 不改 BFF 服务层或前端路由。

## Config / Permission

- GitOps base 和 dev-1 / sta-1 overlay 的 NetworkPolicy 中，业务 client namespace 只允许访问 `9090`。
- Consul namespace 继续允许访问 health/readiness 端口。
- 删除 `apps/{quote-api,origination-api,applicant-api}/base/consul-config.yaml` 和 `apps/fides-bff/overlays/{dev-1,sta-1}/runtime-config-consul.yaml` 这类旧 KV bootstrap Job。
- 保留 ConfigMap 中用于 Consul 注册和 health check 的配置。

## Observability

- 保留 OTLP exporter 和 trace propagation。
- Evidence 中记录 dev-1 / sta-1 smoke 的业务 ID、Argo revision、image digest、config scan 和 trace/log 结论。
- 扫描输出必须说明允许项，避免把 OTLP HTTP、Consul HTTP API 或 health/readiness 误报为业务 HTTP。

## Testing Strategy

- business-repo:
  - 先运行 targeted tests，确认删除前 HTTP adapter tests 是待删除目标。
  - 删除后运行 quote-api、origination-api 单元测试和相关 Java CI。
  - 运行业务 HTTP adapter grep，确认只剩 health/readiness HTTP adapter。
- gitops-repo:
  - `kubectl kustomize` dev-1 / sta-1 overlays。
  - grep 渲染结果，确认 client namespace 不再暴露 80/8080 业务 ingress，旧 Consul KV bootstrap Job 不再存在。
- runtime:
  - dev-1 smoke 通过后再 sta-1。
  - 验证 live ConfigMap、NetworkPolicy、Argo app health 和 trace/log evidence。

## Rollout And Rollback

- 先合并并发布 business-repo 镜像，再清理 GitOps 访问面。
- dev-1 失败时不推进 sta-1。
- 回滚优先使用 GitOps image digest 或 NetworkPolicy commit 回退。
- 业务 HTTP adapter 删除失败时回滚 business-repo commit，不扩大到 IDL 或 BFF 外部 HTTP。

## Risks

| Risk | Mitigation |
|---|---|
| 删除业务 HTTP adapter 后编译失败 | 先删除对应 tests，再跑 Java tests 和 CI |
| NetworkPolicy 误阻断 health/readiness | Consul namespace health/readiness 端口保留 |
| live trace 不可查 | 用 smoke、config、logs 和 Argo state 形成等效 evidence，并记录 trace 缺口 |
