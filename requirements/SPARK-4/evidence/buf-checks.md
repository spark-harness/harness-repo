# SPARK-4 Buf Evidence

## Context

- Requirement: SPARK-4
- Checked at: 2026-06-09T08:22:10+08:00
- Contract file: `idl-repo/vesta/spark/user/v1/profile.proto`
- Generated Java contracts: `idl-java-repo/src/main/java` and `idl-java-repo/src/main/grpc-java`
- Generated Go contracts: `.generated/idl/go`

## Commands

| Command | Working Directory | Result |
|---|---|---|
| `buf lint` | `idl-repo` | PASS |
| `buf generate` | `idl-repo` | PASS |
| `buf breaking --against .git#branch=master` | `idl-repo` | PASS |
| `mvn install` | `idl-java-repo` | PASS |

## Notes

- `ProfileService/UpdateUsername` is additive.
- Existing `PingService` and `AuthService` contracts were not deleted or modified.
