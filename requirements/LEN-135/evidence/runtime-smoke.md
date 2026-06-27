---
requirement_id: "LEN-135"
evidence_type: "runtime-smoke"
verified_by: "Codex"
verified_at: "2026-06-28T06:56:20+08:00"
status: "warn"
---

# Runtime Smoke

## Scope

本证据覆盖 vincent-k3s / lendora-sta 的 fides-bff quote/origination 下游配置、受保护 BFF 接口 smoke、下游 DB 写入、k8s Service 和 Consul 发现。

由于当前 vincent-k3s 缺少 Argo CD，本次 runtime smoke 使用已渲染通过的 GitOps manifest 和运行时 apply/rollout 状态验证功能，不声称 Argo CD Healthy/Synced。

## Runtime Inputs

| Item | Value |
|---|---|
| Cluster | `vincent-k3s` |
| Kubeconfig | `~/.kube/vincent-k3s.yaml` with `GODEBUG=tlsmlkem=0` |
| Namespace | `lendora-sta-fides-bff` |
| fides-bff Image | `ghcr.io/spark-harness/fides-bff@sha256:dad7a58f4305b2f41f0577602315c747487c8d0e2220a5b08d88c08167397f3a` |
| quote-api Image | `ghcr.io/spark-harness/quote-api@sha256:52373dfe19fdee70bb3ef081b7c64b280804e5e6cc6de962b0d380f71e2b1915` |
| origination-api Image | `ghcr.io/spark-harness/origination-api@sha256:94ea8d38c46341db044ede4ef6586e7cef96a2745d28fef2f114b5dd3d35880a` |
| Runtime Secret | `lendora-sta-fides-bff/fides-bff-runtime`, key `token-secret` exists; value not recorded |
| Trace ID | `4bf92f3577b34da6a3ce929d0e0e4736` |
| Applicant | `applicant_len135_20260628065400` |

## Commands And Results

| Command | Result |
|---|---|
| `kubectl get deploy fides-bff -n lendora-sta-fides-bff -o jsonpath='{image,readyReplicas/replicas}'` | PASS; image digest above, READY `1/1` |
| `kubectl get configmap fides-bff-config -n lendora-sta-fides-bff -o yaml` | PASS; contains quote/origination Consul discovery, empty `base_url`, 3s timeout, HMAC token mode and TTL |
| `kubectl get secret fides-bff-runtime -n lendora-sta-fides-bff` | PASS; Secret exists with `token-secret` key |
| `kubectl get ns -L lendora.io/quote-api-client,lendora.io/origination-api-client` | PASS; `lendora-sta-fides-bff` has both labels |
| `curl http://127.0.0.1:18080/api/v1/health` through port-forward | PASS; HTTP 200, `{"status":"ok","version":"dev"}` |
| Consul health API for `quote-api`, `origination-api`, `fides-bff` with `passing=true` | PASS; all services returned passing entries |

## Smoke Evidence

| Check | Evidence |
|---|---|
| Protected pricing quote | `POST /api/v1/pricing/quotes` via BFF returned HTTP 200 and `quote_c2662b9b-174a-41be-8348-b663e8c2901c` |
| Protected loan create | `POST /api/v1/loan-applications` via BFF returned HTTP 200 and `app_4f2d0819-f07c-4bfa-a547-3bc2bcb9cef0`, status `draft`, currentStep `loan_request` |
| Protected loan get | `GET /api/v1/loan-applications/app_4f2d0819-f07c-4bfa-a547-3bc2bcb9cef0` via BFF returned HTTP 200 with loan amount `120000.00`, term `24`, quoteId `quote_c2662b9b-174a-41be-8348-b663e8c2901c` |
| Protected loan patch | `PATCH /api/v1/loan-applications/app_4f2d0819-f07c-4bfa-a547-3bc2bcb9cef0` via BFF returned HTTP 200, status `draft`, currentStep `loan_request` |
| Quote DB write | PostgreSQL `quote.quotes` row: `quote_c2662b9b-174a-41be-8348-b663e8c2901c|applicant_len135_20260628065400|120000.00|24|debt_consolidation|4bf92f3577b34da6a3ce929d0e0e4736` |
| Application DB write | PostgreSQL `origination.loan_applications` row: `app_4f2d0819-f07c-4bfa-a547-3bc2bcb9cef0|applicant_len135_20260628065400|draft|loan_request|120000.00|24|debt_consolidation|quote_c2662b9b-174a-41be-8348-b663e8c2901c` |
| Idempotency DB write | PostgreSQL `origination.idempotency_records` rows include create key `len135-create-1782600840` and patch key `len135-patch-retry-1782600860` for the same application |
| Trace evidence | fides-bff access logs show pricing/create/get/patch with trace id `4bf92f3577b34da6a3ce929d0e0e4736` and HTTP 200; quote DB row stores the same trace id |
| Downstream validation boundary | A mismatched patch using the same quoteId with different loan terms returned HTTP 422 `amount_out_of_range`, proving downstream quote validation remained active |

## Consul Evidence

| Service | Address | Port | Status |
|---|---|---:|---|
| quote-api | `quote-api.lendora-sta-quote-api.svc.cluster.local` | 80 | passing |
| origination-api | `origination-api.lendora-sta-origination-api.svc.cluster.local` | 80 | passing |
| fides-bff | `fides-bff.lendora-sta-fides-bff.svc.cluster.local` | 8000 | passing |

## Environment Warnings

- Argo CD is not installed in vincent-k3s: `kubectl get ns argocd` returned NotFound, and CRDs `applications.argoproj.io` / `appprojects.argoproj.io` are absent. AC9 is satisfied by recording this WARN instead of claiming Healthy/Synced.
- The `lendora-sta-postgres/postgres` Service initially selected both `postgres-0` and historical `postgres-747897f985-vpkpf`; only `postgres-0` had the `quote` and `origination` databases. Runtime verification patched the Service selector to `statefulset.kubernetes.io/pod-name=postgres-0` before DB evidence was collected. This is an environment drift follow-up, not a LEN-135 GitOps change.
- Java downstream services did not emit request-level business logs for the smoke window. Header propagation is evidenced by fides-bff logs, quote DB `trace_id`, and existing code/tests that forward `x-applicant-id`, `traceparent`, `tracestate`, and `Idempotency-Key`.

