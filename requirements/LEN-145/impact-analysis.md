---
requirement_id: "LEN-145"
owner: "core"
status: "approved"
updated_at: "2026-07-01"
approved_by: "forest"
approved_at: "2026-07-01T22:43:54+08:00"
decision: "用户授权批准 LEN-145 服务仓库检查；本需求涉及 harness-repo、business-repo、gitops-repo，不涉及 IDL。"
---

# Impact Analysis

## Summary

LEN-145 影响两个 Java 服务和对应 GitOps 配置：`quote-api`、`origination-api`、Consul seed Job、dev-1 / sta-1 overlays。

不涉及 IDL、数据库 schema、业务 API 或前端页面。

## Affected Domains

| Domain | Impact |
|---|---|
| pricing | `quote-api` 配置读取和 tracing 导出 |
| applicant | `origination-api` 配置读取、quote 下游地址配置和 tracing 导出 |
| platform/runtime | Consul KV seed、Argo CD 同步、运行时私密值持久性 |

## Affected Services And Repos

| Repo | Path | Impact |
|---|---|---|
| business-repo | `apps/quote-api` | POM、`application.yml`、配置模型测试 |
| business-repo | `apps/origination-api` | POM、`application.yml`、配置模型测试 |
| gitops-repo | `apps/quote-api` | ConfigMap、Deployment、Consul seed Job、dev/sta overlays |
| gitops-repo | `apps/origination-api` | ConfigMap、Deployment、Consul seed Job、dev/sta overlays |
| harness-repo | `requirements/LEN-145` | lifecycle traceability |

## Upstream / Downstream

- `fides-bff` 是 `quote-api` 与 `origination-api` 的上游消费者。
- `origination-api` 下游调用 `quote-api`。
- 本需求不改变调用协议，只改变启动期配置与 tracing 导出。

## API And Protobuf Contract Impact

- Protobuf IDL required: no.
- Proto files: no changes.
- Buf module/config: no changes.
- Generated contract repos: no changes.
- Compatibility risk: none for business contracts.

## Data, Migration, Cache, Runtime Storage

- Database schema: no changes.
- Redis/cache: no changes.
- Runtime storage: Consul KV remains the runtime configuration store for non-Git private OTLP values.

## Config, Permission, Observability

## Config

- Add Spring Cloud Consul Config dependency and `optional:consul:` import to quote/origination.
- Add standard OTLP endpoint/header/sampler/resource attribute config surface.
- GitOps ConfigMap enables Spring Cloud Consul Config and sets per-env Consul prefix.
- GitOps no longer injects empty OTLP endpoint env that would override Consul.
- Consul seed Job preserves existing `otel.exporter.otlp.traces.endpoint` and `headers` when rewriting the service config key.

## Permission

- No user permission changes.
- Pod access to Consul remains network-policy and service DNS based.
- K8s DB password Secret remains unchanged.

## Observability

- Tracing uses OpenTelemetry Spring Boot instrumentation.
- `service.name` is stable: `quote-api`, `origination-api`.
- `deployment.environment` comes from runtime env attributes.
- Logs and docs must not print real Sentry values.

## Rollout And Rollback

## Rollout

1. Merge business and GitOps changes.
2. Sync dev-1 first.
3. Confirm Consul KV still contains redacted endpoint/header after seed Job.
4. Restart quote/origination.
5. Trigger smoke flow and query trace by service/env.
6. Promote to sta-1 after dev evidence.

## Rollback

- Roll back business image to previous digest if startup fails.
- Roll back GitOps config if Consul Config import causes unexpected startup behavior.
- Existing private Consul values can remain; old images ignore them.

## Risks And Mitigations

| Risk | Mitigation |
|---|---|
| Consul Config enabled in local tests causes external dependency | Default `spring.cloud.consul.enabled=false`; k8s ConfigMap enables it explicitly |
| GitOps seed overwrites private OTLP values | Seed script reads existing key and appends existing endpoint/header before PUT |
| Empty env overrides Consul endpoint | Remove empty `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` from ConfigMap |
| Real Sentry values leak into Git | Only commit property names, placeholders and merge-safe script |
