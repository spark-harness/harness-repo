# LEN-9 Local Verification Evidence

Checked at: 2026-06-28T04:27:13+08:00

## Scope

- business-repo: `apps/origination-api`
- business-repo: `tooling/java-quality/projects.yaml`
- business-repo: `tooling/java-quality/config/spotbugs-exclude.xml`
- harness-repo: `.service-matrix/dependencies.yaml`
- harness-repo: `requirements/LEN-9`

## Commands

| Command | Working directory | Result | Evidence |
|---|---|---|---|
| `mvn test -q` | `business-repo/apps/origination-api` | PASS | 19 tests passed. |
| `mvn package -DskipTests -q` | `business-repo/apps/origination-api` | PASS | Service jar packaging succeeded. |
| `python3 tooling/java-quality/java_quality.py plan apps/origination-api/pom.xml apps/origination-api/src/main/java/com/spark/origination/bootstrap/OriginationApiApplication.java tooling/java-quality/projects.yaml` | `business-repo` | PASS | Project graph selects `origination-api`; because `projects.yaml` changed, all Java projects are selected for full graph planning. |
| `python3 tooling/java-quality/java_quality.py run-project spring-starter` | `business-repo` | PASS | Installs `spark-spring-clean-architecture-starter` snapshot into `.worktrees/LEN-9/.m2` for downstream quality. |
| `python3 tooling/java-quality/java_quality.py run-project origination-api` | `business-repo` | PASS | Spotless, Checkstyle, 19 tests, and SpotBugs passed. |

## Behavior Covered

- `POST /api/v1/loan-applications` creates draft with `status=draft` and `currentStep=loan_request`.
- `GET /api/v1/loan-applications/{applicationId}` returns loan and acceptedQuote for prefill.
- `PATCH /api/v1/loan-applications/{applicationId}` updates loan terms and acceptedQuote without advancing current step.
- Missing `Idempotency-Key` maps to `idempotency_key_required`.
- Same idempotency key and same request replays the original application.
- Same idempotency key and different request is rejected as `validation_error`.
- Cross-applicant access is rejected.
- quote not found, expired, forbidden and unavailable paths map to stable errors.
- `HttpQuoteGateway` forwards `x-applicant-id`, `traceparent`, and `tracestate` to quote-api internal read.
- JDBC migration, save, update, read, and idempotency conflict behavior are covered with H2 PostgreSQL mode.

## Deferred Scope

- Kubernetes deployment, application DB provisioning, readiness in cluster, and service discovery are LEN-134.
- BFF origination facade is LEN-133.
- Frontend Continue silent save is LEN-11.
