# LEN-129 Implementation Verification Evidence

## Scope

- Requirement: `LEN-129`
- Business repo: `/Users/forest/Code/spark/.worktrees/LEN-129/business-repo`
- Business branch: `feature/LEN-129-fides-bff-startup-config`
- Service: `apps/fides-bff`
- Harness repo: `/Users/forest/Code/spark/.worktrees/LEN-129/harness-repo`
- Harness branch: `feature/LEN-129-fides-bff-startup-config`

## Implementation Summary

- Added startup config loader in `apps/fides-bff/cmd/fides-bff/config_loader.go`.
- Kept `configs/config.yaml` as default lowest-priority config source.
- Added local `.env` loading that does not override existing process environment variables.
- Added explicit no-prefix environment allowlist mapped to Kratos config paths.
- Added Kratos `contrib/config/consul/v2` Consul KV YAML startup config source.
- Disabled Consul config watch to keep this requirement startup-only.
- Added remote YAML / JSON pre-validation before passing Consul values to Kratos decoder.
- Added `.env.example`, `.gitignore` update, and README config guidance.

## Verification Commands

All commands were run from:

```text
/Users/forest/Code/spark/.worktrees/LEN-129/business-repo/apps/fides-bff
```

| Command | Result |
|---|---|
| `go test ./cmd/fides-bff -run TestLoadBootstrap -count=1` | PASS |
| `go test ./... -count=1` | PASS |
| `go vet ./...` | PASS |
| `make lint` | PASS, `golangci-lint run ./...`, `0 issues` |
| `make build` | PASS |

The focused config tests also clean up `.env`-loaded process environment keys so test execution does not leak allowlisted values into later cases.

## Acceptance Coverage

| AC | Evidence |
|---|---|
| AC1 | `TestLoadBootstrap_DefaultConfigOnly` covers default `configs/config.yaml` load without `.env`, env, or Consul config. |
| AC2 | `TestLoadBootstrap_EnvFileDoesNotOverrideExistingEnvironment` covers `.env` loading for allowlisted keys. |
| AC3 | `TestLoadBootstrap_EnvFileDoesNotOverrideExistingEnvironment` covers real environment priority over `.env`. |
| AC4 | `TestLoadBootstrap_ConsulOverridesFileAndEnvironment` covers Consul KV YAML overriding file and environment-mapped values. |
| AC5 | `TestLoadBootstrap_AllowlistIgnoresUnrelatedEnvironment` covers unrelated host environment variables being ignored. |
| AC6 | `TestLoadBootstrap_DefaultConfigOnly` and default `CONFIG_CONSUL_ENABLED=false` path cover startup without Consul config source. |
| AC7 | `TestLoadBootstrap_ConsulEnabledMissingKeyFails`, `TestLoadBootstrap_InvalidConsulBootstrapFails`, and `TestLoadBootstrap_ErrorDoesNotExposeSecrets` cover failure behavior and secret-safe error text. |
| AC8 | Config loader tests cover `.env`, allowlist mapping, priority merge, Consul missing/error paths, startup-only watch disable, and secret boundary checks. |
| AC9 | `.env.example` and `README.md` document config priority, Consul KV path, bootstrap source, secret boundary, and no hot reload. |

## Contract / IDL Evidence

- IDL impact: `no`.
- No `.proto` files changed.
- No generated contract repositories changed.
- No HTTP route or external API contract changed.

## Security Evidence

- `.env` is ignored in `apps/fides-bff/.gitignore`.
- `.env.example` contains only placeholders and non-secret local defaults.
- README states Consul KV stores only non-secret runtime config.
- Test-only sentinel values such as `super-secret-token` are fake and used only to assert redaction boundaries.
