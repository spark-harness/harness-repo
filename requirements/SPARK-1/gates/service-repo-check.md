<!-- Generated from service-repo-check.gate.json. Do not edit blocking fields here. -->

# 服务仓库检查门禁

## 元数据

- Requirement: `SPARK-1`
- Gate: `service-repo-check`
- Stage: `4.3`
- Checked by: `service_repo_checker`
- Checked at: `2026-06-03T00:00:00+08:00`
- Result: `BLOCKED`
- Blocks next stage: `true`

## 结论

服务、IDL 和证据路径已就位，但三仓分支策略不满足要求，不能进入 4.4 编码循环或合并。

## 输入快照

| Path | SHA-256 |
| --- | --- |
| `requirements/SPARK-1/impact-analysis.md` | `193ee06ec9b65494c2291e11d87d050b90ceeb3a04246bfd7479eeabe20d54fa` |
| `requirements/SPARK-1/design.md` | `84f0a198fde90416e02947de09c26665e5d55a3cc013d420fe6084f7c2a352e3` |
| `requirements/SPARK-1/tasks.json` | `1953ad6e202fb76bf58d8a2078453ba398825d400dbabf2483a7811ed9f00453` |
| `.service-matrix/dependencies.yaml` | `77862a05e23a539cdb42d8229099ac1624283dd887d8a8b25537fd14bef5627d` |

## 检查项

| Item | Result | Evidence |
| --- | --- | --- |
| 涉及服务存在于服务矩阵 | `PASS` | user-api and aegis exist in .service-matrix/dependencies.yaml. |
| repo_path 能解析到实际业务仓目录 | `PASS` | ../business-repo/services/backend/user-api and ../business-repo/services/frontend/aegis exist. |
| IDL 仓和 Buf v2 配置已就位 | `PASS` | ../idl-repo/buf.yaml, ../idl-repo/buf.gen.yaml, and ../idl-repo/vesta/spark/user/v1/ping.proto exist. |
| Harness 仓、业务仓、IDL 仓分支必须包含需求 ID | `BLOCKED` | Current branch snapshot is master/master/master; none contains SPARK-1. |

## 阻塞问题

| Issue | Required action | Owner |
| --- | --- | --- |
| 三仓当前都在 master 分支，不满足需求分支策略。 | 在 harness-repo、business-repo、idl-repo 切到同名需求分支，例如 feature/SPARK-1-harness-lifecycle，再重新生成本门禁。 | `Harness Team` |

## 警告

无。

## 豁免

- Required: `false`

## 外部证据

| Path | SHA-256 |
| --- | --- |
| `requirements/SPARK-1/evidence/buf-checks.md` | `81f157579a5d560b0de0096aec07006262e9d6740136c762c359ea040ecc1bb7` |
| `requirements/SPARK-1/evidence/user-api-tests.md` | `2ede6b1b605a799681496bd5c4dc2a23159029c480d0d113762b6b07ff680596` |

