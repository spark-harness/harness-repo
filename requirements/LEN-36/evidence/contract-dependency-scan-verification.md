# LEN-36 Contract Dependency Scan Verification

## Scope

- business-repo scanner: `scripts/contract_dependency_scan.py`
- scanner config: `config/contract-dependencies.json`
- workflow: `.github/workflows/contract-dependency-scan.yml`
- source rule: `context/team/contract-versioning.md` from LEN-35

## Commands

| Command | Result | Notes |
|---|---|---|
| `python3 -m unittest tests/test_contract_dependency_scan.py` | PASS | 14 fixture tests cover Java formal, Java dependencyManagement formal, Java RC pass/fail, Java SNAPSHOT fail, Go formal, Go RC pass/fail, Go pseudo-version fail, Go local replace fail, go.sum mapping, and non-dependency changed-file scans. |
| `python3 scripts/contract_dependency_scan.py --mode master --root tests/contract_dependency_scan/fixtures/java-formal-pass` | PASS | Representative master formal pass. |
| `python3 scripts/contract_dependency_scan.py --mode rc --root tests/contract_dependency_scan/fixtures/java-rc-pass` | PASS | Representative RC pass. |
| `python3 scripts/contract_dependency_scan.py --mode master --path .github/workflows/contract-dependency-scan.yml --path scripts/contract_dependency_scan.py --path config/contract-dependencies.json` | PASS | Matches this PR shape: scanner/config/workflow changes do not scan historical dependency files. |
| `python3 scripts/contract_dependency_scan.py --mode master --path services/backend/user-api/pom.xml` | BLOCKED | If a PR touches `user-api` dependency file, existing `com.spark.contract:spark-idl-java:0.1.0-SNAPSHOT` is rejected. |
| `python3 scripts/contract_dependency_scan.py --mode master --root .` | BLOCKED | Manual full scan still exposes existing `services/backend/user-api/pom.xml` SNAPSHOT debt. |

## Current Blocking Finding

```text
file=services/backend/user-api/pom.xml dependency=com.spark.contract:spark-idl-java version=0.1.0-SNAPSHOT rule=snapshot_not_allowed message=Contract SNAPSHOT dependencies are not allowed in CI gates.
```

This is expected existing debt, not a blocker for landing the scanner itself. LEN-36 intentionally does not implement contract publication or change business service dependencies. The debt becomes blocking for PRs that touch the dependency file or for manual full-repo scans until a formal `spark-idl-java` version exists and `user-api` is updated to consume it.
