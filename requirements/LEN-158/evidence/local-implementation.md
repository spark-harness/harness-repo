---
requirement_id: "LEN-158"
evidence_type: "local-implementation"
status: "partial-pass"
updated_at: "2026-07-04T18:20:45+08:00"
owner: "forest"
---

# Local Implementation Evidence

## Scope

本证据覆盖 LEN-160、LEN-161 的 GitOps 与 live cluster 平台底座验证，覆盖 LEN-163、LEN-166、LEN-169、LEN-170 的本地实现与静态验证，并覆盖 LEN-164、LEN-167、LEN-171 的 GitOps 草案渲染。

不覆盖 LEN-173 / LEN-174 的 live dev-1、sta-1 rollout 和业务 smoke。环境切换仍必须串行执行。

## Implementation Summary

| Area | Result |
|---|---|
| VSO platform | 新增 VSO controller、VaultConnection、服务级 VaultAuth、service account 和 ArgoCD app/project 声明；live `VaultConnection` 指向 `http://vault.vault.svc.cluster.local:8200` 且 Ready。 |
| Vault runtime paths | GitOps 声明每个环境、每个服务的 VaultStaticSecret；Vault source key 使用最终 env 名；fides-web path 使用 `spark/lendora/{env}/fides-web/runtime`；目标 Secret 设置 `excludeRaw: true`。 |
| Vault server | GitOps 新增 standalone Vault + PVC；live cluster 已初始化、解封，并把 root/unseal 材料保存为 cluster Secret，不进入 Git。 |
| Vault policies/roles | GitOps 新增 bootstrap Job；live cluster 已启用 `kv`、Kubernetes auth，并创建 dev-1 / sta-1 各服务 path-scoped policy 和 role。 |
| Vault value migration | live cluster 已从现有 Kubernetes runtime Secret 迁移到 Vault path，迁移只使用最终 env key，不保留旧 key 兼容。 |
| fides-bff | 删除 Consul KV config loader，回归 Kratos file/env source；保留 Consul 服务注册/发现配置。 |
| fides-web | 新增 `src/config/env.ts`，限制散落 `process.env`；删除 Consul runtime config source。 |
| Java services | quote-api、origination-api、applicant-api 移除 Spring Cloud Consul Config；保留 ConsulServiceRegistration。 |
| GitOps service injection | 目标 Deployment 使用 non-secret ConfigMap `envFrom` 加 VSO runtime Secret `envFrom`。 |
| Consul KV bootstrap | 目标服务代码不再读取 Consul KV；GitOps bootstrap Job 暂保留，等 T5 dev-1 / sta-1 验证后再删除。 |
| Hard cut | 服务 runtime Secret 不保留旧兼容 key；共享 PostgreSQL init Job 保留原共享命名空间 Secret key，避免把共享初始化和服务 runtime Secret 耦合。 |

## Verification Commands

| Repository | Command | Result |
|---|---|---|
| business-repo/apps/fides-web | `pnpm vitest run src/config/env.test.ts src/infrastructure/runtime-config/runtime-config.test.ts src/infrastructure/bff/proxy-config.test.ts` | PASS, 12 tests |
| business-repo/apps/fides-web | `pnpm lint` | PASS, 1 existing warning in `mock-otp-auth-gateway.ts` |
| business-repo/apps/fides-web | `pnpm test` | PASS, 95 passed, 1 skipped |
| business-repo/apps/fides-web | `pnpm lint:deps` | PASS |
| business-repo/apps/fides-web | `FIDES_BFF_BASE_URL=http://127.0.0.1:8001/api/v1 pnpm build` | PASS |
| business-repo/apps/fides-bff | `go test ./cmd/fides-bff -run TestLoadBootstrap -count=1` | PASS |
| business-repo/apps/fides-bff | `go test ./... -count=1` | PASS |
| business-repo/apps/fides-bff | `go vet ./...` | PASS |
| business-repo/apps/fides-bff | `go build -buildvcs=false ./cmd/fides-bff` | PASS |
| business-repo/apps/quote-api | `mvn -q test spotless:check checkstyle:check spotbugs:check` | PASS |
| business-repo/apps/origination-api | `mvn -q test spotless:check checkstyle:check spotbugs:check` | PASS |
| business-repo/apps/applicant-api | `mvn -q test spotless:check checkstyle:check spotbugs:check` | PASS |
| gitops-repo | `/usr/local/bin/kubectl kustomize` for VSO platform, lendora clusters, shared dependencies, and dev-1 / sta-1 target app overlays | PASS |
| live cluster | `kubectl apply -k platform/vault-server`; `vault operator init`; `vault operator unseal`; `kubectl apply -k platform/vault-bootstrap`; `kubectl apply -k platform/vault-secrets-operator`; `kubectl apply -k platform/vault-runtime-auth` | PASS |
| live cluster | `kubectl get vaultconnection -A`; `kubectl get vaultauth -A` | PASS, `default` and 10 service `VaultAuth` are Healthy/Ready |
| live cluster | temporary `VaultStaticSecret` probe for `spark/lendora/dev-1/quote-api/runtime` into `len158-vso-probe` | PASS, synced only `QUOTE_JDBC_PASSWORD`, `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`, `OTEL_EXPORTER_OTLP_TRACES_HEADERS`; probe deleted |
| gitops-repo rendered output | `rg -n "SPRING_CLOUD_CONSUL|CONFIG_CONSUL_|FIDES_RUNTIME_CONFIG_CONSUL|FIDES_RUNTIME_CONFIG_JSON|fides-bff-config|NEXT_PUBLIC_" /tmp/len158-*.yaml` | PASS, no matches |
| business-repo | `git diff --check` | PASS |
| gitops-repo | `git diff --check` | PASS |
| harness-repo | `git diff --check` | PASS |
| harness-repo | `janus gate validate requirements/LEN-158/gates/*.gate.json` | PASS |
| harness-repo | `janus requirement status LEN-158` | PASS, stage 4.4; merge-readiness missing |

## Not Completed

- 未 apply 到 live dev-1。
- 未执行 dev-1 rollout、业务 smoke、trace 验证。
- 未 apply 到 live sta-1。
- 未执行 sta-1 rollout、业务 smoke、trace 验证。
- 未创建 merge-readiness gate。
- 未创建、推送或合并 PR。

## Residual Risk

- 新增 Vault server 采用 standalone file storage，重启后需要使用 cluster 内 `vault-unseal-key` 解封；该材料未进入 Git。
- VSO controller remote base 渲染存在 upstream kustomize deprecation warning，不影响当前渲染结果。
