# LEN-98 Verification Evidence

## 2026-06-24

### IDL

Command:

```bash
buf lint
buf generate --template buf.gen.go.yaml --path vesta/lendora/fides-bff/v1/auth.proto
buf generate --template buf.gen.openapi.yaml --path vesta/lendora/fides-bff/v1/auth.proto
scripts/check-openapi-v3.sh
```

Result: PASS.

Notes:

- `buf.gen.go.yaml` now generates Kratos HTTP binding via local `protoc-gen-go-http`.
- `buf.gen.openapi.yaml` generates OpenAPI v3 via local `protoc-gen-openapi`.
- OpenAPI output is `idl-repo/openapi/fides-bff/openapi.yaml`.

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
pnpm install
pnpm generate
pnpm build
git push origin feature/LEN-98-fides-bff-openapi-ts-client
git push origin v0.1.0-len98.3
```

Result: PASS.

Notes:

- Private remote `spark-harness/idl-ts-repo` was created.
- `@spark-harness/fides-bff-client` is published as a Git tag dependency at `v0.1.0-len98.3`.

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

- `pnpm test`: 12 test files passed, 1 skipped; 50 tests passed, 1 skipped.
- `pnpm lint:deps`: no dependency violations.
- `pnpm build`: passed after removing `next/font/google` external Google Fonts dependency and using a system font stack.

## Release Dependency Closure

- Created private remote repository `spark-harness/idl-ts-repo`.
- Pushed TS client package and tag `v0.1.0-len98.3`.
- Pushed `idl-go-repo` generated HTTP binding branch and tag `v0.2.2-len98.1`.
- Replaced local file dependency and local Go replace with Git tags.
