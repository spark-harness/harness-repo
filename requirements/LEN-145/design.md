---
requirement_id: "LEN-145"
owner: "core"
status: "approved"
updated_at: "2026-07-01"
approved_by: "forest"
approved_at: "2026-07-01T22:42:35+08:00"
decision: "用户授权批准 LEN-145 设计文档，并继续任务拆分、实现、验证和 PR。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| BR2, AC1, AC2 | Add Spring Cloud Consul Config and `optional:consul:` to quote/origination | Aligns with applicant-api ConfigData model |
| BR3 | Keep Consul disabled by default in `application.yml`; enable in GitOps ConfigMap | Local tests do not require Consul |
| BR4, AC5 | Set per-env Consul prefix and `OTEL_RESOURCE_ATTRIBUTES` in GitOps | Supports `deployment.environment=dev-1/sta-1` |
| BR1, BR5, AC3, AC4 | Consul seed Job preserves existing endpoint/header and never commits real values | Prevents GitOps from clearing private OTLP values |
| AC1, AC2 | Add OpenTelemetry Spring Boot starter and standard OTLP config surface | Enables standard exporter without Sentry SDK |

## Summary

The solution makes `quote-api` and `origination-api` read startup configuration from Consul through Spring Boot ConfigData. GitOps enables Consul Config only in deployed environments and leaves local defaults safe for developer tests.

Sentry remains only an OTLP backend. The services use OpenTelemetry standard configuration and do not include Sentry SDK or Sentry-specific code.

## Affected Services

| Service | Change |
|---|---|
| quote-api | POM dependencies, `application.yml`, config model test |
| origination-api | POM dependencies, `application.yml`, config model test |
| quote-api GitOps | ConfigMap, Deployment env, Consul seed Job, dev/sta overlays |
| origination-api GitOps | ConfigMap, Deployment env, Consul seed Job, dev/sta overlays |

## API / Contract Design

- API endpoints: no changes.
- HTTP/gRPC contracts: no changes.
- Protobuf: no changes.
- Generated contracts: no changes.

## Application Design

## Consul Config

Each service imports optional Consul Config:

```text
spring.config.import=optional:consul:
```

The service default config sets:

```text
spring.cloud.consul.enabled=false
spring.cloud.consul.config.enabled=false
spring.cloud.consul.config.format=yaml
spring.cloud.consul.config.name=<service>
spring.cloud.consul.config.data-key=config
```

GitOps sets runtime values:

```text
SPRING_CLOUD_CONSUL_ENABLED=true
SPRING_CLOUD_CONSUL_CONFIG_ENABLED=true
SPRING_CLOUD_CONSUL_CONFIG_PREFIX=spark/lendora/<env>
```

This maps service config to:

```text
spark/lendora/<env>/<service>/config
```

## OpenTelemetry

The services use `opentelemetry-spring-boot-starter`. Runtime config exposes:

```text
otel.traces.exporter
otel.traces.sampler
otel.traces.sampler.arg
otel.exporter.otlp.traces.protocol
otel.exporter.otlp.traces.endpoint
otel.exporter.otlp.traces.headers
otel.resource.attributes
```

GitOps commits only non-secret settings. Endpoint/header values stay in Consul and are preserved by the seed Job.

## GitOps Consul Seed

The seed Job writes the public YAML structure but first reads the existing Consul key. If the existing key contains `endpoint:` or `headers:`, the Job appends those exact values to the generated YAML before PUT.

This is not a complete YAML merge engine. It is a scoped persistence guard for the private OTLP lines required by LEN-145.

## Data / Config / Permission

- Data: no database changes.
- Config: Consul Config enabled in dev-1 / sta-1, default disabled locally.
- Secrets: no real Sentry value in Git; DB password Secret injection remains.
- Permissions: no user permission changes.

## Observability

- `service.name=quote-api` and `service.name=origination-api`.
- `deployment.environment=dev-1` or `sta-1` from `OTEL_RESOURCE_ATTRIBUTES`.
- Trace export uses standard OTLP HTTP/protobuf.
- Logs and verification output must redact endpoint headers and public keys.

## Testing Strategy

- Config model tests assert Consul import and OTLP config surface.
- POM tests assert Consul Config and OpenTelemetry starter dependencies.
- Service tests run for quote/origination.
- Kustomize build validates dev-1 and sta-1 overlays.
- Runtime smoke after deployment verifies real traces in Sentry or OTLP receiver.

## Rollout And Rollback

- Roll out dev-1 first.
- Re-run Consul seed Job and confirm existing endpoint/header survives.
- Restart Deployments and query trace.
- Roll out sta-1 after dev evidence.
- Rollback by reverting GitOps and business image changes; existing Consul private values can remain.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Seed script misses unusually formatted YAML | Runtime values are written in the known `endpoint:` / `headers:` shape; verification checks redacted output | core |
| OpenTelemetry starter changes startup classpath | Narrow config tests and service tests run before delivery | core |
| Consul key missing private values in a new env | Service starts with exporter config but cannot export to Sentry until operator writes private values | core |
