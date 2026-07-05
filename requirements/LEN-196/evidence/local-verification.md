# Local Verification

## 2026-07-05T09:16:49+08:00

Worktrees:

- `/Users/forest/Code/spark/.worktrees/LEN-196/business-repo`
- `/Users/forest/Code/spark/.worktrees/LEN-196/gitops-repo`
- `/Users/forest/Code/spark/.worktrees/LEN-196/harness-repo`

### Test-First Baseline

Commands:

```bash
set -e
! rg -n "QuoteHttpAdapter|QuoteHttpExceptionHandler|LoanApplicationHttpAdapter|LoanApplicationHttpExceptionHandler|/internal/v1/pricing|/api/v1/pricing/quotes|/api/v1/loan-applications" apps/quote-api apps/origination-api

set -e
! rg -n "quote-api-consul-config|origination-api-consul-config|applicant-api-consul-config" apps/quote-api apps/origination-api apps/applicant-api
```

Baseline result before edits: FAIL as expected.

Observed baseline findings:

- `quote-api` still had `QuoteHttpAdapter`, `QuoteHttpExceptionHandler`, and `QuoteHttpAdapterTest`.
- `origination-api` still had `LoanApplicationHttpAdapter`, `LoanApplicationHttpExceptionHandler`, and `LoanApplicationHttpAdapterTest`.
- GitOps still had stale `quote-api-consul-config`, `origination-api-consul-config`, and `applicant-api-consul-config` files.

### Business Repo Verification

Commands:

```bash
set -e
! rg -n "QuoteHttpAdapter|QuoteHttpExceptionHandler|LoanApplicationHttpAdapter|LoanApplicationHttpExceptionHandler|/internal/v1/pricing|/api/v1/pricing/quotes|/api/v1/loan-applications" apps/quote-api apps/origination-api

mvn -B -f apps/quote-api/pom.xml test
mvn -B -f apps/origination-api/pom.xml test

cd apps/fides-bff
GOPRIVATE=github.com/spark-harness/* GONOSUMDB=github.com/spark-harness/* go test ./... -count=1
```

Result: PASS

Observed:

- `quote-api` business HTTP adapter scan returned no matches under `apps/quote-api`.
- `origination-api` business HTTP adapter scan returned no matches under `apps/origination-api`.
- `quote-api` Maven tests: BUILD SUCCESS, 23 tests.
- `origination-api` Maven tests: BUILD SUCCESS, 43 tests.
- `fides-bff` Go tests: PASS for all packages.

Allowed HTTP paths remain:

- `fides-bff` external HTTP `/api/v1`.
- `fides-web` BFF proxy HTTP.
- Java service `HealthHttpAdapter` `/health` and `/ready`.
- Consul discovery/registration HTTP API.
- OTLP `http/protobuf`.

### Contract Dependency Scan

Command:

```bash
python3 scripts/contract_dependency_scan.py --mode master \
  --path apps/fides-bff/go.mod \
  --path apps/fides-bff/go.sum \
  --path apps/quote-api/pom.xml \
  --path apps/origination-api/pom.xml
```

Result: PASS

Observed output:

```text
No contract dependency violations found.
```

### GitOps Rendering

Commands:

```bash
for app in quote-api origination-api applicant-api fides-bff; do
  for env in dev-1 sta-1; do
    kubectl kustomize apps/$app/overlays/$env >/tmp/len196-$app-$env.yaml
  done
done

set -e
! find apps -path '*consul-config.yaml' -o -path '*runtime-config-consul.yaml' |
  rg 'quote-api|origination-api|applicant-api|fides-bff'
```

Result: PASS

Rendered NetworkPolicy checks:

- `quote-api` dev-1/sta-1 client namespace ingress exposes only `9090`; `lendora-shared-consul` ingress keeps `8080`.
- `origination-api` dev-1/sta-1 client namespace ingress exposes only `9090`; `lendora-shared-consul` ingress keeps `8080`.
- `applicant-api` dev-1/sta-1 client namespace ingress exposes only `9090`; `lendora-shared-consul` ingress keeps `8080`.
- Service port `80` remains in rendered Services for Java health/readiness only.
- `fides-bff` external HTTP Service port `8000` remains by design.
- No stale `*-consul-config` or `runtime-config-consul` Job renders.

### Current Limit

Runtime dev-1 / sta-1 smoke must run after business image release and GitOps promotion. This local evidence only covers source, tests, contract dependency, and rendered manifest readiness.
