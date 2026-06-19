---
requirement_id: "LEN-35"
owner: "Codex"
status: "approved"
updated_at: "2026-06-20"
approved_by: "Forest"
approved_at: "2026-06-20T00:49:44+08:00"
decision: "批准 LEN-35 design，允许进入任务拆分。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, AC1 | D1: 在团队级 context 中定义 development、rc、formal 三类契约发布阶段 | 作为后续需求、设计和门禁引用入口 |
| R2, AC2 | D2: Java 版本规则分为 ticket scoped snapshot、不可变 RC、formal SemVer | 不修改 idl-java-repo 代码 |
| R3, AC3, AC4 | D3: Go 生成仍由 Buf 负责，分发由自有 idl-go-repo Go module tag 负责 | 不使用 BSR Generated SDK |
| R4, AC5 | D4: Formal 发布由 idl-repo 人工 SemVer tag 驱动，CI 以 tag commit 为唯一输入 | 删除 release file 方案 |
| R5, AC6, AC8 | D5: Merge-readiness 检查 master-bound 依赖类型和线上 artifact/tag 证据 | 不允许 RC 进入 master |
| R6 | D6: 不要求 Traceability Manifest，改用 tag、CI run、artifact metadata、module tag 和测试证据追溯 | 降低流程复杂度 |
| R7, AC10 | D7: Worktree 规则明确 idl-java-repo / idl-go-repo 默认不进入 worktree | 需要改发布流水线时再加入 |
| R8 | D8: 新增 context/team/contract-versioning.md 并更新团队索引 | 长期知识沉淀 |

## Summary

本设计把契约版本治理沉淀为团队级 context，并把 LEN-35 的 requirement / impact-analysis / gate 与该 context 关联起来。

先说不是什么：本设计不新增或修改 proto，不修改 Java / Go 生成物仓，不实现发布 CI，也不规定团队分支模型。它只定义后续实现和门禁必须遵守的版本语义、消费限制和追溯证据。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| user-api | 无代码变更；作为未来消费 IDL 生成契约的示例消费者 | 服务矩阵中 idl_required=true |
| IDL contract governance | 新增团队级版本治理 context | 约束 idl-repo tag 驱动发布和业务仓消费 |
| Harness governance | 新增 LEN-35 生命周期文档和 requirement-review gate | 使规则可评审、可追溯 |

## API / Contract Design

- Protobuf IDL required: 本需求涉及 IDL 治理，但不修改具体 proto。
- Proto files: 不修改；当前服务矩阵记录 user-api proto path 为 {idl-repo}/vesta/spark/user/v1。
- Buf module: local/spark-user。
- Buf config version: v2。
- Generated outputs: 不生成。
- Breaking check baseline: 不适用；本需求不改变 wire contract。
- Compatibility strategy: 仍以 contract-compatibility.md 管理字段、RPC、HTTP、事件和错误码兼容性；本需求补充版本发布和消费约束。

## Application Design

新增团队级规则文件：

```text
context/team/contract-versioning.md
```

该文件承担下列职责：

- 定义 development、rc、formal 三类版本。
- 定义 Java ticket scoped snapshot、RC 和 formal SemVer 格式。
- 定义 Go module tag 分发和 v2+ /vN 规则。
- 定义 formal 发布由 idl-repo SemVer tag 驱动。
- 定义 master-bound business change 只能消费 formal version。
- 定义无 Traceability Manifest 时的最小追溯证据。
- 定义 idl-java-repo / idl-go-repo 默认不进入 worktree 的规则。
- 定义 merge-readiness 应检查的依赖类型和证据。

更新团队 context 索引：

```text
context/team/INDEX.md
```

后续具体 IDL 变更设计应同时引用：

- context/team/contract-compatibility.md
- context/team/contract-versioning.md

## Data / Config / Permission

- Data model: 无。
- Config: 本阶段不新增 CI 配置；后续发布流水线实现时应读取 idl-repo tag。
- Permission: 本阶段无权限变更；后续 CI 可能需要跨仓读取 idl-repo 并发布 Java artifact / Go module tag。

## Observability

- Logs: 不新增运行时日志。发布 CI 的 run log 是版本追溯证据的一部分。
- Metrics: 无运行时指标。
- Tracing: 无。
- Events: 无。

## Testing Strategy

本需求是 Harness 文档和治理规则变更，验证重点是结构、门禁和可追溯性：

- janus requirement gate-check --requirement LEN-35 --gate requirement-review --owner Forest 生成并验证需求评审门禁。
- janus gate validate requirements/LEN-35/gates/requirement-review.gate.json 校验 gate JSON。
- janus gate render --input requirements/LEN-35/gates/requirement-review.gate.json --output requirements/LEN-35/gates/requirement-review.md --check 校验审计 Markdown 与 JSON 同步。
- git diff --check 检查文档格式。

后续实现发布流水线或业务依赖扫描时，测试策略再补充对应 CI / Maven / Go module 验证。

## Rollout And Rollback

- Gray release: 不适用；这是团队治理和文档变更。
- Kill switch: 如规则阻断现有交付，在具体需求设计或门禁中记录临时处理；master 仍不得消费 RC、SNAPSHOT、pseudo-version、branch dependency 或 local replace。
- Rollback: 回滚 requirements/LEN-35、context/team/contract-versioning.md 和 context/team/INDEX.md 变更即可。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| 没有 Traceability Manifest 后证据分散 | 明确最小证据集合：idl-repo tag、tag commit、CI run、artifact metadata、Go module tag、consumer commit、测试结果 | Codex |
| 发布 CI 目前可能不支持 tag 驱动 Java / Go 同步发布 | 本设计只定义规则；任务阶段将发布流水线能力列为单独任务或风险，不默认加入生成仓 worktree | Codex |
| 门禁扫描 Maven / go.mod 的能力尚未实现 | 在任务拆分中单独定义 merge-readiness 检查规则或 Janus 扩展任务 | Codex |
| 团队把版本治理误认为兼容性豁免 | 在 context 中明确版本治理不替代 contract-compatibility.md，breaking change 仍需兼容策略、迁移和回滚 | Codex |
