# Local Verification

## Scope

验证 LEN-151 对 `applicant-api`、`quote-api`、`origination-api` 的健康检查 DB 探活噪音修复。

## Root Cause

静态证据显示健康检查 DB 噪音来自两类路径：

- `quote-api` 和 `origination-api` 配置中 `management.health.db.enabled=true`。
- 三个 Java 服务存在自定义 JDBC `RuntimeDependencyProbe`，在 readiness 路径执行 `select 1`。

## Failing Baseline

以下命令在实现前失败，证明旧实现仍启用 DB health / JDBC health probe：

```bash
mvn -Dtest=ApplicantConfigurationModelTest,RedisJdbcApplicationWiringTest,ReadinessHttpAdapterTest test
mvn -Dtest=QuoteConfigurationModelTest,QuoteApplicationWiringTest,HealthHttpAdapterTest test
mvn -Dtest=OriginationConfigurationModelTest,OriginationApplicationWiringTest test
```

失败点：

- applicant-api 缺少 `management.health.db.enabled=false`，且装配 `JdbcRuntimeDependencyProbe`。
- quote-api 装配 `JdbcRuntimeDependencyProbe`，且 DB health 为 true。
- origination-api 装配 `JdbcRuntimeDependencyProbe`，且 DB health 为 true。

## Verification Commands

```bash
mvn -Dtest=ApplicantConfigurationModelTest,RedisJdbcApplicationWiringTest,ReadinessHttpAdapterTest test
mvn -Dtest=QuoteConfigurationModelTest,QuoteApplicationWiringTest,HealthHttpAdapterTest test
mvn -Dtest=OriginationConfigurationModelTest,OriginationApplicationWiringTest test
mvn test
```

## Results

| Module | Command | Result |
|---|---|---|
| `apps/applicant-api` | `mvn -Dtest=ApplicantConfigurationModelTest,RedisJdbcApplicationWiringTest,ReadinessHttpAdapterTest test` | PASS, 9 tests |
| `apps/quote-api` | `mvn -Dtest=QuoteConfigurationModelTest,QuoteApplicationWiringTest,HealthHttpAdapterTest test` | PASS, 7 tests |
| `apps/origination-api` | `mvn -Dtest=OriginationConfigurationModelTest,OriginationApplicationWiringTest test` | PASS, 6 tests |
| `apps/applicant-api` | `mvn test` | PASS, 61 tests |
| `apps/quote-api` | `mvn test` | PASS, 20 tests |
| `apps/origination-api` | `mvn test` | PASS, 37 tests |

## Notes

- Maven emitted GitHub Packages metadata warnings for cached / unauthorized SNAPSHOT metadata lookup, but dependencies resolved from local cache and test goals completed.
- `quote-api` full test initially exposed a test isolation issue: the new wiring test reused the default `jdbc:h2:mem:quote` database name. The test was corrected to use `jdbc:h2:mem:quote-wiring`, after which full `mvn test` passed.
- No `.proto`, Buf, generated contract, repository, migration, or business API files changed.
