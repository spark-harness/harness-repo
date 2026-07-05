# LEN-212 Contract Evidence

## Scope

- `idl-repo` changed `buf.gen.go.yaml` to generate fides-bff Kratos v3 HTTP bindings.
- `.proto` business fields and HTTP annotations were not changed.
- `idl-go-repo` was updated from the generated output and published as formal tag `v0.2.8`.
- `business-repo/apps/fides-bff` consumes `github.com/spark-harness/idl-go-repo v0.2.8`.

## Formal Version Evidence

| Artifact | Version / Commit | Evidence |
|---|---|---|
| `idl-repo` tag | `v0.2.8` -> `751d619b074e74e8f300824760169f94c56f1d5f` | `git ls-remote --tags origin v0.2.8` |
| `idl-go-repo` tag | `v0.2.8` -> `7926cfb849f41fa6ab082e703d65db958e58864a` | `git ls-remote --tags origin v0.2.8` |
| Go module resolution | `github.com/spark-harness/idl-go-repo@v0.2.8` origin hash `7926cfb849f41fa6ab082e703d65db958e58864a` | `GOPRIVATE=github.com/spark-harness/* GONOSUMDB=github.com/spark-harness/* GOPROXY=direct go list -m -json github.com/spark-harness/idl-go-repo@v0.2.8` |

## IDL Delivery Evidence

- `idl-repo` PR: `https://github.com/spark-harness/idl-repo/pull/17`
- `idl-repo` merged to `master` at `751d619b074e74e8f300824760169f94c56f1d5f`.
- `idl-go-repo` PR: `https://github.com/spark-harness/idl-go-repo/pull/4`
- `idl-go-repo` merged to `master` at `7926cfb849f41fa6ab082e703d65db958e58864a`.
- Argo checks observed passing for `idl-repo`: `spark/idl-contract-gate`, `spark/idl-delivery-readiness`, `spark/pr-metadata`.

## Buf Verification

Commands run from `/Users/forest/Code/spark/.worktrees/LEN-212/idl-repo` after `idl-repo v0.2.8` and `idl-go-repo v0.2.8` were published:

| Command | Result | Notes |
|---|---|---|
| `buf lint` | PASS | No output. |
| `buf breaking --against '.git#branch=master'` | PASS | No output. Baseline: `master`. |
| `buf generate --template buf.gen.go.yaml` | PASS after retry with `GOPROXY=direct` | First attempt failed while loading the Kratos v3 generator deprecation metadata from `proxy.golang.org` with EOF. The direct retry completed with no output. |
| `git status --short` in `idl-repo` | PASS | No dirty files after generation. |

Generator verified:

```text
github.com/go-kratos/kratos/cmd/protoc-gen-go-http/v3@v3.0.0-20260626125723-668db92c2c00
```

## Dependency Scan

Command:

```bash
rg -n "go-kratos/kratos/v2|protoc-gen-go-http/v2" apps/fides-bff packages/go/bffkit
```

Result: no matches.

## Decision

LEN-212 satisfies the release-bound contract rule: `fides-bff` consumes a formal generated Go contract tag and does not depend on local `replace`, pseudo-version, RC, or unpublished generated output.
