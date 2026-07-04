---
requirement_id: "LEN-158"
analyst: "forest"
status: "approved"
updated_at: "2026-07-04"
approved_by: "forest"
approved_at: "2026-07-04T16:29:45+08:00"
decision: "用户在 2026-07-04 授权 Agent 批准任务执行中所有请求；批准 LEN-158 service repo readiness，涉及 harness-repo、business-repo、idl-repo、gitops-repo；idl-repo 仅用于 fides-bff/applicant-api proto readiness。"
idl_impact: "no"
idl_impact_reason: "未声明 protobuf IDL 或外部契约影响。"
---

# Impact Analysis

## Summary

本需求将 Lendora dev-1 / sta-1 中五个目标服务的运行配置从 Consul KV 和人工 Secret 迁移到 Vault/VSO 同步的 Kubernetes Secret。影响面覆盖 GitOps 平台资源、业务服务配置读取代码、环境变量命名、Secret 权限、rollout 验证和 Consul KV bootstrap 清理。

## Affected Domains

- 平台配置：VSO controller、CRD、VaultConnection、VaultAuth、ArgoCD diff ignore。
- 前端体验：fides-web runtime config 从 Consul 切到强类型 server env。
- BFF：fides-bff 回归 Kratos file/env source，删除自定义 Consul config loader。
- 后端服务：Java 服务移除 Spring Cloud Consul Config，保留 Consul 注册发现。
- GitOps 交付：dev-1 / sta-1 的 Deployment、VaultStaticSecret、ConfigMap、Job 和 kustomization 需要调整。
- 运行验证：Secret 同步、rollout、readiness、smoke 和 trace 串联必须按环境串行验证。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides | `{business-repo}/apps/fides-web`, `{gitops-repo}/apps/fides` | 强类型 env、public runtime config 白名单、VSO Secret envFrom | No |
| fides-bff | `{business-repo}/apps/fides-bff`, `{gitops-repo}/apps/fides-bff`, `{idl-repo}/vesta/lendora/fides-bff/v1` | 删除 Consul KV config loader，使用 VSO Secret envFrom；同分支 proto readiness 检查 | Yes, not changed |
| applicant-api | `{business-repo}/apps/applicant-api`, `{gitops-repo}/apps/applicant-api`, `{idl-repo}/vesta/lendora/applicant/v1` | 移除 Spring Cloud Consul Config，补齐 env placeholder；同分支 proto readiness 检查 | Yes, not changed |
| quote-api | `{business-repo}/apps/quote-api`, `{gitops-repo}/apps/quote-api` | 移除 Spring Cloud Consul Config，使用 env/Vault | No |
| origination-api | `{business-repo}/apps/origination-api`, `{gitops-repo}/apps/origination-api` | 移除 Spring Cloud Consul Config，使用 env/Vault | No |
| Vault/VSO platform | `{gitops-repo}/apps/vault-secrets-operator`, `{gitops-repo}/apps/vault-platform` | 安装 VSO，声明共享 VaultConnection/VaultAuth 模板 | No |

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: no.
- Contract repo: none.
- Proto files: none.
- Buf module: unchanged.
- Buf config version: v2.
- Required buf checks: not required because protobuf is unchanged.
- Breaking baseline: not applicable.
- Compatibility risk: runtime configuration source changes only. HTTP/protobuf APIs remain unchanged.

## Data Impact

- Database schema: none.
- Data migration: none.
- Backfill: none.
- Cache: none.
- Runtime storage: Vault paths become the source for runtime configuration; VSO writes Kubernetes Secrets.
- Existing Kubernetes Secret migration: key names must be recorded and migrated without writing values to Git.

## Config / Permission / Observability Impact

- Config: five services move from Consul KV config bootstrap to VSO Secret `envFrom`.
- Config: non-sensitive stable values may remain in ConfigMap; sensitive and environment-specific values move to Vault runtime paths.
- Permission: each service needs a minimal Vault policy and role scoped to its own path.
- Permission: service namespace VaultAuth must not grant cross-service read.
- Metrics: no metric name change expected.
- Logs: startup logs must not print secret values.
- Tracing: OTLP/Sentry endpoint/header values remain secret material and are injected by env when configured.
- Events: no domain event change.
- Service discovery: Consul registration/discovery remains in place and must not be removed.

## Rollout And Rollback

- Gray release: platform/Vault first, then code changes, then GitOps dev-1 by service order, then sta-1.
- Service order: quote-api, origination-api, applicant-api, fides-bff, fides-web.
- Kill switch: revert service Deployment `envFrom` and VSO resources to prior GitOps revision, then restart Pods.
- Rollback steps: revert GitOps PR or commit, sync Argo app, confirm old configuration source is restored, keep Consul service discovery unchanged.
- Cleanup: delete Consul KV bootstrap only after dev-1 and sta-1 pass smoke and logs prove services no longer read Consul KV.

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| VSO CRD or controller is not ready | Business VaultStaticSecret cannot sync | Apply LEN-160 first and verify controller Ready before service resources | forest |
| Vault path misses an existing key | Service starts with missing config | Record existing Secret key set before migration; fail fast on required env | forest |
| fides-web exposes non public key | Sensitive config leaks to browser | Keep client schema empty and whitelist `/api/runtime-config` output | forest |
| Java service loses Consul registration | Cross-service calls fail | Remove Consul Config only; preserve registration properties and classes | forest |
| GitOps cleanup deletes service discovery resources | Runtime outage | Explicitly exclude `lendora-shared-consul`, service registration, and NetworkPolicy | forest |
| sta-1 is switched before dev-1 proof | Wider blast radius | Enforce serial environment gate in tasks and evidence | forest |
