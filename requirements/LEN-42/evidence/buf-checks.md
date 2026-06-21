# LEN-42 Buf Checks Evidence

## Scope

- Requirement: LEN-42
- Branch: `feature/LEN-42-buf-plugin-version-lock`
- Verified at: 2026-06-21T13:14:03+08:00
- IDL change type: config-only

## Remote Plugin Version Baseline

| Plugin | Locked version |
|---|---|
| `buf.build/protocolbuffers/go` | `v1.36.11` |
| `buf.build/grpc/go` | `v1.6.2` |
| `buf.build/protocolbuffers/java` | `v35.1` |
| `buf.build/grpc/java` | `v1.82.0` |

## Commands

Run from `/Users/forest/Code/spark/.worktrees/LEN-42/idl-repo`.

| Command | Result | Notes |
|---|---|---|
| `buf lint` | PASS | No lint output. |
| `buf generate` | PASS | Generated into configured output paths under `.worktrees/LEN-42/.generated/idl-go` and `.worktrees/LEN-42/idl-java-repo`; these verification outputs were removed because generated contract repos are not in scope. |
| `buf breaking --against .git#branch=master` | PASS | No breaking output. |

## Generated Output Handling

`buf generate` produced 48 verification files under:

- `.worktrees/LEN-42/.generated/idl-go`
- `.worktrees/LEN-42/idl-java-repo`

These files were not committed. LEN-42 only locks Buf remote plugin versions in `idl-repo`; it does not update generated Java or Go contract repositories.

## Locking Boundary

`buf.lock` is not created by this requirement. Current `idl-repo/buf.yaml` has no `deps`, and `buf.lock` would only lock external proto module dependencies declared in `buf.yaml`.

Remote code generation plugins are locked in `buf.gen.yaml` and `buf.gen.go.yaml` via `remote:<plugin-version>`.

## Residual Risk

`revision` is intentionally not set. The task confirmed plugin versions from BSR pages, but did not establish a source of truth for each plugin version's BSR revision sequence. A future ticket can add revision locking once that source is defined.
