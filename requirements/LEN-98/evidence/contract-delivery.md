# LEN-98 Contract Delivery Evidence

## Go Generated Contract

- Repository: `spark-harness/idl-go-repo`
- Branch: `feature/LEN-98-fides-bff-openapi-ts-client`
- Tag: `v0.2.2-len98.1`
- Commit: `e2237b2`

Command:

```bash
go test ./...
```

Result: PASS.

Consumer verification:

```bash
GOPRIVATE=github.com/spark-harness/* go test ./...
```

Result: PASS in `business-repo/services/backend/fides-bff`.

## TypeScript Generated Contract

- Repository: `spark-harness/idl-ts-repo`
- Branch: `feature/LEN-98-fides-bff-openapi-ts-client`
- Package: `@spark-harness/idl-ts-client`
- Tag: `v0.1.0-len98.4`
- Commit: `9661620`

Generation source:

- Repository: `spark-harness/idl-openapi-repo`
- Path: `vesta/lendora/fides-bff/v1/openapi.yaml`
- Generator image: `openapitools/openapi-generator-cli:v7.14.0`

Command:

```bash
pnpm build
```

Result: PASS.

Consumer verification:

```bash
pnpm test
pnpm lint:deps
pnpm build
```

Result: PASS in `business-repo/services/frontend/fides`.
