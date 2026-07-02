# LEN-153 Buf And Generated Contract Evidence

## Scope

Requirement: `LEN-153`

Branch: `feature/LEN-153-fides-bff-contracts`

IDL worktree: `/Users/forest/Code/spark/.worktrees/LEN-153/idl-repo`

Checked at: `2026-07-02T23:36:00+08:00`

## Commands

| Command | Result | Notes |
|---|---|---|
| `buf lint` | PASS | No output. |
| `buf generate` | PASS | Default template is currently empty; this is not the primary generation evidence. |
| `buf generate --template buf.gen.go.yaml` | PASS | Generated Go protobuf, gRPC and Kratos HTTP staging files under `../.generated/idl-go`. |
| `buf generate --template buf.gen.openapi.yaml` | PASS | Generated OpenAPI staging file under `../.generated/openapi/openapi.yaml`. |
| `buf breaking --against .git#branch=master` | PASS | No output. |
| `git diff --check` across harness-repo, idl-repo, idl-go-repo, idl-openapi-repo, idl-ts-repo | PASS | TS generated files had generator trailing whitespace; cleaned mechanically and rebuilt before final diff check. |

## Generated Go Evidence

Generated files include:

```text
../.generated/idl-go/vesta/lendora/fides-bff/v1/loan_application.pb.go
../.generated/idl-go/vesta/lendora/fides-bff/v1/loan_application_grpc.pb.go
../.generated/idl-go/vesta/lendora/fides-bff/v1/loan_application_http.pb.go
../.generated/idl-go/vesta/lendora/fides-bff/v1/pricing.pb.go
../.generated/idl-go/vesta/lendora/fides-bff/v1/pricing_grpc.pb.go
../.generated/idl-go/vesta/lendora/fides-bff/v1/pricing_http.pb.go
```

Generated HTTP registration evidence:

```text
RegisterFidesBffPricingServiceHTTPServer
POST /api/v1/pricing/quotes

RegisterFidesBffLoanApplicationServiceHTTPServer
POST /api/v1/loan-applications
GET /api/v1/loan-applications/{application_id}
PATCH /api/v1/loan-applications/{application_id}
```

## OpenAPI Evidence

Generated OpenAPI path evidence from `../.generated/openapi/openapi.yaml`:

```text
/api/v1/pricing/quotes
/api/v1/loan-applications
/api/v1/loan-applications/{applicationId}
```

Generated operation tags include:

```text
FidesBffPricingService
FidesBffLoanApplicationService
```

## Generated Repository Evidence

Generated repositories were cloned under `/Users/forest/Code/spark/.worktrees/LEN-153` and checked out on `feature/LEN-153-fides-bff-contracts`.

Generated repository PRs were merged to `master` before final source repo delivery:

| Repository | PR | Result |
|---|---|---|
| `idl-go-repo` | `spark-harness/idl-go-repo#3` | merged |
| `idl-openapi-repo` | `spark-harness/idl-openapi-repo#2` | merged |
| `idl-ts-repo` | `spark-harness/idl-ts-repo#2` | merged |

### idl-go-repo

Synced from `../.generated/idl-go` with `.git`, `go.mod`, `go.sum` and `README.md` excluded.

Validation:

```text
go test ./...
```

Result: PASS.

### idl-openapi-repo

Synced:

```text
vesta/lendora/fides-bff/v1/openapi.yaml
```

The OpenAPI file contains pricing and loan-application paths listed above.

### idl-ts-repo

Commands:

```text
pnpm install --frozen-lockfile
pnpm generate
pnpm build
git diff --check
```

Result: PASS.

Workflow source inspected:

```text
gitops-repo/workflows/templates/github-idl-release-workflow-template.yaml
```

Relevant arguments:

```text
-g typescript-fetch
-i /workspace/idl-openapi-repo/vesta/lendora/fides-bff/v1/openapi.yaml
-o /workspace/idl-ts-repo/src/vesta/lendora/fides-bff/v1
--additional-properties=supportsES6=true,withInterfaces=true,useSingleRequestParameter=true,importFileExtension=.js
```

Generated SDK evidence:

```text
src/vesta/lendora/fides-bff/v1/apis/FidesBffPricingServiceApi.ts
src/vesta/lendora/fides-bff/v1/apis/FidesBffLoanApplicationServiceApi.ts
dist/vesta/lendora/fides-bff/v1/apis/FidesBffPricingServiceApi.js
dist/vesta/lendora/fides-bff/v1/apis/FidesBffLoanApplicationServiceApi.js
```

Conclusion: LEN-153 produces the Go, OpenAPI and TypeScript generated contract outputs required by the Jira DoD.

## Parent Story Coverage

| Parent AC | Contract Coverage |
|---|---|
| LEN-152 AC1 | Existing auth proto remains compatible for mobile verification. |
| LEN-152 AC2 | New pricing proto covers loan quote creation through BFF. |
| LEN-152 AC3 | New loan-application proto covers create/get/update draft through BFF. |
| LEN-152 AC4 | Existing identity-profile proto remains present for profile read/write. |
| LEN-152 AC6 | Service names and HTTP paths are present in generated Go/OpenAPI outputs, enabling later trace attribution by fides-bff route and downstream service. |
