---
requirement_id: "SPARK-2"
gate_id: "service-repo-check"
gate_name: "服务仓库检查门禁"
stage: "4.3"
checked_by: "service_repo_checker"
checked_at: "2026-06-03T23:09:00+08:00"
result: "BLOCKED"
blocks_next_stage: true
---

<!-- Generated from service-repo-check.gate.json. Do not edit blocking fields here. -->

# 服务仓库检查门禁

## 结论

机器检查通过，但尚未获得人工服务仓库检查批准，不能进入编码循环或合并。

## 输入快照

| Path | SHA-256 |
| --- | --- |
| `requirements/SPARK-2/impact-analysis.md` | `ed6338609b0482ede50a6029366a3577701e6b0ba2f4aa68a321eb5aa8769b9f` |
| `requirements/SPARK-2/design.md` | `caed5bb615c33b6e8fcb33829d2e0d2208e502a42c770f5f24e5f8f16b0773aa` |
| `requirements/SPARK-2/tasks.json` | `abf6091a70aa6cc9de06f7b0c31b0ec97b21514e018b211331a6f7a0899dcc1d` |
| `.service-matrix/dependencies.yaml` | `77862a05e23a539cdb42d8229099ac1624283dd887d8a8b25537fd14bef5627d` |
| `context/project/spark/user/current-state.md` | `eafb882b61d68cb32cd41a4fba632e601e1398e98973f6d6aedbd198614a19e4` |
| `context/harness-framework/gate-policy.md` | `e2af35b2c1e0eff8aa9ee3ea854cde58e59f44d84b27026ce98f781610a176fa` |
| `context/harness-framework/gate-implementation.md` | `4017a3e9a1a9e6413b646662a2f29436b7fba117e22fa4043d2132d5c819dafa` |

## 检查项

| Item | Result | Evidence |
| --- | --- | --- |
| 涉及服务存在于服务矩阵 | `PASS` | user-api and aegis exist in .service-matrix/dependencies.yaml. |
| repo_path 能解析到实际业务仓目录 | `PASS` | ../business-repo/services/backend/user-api and ../business-repo/services/frontend/aegis exist. |
| IDL 仓和 Buf v2 配置已就位 | `PASS` | ../idl-repo/buf.yaml, ../idl-repo/buf.gen.yaml, and ../idl-repo/vesta/spark/user/v1/auth.proto exist. |
| Harness 仓、业务仓、IDL 仓分支必须包含需求 ID | `PASS` | Current branch snapshot is feature/SPARK-2-mobile-code-register for all three repositories. |
| 项目当前状态已同步 | `PASS` | context/project/spark/user/current-state.md records AuthService, mobile code rules, and SPARK-2 decision. |

## 阻塞问题

| Issue | Required action | Owner |
| --- | --- | --- |
| 服务仓库环境已完成机器检查，但缺少人工服务仓库检查批准记录。 | 请负责人确认三仓分支、IDL 仓、服务路径和证据后，将本门禁更新为 PASS 或按豁免规则更新为 WAIVED。 | `Human Reviewer` |

## 警告

无。

## 豁免

- Required: `false`

## 外部证据

| Path | SHA-256 |
| --- | --- |
| `requirements/SPARK-2/evidence/buf-checks.md` | `5032608fa7eb93604a7a4e0482d750d7c655393e5ecc4829dc1ec8f58ca0a3d6` |
| `requirements/SPARK-2/evidence/user-api-tests.md` | `91fe79864911d1f0c642334a46d876a69dc2b47dfd9955e5de06f74e978ae6dc` |

