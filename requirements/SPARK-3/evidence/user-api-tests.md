# User API Test Evidence

Command:

```sh
mvn test
```

Working directory:

```text
business-repo/services/backend/user-api
```

Result:

```text
BUILD SUCCESS
Tests run: 16, Failures: 0, Errors: 0, Skipped: 0
```

Coverage relevant to SPARK-3:

- `HealthHttpAdapterTest.ready_whenCalled_shouldReturnReadinessStatus`
- `HealthHttpAdapterTest.health_whenCalled_shouldReturnServiceStatus`
