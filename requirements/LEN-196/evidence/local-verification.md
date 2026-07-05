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

### Runtime Delivery

Merged PRs:

- business-repo PR #51: `2f77dd4adee00f2ec21e17bd3fa29b82d8c95c2a`
- gitops-repo PR #50: `96deff33dd14aeaba8ab23be3163e885c0ee8ee5`
- gitops-repo PR #51 sta-1 image promotion: `90fb39d117355f152396c202204ef1f9242bd0f9`

Business image release:

- Argo workflow: `business-image-release-2f77dd4adee0`
- Phase: `Succeeded`
- Started: `2026-07-05T01:47:44Z`
- Finished: `2026-07-05T01:56:57Z`

dev-1 live state after GitOps sync:

- Argo revision:
  - `lendora-dev-1-quote-api`: `96deff33dd14aeaba8ab23be3163e885c0ee8ee5`, Synced, Healthy
  - `lendora-dev-1-origination-api`: `96deff33dd14aeaba8ab23be3163e885c0ee8ee5`, Synced, Healthy
  - `lendora-dev-1-applicant-api`: `96deff33dd14aeaba8ab23be3163e885c0ee8ee5`, Synced, Healthy
  - `lendora-dev-1-fides-bff`: `96f39e0209f3a2919e6eb1cb8cb44bf571e28d91`, Synced, Healthy
- Images:
  - `quote-api`: `ghcr.io/spark-harness/quote-api@sha256:b248b8e5a1e1003c497bc11d2d456bb78bc63f07ac82fdfe2059df72daab212e`
  - `origination-api`: `ghcr.io/spark-harness/origination-api@sha256:1265b0413302ac100d56597fa784c5687d90204a79e8d607b0e754fb45582cc6`
  - `applicant-api`: `ghcr.io/spark-harness/applicant-api@sha256:6511033b8eda880705d4d58c85280d302eb24b6e3f5c4a4e5b3f488adf3274ff`
  - `fides-bff`: `ghcr.io/spark-harness/fides-bff@sha256:3646741f748011b92b91549a44538812a502a00db34d63abe219582e0862367e`
- NetworkPolicy:
  - `quote-api-ingress`: `lendora-dev-1` -> `9090`; `lendora-shared-consul` -> `8080`
  - `origination-api-ingress`: `lendora-dev-1` -> `9090`; `lendora-shared-consul` -> `8080`
  - `applicant-api-ingress`: `lendora-dev-1` -> `9090`; `lendora-shared-consul` -> `8080`

dev-1 smoke:

- Command: public BFF API smoke against `https://dev-1-api.fuzzytails.fun`
- Result: PASS
- Run: `len196-dev-20260705100551`
- Applicant: `applicant_5e2cddbb-821d-41b2-a41e-1e7b51018fad`
- Quote create: `quote_afa720e6-14da-4db6-a8a5-821ed65b0fa9`
- Quote patch: `quote_e5577e96-0136-4614-b4a7-ff63517c405c`
- Application: `app_9a244eb5-f52f-4969-a222-21b0846df5c5`
- Covered calls:
  - `GET /api/v1/health`
  - `POST /api/v1/auth/otp:send`
  - `POST /api/v1/auth/otp:verify`
  - `POST /api/v1/pricing/quotes`
  - `POST /api/v1/loan-applications`
  - `GET /api/v1/loan-applications/{id}`
  - `PATCH /api/v1/loan-applications/{id}`
  - `PUT /api/v1/me/identity-profile`
  - `GET /api/v1/me/identity-profile`

sta-1 live state after GitOps sync and image promotion:

- Argo revision:
  - `lendora-sta-1-quote-api`: `90fb39d117355f152396c202204ef1f9242bd0f9`, Synced, Healthy
  - `lendora-sta-1-origination-api`: `90fb39d117355f152396c202204ef1f9242bd0f9`, Synced, Healthy
  - `lendora-sta-1-applicant-api`: `96deff33dd14aeaba8ab23be3163e885c0ee8ee5`, Synced, Healthy
  - `lendora-sta-1-fides-bff`: `96deff33dd14aeaba8ab23be3163e885c0ee8ee5`, Synced, Healthy
- Images:
  - `quote-api`: `ghcr.io/spark-harness/quote-api@sha256:b248b8e5a1e1003c497bc11d2d456bb78bc63f07ac82fdfe2059df72daab212e`
  - `origination-api`: `ghcr.io/spark-harness/origination-api@sha256:1265b0413302ac100d56597fa784c5687d90204a79e8d607b0e754fb45582cc6`
  - `applicant-api`: `ghcr.io/spark-harness/applicant-api@sha256:c3f1aea07528ad02a8864bd8e6d3c9e6d462f1696c9251cabc0ca6170fa23a5a`
  - `fides-bff`: `ghcr.io/spark-harness/fides-bff@sha256:c8a8fff46842446a9d247a21be307bea4e1ed12db6a712f6587aad13338365fb`
- NetworkPolicy:
  - `quote-api-ingress`: `lendora-sta-1` -> `9090`; `lendora-shared-consul` -> `8080`
  - `origination-api-ingress`: `lendora-sta-1` -> `9090`; `lendora-shared-consul` -> `8080`
  - `applicant-api-ingress`: `lendora-sta-1` -> `9090`; `lendora-shared-consul` -> `8080`

sta-1 smoke:

- Command: public BFF API smoke against `https://sta-1-api.fuzzytails.fun`
- Result: PASS
- Run: `len196-sta-20260705101932`
- Applicant: `applicant_192ac6df-6bc6-4f42-951b-3873bf72ba69`
- Quote create: `quote_d79dd8f4-3bfc-4991-8154-4ff64404f296`
- Quote patch: `quote_cdbad035-bfee-4efc-9828-cc86655cb3a1`
- Application: `app_e894cedb-c7bd-4713-9ebe-abe4bf88219b`
- Covered calls match the dev-1 smoke list.

Allowed HTTP boundaries confirmed:

- BFF public/external HTTP remains on `fides-bff` Service port `8000`.
- Java service HTTP remains on Kubernetes Service port `80` only for `/health` and `/ready`.
- `lendora-shared-consul` retains `8080` access for Java readiness checks.
- Internal business service calls use gRPC over `9090`; business namespace NetworkPolicy no longer allows Java business HTTP ports.
