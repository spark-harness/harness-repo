# Local Verification

## 2026-07-05T07:46:42+08:00

Worktree: `/Users/forest/Code/spark/.worktrees/LEN-192/business-repo`

### Go Tests

Command:

```bash
cd apps/fides-bff && GOPRIVATE=github.com/spark-harness/* GONOSUMDB=github.com/spark-harness/* go test ./... -count=1
```

Result: PASS

Observed packages:

- `github.com/spark/fides-bff/cmd/fides-bff`: PASS
- `github.com/spark/fides-bff/internal/biz`: PASS
- `github.com/spark/fides-bff/internal/conf`: no test files
- `github.com/spark/fides-bff/internal/data`: PASS
- `github.com/spark/fides-bff/internal/observability`: PASS
- `github.com/spark/fides-bff/internal/server`: PASS
- `github.com/spark/fides-bff/internal/service`: no test files

### Contract Dependency Scan

Command:

```bash
python3 scripts/contract_dependency_scan.py --mode master --path apps/fides-bff/go.mod --path apps/fides-bff/go.sum
```

Result: PASS

Observed output:

```text
No contract dependency violations found.
```

### GitOps Rendering

Worktree: `/Users/forest/Code/spark/.worktrees/LEN-192/gitops-repo`

Commands:

```bash
kubectl kustomize apps/fides-bff/overlays/dev-1 > /tmp/len192-fides-bff-dev-1.yaml
rg -n "ORIGINATION_(HTTP|GRPC|CONSUL)" /tmp/len192-fides-bff-dev-1.yaml
kubectl kustomize apps/fides-bff/overlays/sta-1 > /tmp/len192-fides-bff-sta-1.yaml
rg -n "ORIGINATION_(HTTP|GRPC|CONSUL)" /tmp/len192-fides-bff-sta-1.yaml
rg -n "ORIGINATION_HTTP|origination.*http|http.*origination" apps/fides-bff
```

Result: PASS

Observed rendered values:

- dev-1 includes `ORIGINATION_CONSUL_SERVICE_NAME: dev-1-origination-api`.
- dev-1 includes `ORIGINATION_GRPC_TIMEOUT: 3s`.
- dev-1 includes `ORIGINATION_GRPC_PLAINTEXT: "true"`.
- sta-1 includes `ORIGINATION_CONSUL_SERVICE_NAME: sta-1-origination-api`.
- sta-1 includes `ORIGINATION_GRPC_TIMEOUT: 3s`.
- sta-1 includes `ORIGINATION_GRPC_PLAINTEXT: "true"`.
- No `ORIGINATION_HTTP_BASE_URL` or `ORIGINATION_HTTP_TIMEOUT` remains in rendered dev-1 or sta-1 fides-bff config.

### Hard Cut Contract Checks

- `apps/fides-bff/go.mod` consumes `github.com/spark-harness/idl-go-repo v0.2.7`.
- `OriginationClient` calls `OriginationLoanApplicationService` over gRPC for create, get, update, and advance.
- `OriginationGRPCConsulResolver` uses Consul `grpc_port`.
- `ORIGINATION_HTTP_BASE_URL`, `ORIGINATION_HTTP_TIMEOUT`, `quote.http`, and `QuoteHTTP` are not part of the origination client/config path.
- BFF external HTTP server remains by design.
- Review finding fix: formal `ORIGINATION-PARAM-0001` now maps conservatively to `validation_error` except locally deterministic missing idempotency.
- Review finding fix: `AdvanceApplicationStep` maps gRPC `Unauthenticated` to BFF `forbidden`.
- Origination gRPC error spans include mapped stable `error_code`.

### Review Fix Regression

Command:

```bash
cd apps/fides-bff && GOPRIVATE=github.com/spark-harness/* GONOSUMDB=github.com/spark-harness/* go test ./internal/data -run 'TestOriginationClient' -count=1
```

Result: PASS

### CI Lint Regression

Command:

```bash
cd apps/fides-bff && golangci-lint run ./...
```

Result: PASS

Observed output:

```text
0 issues.
```

Note: CI initially reported unused `staticURLResolver` after origination HTTP client removal. The unused resolver was removed and lint passed locally.

## 2026-07-05T08:46:19+08:00

Worktrees:

- `/Users/forest/Code/spark/.worktrees/LEN-192/business-repo`
- `/Users/forest/Code/spark/.worktrees/LEN-192/gitops-repo`
- `/Users/forest/Code/spark/.worktrees/LEN-192/harness-repo`

### PR Merge Evidence

GitHub PR state was rechecked after merge:

- harness-repo PR #57: MERGED into `master` at `2026-07-05T00:15:47Z`, merge commit `718e6cfcbe70041cf422196f0cd05564df190b96`.
- business-repo PR #50: MERGED into `master` at `2026-07-05T00:16:02Z`, merge commit `171ad584ae7e7f42e4a9fb7156a705e5cb78ff9c`.
- gitops-repo PR #48: MERGED into `master` at `2026-07-05T00:16:15Z`, merge commit `9ab1adff4babeb5cd6869c9fdab24e679fa5d793`.
- gitops-repo PR #49: MERGED into `master` at `2026-07-05T00:40:04Z`, merge commit `cd4575b538c69af4e3796c277337f16d4208a607`.

### Image Release

Command:

```bash
GODEBUG=tlsmlkem=0 kubectl --kubeconfig ~/.kube/vincent-k3s.yaml \
  -n argo get workflow business-image-release-171ad584ae7e -o json
```

Result: PASS

Observed workflow:

- name: `business-image-release-171ad584ae7e`
- status: `Succeeded`
- started: `2026-07-05T00:16:05Z`
- finished: `2026-07-05T00:25:52Z`
- promoted GitOps commit: `7971316e90e99cf9978859fc23a154c68c758602`
- fides-bff image digest: `sha256:c8a8fff46842446a9d247a21be307bea4e1ed12db6a712f6587aad13338365fb`

### Runtime State

Commands:

```bash
GODEBUG=tlsmlkem=0 kubectl --kubeconfig ~/.kube/vincent-k3s.yaml \
  -n argocd get app lendora-dev-1-fides-bff lendora-sta-1-fides-bff -o json

GODEBUG=tlsmlkem=0 kubectl --kubeconfig ~/.kube/vincent-k3s.yaml \
  -n lendora-dev-1 get deploy fides-bff -o json

GODEBUG=tlsmlkem=0 kubectl --kubeconfig ~/.kube/vincent-k3s.yaml \
  -n lendora-sta-1 get deploy fides-bff -o json

GODEBUG=tlsmlkem=0 kubectl --kubeconfig ~/.kube/vincent-k3s.yaml \
  -n lendora-dev-1 get configmap fides-bff-env -o json

GODEBUG=tlsmlkem=0 kubectl --kubeconfig ~/.kube/vincent-k3s.yaml \
  -n lendora-sta-1 get configmap fides-bff-env -o json
```

Result: PASS

Observed Argo state:

- `lendora-dev-1-fides-bff`: Synced, Healthy, revision `cd4575b538c69af4e3796c277337f16d4208a607`.
- `lendora-sta-1-fides-bff`: Synced, Healthy, revision `cd4575b538c69af4e3796c277337f16d4208a607`.

Observed deployment image:

- dev-1: `ghcr.io/spark-harness/fides-bff@sha256:c8a8fff46842446a9d247a21be307bea4e1ed12db6a712f6587aad13338365fb`
- sta-1: `ghcr.io/spark-harness/fides-bff@sha256:c8a8fff46842446a9d247a21be307bea4e1ed12db6a712f6587aad13338365fb`

Observed `fides-bff-env` origination settings:

- dev-1 `ORIGINATION_CONSUL_SERVICE_NAME=dev-1-origination-api`
- sta-1 `ORIGINATION_CONSUL_SERVICE_NAME=sta-1-origination-api`
- both environments keep `ORIGINATION_CONSUL_ADDRESS=consul.lendora-shared-consul.svc.cluster.local:8500`
- both environments keep `ORIGINATION_CONSUL_SCHEME=http`
- both environments keep `ORIGINATION_GRPC_TIMEOUT=3s`
- both environments keep `ORIGINATION_GRPC_PLAINTEXT=true`
- neither environment contains `ORIGINATION_HTTP_*`

### Public BFF Smoke

dev-1 smoke through `https://dev-1-api.fuzzytails.fun`:

- applicant: `applicant_06c02015-f299-4f3e-90fe-8be469b5f79e`
- initial quote: `quote_4b260ee2-ebbf-40b1-b8ee-1e42460c2709`
- create loan application: HTTP 200, application `app_8026effa-79a2-45a4-9459-ce36dfb48564`
- get loan application: HTTP 200
- patch loan application: HTTP 200, quote `quote_64c72375-a2a7-4efb-b69c-db139c25d5b2`
- identity profile upsert and advance: HTTP 200, `currentStep=identity_information`

sta-1 smoke through `https://sta-1-api.fuzzytails.fun`:

- applicant: `applicant_4b20ff36-f5ec-49b4-b257-35cc44d597f8`
- initial quote: `quote_993d07ef-aded-485a-b99b-198727ea80c4`
- create loan application: HTTP 200, application `app_a0950079-4c47-4a67-9fc2-46992ce511b5`
- get loan application: HTTP 200
- patch loan application: HTTP 200, quote `quote_0eb52f3d-5eac-4ca4-8aa7-f50b86fe18a9`
- identity profile upsert and advance: HTTP 200, `currentStep=identity_information`

### Hard Cut Runtime Conclusion

- fides-bff consumes origination through Consul-discovered gRPC service names in dev-1 and sta-1.
- Runtime config no longer exposes origination business HTTP settings.
- BFF external HTTP remains by design.
- `lendora-shared-consul` remains in use for service discovery and was not removed.
