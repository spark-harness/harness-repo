# SPARK-5 Buf Checks

## Context

- Requirement: `SPARK-5`
- Checked at: `2026-06-10T08:35:49+08:00`
- Working directory: `idl-repo`
- Branch: `feature/SPARK-5-user-disable-restore`

## Commands

```bash
buf lint
buf generate
buf breaking --against .git#branch=master
```

## Result

- `buf lint`: PASS
- `buf generate`: PASS
- `buf breaking --against .git#branch=master`: PASS

## Contract Changes

- Updated `vesta/spark/user/v1/profile.proto`.
- Added `ProfileService/DisableUser`.
- Added `ProfileService/RestoreUser`.
- Added `DisableUserRequest`, `DisableUserResponse`, `RestoreUserRequest`, and `RestoreUserResponse`.
- Existing `UpdateUsername` request and response fields were not modified.

## Generated Outputs

- Updated Java generated contract files under `idl-java-repo/src/main/java/com/vesta/spark/user/v1`.
- Updated Java gRPC stub under `idl-java-repo/src/main/grpc-java/com/vesta/spark/user/v1/ProfileServiceGrpc.java`.
- Updated Go generated output under `.generated/idl/go/vesta/spark/user/v1/profile.pb.go`.

## Notes

Initial `buf lint` rejected a shared `UserStatusResponse` because Buf requires RPC response message names to match each RPC. The final contract uses separate `DisableUserResponse` and `RestoreUserResponse` messages.
