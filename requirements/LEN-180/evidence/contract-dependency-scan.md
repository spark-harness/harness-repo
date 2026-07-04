# Contract Dependency Scan

## 2026-07-05T02:31:00+08:00

Formal IDL release:

- `idl-repo` PR: `spark-harness/idl-repo#15`
- `idl-repo` merge commit: `b2bf12ad55b64ad1bda858540ee2f50fd65c0957`
- `idl-repo` formal tag: `v0.2.7`
- Java artifact: `com.spark.contract:spark-idl-java:0.2.7`
- Java package version id: `62708020`
- `idl-go-repo` tag: `v0.2.7`

Business consumer:

- File: `business-repo/apps/origination-api/pom.xml`
- Property: `spark.contract.version=0.2.7`

Command:

```bash
python3 scripts/contract_dependency_scan.py --mode master --path apps/origination-api/pom.xml
```

Result: PASS

Output:

```text
No contract dependency violations found.
```

Conclusion:

- `origination-api` consumes a formal Java contract version.
- No master-bound SNAPSHOT, RC, pseudo-version, branch dependency, or local replacement is used for the generated contract.
