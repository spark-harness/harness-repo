# LEN-137 Buf Checks

## Scope

- Requirement: `LEN-137`
- Task: `T2 / LEN-138 IDL 身份信息与步骤推进契约`
- IDL repo: `/Users/forest/Code/spark/.worktrees/LEN-137/idl-repo`
- Branch: `feature/LEN-137-identity-information`
- Checked at: `2026-06-28T22:42:00+08:00`

## Change Classification

Additive protobuf change:

- New applicant-api profile service and messages.
- New origination-api draft step service and messages.
- New fides-bff identity profile HTTP facade service and messages.
- No existing RPC, field number, field type or enum value is replaced or deleted.

## Commands

```text
buf lint
```

Result: PASS.

```text
buf generate
```

Result: PASS.

Note: `buf.gen.yaml` currently has an empty `plugins` list, so this command validates generation configuration but does not emit Java or Go generated contracts.

```text
buf generate --template buf.gen.java.yaml
```

Result: PASS.

Generated staging output:

- `../idl-java-repo/src/main/java/com/vesta/lendora/applicant/v1/*`
- `../idl-java-repo/src/main/java/com/vesta/lendora/fides_bff/v1/*`
- `../idl-java-repo/src/main/java/com/vesta/lendora/origination/v1/*`
- `../idl-java-repo/src/main/grpc-java/com/vesta/lendora/applicant/v1/ApplicantProfileServiceGrpc.java`
- `../idl-java-repo/src/main/grpc-java/com/vesta/lendora/origination/v1/OriginationDraftServiceGrpc.java`

```text
buf generate --template buf.gen.go.yaml
```

Result: PASS.

Generated staging output:

- `../.generated/idl-go/vesta/lendora/applicant/v1/profile*.go`
- `../.generated/idl-go/vesta/lendora/origination/v1/draft*.go`
- `../.generated/idl-go/vesta/lendora/fides-bff/v1/identity_profile*.go`

```text
buf breaking --against .git#branch=master
```

Result: PASS.

## Files

- `buf.yaml`
- `vesta/lendora/applicant/v1/profile.proto`
- `vesta/lendora/origination/v1/draft.proto`
- `vesta/lendora/fides-bff/v1/identity_profile.proto`

## Compatibility Notes

- fides-bff keeps the existing `vesta/lendora/fides-bff/v1` directory convention. `buf.yaml` extends the existing `PACKAGE_DIRECTORY_MATCH` ignore list for the new fides-bff proto, matching the existing `auth.proto` exception.
- `../idl-java-repo` in this local worktree is generated staging output, not an isolated generated-contract Git worktree.
- Generated contract publication completed as `v0.2.4`; business services and fides-web consume the published Java, Go and TypeScript artifacts recorded in `evidence/generated-artifacts.md`.
