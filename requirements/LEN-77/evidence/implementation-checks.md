# LEN-77 Implementation Checks

## Static GitOps Rendering

在 `gitops-repo` 运行：

```bash
kubectl kustomize clusters/lendora-sta >/tmp/lendora-sta-cluster.yaml
kubectl kustomize apps/lendora-sta-dependencies/overlays/sta >/tmp/lendora-sta-deps.yaml
kubectl kustomize apps/applicant-api/overlays/lendora-sta >/tmp/lendora-sta-applicant.yaml
kubectl kustomize apps/fides-bff/overlays/lendora-sta >/tmp/lendora-sta-bff.yaml
kubectl kustomize apps/fides/overlays/lendora-sta >/tmp/lendora-sta-fides.yaml
kubectl kustomize workflows/templates >/tmp/lendora-workflows-templates.yaml
kubectl kustomize workflows/ci >/tmp/lendora-workflows-ci.yaml
```

Result: PASS.

Rendered coverage:

- `clusters/lendora-sta`: Namespace、AppProject、Argo CD Application。
- `apps/lendora-sta-dependencies/overlays/sta`: PostgreSQL、Redis、Consul Deployment / Service。
- `apps/applicant-api/overlays/lendora-sta`: ConfigMap、Deployment、Service、NetworkPolicy。
- `apps/fides-bff/overlays/lendora-sta`: ConfigMap、Deployment、Service。
- `apps/fides/overlays/lendora-sta`: Deployment、Service。
- `workflows/ci`: business-repo master push Sensor triggers applicant-api、fides-bff、fides image release workflows.
- `workflows/templates`: `github-image-release` exposes build context, Dockerfile and GitOps promotion parameters.

## Business Build And Tests

在 `business-repo/services/backend/applicant-api` 运行：

```bash
mvn -q -DskipTests package
```

Result: PASS.

在 `business-repo/services/backend/fides-bff` 运行：

```bash
go test ./... -count=1
```

Result: PASS.

在 `business-repo/services/frontend/fides` 运行：

```bash
pnpm install --frozen-lockfile
pnpm lint:deps
pnpm test
```

Result: PASS. `pnpm test` reported 12 passed test files, 1 skipped smoke file, 50 passed tests, 1 skipped test.

Re-run after image release Sensor changes:

- `mvn -q -DskipTests package`: PASS.
- `go test ./... -count=1`: PASS.
- `pnpm lint:deps && pnpm test`: PASS.

Focused runtime follow-up tests:

```bash
mvn -q -Dtest=ConsulServiceRegistrationTest,ApplicantAuthConfigurationTest test
go test ./internal/server ./internal/conf ./cmd/fides-bff
./node_modules/.bin/vitest run \
  src/presentation/mobile-verification/mobile-verification-screen.test.tsx \
  src/api/mobile-verification/create-mobile-verification-controller.test.ts \
  src/infrastructure/mobile-verification/rest-otp-auth-gateway.test.ts
```

Result: PASS. Frontend focused run reported 3 files and 20 tests passed.

## Docker Build Attempt

在 `business-repo` 运行三服务 Docker build：

```bash
docker build -f services/backend/fides-bff/Dockerfile -t lendora/fides-bff:len77-test .
docker build -f services/frontend/fides/Dockerfile -t lendora/fides:len77-test .
docker build -f services/backend/applicant-api/Dockerfile -t lendora/applicant-api:len77-test .
```

Result: INCONCLUSIVE.

Reason: Docker build metadata pull stalled for more than two minutes; builds were interrupted. The applicant-api build also reported Docker daemon connection contention (`only one connection allowed`) during interruption.

Follow-up: the image release path subsequently produced runtime digests and `vincent-k3s` successfully pulled them.

## Runtime Cluster Checks

Cluster:

```bash
GODEBUG=tlsmlkem=0 KUBECONFIG=$HOME/.kube/vincent-k3s.yaml kubectl config current-context
```

Result: PASS. Current context is `vincent-k3s`.

Runtime images:

| Service | Namespace | Digest | Runtime result |
|---|---|---|---|
| applicant-api | `lendora-sta-applicant-api` | `sha256:8249e6c25693c810c3d59a7ca562823683ea4784bd56a74d907e5a2cefbb1ee4` | Deployment `1/1` Ready |
| fides-bff | `lendora-sta-fides-bff` | `sha256:b95914c46980c0c1e3ee433f0230c2322e6a764f43c6c54a9ff37b890811ee45` | Deployment `1/1` Ready |
| fides | `lendora-sta-fides` | `sha256:60ff63c63633c385ad7cc1bb56e793de775f53e9c7ccaa61adf1c9e70fd27af2` | Deployment `1/1` Ready |

Public route decision:

- `lendora-sta.fuzzytails.fun` and `lendora-api-sta.fuzzytails.fun` were not usable during validation because public DNS / certificate issuance could not resolve them.
- Temporary STA public entry is `https://api.fuzzytails.fun`.
- `https://api.fuzzytails.fun/api/v1*` routes to `fides-bff`.
- `https://api.fuzzytails.fun/` routes to `fides`.
- Final `lendora-*` DNS and certificate setup remains follow-up technical debt, not a blocker for the LEN-77 implementation-first closure.

Public health:

```bash
curl -kfsS https://api.fuzzytails.fun/api/v1/health
```

Result: PASS.

Observed response:

```json
{"status":"ok","version":"dev"}
```

Consul health:

```bash
GODEBUG=tlsmlkem=0 KUBECONFIG=$HOME/.kube/vincent-k3s.yaml \
  kubectl exec -n lendora-sta-consul deploy/consul -- \
  wget -qO- http://127.0.0.1:8500/v1/health/checks/applicant-api
```

Result: PASS. Consul reported `Status: passing`; check output included:

```text
HTTP GET http://applicant-api.lendora-sta-applicant-api.svc.cluster.local:80/ready: 200
```

## Residual Non-Blocking Items

- Final `lendora-*` DNS / certificate setup is unresolved and should be handled by a follow-up ticket.
- STA uses `APPLICANT_MIGRATIONS_ENABLED=false` after schema bootstrap to avoid repeated Flyway startup failures against the existing database; long-term migration ownership should be handled separately.
- OTEL endpoint is disabled / not wired for this STA closure; runtime evidence relies on readiness, service health, smoke, and log inspection.
