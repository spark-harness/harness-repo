---
requirement_id: "LEN-36"
gate_id: "merge-readiness"
gate_name: "合并就绪门禁"
stage: "5.1"
checked_by: "merge_readiness_checker"
checked_at: "2026-06-20T11:52:17+08:00"
result: "PASS"
blocks_next_stage: false
---

<!-- Generated from merge-readiness.gate.json. Do not edit blocking fields here. -->

# 合并就绪门禁

## 结论

LEN-36 scanner, fixture tests, changed-file PR workflow, and Harness evidence are ready. Existing user-api SNAPSHOT dependency remains a recorded follow-up for full-repo scans.

## 输入快照

| Path | SHA-256 |
| --- | --- |
| `requirements/LEN-36/requirement.md` | `cfc217ea5f19ec1258380663a4e9a9286ec2ce98695bd508ecfaa9ca822de721` |
| `requirements/LEN-36/impact-analysis.md` | `3ffd30b7960ae58a6ec5d20cd2c64d328886ba5e00b7d6a6b357af9561c334e9` |
| `requirements/LEN-36/design.md` | `7b17e99f7c441c47343ccacae3e88d042adef1f103df5882a2a04c022182d8ad` |
| `requirements/LEN-36/tasks.json` | `d98a52a63cb6821313428566e1fc13b5661217c3a1d6cb4bfcfd2c6cefe68c69` |
| `requirements/LEN-36/gates/requirement-review.gate.json` | `63ea1f6e7e46f602865180d5582fb78d4163fb5fde2d028f939a0b4a25d9ecfa` |
| `requirements/LEN-36/gates/design-review.gate.json` | `b4aa6cd4ada21c741dd3404903574545e5717c5abec3c3a632b2791759c821c3` |
| `requirements/LEN-36/gates/dev-entry.gate.json` | `086eb71ca52dc9204435604c0db74e3d746379423cc380f102bf19edb4b56ad8` |
| `requirements/LEN-36/gates/service-repo-check.gate.json` | `95fc53de3a79106a87c82c8fcb8b2f9979c2e7a9ba58d1ec488587bbcc090524` |
| `.service-matrix/dependencies.yaml` | `fd4ff8d37331eada97ebe2fe539e993d70146462d2e5243664351a593a03e091` |

## 检查项

| Item | Result | Evidence |
| --- | --- | --- |
| 阶段门禁已通过 | `PASS` | requirement-review, design-review, dev-entry, and service-repo-check are present and not BLOCKED. |
| 实现证据已记录 | `PASS` | 1 evidence files recorded. |
| business-repo contract dependency scan | `PASS` | Changed-file scan for this PR shape passed: workflow/script/config changes do not scan historical dependency files; touching services/backend/user-api/pom.xml still fails on the existing SNAPSHOT dependency. |
| IDL 证据已记录 | `PASS` | Buf or contract evidence exists. |
| 人工批准记录合法 | `PASS` | requirements/LEN-36/tasks.json approved by Forest at 2026-06-20T11:46:53+08:00. |

## 阻塞问题

无。

## 警告

| Issue | Follow-up action | Owner |
| --- | --- | --- |
| Manual full-repo contract dependency scan still finds services/backend/user-api/pom.xml consuming com.spark.contract:spark-idl-java:0.1.0-SNAPSHOT. | Publish a formal spark-idl-java version and update user-api in a separate requirement before requiring full-repo scans to pass. | `Contract / user-api owner` |

## 豁免

- Required: `false`

## 外部证据

| Path | SHA-256 |
| --- | --- |
| `requirements/LEN-36/evidence/contract-dependency-scan-verification.md` | `0b5fcd6386a25deff9c0ab2580ec3a7495a999063249aec4373b66c5120d654a` |
