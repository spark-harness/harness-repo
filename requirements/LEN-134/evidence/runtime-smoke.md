---
requirement_id: "LEN-134"
evidence_type: "runtime-smoke"
verified_by: "Codex"
verified_at: "2026-06-28T05:32:24+08:00"
status: "warn"
---

# Runtime Smoke

## Scope

本证据覆盖 vincent-k3s / lendora-sta 的 origination-api 实际部署、访问、application DB 写入读取、k8s Service 和 Consul 发现。

由于当前集群缺少 Argo CD，本次 runtime smoke 使用已经渲染通过的 GitOps manifest 直接 `kubectl apply` 到集群。该操作用于验证运行时可用性，不替代最终 GitOps controller 同步能力。

## Runtime Inputs

| Item | Value |
|---|---|
| Cluster | `vincent-k3s` |
| Kubeconfig | `~/.kube/vincent-k3s.yaml` with `GODEBUG=tlsmlkem=0` |
| Namespace | `lendora-sta-origination-api` |
| origination-api Image | `ghcr.io/spark-harness/origination-api@sha256:94ea8d38c46341db044ede4ef6586e7cef96a2745d28fef2f114b5dd3d35880a` |
| quote-api Image | `ghcr.io/spark-harness/quote-api@sha256:52373dfe19fdee70bb3ef081b7c64b280804e5e6cc6de962b0d380f71e2b1915` |
| Runtime Secret | `lendora-sta-origination-api/origination-api-runtime` with keys `db-password`, `otlp-traces-headers` |
| DB Init Secret | `lendora-sta-postgres/origination-api-runtime` with keys `db-password`, `otlp-traces-headers` |
| Image Pull Secret | `lendora-sta-origination-api/ghcr-pull` |

Secret value 不写入仓库或证据。

## Commands And Results

| Command | Result |
|---|---|
| `kubectl apply -f clusters/lendora-sta/namespaces.yaml` | PASS; `lendora-sta-origination-api` created/configured, `lendora-sta-fides-bff` and `lendora-sta-origination-api` labels configured |
| Copy `ghcr-pull` from `lendora-sta-quote-api` to `lendora-sta-origination-api` | PASS |
| Create `origination-api-runtime` secrets in `lendora-sta-origination-api` and `lendora-sta-postgres` | PASS; verified keys only |
| `kubectl apply -k apps/lendora-sta-dependencies/overlays/sta` | PASS; `origination-postgres-init` created |
| `kubectl -n lendora-sta-postgres wait --for=condition=complete job/origination-postgres-init --timeout=180s` | PASS; job complete |
| `kubectl apply -k apps/origination-api/overlays/lendora-sta` | PASS; ServiceAccount, ConfigMaps, Service, Deployment, Consul config Job and NetworkPolicy created |
| `kubectl -n lendora-sta-origination-api rollout status deploy/origination-api --timeout=240s` | PASS; deployment successfully rolled out |
| `kubectl -n lendora-sta-quote-api set image deployment/quote-api quote-api=<fixed digest>` | PASS; quote-api internal quote boundary fixed for runtime smoke |

## Smoke Evidence

| Check | Evidence |
|---|---|
| Pod Ready | `deployment.apps/origination-api` READY `1/1`; pod `origination-api-74fcdf94cf-b2mkv` READY `1/1` |
| k8s Service | `service/origination-api` ClusterIP `10.43.16.248`, port `80/TCP`; endpoint `10.42.0.58:8080` |
| DB init | `job/origination-postgres-init` Complete `1/1`; logs show `CREATE ROLE` and `CREATE DATABASE` |
| `/ready` | From `lendora-sta-fides-bff` debug pod: `{"dependencies":{"consul":"UP","postgresql":"UP"},"status":"READY","service":"origination-api"}` |
| Quote create | `POST /api/v1/pricing/quotes` returned `quote_ab73b8fb-ea93-4b71-8733-7e7d692f5f16` |
| Quote internal get | `GET /internal/v1/pricing/quotes/{quoteId}` returned product `PIL`, amount `120000.00` |
| Draft create | `POST /api/v1/loan-applications` returned `app_bda9edac-b257-4ff9-a74b-112ab322b134`, status `draft`, currentStep `loan_request` |
| Draft get | `GET /api/v1/loan-applications/app_bda9edac-b257-4ff9-a74b-112ab322b134` returned same draft, amount `120000.00`, acceptedQuoteId `quote_ab73b8fb-ea93-4b71-8733-7e7d692f5f16` |
| DB write | PostgreSQL `origination` DB row: `app_bda9edac-b257-4ff9-a74b-112ab322b134|applicant_len134-20260628052844|draft|loan_request|120000.00|24|quote_ab73b8fb-ea93-4b71-8733-7e7d692f5f16` |
| Idempotency DB write | PostgreSQL `idempotency_records` row: `applicant_len134-20260628052844|create|app_bda9edac-b257-4ff9-a74b-112ab322b134` |
| Consul discovery | Consul health API returned service `origination-api`, address `origination-api.lendora-sta-origination-api.svc.cluster.local`, port `80`, service check `passing` with `/ready` output READY |
| Network boundary | `lendora-sta-origination-api` namespace has `lendora.io/quote-api-client=true` for quote validation; `lendora-sta-fides-bff` has `lendora.io/origination-api-client=true` for smoke access |

## Environment Warning

AC3 requires Argo CD Application Healthy/Synced. Live cluster check showed:

- `kubectl get ns argocd` -> `NotFound`
- Argo CD CRDs `applications.argoproj.io` and `appprojects.argoproj.io` are absent

因此本票运行时功能已验证成功，但 GitOps controller 同步健康状态在当前 vincent-k3s 环境不可验证。
