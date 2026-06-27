---
requirement_id: "LEN-131"
evidence_type: "runtime-smoke"
verified_by: "Codex"
verified_at: "2026-06-28T02:54:35+08:00"
status: "warn"
---

# Runtime Smoke

## Scope

本证据覆盖 vincent-k3s / lendora-sta 的 quote-api 实际部署、访问、DB 写入、k8s Service 和 Consul 发现。

由于当前集群缺少 Argo CD，本次 runtime smoke 使用已经渲染通过的 GitOps manifest 直接 `kubectl apply` 到集群。该操作用于验证运行时可用性，不替代最终 GitOps controller 同步能力。

## Runtime Inputs

| Item | Value |
|---|---|
| Cluster | `vincent-k3s` |
| Kubeconfig | `~/.kube/vincent-k3s.yaml` with `GODEBUG=tlsmlkem=0` |
| Namespace | `lendora-sta-quote-api` |
| Image | `ghcr.io/spark-harness/quote-api@sha256:551b29fdf5f31be37ed962890e5d61b89163d27d2810087a041cd7074124df63` |
| Runtime Secret | `lendora-sta-quote-api/quote-api-runtime` with keys `db-password`, `otlp-traces-headers` |
| DB Init Secret | `lendora-sta-postgres/quote-api-runtime` with keys `db-password`, `otlp-traces-headers` |
| Image Pull Secret | `lendora-sta-quote-api/ghcr-pull` |

Secret value 不写入仓库或证据。

## Commands And Results

| Command | Result |
|---|---|
| `kubectl apply -f clusters/lendora-sta/namespaces.yaml` | PASS；`lendora-sta-quote-api` created，`lendora-sta-fides-bff` label configured |
| Copy `ghcr-pull` from `lendora-sta-applicant-api` to `lendora-sta-quote-api` | PASS |
| Create `quote-api-runtime` secrets in `lendora-sta-quote-api` and `lendora-sta-postgres` | PASS；verified keys only |
| `kubectl kustomize apps/lendora-sta-dependencies/overlays/sta \| kubectl apply -f -` | PASS；`quote-postgres-init` created |
| `kubectl -n lendora-sta-postgres wait --for=condition=complete job/quote-postgres-init --timeout=180s` | PASS；job complete |
| `kubectl kustomize apps/quote-api/overlays/lendora-sta \| kubectl apply -f -` | PASS；ServiceAccount、ConfigMaps、Service、Deployment、Consul config Job、NetworkPolicy created |
| `kubectl -n lendora-sta-quote-api rollout status deploy/quote-api --timeout=240s` | PASS；deployment successfully rolled out |

## Smoke Evidence

| Check | Evidence |
|---|---|
| Pod Ready | `deployment.apps/quote-api` READY `1/1`; pod `quote-api-57659c65c6-5pwz6` READY `1/1`, restart `0` |
| k8s Service | `service/quote-api` ClusterIP `10.43.255.128`, port `80/TCP`; EndpointSlice points to pod `10.42.0.244:8080` |
| `/ready` | From `lendora-sta-fides-bff` debug pod: `{"service":"quote-api","dependencies":{"consul":"UP","postgresql":"UP"},"status":"READY"}` |
| Quote create | `POST /api/v1/pricing/quotes` returned `quote_71b0fe6f-c274-4a8f-b4a6-028c92a6d677`, monthly `8560.75`, APR `0.0520`, totalPayable `102729.00` |
| DB write | PostgreSQL `quote` DB row: `quote_71b0fe6f-c274-4a8f-b4a6-028c92a6d677|len131-final-applicant|100000.00|12|33333333333333333333333333333333` |
| Consul discovery | Consul health API returned service `quote-api`, address `quote-api.lendora-sta-quote-api.svc.cluster.local`, port `80`, checks `passing`, `passing` |
| Network boundary | A temporary curl pod from `lendora-sta-quote-api` namespace could not reach quote-api due to ingress NetworkPolicy; access from `lendora-sta-fides-bff` namespace succeeded because it has label `lendora.io/quote-api-client=true` |

## Environment Warning

AC3 requires Argo CD Application Healthy/Synced. Live cluster check showed:

- `kubectl get ns argocd` -> `NotFound`
- Argo CD CRDs `applications.argoproj.io` and `appprojects.argoproj.io` are absent

因此本票运行时功能已验证成功，但 GitOps controller 同步健康状态在当前 vincent-k3s 环境不可验证。

