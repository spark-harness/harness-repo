# LEN-137 Service Test Evidence

## Scope

- Requirement: `LEN-137`
- Tasks: `T3`, `T4`, `T5`, `T6`
- Checked at: `2026-06-29T10:56:32+08:00`

## Commands

### fides-web

```text
pnpm test
```

Result: PASS.

Summary:

```text
Test Files  22 passed | 1 skipped (23)
Tests       86 passed | 1 skipped (87)
```

```text
pnpm lint
```

Result: PASS with warning.

Known warning:

```text
src/infrastructure/mobile-verification/mock-otp-auth-gateway.ts
37:22  warning  '_command' is defined but never used
```

```text
pnpm lint:deps
```

Result: PASS.

Summary:

```text
no dependency violations found (70 modules, 155 dependencies cruised)
```

```text
pnpm build
```

Result: PASS.

### fides-bff

```text
GIT_CONFIG_GLOBAL=<temporary-gh-credential-helper> \
GOPRIVATE=github.com/spark-harness/* \
GONOSUMDB=github.com/spark-harness/* \
GOPROXY=direct \
go test ./...
```

Result: PASS.

### applicant-api

```text
mvn test
```

Result: PASS.

Summary:

```text
Tests run: 60, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

### origination-api

```text
mvn test
```

Result: PASS.

Summary:

```text
Tests run: 31, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

## Notes

- Maven printed cached GitHub Packages metadata `401` warnings for a snapshot dependency, but resolved required dependencies from local cache and completed successfully.
- `origination-api` HTTP integration test now disables the unrelated gRPC server for that test scope, avoiding collisions with local long-running services on default gRPC ports.
- `origination-api` HTTP test quote fixture now uses a runtime future `validUntil` value. The previous fixed `2026-06-28T23:59:00Z` timestamp became expired on `2026-06-29` and made the valid-quote test return `410 GONE`.
- `fides-web` regression coverage now includes stale draft owner mismatch: when `draftPointer.applicantId` differs from the verified session applicant, the controller clears the pointer and creates a new draft instead of PATCHing the old application.
