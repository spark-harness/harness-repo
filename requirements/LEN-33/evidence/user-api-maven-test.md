# LEN-33 user-api Maven Test Evidence

## Scope

- Requirement: `LEN-33`
- Repository: `business-repo`
- Branch: `feature/LEN-33`
- Working directory: `services/backend/user-api`
- Command: `mvn test`
- Run time: 2026-06-18 00:13 +08:00

## Result

`PASS`

Maven summary:

```text
Tests run: 36, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

Diff hygiene:

```text
git diff --check
<no output>
```

## Covered Acceptance

- AC1: Spring Boot application starts and `/actuator/health` reports `UP`.
- AC2: `user-api` has explicit Clean Architecture layer guidance in service README and layer README files.
- AC3: ArchUnit domain boundary test passes.
- AC4: `mvn test` is the local and CI command.
- AC5: No protobuf IDL, generated contract, business API, persistence schema, or business rule change was made.

## New Verification Points

- `UserApiApplicationSmokeTest` starts the app on a random HTTP port and calls `/actuator/health`.
- `DomainLayerArchitectureTest` prevents `domain` classes from depending on Spring, persistence, gRPC, adapter, or infrastructure packages.
- `pom.xml` uses Java 21 and includes Actuator plus ArchUnit test dependency.
- `user-api-ci.yml` runs `mvn test` on Java 21 for `services/backend/user-api/**` changes.

## Notes

Maven emitted cached GitHub Packages metadata warnings for `spark-spring-clean-architecture-starter` and `spark-idl-java`:

```text
status code: 401, reason phrase: Unauthorized
```

The build still resolved required artifacts from the local Maven cache and completed successfully. No new IDL dependency or generated contract was introduced by LEN-33.
