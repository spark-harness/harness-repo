# LEN-12 applicant-api 测试证据

## Scope

- Requirement: `LEN-12`
- Branch: `feature/applicant-api/LEN-12`
- Business repo: `.worktrees/LEN-12/business-repo`
- Service: `services/backend/applicant-api`

## Preconditions

`applicant-api` 当前消费同分支本地生成契约和 starter snapshot。运行服务测试前，本地安装：

```bash
cd /Users/forest/Code/spark/.worktrees/LEN-12/idl-java-repo
mvn install -DskipTests

cd /Users/forest/Code/spark/.worktrees/LEN-12/business-repo/packages/spring-starter
mvn install -DskipTests
```

Results:

- `idl-java-repo mvn install -DskipTests`: PASS.
- `packages/spring-starter mvn install -DskipTests`: PASS.

说明：`idl-java-repo` 本地安装只用于开发机验证。LEN-12 的正式交付不手工提交或推送
`idl-java-repo` 生成物；Java contract artifact 应由 `idl-repo` 的
`sync-java-idl` CI 在同名分支生成、编译、推送并触发发布。

## Command

```bash
cd /Users/forest/Code/spark/.worktrees/LEN-12/business-repo/services/backend/applicant-api
mvn test
```

## Result

PASS.

Maven summary:

```text
Tests run: 29, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

## Coverage

- `ApplicantAuthUseCaseTest`: validates Hong Kong phone acceptance, non-Hong Kong rejection, OTP cooldown, expiration, wrong-code attempts, lockout, applicant find-or-create, access/refresh TTL, refresh non-rolling behavior, and idempotency replay.
- `ApplicantAuthGrpcAdapterTest`: validates generated applicant gRPC contract integration and error mapping for send, verify, and refresh flows.
- `RedisAuthRepositoryTest`: validates Redis-backed OTP challenge TTL/cooldown, refresh token expiry, idempotency replay, and idempotency conflict behavior through the runtime state port implementations.
- `JdbcApplicantRepositoryTest`: validates durable applicant find-or-create behavior and stable applicant ID for the same phone number.
- `ApplicantAuthConfigurationTest`: validates production/runtime fail-fast rules for test OTP provider and HMAC token secret.
- `ApplicantAuthTelemetryTest`: validates low-cardinality success/failure metrics with stable operation/result/error_code labels.
- `HealthHttpAdapterTest`: validates service health/readiness endpoints.
- `ApplicantApiApplicationSmokeTest`: validates Spring Boot context startup and confirms the default in-memory profile does not create a DataSource.
- `DomainLayerArchitectureTest`: validates domain layer dependency boundary.

## Known Limits

- Redis-backed runtime state, JDBC applicant persistence, HMAC token signing,
  and production test-provider fail-fast are implemented and covered by
  service tests.
- T7 runtime safety and observability hardening are covered for production
  fail-fast checks, Redis health profile behavior, Redis timeout config,
  low-cardinality metrics, current span error_code marking, and sensitive-field
  logging review. Full dashboard and alert wiring remain deployment work.

## Rebase Verification

After rebasing LEN-12 worktrees onto `origin/master` on 2026-06-20, the same
service test command was rerun and passed.

## T6/T7 Verification

On 2026-06-20, after implementing Redis/JDBC runtime adapters, HMAC token
service, runtime mode configuration, Redis health profile behavior, and
production fail-fast checks, the same service test command was rerun and
passed:

```text
Tests run: 29, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

## Generated Contract Runtime Alignment Verification

On 2026-06-20, a local generated-contract verification run found that the
current remote Java generator emits protobuf Java `4.35.1`. A local
`applicant-api` test run failed in `ApplicantAuthGrpcAdapterTest` when that
gencode was installed with a generated-contract runtime still resolving
`protobuf-java 4.35.0`:

```text
Detected incompatible Protobuf Gencode/Runtime versions when loading SendOtpRequest:
gencode 4.35.1, runtime 4.35.0.
```

Local verification fix:

- generated and installed a local Java contract artifact whose protobuf runtime
  was not older than the generated applicant gencode;
- reran `mvn install -DskipTests` in `.worktrees/LEN-12/idl-java-repo`;
- reran `mvn test` in `.worktrees/LEN-12/business-repo/services/backend/applicant-api`.

The generated Java contract repo is not a manual LEN-12 deliverable. The
source-of-truth delivery path is the `idl-repo` CI sync workflow, which must
generate and publish a compatible Java contract artifact for the same branch.
本地 `mvn test` 结果依赖开发机 `.m2` 中安装过的临时 generated-contract artifact；
CI 结果以 `idl-repo` sync 生成并发布后的 artifact 为准。

Final result:

```text
Tests run: 29, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

## Formal Contract Consumption Verification

After `idl-repo` formal tag `v0.1.0` published
`com.spark.contract:spark-idl-java:0.1.0`, `applicant-api` was changed to
consume the formal Maven artifact instead of `0.1.0-SNAPSHOT`.

Contract dependency scan:

```bash
cd /Users/forest/Code/spark/.worktrees/LEN-12/business-repo
python3 scripts/contract_dependency_scan.py --mode master --path services/backend/applicant-api/pom.xml
```

Result: PASS.

Service test with GitHub Packages credentials supplied through a temporary
Maven settings file:

```bash
cd /Users/forest/Code/spark/.worktrees/LEN-12/business-repo/services/backend/applicant-api
mvn -s /private/tmp/len12-maven-settings/settings.xml test
```

Result: PASS.

Maven downloaded `com.spark.contract:spark-idl-java:0.1.0` from GitHub
Packages and the test summary remained:

```text
Tests run: 29, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```
