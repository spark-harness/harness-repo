---
requirement_id: "LEN-158"
evidence_type: "local-implementation"
status: "pass"
updated_at: "2026-07-04T19:46:18+08:00"
owner: "forest"
---

# Local Implementation Evidence

## Scope

本证据覆盖 LEN-160、LEN-161 的 GitOps 与 live cluster 平台底座验证，覆盖 LEN-163、LEN-166、LEN-169、LEN-170 的本地实现与静态验证，覆盖 LEN-164、LEN-167、LEN-171 的 GitOps 合并，并覆盖 LEN-173、LEN-174 的 dev-1 / sta-1 串行切换、rollout、smoke 和旧 Consul KV bootstrap 清理。

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
| Consul KV bootstrap | 服务级 Consul KV bootstrap Job/ConfigMap 已从 GitOps runtime app overlays 删除，并已从 dev-1 / sta-1 live namespace prune。 |
| Hard cut | 服务 runtime Secret 不保留旧兼容 key；dev-1 / sta-1 runtime Secrets 只包含最终 env key。 |
| PR merge | business-repo PR #45、gitops-repo PR #39/#40/#41 已合并；harness-repo PR #49 等待本证据和 merge-readiness。 |

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
| business-repo PR #45 | `gh pr view 45 --repo spark-harness/business-repo` | MERGED, merge commit `d5b02f259cd5a46a0322917ff1f709f476a5b5da` |
| business-repo image release | Argo workflow `business-image-release-d5b02f259cd5` and GitHub status `spark/business-image-release` | Succeeded; dev-1 image digests promoted |
| gitops-repo PR #39 | `gh pr view 39 --repo spark-harness/gitops-repo` | MERGED, VSO runtime config, merge commit `32ddf532cbee0721676c6db3ce9ae6709dc9d503` |
| gitops-repo PR #40 | `gh pr view 40 --repo spark-harness/gitops-repo` | MERGED, removed service-level Consul KV bootstrap, merge commit `d03da389f0a0891847a6bcedc0baa98e382cd73e` |
| gitops-repo PR #41 | `gh pr view 41 --repo spark-harness/gitops-repo` | MERGED, promoted sta-1 to LEN-158 images, merge commit `a50ee66816c62ad9ee15f41b1feb52df2f4dc165` |
| dev-1 Argo | `kubectl get app -n argocd lendora-dev-1-*` | Five runtime apps Synced/Healthy at `d03da389f0a0891847a6bcedc0baa98e382cd73e` |
| dev-1 VSO | `kubectl get vaultstaticsecret -n lendora-dev-1`; `kubectl get secret ... | jq '.data | keys'` | Five VaultStaticSecret resources Synced/Healthy/Ready; target Secrets contain only final env keys |
| dev-1 rollout | `kubectl rollout status -n lendora-dev-1 deploy/{quote-api,origination-api,applicant-api,fides-bff,fides}` | PASS |
| dev-1 smoke | curl from in-namespace smoke pod to quote/origination/applicant `/ready`, fides-bff `/api/v1/health`, fides `:3000/` | PASS, all HTTP 200 |
| dev-1 Consul cleanup | `kubectl get job,cm -n lendora-dev-1 | rg 'consul-config|runtime-config'` | PASS, no service-level bootstrap resources |
| sta-1 Argo | `kubectl get app -n argocd lendora-sta-1-*` | Five runtime apps Synced/Healthy at `a50ee66816c62ad9ee15f41b1feb52df2f4dc165` |
| sta-1 VSO | `kubectl get vaultstaticsecret -n lendora-sta-1`; `kubectl get secret ... | jq '.data | keys'` | Five VaultStaticSecret resources Synced/Healthy/Ready; target Secrets contain only final env keys |
| sta-1 rollout | `kubectl rollout status -n lendora-sta-1 deploy/{quote-api,origination-api,applicant-api,fides-bff,fides}` | PASS |
| sta-1 smoke | curl from in-namespace smoke pod to quote/origination/applicant `/ready`, fides-bff `/api/v1/health`, fides `:3000/` | PASS, all HTTP 200 |
| sta-1 Consul cleanup | `kubectl get job,cm -n lendora-sta-1 | rg 'consul-config|runtime-config'` | PASS, no service-level bootstrap resources |
| Consul discovery retained | `curl http://consul.lendora-shared-consul.svc.cluster.local:8500/v1/catalog/services` | PASS, dev-1 / sta-1 service registrations still present |

## Runtime Fixes During Cutover

- dev-1 `quote-api` initially failed DB auth because the old shared PostgreSQL init used a 45-byte `db-password` including a trailing newline while final env key migration produced a 44-byte `QUOTE_JDBC_PASSWORD`. The PostgreSQL `dev_1_quote` and `sta_1_quote` roles were reset to the final env value.
- sta-1 `quote-api` initially failed OTEL startup because the migrated Vault path had an empty `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`; the current sta Consul KV endpoint/headers were copied once into the sta Vault path, then VSO re-synced the final env Secret.

## Residual Risk

- 新增 Vault server 采用 standalone file storage，重启后需要使用 cluster 内 `vault-unseal-key` 解封；该材料未进入 Git。
- VSO controller remote base 渲染存在 upstream kustomize deprecation warning，不影响当前渲染结果。
- `lendora-shared-consul` 保留用于服务注册/发现，不应作为本需求清理对象。
