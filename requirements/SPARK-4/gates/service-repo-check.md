<!-- Generated from service-repo-check.gate.json. Do not edit blocking fields here. -->

# 服务仓库检查门禁

## 元数据

- Requirement: `SPARK-4`
- Gate: `service-repo-check`
- Stage: `4.3`
- Checked by: `service_repo_checker`
- Checked at: `2026-06-09T08:22:12+08:00`
- Result: `PASS`
- Blocks next stage: `false`

## 结论

服务仓库检查通过，SPARK-4 的 Harness、业务、IDL 和生成契约仓均处于同名需求分支并完成验证。

## 输入快照

| Path | SHA-256 |
| --- | --- |
| `requirements/SPARK-4/impact-analysis.md` | `421421a2b0a029afea0ddfaf2ab5cd682bf2a9b105e55f40f68d5acd6ea7c898` |
| `requirements/SPARK-4/design.md` | `575de62b5a7d2a86e725874dc634c6163002ecfab199caed8add5b95baa3aa09` |
| `requirements/SPARK-4/tasks.json` | `f2f972b1fc915d25d602ded004cc0e721767be50fbdbaf9e7d19a899a25c8365` |
| `.service-matrix/dependencies.yaml` | `77862a05e23a539cdb42d8229099ac1624283dd887d8a8b25537fd14bef5627d` |

## 检查项

| Item | Result | Evidence |
| --- | --- | --- |
| 涉及服务存在于服务矩阵 | `PASS` | user-api and aegis exist in .service-matrix/dependencies.yaml. |
| 业务仓、IDL 仓和生成契约仓分支对齐需求 ID | `PASS` | harness-repo, business-repo, idl-repo, and idl-java-repo are on feature/SPARK-4-update-username. |
| IDL 和服务验证通过 | `PASS` | buf lint, buf generate, buf breaking, idl-java mvn install, and user-api mvn test passed. |

## 阻塞问题

无。

## 警告

无。

## 豁免

- Required: `false`

## 外部证据

| Path | SHA-256 |
| --- | --- |
| `requirements/SPARK-4/evidence/buf-checks.md` | `7086931ed18672db5bbdbda90ca93a866127a00e94a5ce633198354ec97d7d08` |
| `requirements/SPARK-4/evidence/user-api-tests.md` | `c0887d9f81b1b170e6520397f5b899b20b699a581b7ef647d90dee01f017af8f` |

