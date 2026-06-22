# LEN-43 Buf Checks

## Scope

- Requirement: LEN-43
- IDL repo: `/Users/forest/Code/spark/.worktrees/LEN-43/idl-repo`
- Proto: `vesta/lendora/fides-bff/v1/auth.proto`
- Change type: additive new service / RPC / message

## Commands

Run on 2026-06-21:

```bash
buf dep update
buf lint
buf generate
buf breaking --against .git#branch=master
```

Result: all commands exited 0 after adding the `buf.build/googleapis/googleapis`
dependency for `google/api/annotations.proto`.

## Notes

- `buf.lock` pins `buf.build/googleapis/googleapis` at commit
  `c17df5b2beca46928cc87d5656bd5343`.
- `buf.yaml` contains a targeted `PACKAGE_DIRECTORY_MATCH` lint exception for
  `vesta/lendora/fides-bff/v1/auth.proto` because the approved source path uses
  `fides-bff` while protobuf package syntax requires `fides_bff`.
- Go generated verification output was produced under:

```text
/Users/forest/Code/spark/.worktrees/LEN-43/.generated/idl-go/vesta/lendora/fides-bff/v1/auth.pb.go
/Users/forest/Code/spark/.worktrees/LEN-43/.generated/idl-go/vesta/lendora/fides-bff/v1/auth_grpc.pb.go
```

- `buf generate` also wrote Java generated side effects under
  `/Users/forest/Code/spark/.worktrees/LEN-43/idl-java-repo` because the global
  generation template includes Java outputs. LEN-43 does not edit
  `idl-java-repo`; that generated side-effect directory was removed and is not
  part of the deliverable.
