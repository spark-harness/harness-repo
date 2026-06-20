# LEN-38 Go IDL Publishing Evidence

## Summary

本证据记录 Go IDL 生成物发布链路的实现和本地验证。

## Environment

- Timestamp: 2026-06-20T10:24:08Z
- Requirement: LEN-38
- Branch: `feature/LEN-38-go-idl-publishing`
- Go module path: `github.com/spark-harness/idl-go-repo`
- Go repo: `https://github.com/spark-harness/idl-go-repo`
- Go repo default branch: `master`
- Initial Go repo commit: `2d33cee3891ee1ca35429490547e02820438c178`
- Go repo gRPC stub commit: `b0c16809791831ba9461ddd5ebec1fa6eeaf2580`
- Branch sync CI run: `https://github.com/spark-harness/idl-repo/actions/runs/27868669016`
- RC publish CI run: `https://github.com/spark-harness/idl-repo/actions/runs/27868778869`
- RC tag: `v0.1.0-rc.LEN-38.20260620.7976082`

## Implemented Changes

- `idl-go-repo` initialized with:
  - `go.mod`
  - `go.sum`
  - README
  - generated `vesta/spark/user/v1/*.pb.go`
  - generated `vesta/spark/user/v1/*_grpc.pb.go`
- `idl-repo` added:
  - `buf.gen.go.yaml`
  - `.github/workflows/sync-go-idl.yml`
  - `.github/workflows/publish-go-idl.yml`
  - README documentation for Go sync and publish.
- `idl-repo/buf.gen.yaml` changed Go output to staging path `../.generated/idl-go`.
- LEN-38 design updated to document staging generation instead of direct generation into the Go repo root.

## Verification Commands

```text
buf --version
```

Result:

```text
1.63.0
```

```text
go version
```

Result:

```text
go version go1.26.2 darwin/arm64
```

```text
buf lint
```

Result: passed with no output.

```text
buf generate --template buf.gen.go.yaml
```

Result: passed with no output.

```text
go mod tidy
go test ./...
```

Result:

```text
?    github.com/spark-harness/idl-go-repo/vesta/spark/user/v1 [no test files]
```

```text
gh run view 27868669016 --repo spark-harness/idl-repo --json conclusion,status,url,headSha,workflowName,displayTitle
```

Result:

```text
{"conclusion":"success","displayTitle":"ci(idl): publish go generated contracts","headSha":"e514a77ea8fec0f901b7edab4b11083febbf44b9","status":"completed","url":"https://github.com/spark-harness/idl-repo/actions/runs/27868669016","workflowName":"Sync Go IDL"}
```

```text
git ls-remote --heads https://github.com/spark-harness/idl-go-repo.git feature/LEN-38-go-idl-publishing master
```

Result:

```text
b0c16809791831ba9461ddd5ebec1fa6eeaf2580 refs/heads/feature/LEN-38-go-idl-publishing
b0c16809791831ba9461ddd5ebec1fa6eeaf2580 refs/heads/master
```

```text
gh run view 27868778869 --repo spark-harness/idl-repo --json conclusion,status,url,headSha,workflowName,displayTitle
```

Result:

```text
{"conclusion":"success","displayTitle":"ci(idl): allow rc go publish tags","headSha":"7976082366bd77e78a50ff7235a1d7f9ce8e2f5c","status":"completed","url":"https://github.com/spark-harness/idl-repo/actions/runs/27868778869","workflowName":"Publish Go IDL"}
```

```text
git ls-remote --tags https://github.com/spark-harness/idl-go-repo.git 'v0.1.0-rc.LEN-38.20260620.7976082*'
```

Result:

```text
b0c16809791831ba9461ddd5ebec1fa6eeaf2580 refs/tags/v0.1.0-rc.LEN-38.20260620.7976082
```

```text
ruby -e 'require "yaml"; Dir[".github/workflows/*.yml"].each { |f| YAML.load_file(f); puts "valid #{f}" }'
```

Result:

```text
valid .github/workflows/publish-go-idl.yml
valid .github/workflows/sync-go-idl.yml
valid .github/workflows/branch-coherence.yml
valid .github/workflows/sync-java-idl.yml
```

```text
valid_rc='v1.8.0-rc.LEN-38.20260620.4a589e4'
invalid_rc='v1.8.0-rc.len38.20260620.4a589e4'
formal='v1.8.0'
```

Result: RC and formal tag regex checks passed; lowercase ticket RC example was rejected.

## Notes

- Test-first exception: this is generated-contract infrastructure and GitHub Actions configuration, not business behavior. Verification uses Buf, Go module compilation, workflow YAML parsing, and tag pattern checks.
- `buf.gen.go.yaml` uses managed `go_package_prefix` override so generated Go packages align with `github.com/spark-harness/idl-go-repo` without changing wire contract.
- Direct `buf generate` to the generated repo root is intentionally avoided because `clean: true` can remove `.git` and module files.
- Formal publish workflow was not triggered with a real formal SemVer tag in this validation pass because formal tags are the release source of truth and should be created only for an approved formal release.
