# LEN-211 Local Verification

检查时间：2026-07-05T18:09:34+08:00

## Summary

LEN-211 的业务仓、共享 starter、Go BFF、Java quality 和 diff 检查已在本地通过。Maven 以离线模式执行；执行前清理过本机 `.m2` 中 stale `.lastUpdated` / resolver 元数据，并先将本次 `spring-starter` 安装到本地 Maven 仓库，以便服务测试消费同一分支的共享 starter。

## Commands

| Repo | Command | Result |
|---|---|---|
| business-repo/packages/java/spring-starter | `mvn -o -q test` | PASS，12 tests |
| business-repo/packages/java/spring-starter | `mvn -o -q install` | PASS，本地安装 starter artifact |
| business-repo/apps/applicant-api | `mvn -o -q test` | PASS，64 tests |
| business-repo/apps/quote-api | `mvn -o -q test` | PASS，23 tests |
| business-repo/apps/origination-api | `mvn -o -q test` | PASS，45 tests |
| business-repo/apps/fides-bff | `gofmt -w internal/data/quote_client.go internal/data/quote_client_test.go && go test ./internal/data -count=1` | PASS |
| business-repo | `python3 tooling/java-quality/tests/test_java_quality.py` | PASS，16 tests |
| business-repo | `git diff --check` | PASS |
| idl-repo | `git diff --check` | PASS |
| harness-repo | `git diff --check` | PASS |

## Notes

- `spring-starter` 和 quote/origination/applicant 测试输出包含预期的异常路径日志，例如 gRPC handler 测试中的 `IllegalStateException: boom`，命令退出码为 0。
- applicant-api 完整测试中出现 OTel exporter 对测试 endpoint 的连接错误日志，但测试断言和 Maven 结果通过；该日志来自测试中显式启用 `otel.traces.exporter=otlp` / `otel.logs.exporter=otlp`。
- Maven Central 在本机一度返回 403，GitHub Packages 返回 401；本轮最终验证使用已缓存依赖和本地安装的本分支 starter。
