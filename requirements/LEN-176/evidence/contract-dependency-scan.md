# Contract Dependency Scan

验证时间：2026-07-05T01:19:15+08:00

工作目录：`/Users/forest/Code/spark/.worktrees/LEN-176/business-repo`

```bash
python3 scripts/contract_dependency_scan.py --mode master --path apps/quote-api/pom.xml
```

结果：通过。

```text
No contract dependency violations found.
```

## Formal Contract Evidence

- `idl-repo` PR: https://github.com/spark-harness/idl-repo/pull/14
- `idl-repo` merge commit: `042af3374be47e6e2854adab79930260945f2403`
- Formal IDL tag: `v0.2.6`
- Java artifact: `com.spark.contract:spark-idl-java:0.2.6`
- Maven package version id: `62707495`
- Go generated contract tag: `spark-harness/idl-go-repo` `v0.2.6`

## Decision

`apps/quote-api/pom.xml` 已从 `0.1.0-SNAPSHOT` 切换到 formal `0.2.6`。master-bound business change 不再消费 SNAPSHOT contract。
