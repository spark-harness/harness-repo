# LEN-98 Buf And OpenAPI Checks

## 2026-06-24

Commands:

```bash
buf lint
buf generate --template buf.gen.go.yaml --path vesta/lendora/fides-bff/v1/auth.proto
buf generate --template buf.gen.openapi.yaml --path vesta/lendora/fides-bff/v1/auth.proto
scripts/check-openapi-v3.sh
```

Result: PASS.

Contract outputs:

- `idl-repo/openapi/fides-bff/openapi.yaml`
- `idl-go-repo/vesta/lendora/fides-bff/v1/auth_http.pb.go`

Notes:

- `buf.gen.go.yaml` uses local `protoc-gen-go`, `protoc-gen-go-grpc`, and `protoc-gen-go-http`.
- `buf.gen.openapi.yaml` uses local `protoc-gen-openapi`.
