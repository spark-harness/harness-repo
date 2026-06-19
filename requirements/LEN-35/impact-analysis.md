---
requirement_id: "LEN-35"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-20"
approved_by: "Forest"
approved_at: "2026-06-20T00:55:58+08:00"
decision: "批准 LEN-35 impact-analysis 与服务仓库检查，允许进入后续交付验证。"
idl_impact: "yes"
idl_impact_reason: "本需求不修改具体 .proto，但定义 IDL 生成契约的发布、消费、版本和门禁规则，影响 protobuf 契约治理和业务仓消费方式。"
---

# Impact Analysis

## Summary

本需求新增团队级契约版本治理规则，影响 Harness 文档、需求门禁口径、IDL 生成契约发布流程和业务仓依赖检查；不直接修改业务 `.proto`、生成代码或业务服务实现。

## Affected Domains

- user：当前服务矩阵中 user-api 依赖 idl-repo 的 protobuf 契约，是后续消费规则的主要示例域。
- shared / team governance：新增团队级 context，适用于所有未来 IDL 生成契约和业务消费者。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| user-api | business-repo (services/backend/user-api) | 未来 master-bound 变更消费 IDL 生成契约时，需要遵守 formal version 规则和 merge-readiness 检查 | Yes（服务既有属性）；本需求不改 IDL |
| —（IDL contract governance） | idl-repo | Formal 发布由 idl-repo SemVer tag 驱动；本需求只定义规则，不修改 proto | Yes（规则影响 IDL 发布方式） |
| —（Harness governance） | harness-repo | 新增 LEN-35 生命周期产物和 context/team/contract-versioning.md | No |

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: **Yes, governance only**。
- Contract repo: idl-repo。
- Proto files: 不修改具体 proto；当前服务矩阵登记 user-api proto path 为 {idl-repo}/vesta/spark/user/v1。
- Buf module: local/spark-user。
- Buf config version: v2。
- Required buf checks: 本需求不修改 proto，因此不需要为本次文档变更运行 buf lint/generate/breaking 作为实现证据；后续具体 IDL 变更仍需遵守 contract-compatibility.md。
- Breaking baseline: 不适用；本需求不改变 wire contract。
- Compatibility risk: wire 兼容风险低；流程和发布治理风险中等。

## Generated Contract Impact

- idl-java-repo: 默认不进入 worktree。本需求仅定义 Java artifact 版本消费规则，不修改生成仓代码。
- idl-go-repo: 默认不进入 worktree。本需求仅定义 Go module tag 分发规则，不修改生成仓代码。
- 如果设计阶段确认需要新增或修改发布流水线、tag 触发 CI 或生成仓脚本，再将对应仓库加入 worktree 和任务计划。

## Data Impact

- Database schema: 无。
- Data migration: 无。
- Backfill: 无。
- Cache: 无。

## Config / Permission / Observability Impact

- Config: 后续发布 CI 可能需要读取 idl-repo tag 并发布 Maven artifact / Go module tag；本需求阶段只定义规则。
- Permission: 后续 CI 可能需要跨仓读写权限，用于从 idl-repo tag 生成并发布到 idl-java-repo / idl-go-repo 或包仓。
- Metrics: 不新增运行时指标。
- Logs: 发布 CI 应保留 run log，作为无 manifest 模型下的追溯证据之一。
- Tracing: 无运行时 tracing 影响。
- Events: 无。

## Rollout And Rollback

- Gray release: 不适用；本需求是治理规则和文档上下文变更。
- Kill switch: 如新规则阻断现有交付，可在设计或门禁中记录临时处理，但 master 仍不得消费 RC / SNAPSHOT / pseudo-version / branch dependency / local replace。
- Rollback steps: 回滚 `requirements/LEN-35` 和 `context/team/contract-versioning.md` 相关文档变更即可；无运行时数据残留。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| 不要求 Traceability Manifest 后追溯证据不足 | 难以重建某次业务消费对应的 IDL commit 和生成物版本 | 明确以 idl-repo tag、CI run、artifact metadata、Go module tag 和业务测试证据作为最小追溯集合 | Codex |
| idl-java-repo / idl-go-repo 不进入 worktree 导致发布流水线缺口延后暴露 | 需求文档通过，但实现阶段发现 CI 不支持 tag 驱动发布 | 在设计阶段将发布流水线能力作为显式风险；若需修改流水线，再加入对应 worktree | Codex |
| 业务仓仍使用本地 replace 或 RC 准备合 master | master 依赖不可复现或不稳定契约 | 在 merge-readiness 增加依赖扫描和证据检查 | Codex |
| Go v2+ module path 与 tag major 不一致 | 下游无法正确消费或出现 +incompatible | 在 context 中定义 /vN、require path、import path、tag major 一致规则 | Codex |
