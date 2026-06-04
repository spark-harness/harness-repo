# User API Tests

## Metadata

- Requirement ID: SPARK-2
- Checked At: 2026-06-03T23:08:21+08:00
- Branch: feature/SPARK-2-mobile-code-register

## Command

```bash
cd /Users/forest/Code/spark/business-repo/services/backend/user-api
mvn -B test
```

## Result

PASS

```text
Tests run: 15, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

## Covered Acceptance Criteria

- AC1: `RegisterOrLoginUseCaseTest` covers first mobile registration.
- AC2: `RegisterOrLoginUseCaseTest` covers repeated mobile returning existing user.
- AC3: `RegisterOrLoginUseCaseTest` covers invalid mobile rejection.
- AC4: `RegisterOrLoginUseCaseTest` covers wrong verification code rejection.
- AC5: `AuthGrpcAdapterTest` covers successful gRPC registration response.
- AC6: `AuthGrpcAdapterTest` covers gRPC `INVALID_ARGUMENT`.
