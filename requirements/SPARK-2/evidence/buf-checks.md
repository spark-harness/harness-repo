# Buf Checks

## Metadata

- Requirement ID: SPARK-2
- Checked At: 2026-06-03T23:06:49+08:00
- Branch: feature/SPARK-2-mobile-code-register

## Commands

```bash
cd /Users/forest/Code/spark/idl-repo
buf lint
buf generate

cd /Users/forest/Code/spark/idl-java-repo
mvn -B test install
```

## Result

- `buf lint`: PASS
- `buf generate`: PASS
- `mvn -B test install`: PASS

## Notes

- Added `vesta/spark/user/v1/auth.proto`.
- Generated Java classes under `idl-java-repo/src/main/java/com/vesta/spark/user/v1`.
- Generated gRPC stub `AuthServiceGrpc` under `idl-java-repo/src/main/grpc-java/com/vesta/spark/user/v1`.
