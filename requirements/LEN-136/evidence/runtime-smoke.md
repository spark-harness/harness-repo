# LEN-136 Runtime Smoke Evidence

## Scope

- Requirement: LEN-136
- Verified at: `2026-06-28T18:24:00+08:00`
- Cluster context: `vincent-k3s`
- Kubeconfig: `$HOME/.kube/vincent-k3s.yaml`
- Harness HEAD: `1284146`
- GitOps HEAD: `4f13f72`

## Result

PASS for runtime workloads, shared infrastructure, Consul KV / catalog, PostgreSQL databases, Redis logical DBs, Caddy config rollout, DNS records, TLS certificate issuance, and public HTTPS smoke for the four target hostnames.

## Cluster State

Read-only precheck:

```bash
GODEBUG=tlsmlkem=0 KUBECONFIG=$HOME/.kube/vincent-k3s.yaml kubectl config current-context
GODEBUG=tlsmlkem=0 KUBECONFIG=$HOME/.kube/vincent-k3s.yaml kubectl get ns
GODEBUG=tlsmlkem=0 KUBECONFIG=$HOME/.kube/vincent-k3s.yaml kubectl get crd applications.argoproj.io appprojects.argoproj.io
```

Result:

- Current context: `vincent-k3s`.
- Existing old namespaces included `lendora-sta-*`.
- Initial precheck found Argo CD CRDs were not installed: `applications.argoproj.io` and `appprojects.argoproj.io` returned NotFound.

Operational implication at first deployment: live verification used direct `kubectl apply` for rendered Kubernetes resources.

Argo CD was then installed and verified with fixed version `v3.4.4`.

Installation evidence:

```text
Release: argoproj/argo-cd v3.4.4
Published at: 2026-06-18T09:36:37Z
Manifest URL: https://raw.githubusercontent.com/argoproj/argo-cd/v3.4.4/manifests/install.yaml
Manifest SHA-256: b0f9119821f2e19b852c842b9cb235eb9c3ef1549554fbda6aa5904e8d440eae
Namespace: argocd
```

Install commands:

```bash
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -n argocd -f /tmp/argocd-v3.4.4/install.yaml
kubectl apply --server-side=true -n argocd -f /tmp/argocd-v3.4.4/install.yaml
```

Notes:

- Client-side apply created the main Argo CD control plane but failed the large `applicationsets.argoproj.io` CRD because the last-applied annotation exceeded Kubernetes annotation size.
- Server-side apply installed the CRDs, including `applicationsets.argoproj.io`.
- A later server-side apply reported field-manager conflicts for objects already created by client-side apply. This did not block runtime readiness.

Argo CD install verification:

```text
applications.argoproj.io: present
appprojects.argoproj.io: present
applicationsets.argoproj.io: present
argocd-application-controller: 1/1
argocd-applicationset-controller: 1/1
argocd-dex-server: 1/1
argocd-notifications-controller: 1/1
argocd-redis: 1/1
argocd-repo-server: 1/1
argocd-server: 1/1
```

Argo CD sync smoke:

```text
Application: argocd-smoke-guestbook
Source: https://github.com/argoproj/argocd-example-apps.git / guestbook
Result: Synced / Healthy
Workload: argocd-smoke/guestbook-ui 1/1 Running
Cleanup: smoke Application and argocd-smoke namespace deleted
```

LEN-136 Application verification:

- `lendora-shared`, `lendora-dev-1`, and `lendora-sta-1` AppProjects were created in `argocd`.
- 11 LEN-136 Applications were created in `argocd`.
- After GitOps commit `4f13f72` was pushed to `origin/feature/LEN-136-argocd-dev1-sta1`, all 11 Applications were temporarily patched to `targetRevision: feature/LEN-136-argocd-dev1-sta1` and hard refreshed.
- Argo CD generated manifests from the pushed branch successfully; no `ComparisonError` or manifest generation condition remained.
- Shared infrastructure and `dev-1` Applications reached `Synced / Healthy` with automated sync.
- `sta-1` Applications reached `OutOfSync / Healthy` with manual sync policy, which matches the required sta deployment behavior.
- After user verification, all 11 Applications were patched back to `targetRevision: master` and hard refreshed. They returned to `Unknown / Healthy` because remote `master` does not yet contain the LEN-136 paths. This is expected until the GitOps PR is merged.

## Applied Runtime Resources

Applied namespaces:

```bash
kubectl apply -f clusters/lendora-shared/namespaces/postgres.yaml
kubectl apply -f clusters/lendora-shared/namespaces/redis.yaml
kubectl apply -f clusters/lendora-shared/namespaces/consul.yaml
kubectl apply -f clusters/lendora-dev-1/namespaces/business.yaml
kubectl apply -f clusters/lendora-sta-1/namespaces/business.yaml
```

Created namespaces:

- `lendora-shared-postgres`
- `lendora-shared-redis`
- `lendora-shared-consul`
- `lendora-dev-1`
- `lendora-sta-1`

Copied existing bootstrap Secrets into the new namespace model:

- `postgres-auth` to `lendora-shared-postgres`
- `redis-auth` to `lendora-shared-redis`
- `applicant-api-runtime`, `quote-api-runtime`, `origination-api-runtime`, `fides-bff-runtime`, `ghcr-pull` to both `lendora-dev-1` and `lendora-sta-1`
- DB runtime Secrets also copied to `lendora-shared-postgres` for database init jobs

Live bootstrap fix:

- Added empty `otlp-traces-headers` key to `applicant-api-runtime` in `lendora-dev-1`, `lendora-sta-1`, and `lendora-shared-postgres` because the deployment requires the key and the old Secret did not contain it.

Applied shared infrastructure:

```bash
kubectl apply -k apps/lendora-shared-dependencies/overlays/shared
```

Runtime corrections made during live apply and reflected back into GitOps:

- Added `postgres-data`, `redis-data`, and `consul-data` PVC manifests.
- Added namespace patches for those PVCs in the shared overlay.
- Set initial dev overlay digests to the currently runnable image digests. The image release workflow still automatically promotes future digests to dev overlays.

Shared rollout result:

```text
deployment/postgres: rolled out
deployment/redis: rolled out
deployment/consul: rolled out
job/applicant-postgres-init: Complete
job/quote-postgres-init: Complete
job/origination-postgres-init: Complete
```

Applied business overlays:

```bash
for env in dev-1 sta-1; do
  for app in applicant-api quote-api origination-api fides-bff fides; do
    kubectl apply -k "apps/$app/overlays/$env"
  done
done
```

Rollout result:

| Namespace | Deployment | Result |
|---|---|---|
| `lendora-dev-1` | `applicant-api` | 1/1 Running |
| `lendora-dev-1` | `quote-api` | 1/1 Running |
| `lendora-dev-1` | `origination-api` | 1/1 Running |
| `lendora-dev-1` | `fides-bff` | 1/1 Running |
| `lendora-dev-1` | `fides` | 1/1 Running |
| `lendora-sta-1` | `applicant-api` | 1/1 Running |
| `lendora-sta-1` | `quote-api` | 1/1 Running |
| `lendora-sta-1` | `origination-api` | 1/1 Running |
| `lendora-sta-1` | `fides-bff` | 1/1 Running |
| `lendora-sta-1` | `fides` | 1/1 Running |

## Service Smoke

Applicant API readiness was verified through `kubectl port-forward`:

```text
lendora-dev-1 /ready -> 200 {"dependencies":{"consul":"UP","postgresql":"UP","redis":"UP"},"service":"applicant-api","status":"READY"}
lendora-sta-1 /ready -> 200 {"status":"READY","service":"applicant-api","dependencies":{"consul":"UP","postgresql":"UP","redis":"UP"}}
```

Additional dev service checks:

```text
quote-api /ready -> 200 {"service":"quote-api","dependencies":{"consul":"UP","postgresql":"UP"},"status":"READY"}
origination-api /ready -> 200 {"dependencies":{"consul":"UP","postgresql":"UP"},"service":"origination-api","status":"READY"}
fides-bff /api/v1/health -> 200 {"status":"ok","version":"dev"}
```

Notes:

- A generic temporary curl pod was blocked from direct service access by NetworkPolicy. This is consistent with the restrictive ingress model.
- Not every application image contains a shell, so `kubectl exec ... sh` is not a reliable smoke method for all services.

## Consul Evidence

Command:

```bash
kubectl exec -n lendora-shared-consul deploy/consul -- \
  wget -qO- http://127.0.0.1:8500/v1/catalog/services
```

Filtered service names:

```json
[
  "dev-1-applicant-api",
  "dev-1-origination-api",
  "dev-1-quote-api",
  "sta-1-applicant-api",
  "sta-1-origination-api",
  "sta-1-quote-api"
]
```

KV key checks returned expected keys:

```text
spark/lendora/dev-1/applicant-api/config
spark/lendora/sta-1/applicant-api/config
spark/lendora/dev-1/fides-web/runtime-config
spark/lendora/sta-1/fides-web/runtime-config
```

## PostgreSQL Evidence

Command:

```bash
kubectl exec -n lendora-shared-postgres deploy/postgres -- \
  sh -ceu 'PGPASSWORD="$POSTGRES_PASSWORD" psql -U "$POSTGRES_USER" -d postgres -Atc "select datname from pg_database where datname in (...) order by datname"'
```

Observed databases:

```text
dev_1_applicant
dev_1_origination
dev_1_quote
sta_1_applicant
sta_1_origination
sta_1_quote
```

## Redis Evidence

Command:

```bash
kubectl exec -n lendora-shared-redis deploy/redis -- \
  sh -ceu 'redis-cli -a "$REDIS_PASSWORD" -n 1 ping; redis-cli -a "$REDIS_PASSWORD" -n 2 ping'
```

Result:

```text
PONG
PONG
```

## DNS, Caddy, And Public Hosts

Spaceship DNS records were updated through the Spaceship API using `SPACESHIP_API_KEY` and `SPACESHIP_API_SECRET`.

Endpoint:

```text
PUT https://spaceship.dev/api/v1/dns/records/fuzzytails.fun
```

Confirmed records:

| Host | Type | Address | TTL |
|---|---|---|---|
| `dev-1-api.fuzzytails.fun` | A | `191.101.132.74` | 300 |
| `dev-1-fides.fuzzytails.fun` | A | `191.101.132.74` | 300 |
| `sta-1-api.fuzzytails.fun` | A | `191.101.132.74` | 300 |
| `sta-1-fides.fuzzytails.fun` | A | `191.101.132.74` | 300 |
| `github.fuzzytails.fun` | A | `191.101.132.74` | 300 |

Applied Caddy config:

```bash
kubectl apply -f platform/ingress/caddy-github-webhook.yaml
kubectl rollout restart deploy/caddy -n caddy
kubectl rollout status deploy/caddy -n caddy --timeout=180s
```

Initial result:

- `deployment/caddy`: rolled out.
- `https://api.fuzzytails.fun/api/v1/health`: HTTP 410 with body `legacy Lendora STA route removed`.
- Caddy initially failed ACME while DNS was absent; after Spaceship records were created and Caddy restarted, Caddy obtained certificates for all four new hostnames.

Final cleanup result:

- GitHub webhook EventSource URLs for `harness-repo`, `business-repo`, and `idl-repo` were migrated from `https://api.fuzzytails.fun` to `https://github.fuzzytails.fun`.
- The `api.fuzzytails.fun` Caddy server block was removed and Caddy was rolled out again.
- The Spaceship DNS `api.fuzzytails.fun` A record was deleted with `DELETE https://spaceship.dev/api/v1/dns/records/fuzzytails.fun`.
- A Spaceship API readback returned records for `dev-1-api`, `dev-1-fides`, `sta-1-api`, `sta-1-fides`, and `github`; no `api` record was returned.

Caddy certificate evidence:

```text
certificate obtained successfully: dev-1-api.fuzzytails.fun
certificate obtained successfully: dev-1-fides.fuzzytails.fun
certificate obtained successfully: sta-1-api.fuzzytails.fun
certificate obtained successfully: sta-1-fides.fuzzytails.fun
```

Public HTTPS smoke:

```text
https://dev-1-api.fuzzytails.fun/api/v1/health -> 200 {"status":"ok","version":"dev"}
https://sta-1-api.fuzzytails.fun/api/v1/health -> 200 {"status":"ok","version":"dev"}
https://dev-1-fides.fuzzytails.fun/ -> 200 HTML
https://sta-1-fides.fuzzytails.fun/ -> 200 HTML
```

## Cleanup Status

Old `lendora-sta-*` namespaces and PVCs were deleted after explicit user authorization.

Deleted namespaces:

```text
lendora-sta-applicant-api
lendora-sta-consul
lendora-sta-fides
lendora-sta-fides-bff
lendora-sta-origination-api
lendora-sta-postgres
lendora-sta-quote-api
lendora-sta-redis
```

Deleted PVCs through namespace deletion:

```text
lendora-sta-consul/consul-data
lendora-sta-postgres/postgres-data
lendora-sta-redis/redis-data
```

Deletion command:

```bash
GODEBUG=tlsmlkem=0 KUBECONFIG=$HOME/.kube/vincent-k3s.yaml kubectl delete ns \
  lendora-sta-applicant-api \
  lendora-sta-consul \
  lendora-sta-fides \
  lendora-sta-fides-bff \
  lendora-sta-origination-api \
  lendora-sta-postgres \
  lendora-sta-quote-api \
  lendora-sta-redis
```

Post-delete verification:

```bash
GODEBUG=tlsmlkem=0 KUBECONFIG=$HOME/.kube/vincent-k3s.yaml kubectl get ns --no-headers | rg '^lendora-sta-' || true
GODEBUG=tlsmlkem=0 KUBECONFIG=$HOME/.kube/vincent-k3s.yaml kubectl get pvc -A --no-headers | rg '^lendora-sta-' || true
```

Observed result:

```text
namespace query: lendora-sta-1 only
pvc query: no lendora-sta-* PVCs
```

Post-delete runtime state:

- `lendora-shared-postgres`, `lendora-shared-redis`, and `lendora-shared-consul` deployments remained `1/1`.
- `lendora-dev-1` deployments `applicant-api`, `quote-api`, `origination-api`, `fides-bff`, and `fides` remained `1/1`.
- `lendora-sta-1` deployments `applicant-api`, `quote-api`, `origination-api`, `fides-bff`, and `fides` remained `1/1`.
- `caddy` remained `1/1`.

Post-delete public HTTPS smoke:

```text
https://dev-1-api.fuzzytails.fun/api/v1/health -> 200
https://sta-1-api.fuzzytails.fun/api/v1/health -> 200
https://dev-1-fides.fuzzytails.fun/ -> 200 HTML
https://sta-1-fides.fuzzytails.fun/ -> 200 HTML
```

Note: one immediate post-restart API curl attempt hit a transient TLS/HTTP2 transport failure while Caddy was acquiring certificates. Retrying with HTTP/1.1 after certificate acquisition returned 200 for both API hostnames.

Additional cleanup after explicit user instruction to delete all unnecessary resources:

- Removed old GitOps state: `clusters/lendora-sta`, `apps/lendora-sta-dependencies`, `apps/*/overlays/lendora-sta`, and `docs/lendora-sta-runtime.md`.
- Updated GitOps base defaults so they no longer point to deleted `lendora-sta-*` namespaces.
- Deleted old Consul KV keys: `config/applicant-api/data`, `config/quote-api/data`, `config/origination-api/data`, and `config/fides-web/runtime-config`.
- Added `registry.consul.service_name` support to `fides-bff`, built and pushed `ghcr.io/spark-harness/fides-bff@sha256:c43ff06fb434f688088a954e309a6b16ffc693b04c9ce3b8bb308dce663fb945`, and redeployed both `lendora-dev-1/fides-bff` and `lendora-sta-1/fides-bff`.
- Verified both `fides-bff` deployments run the new digest and are `1/1`.
- Verified Consul agent services now include `dev-1-fides-bff` and `sta-1-fides-bff`; the prior bare `fides-bff` service name is gone.
- Removed local `/tmp/len136-*` verification artifacts.
