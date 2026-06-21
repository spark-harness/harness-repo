# LEN-41 Verification Evidence

## Scope

- Requirement: LEN-41
- Branch: `feature/LEN-41-lendora-applicant-idl`
- Verified at: 2026-06-21T10:36:59+08:00
- Scope verified:
  - `idl-repo` applicant proto path/package migration.
  - Existing Java artifact and Go module coordinates remain unchanged.
  - `idl-java-repo` generated `com.vesta.lendora.applicant.v1` classes while retaining `com.spark.contract:spark-idl-java`.
  - `idl-go-repo` generated `vesta/lendora/applicant/v1` package while retaining `github.com/spark-harness/idl-go-repo`.
  - `business-repo/services/backend/applicant-api` generated Java import migration.
  - `business-repo` contract dependency scanner remains valid for `spark-idl-java` and `idl-go-repo`.
  - `harness-repo/.service-matrix/dependencies.yaml` applicant proto path migration.
  - `janus` delivery verifier accepts LEN-41 release-bound peer and formal contract evidence.

## Commands

| Repo | Command | Result | Notes |
|---|---|---|---|
| `idl-repo` | `buf lint` | PASS | No lint issues. |
| `idl-repo` | `buf generate` | PASS | Generated applicant Java and Go outputs from `vesta/lendora/applicant/v1/auth.proto`. |
| `idl-repo` | `buf breaking --against .git#branch=master` | PASS | Current `FILE` breaking rule set did not report deletion failures. |
| `idl-java-repo` | `mvn -B test` | PASS | `spark-idl-java` compiles with generated Lendora applicant Java classes and existing user classes. |
| `idl-java-repo` | `mvn -B install -DskipTests` | PASS | Installed local `com.spark.contract:spark-idl-java:0.1.0-SNAPSHOT` for consumer source verification. |
| `idl-go-repo` | `go test ./...` | PASS | `github.com/spark-harness/idl-go-repo/vesta/lendora/applicant/v1` and existing user package compile. |
| `business-repo` | `python3 -m unittest tests/test_contract_dependency_scan.py` | PASS | 17 tests passed for existing artifact/module policy. |
| `business-repo` | `python3 scripts/contract_dependency_scan.py --mode master --path services/backend/applicant-api/pom.xml` | PASS | Existing `com.spark.contract:spark-idl-java` formal dependency is accepted by scanner. |
| `business-repo/packages/spring-starter` | `mvn -B install -DskipTests` | PASS | Local prerequisite for applicant-api verification; no source changes intended. |
| `business-repo/services/backend/applicant-api` | `mvn -B test` | FAIL | Historical pre-release check: resolved `spark-idl-java:0.1.0` did not contain `com.vesta.lendora.applicant.v1`. |
| `business-repo/services/backend/applicant-api` | `mvn -B test -Dspark.contract.version=0.1.0-SNAPSHOT` | PASS | 29 tests passed against locally generated `spark-idl-java` with Lendora applicant package. |
| `idl-repo` | `git tag -a v0.2.0 ... && git push origin v0.2.0` | PASS | Formal tag `v0.2.0` points to IDL commit `5909aa0289eb0a10df5259a00b131cb8949e5802`. |
| `idl-repo` | Publish Java IDL workflow run `27888287900` | PASS | Published `com.spark.contract:spark-idl-java:0.2.0` from `v0.2.0`. |
| `idl-repo` | Publish Go IDL workflow run `27888287898` | PASS | Published Go module tag `v0.2.0` in `spark-harness/idl-go-repo`. |
| `idl-repo` | `git tag -a v0.2.1 ... && git push origin v0.2.1` | PASS | Formal tag `v0.2.1` points to IDL master commit `5ae0eb6d9151477f358932996870e085ce2f8a6b`; `git merge-base --is-ancestor v0.2.1 origin/master` confirms it is reachable from `origin/master`. |
| `idl-repo` | Publish Java IDL workflow run `27890705526` | PASS | Published `com.spark.contract:spark-idl-java:0.2.1` from `v0.2.1`; run head SHA is `5ae0eb6d9151477f358932996870e085ce2f8a6b`. |
| `idl-repo` | Publish Go IDL workflow run `27890705528` | PASS | Published Go module tag `v0.2.1` in `spark-harness/idl-go-repo`; run head SHA is `5ae0eb6d9151477f358932996870e085ce2f8a6b`. |
| `idl-java-repo` | `gh api /orgs/spark-harness/packages/maven/com.spark.contract.spark-idl-java/versions --paginate --jq '.[].name'` | PASS | Maven versions include `0.2.0` and `0.2.1`. |
| `idl-go-repo` | `git ls-remote --tags origin 'v0.2.1'` | PASS | Remote Go tag `v0.2.1` exists at `f6f3a4a62fa04231756a24736c68acdc831bd938`. |
| `business-repo/services/backend/applicant-api` | `mvn -B -s <temporary-github-settings> test` | PASS | 29 tests passed against formal `spark-idl-java:0.2.1`; the temporary settings supplied GitHub Packages credentials and was removed after the run. |
| `janus` | `go test ./...` | PASS | Delivery verifier tests cover merged release PR evidence and remote release ref formal tag reachability. |
| `janus` | `go build -o /tmp/janus-len41-fixed ./cmd/janus` | PASS | Built Janus CLI from `feature/LEN-41-lendora-applicant-idl` commit `92af82c`. |
| `janus` | `/tmp/janus-len41-fixed delivery verify --workspace /Users/forest/Code/spark/.worktrees/LEN-41 --requirement LEN-41 --repo business-repo --base master --head feature/LEN-41-lendora-applicant-idl` | PASS | Release-readiness passed: contract scan `formal-only`, formal tag `v0.2.1` reachable from `idl-repo master`, Maven `0.2.1` exists, `harness-repo` has open release PR, and `idl-repo` is accepted as `release_pr_merged`. |

## Contract Shape

The new applicant proto is:

- Path: `idl-repo/vesta/lendora/applicant/v1/auth.proto`
- Package: `vesta.lendora.applicant.v1`
- Java package: `com.vesta.lendora.applicant.v1`
- Go package: `github.com/spark-harness/idl-go-repo/vesta/lendora/applicant/v1;applicantv1pb`

The following coordinates intentionally stayed unchanged:

- Java generated repo: `spark-harness/idl-java-repo`
- Java Maven artifact: `com.spark.contract:spark-idl-java`
- Go generated repo: `spark-harness/idl-go-repo`
- Go module: `github.com/spark-harness/idl-go-repo`

The following stayed unchanged:

- `ApplicantAuthService` RPC names.
- Request and response message names.
- Field names and field numbers.
- Applicant auth business behavior in `applicant-api`.
- `vesta/spark/user/*` source protos and generated `com.vesta.spark.user.v1` Java classes.
- `vesta/spark/user/v1` Go generated package.

## Residual Risks

- Removing old `vesta.spark.applicant.v1` is a namespace replacement. `buf breaking` currently passes under the repo rule set, and formal `0.2.1` contract publication evidence is recorded above.
- Formal `v0.2.0` remains immutable release history, but it points to the pre-squash feature commit and is superseded for release-bound business consumption by `v0.2.1`, whose IDL commit is reachable from `idl-repo` `origin/master`.
- Business PR delivery-readiness depends on Janus PR `spark-harness/janus#3`; until that PR is merged, business CI must build Janus from the same-name `feature/LEN-41-lendora-applicant-idl` branch.
