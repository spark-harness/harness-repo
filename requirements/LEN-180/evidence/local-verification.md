# Local Verification

## 2026-07-05T02:31:00+08:00

Worktree: `/Users/forest/Code/spark/.worktrees/LEN-180/business-repo`

### Java Tests

Commands:

```bash
mvn -B -f packages/java/spring-starter/pom.xml test install
mvn -B -f apps/origination-api/pom.xml test
```

Result: PASS

Observed results:

- `spark-spring-clean-architecture-starter`: 12 tests, 0 failures, 0 errors.
- `origination-api`: 45 tests, 0 failures, 0 errors.
- `OriginationLoanApplicationGrpcAdapterTest`: 6 tests, 0 failures, 0 errors.
- `OriginationDraftGrpcAdapterTest`: 4 tests, 0 failures, 0 errors.

### Java Quality

Command:

```bash
mvn -B -f apps/origination-api/pom.xml spotless:check checkstyle:check
```

Result: PASS

Observed result:

- Spotless: 54 Java files clean.
- Checkstyle: 0 violations.

### Contract Dependency Scan

Command:

```bash
python3 scripts/contract_dependency_scan.py --mode master --path apps/origination-api/pom.xml
```

Result: PASS

Observed output:

```text
No contract dependency violations found.
```

### GitOps Rendering

Worktree: `/Users/forest/Code/spark/.worktrees/LEN-180/gitops-repo`

Commands:

```bash
kubectl kustomize apps/origination-api/overlays/dev-1
kubectl kustomize apps/origination-api/overlays/sta-1
```

Result: PASS

Observed rendered values in both dev-1 and sta-1:

- `SPARK_GRPC_SERVER_PORT: "9090"`
- `SPARK_ORIGINATION_CONSUL_GRPC_PORT: "9090"`
- Deployment container port `grpc: 9090`
- Service port `grpc: 9090`
- NetworkPolicy allows TCP `9090` for same-environment callers and Consul namespace.

### Notes

- `origination-api` business HTTP adapter remains present. Final internal business HTTP cleanup is deferred to `LEN-196`.
- `/health` and `/ready` HTTP adapters remain present.
