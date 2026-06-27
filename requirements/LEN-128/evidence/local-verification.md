# Local Verification

## Commands

| Command | Repo | Result | Evidence |
|---|---|---|---|
| `janus gate validate requirements/LEN-128/gates/requirement-review.gate.json` | harness-repo | PASS | `valid` |
| `janus gate validate requirements/LEN-128/gates/design-review.gate.json` | harness-repo | PASS | `valid` |
| `janus gate validate requirements/LEN-128/gates/dev-entry.gate.json` | harness-repo | PASS | `valid` |
| `janus gate validate requirements/LEN-128/gates/service-repo-check.gate.json` | harness-repo | PASS | `valid` |
| `mvn -Dtest=ApplicantConfigurationModelTest test` | business-repo/apps/applicant-api | PASS | 4 tests, 0 failures |
| `mvn test` | business-repo/apps/applicant-api | PASS | 47 tests, 0 failures |
| `kubectl kustomize apps/applicant-api/overlays/{lendora-sta,prod,sta1,sta2}` | gitops-repo | PASS | all four overlays rendered |
| `rg 'APPLICANT_DB_URL\|APPLICANT_DB_USERNAME\|APPLICANT_DB_PASSWORD\|APPLICANT_REDIS\|APPLICANT_CONSUL\|APPLICANT_TOKEN_SECRET\|APPLICANT_SERVICE_ADDRESS\|APPLICANT_GRPC_PORT' rendered overlays` | gitops-repo | PASS | no old short env aliases found |
| `rg 'password\|token-secret\|headers\|secret' apps/applicant-api/base/consul-config.yaml` | gitops-repo | PASS | no sensitive key in Consul YAML |
| `git diff --check` | harness-repo / business-repo / gitops-repo | PASS | no whitespace errors |

## Requirement Coverage

| Acceptance | Evidence |
|---|---|
| AC1 | `application.yml` keeps local defaults; README documents local-only default boundary. |
| AC2 | `spring.config.import` imports optional Consul Config; GitOps adds non-secret Consul YAML writer; `ApplicantConfigurationModelTest` covers Consul property source override. |
| AC3 | `ApplicantConfigurationModelTest` proves canonical env overrides Consul property source. |
| AC4 | `.env.example` and README use canonical relaxed binding env names. |
| AC5 | `ApplicantAuthConfigurationTest` and `ApplicantConfigurationModelTest` cover fail-fast without exposing secret values. |
| AC6 | `mvn test`, GitOps overlay render, old alias search, and gate validation all passed. |

## Notes

- Maven reported cached GitHub Packages metadata 401 warnings for `spark-spring-clean-architecture-starter` snapshot metadata, but dependency resolution used local artifacts and the test suite completed successfully.
- `kustomize` binary is not installed on this host; verification used `kubectl kustomize`.
