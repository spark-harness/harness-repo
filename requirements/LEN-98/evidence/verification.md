# LEN-98 Verification Evidence

## 2026-06-24

### IDL

Command:

```bash
buf lint
buf generate --template buf.gen.go.yaml --path vesta/lendora/fides-bff/v1/auth.proto
buf generate --template buf.gen.java.yaml --path vesta/lendora/fides-bff/v1/auth.proto
buf generate --template buf.gen.openapi.yaml --path vesta/lendora/fides-bff/v1/auth.proto
scripts/check-openapi-v3.sh
```

Result: PASS.

Notes:

- Generation templates are split into Go, Java, and OpenAPI.
- `buf.gen.go.yaml` now generates Kratos HTTP binding without relying on preinstalled protoc plugins in Argo.
- `buf.gen.openapi.yaml` generates OpenAPI v3 via Buf remote plugin `buf.build/community/google-gnostic-openapi`.
- OpenAPI output is `idl-openapi-repo/vesta/lendora/fides-bff/v1/openapi.yaml`.

### fides-bff

Command:

```bash
go test ./...
```

Result: PASS.

Notes:

- `fides-bff` auth routes are registered through generated `RegisterFidesBffAuthServiceHTTPServer`.
- `fides-bff` consumes `github.com/spark-harness/idl-go-repo v0.2.2-len98.1`.
- Private module verification requires `GOPRIVATE=github.com/spark-harness/*`.

### idl-ts-repo

Commands:

```bash
pnpm generate
pnpm build
git push origin feature/LEN-98-fides-bff-openapi-ts-client
git push -f origin v0.1.0-len98.4
```

Result: PASS.

Notes:

- `pnpm generate` runs Docker image `openapitools/openapi-generator-cli:v7.14.0`.
- Private remote `spark-harness/idl-ts-repo` was created.
- `@spark-harness/idl-ts-client` is published as a Git tag dependency at `v0.1.0-len98.4`.

### gitops-repo

Commands:

```bash
ruby -e "require 'yaml'; YAML.load_file('workflows/templates/github-idl-release-workflow-template.yaml')"
GODEBUG=tlsmlkem=0 kubectl --kubeconfig ~/.kube/vincent-k3s.yaml --context vincent-k3s -n argo apply --server-side --dry-run=server -f workflows/templates/github-idl-release-workflow-template.yaml
```

Result: PASS.

Notes:

- Workflow order is `checkout-idl -> sync-openapi -> checkout-ts-inputs -> generate-ts -> sync-ts -> sync-go -> sync-java -> publish-go -> publish-java`.
- `generate-ts` uses fixed image `openapitools/openapi-generator-cli:v7.14.0`.
- `sync-ts` uses fixed image `node:24-bookworm` and enables pnpm through Corepack before `pnpm install --frozen-lockfile` and `pnpm build`.
- The fixed image was validated with its default `docker-entrypoint.sh` by passing `generate` as container args; shell command `openapi-generator-cli` is not used.
- Manual workflow `idl-repo-release-len98-manual-fr8rj` initially failed in `sync-openapi` because the runner did not have local `protoc-gen-openapi`; the fix is `buf.build/community/google-gnostic-openapi`.
- Manual workflow `idl-repo-release-len98-manual-vfkzb` verified `sync-openapi`, `checkout-ts-inputs`, and `generate-ts`; it then exposed that the previous `sync-ts` runner did not have `pnpm`, fixed by `node:24-bookworm` plus Corepack.
- `vincent-k3s` namespace `argo` has secret `buf-token`; workflow steps that call `buf generate` inject `BUF_TOKEN` so Buf remote generation uses the authenticated bucket.
- Server-side dry-run on `vincent-k3s` returned a non-fatal existing last-applied annotation ownership warning only.

### fides

Command:

```bash
pnpm install
pnpm test
pnpm lint:deps
pnpm build
```

Result: PASS.

Notes:

- `pnpm test`: 12 test files passed, 1 skipped; 51 tests passed, 1 skipped.
- `pnpm lint:deps`: no dependency violations.
- `pnpm build`: passed.

## Release Dependency Closure

- Created private remote repository `spark-harness/idl-ts-repo`.
- Created private remote repository `spark-harness/idl-openapi-repo`.
- Pushed TS client package and tag `v0.1.0-len98.4`.
- Pushed `idl-go-repo` generated HTTP binding branch and tag `v0.2.2-len98.1`.
- Replaced local file dependency and local Go replace with Git tags.
