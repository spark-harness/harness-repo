---
requirement_id: "LEN-158"
owner: "forest"
status: "approved"
updated_at: "2026-07-04"
approved_by: "forest"
approved_at: "2026-07-04T16:27:24+08:00"
decision: "用户在 2026-07-04 授权 Agent 批准任务执行中所有请求；批准 LEN-158 design。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, AC1 | D1：GitOps 声明 VSO controller/CRD、VaultConnection、VaultAuth 和 ArgoCD ignore 规则。 | LEN-160。 |
| R2, AC2 | D2：每个环境每个服务使用独立 Vault runtime path，Vault key 等于最终 env 名。 | LEN-161。 |
| R3, AC3 | D3：fides-bff 删除自定义 Consul config loader，使用 Kratos file/env source。 | LEN-163。 |
| R4, AC4 | D4：fides-web 建立 `src/config/env.ts`，业务代码禁止直接读 `process.env`。 | LEN-166。 |
| R5, AC5 | D5：Java 服务删除 Spring Cloud Consul Config，保留 ConsulServiceRegistration。 | LEN-169、LEN-170。 |
| R6, AC6 | D6：GitOps 为服务声明 VaultStaticSecret 和 Deployment `envFrom`，删除 Consul KV bootstrap。 | LEN-164、LEN-167、LEN-171。 |
| R7, AC7, AC8, AC9, AC10 | D7：dev-1 先切换并验证，sta-1 后切换，最后清理旧链路。 | LEN-173、LEN-174。 |

## Summary

方案分为平台底座、业务代码、GitOps 接入、环境验证四层。平台层先让 VSO 能从 Vault 同步 Secret；代码层让服务通过框架原生 file/env 和强类型 env 读取配置；GitOps 层把 VaultStaticSecret 输出注入 Deployment；验证层按 dev-1 到 sta-1 串行证明服务不再读取 Consul KV。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| fides-web | 新增强类型 env 入口，改 runtime-config/proxy/smoke 读取方式，GitOps 使用 `fides-runtime` | 防止浏览器暴露非 public Vault key |
| fides-bff | 删除 Consul config loader，镜像内置 configs，GitOps 使用 `fides-bff-runtime` | 回归 Kratos 配置模型 |
| quote-api | 删除 Spring Cloud Consul Config 依赖和 import，GitOps 使用 `quote-api-runtime` | env/Vault 成为运行配置来源 |
| origination-api | 删除 Spring Cloud Consul Config 依赖和 import，GitOps 使用 `origination-api-runtime` | env/Vault 成为运行配置来源 |
| applicant-api | 删除 Spring Cloud Consul Config，补齐 JDBC/Redis/token/tracing env placeholder，GitOps 使用 `applicant-api-runtime` | prod profile 仍 fail fast |

## API / Contract Design

- Protobuf IDL required: no.
- Proto files: none.
- Buf module: unchanged.
- Buf config version: v2.
- Generated outputs: none.
- Breaking check baseline: not applicable.
- Compatibility strategy: public HTTP and protobuf contracts remain unchanged; configuration keys are runtime environment contracts.

## Data / Config / Permission

- Data model: no database or cache schema change.
- Config:
  - mount `kv`, path `spark/lendora/{env}/applicant-api/runtime` -> `applicant-api-runtime`
  - mount `kv`, path `spark/lendora/{env}/quote-api/runtime` -> `quote-api-runtime`
  - mount `kv`, path `spark/lendora/{env}/origination-api/runtime` -> `origination-api-runtime`
  - mount `kv`, path `spark/lendora/{env}/fides-bff/runtime` -> `fides-bff-runtime`
  - mount `kv`, path `spark/lendora/{env}/fides-web/runtime` -> `fides-runtime`
- Config: Deployment keeps non-sensitive ConfigMap `envFrom` where useful and adds Secret `envFrom`.
- Config: remove `CONFIG_CONSUL_*`, `FIDES_RUNTIME_CONFIG_CONSUL_*`, and `SPRING_CLOUD_CONSUL_CONFIG_*` after service migration.
- Permission: each service uses a namespace-local VaultAuth bound to a service role with path-scoped read.
- Permission: ArgoCD never stores Vault secret values.

## Observability

- Logs: startup may log config source and missing key names, never values.
- Metrics: no new metric required for config migration.
- Tracing: keep existing OTEL env names and ensure BFF/backend trace chain still works after env migration.
- Events: none.

## Rollout And Rollback

- Gray release: merge platform resources first; merge code and publish images; prepare GitOps resources; apply dev-1 by service order; apply sta-1 after dev-1 proof.
- Service order: quote-api, origination-api, applicant-api, fides-bff, fides-web.
- Kill switch: revert GitOps Secret injection to previous config source and sync Argo; use previous image if code-level config reader regresses.
- Rollback: keep Consul KV bootstrap until sta-1 smoke passes; old bootstrap is removed only at LEN-174.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Platform and service resources are merged out of order | Model tasks with explicit dependencies and keep VSO/Vault path before service VaultStaticSecret | forest |
| Parallel code changes diverge on env names | Define Vault key equals final env name and record service Secret mapping in this design | forest |
| fides-web lint blocks `src/config/env.ts` itself | Configure ESLint exception for that file only | forest |
| Java tests rely on `optional:consul:` | Remove only assertions about Consul Config and preserve service registration tests | forest |
| Secret sync triggers Argo diff noise | Ignore `vso.secrets.hashicorp.com/restartedAt` only | forest |
