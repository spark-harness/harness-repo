# LEN-98 Buf And OpenAPI Checks

## 2026-06-24

Commands:

```bash
buf lint
buf generate --template buf.gen.go.yaml --path vesta/lendora/fides-bff/v1/auth.proto
buf generate --template buf.gen.java.yaml --path vesta/lendora/fides-bff/v1/auth.proto
buf generate --template buf.gen.openapi.yaml --path vesta/lendora/fides-bff/v1/auth.proto
scripts/check-openapi-v3.sh
```

Result: PASS.

Contract outputs:

- `idl-openapi-repo/vesta/lendora/fides-bff/v1/openapi.yaml`
- `idl-go-repo/vesta/lendora/fides-bff/v1/auth_http.pb.go`

Notes:

- Buf generation templates are split by artifact family: Go, Java, and OpenAPI.
- `buf.gen.go.yaml` uses remote Go/gRPC plugins and invokes the Kratos HTTP generator through `go run` so Argo does not depend on preinstalled protoc plugins.
- `buf.gen.openapi.yaml` uses remote plugin `buf.build/community/google-gnostic-openapi` so Argo does not depend on a preinstalled `protoc-gen-openapi` binary.
- TS SDK generation is not a Buf template; it runs after OpenAPI repo push through fixed image `openapitools/openapi-generator-cli:v7.14.0`.
