# LEN-115 - fides-bff Go lint 与内部依赖方向约束

本目录记录 fides-bff Go lint 治理增强的需求、影响分析、设计、任务、门禁和验证证据。

## 范围

- 只涉及 `business-repo/apps/fides-bff/.golangci.yml`。
- 不修改 fides 前端。
- 不修改 applicant-api。
- 不修改 protobuf IDL 或生成契约。
- 不改变运行时业务行为。

## 关键产物

- `requirement.md`
- `impact-analysis.md`
- `design.md`
- `tasks.json`
- `gates/*.gate.json`
- `evidence/local-verification.md`
