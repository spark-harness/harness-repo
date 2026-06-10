# SPARK-5 User API Tests

## Context

- Requirement: `SPARK-5`
- Checked at: `2026-06-10T08:35:49+08:00`
- Service: `user-api`
- Working directory: `business-repo/services/backend/user-api`
- Branch: `feature/SPARK-5-user-disable-restore`

## Command

```bash
mvn test
```

## Result

- Build: PASS
- Tests run: 34
- Failures: 0
- Errors: 0
- Skipped: 0

## Coverage Notes

- `RegisterOrLoginUseCaseTest` covers disabled user login rejection and restored user login success.
- `SetUserEnabledUseCaseTest` covers successful disable, successful restore, blank `user_id`, and missing user.
- `AuthGrpcAdapterTest` covers disabled user login mapped to gRPC `PERMISSION_DENIED`.
- `ProfileGrpcAdapterTest` covers disable/restore success, `INVALID_ARGUMENT`, and `NOT_FOUND`.
