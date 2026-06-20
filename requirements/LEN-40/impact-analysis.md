---
requirement_id: "LEN-40"
analyst: "Harness Team"
status: "approved"
updated_at: "2026-06-20"
approved_by: "forest"
approved_at: "2026-06-21T00:50:33+08:00"
decision: "批准 LEN-40 服务仓库检查门禁。"
idl_impact: "yes"
idl_impact_reason: "不修改 protobuf 文件，但修改 IDL 发布证据与 contract dependency gate 的治理口径。"
---

# Impact Analysis

## Summary

本需求影响 Harness 流程文档、Janus CLI、business-repo contract dependency scan、
三仓 delivery readiness workflow，以及 IDL 发布证据验证口径。

## Affected Domains

- Harness 流程治理。
- 多仓 Git / CI 交付。
- IDL 生成契约发布与消费。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| Harness governance | `harness-repo` | 模板、Git workflow、contract versioning、gate implementation 规则更新 | no |
| Janus CLI | `janus` | 新增 `delivery verify`，统一 peer repo / contract stage 判断 | no |
| Contract dependency scan | `business-repo` | 支持 `rc-or-formal` / `formal-only` 模式名 | no |
| IDL publishing workflows | `idl-repo` | 验证 RC / Formal 发布证据口径，workflow 接入 delivery readiness | yes |

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: yes, governance only.
- Contract repo: `idl-repo`、`idl-java-repo`、`idl-go-repo` 发布证据。
- Proto files: none.
- Buf module: unchanged.
- Buf config version: v2.
- Required buf checks: no `.proto` edits, no Buf check required for this task.
- Breaking baseline: unchanged.
- Compatibility risk: low for protobuf schema, medium for CI behavior because旧同名分支检查会被 Janus 阶段检查替代。

## Generated Contract Impact

- 不修改生成 Java / Go contract 源码。
- 不自动执行 Formal 发布。
- Janus / CI 后续需要验证 formal tag、tag commit、artifact version 与 business dependency。

## Data Impact

- Database schema: none.
- Data migration: none.
- Backfill: none.
- Cache: none.

## Config / Permission / Observability Impact

- Config: GitHub workflow 需要 `JANUS_REPO_TOKEN`、`BRANCH_COHERENCE_TOKEN` 或默认 token 读取 peer repo。
- Permission: artifact registry 只读验证凭据仍需确认。
- Metrics: none.
- Logs: CI 输出 Janus delivery readiness summary。
- Tracing: none.
- Events: none.

## Rollout And Rollback

- Gray release: 先在 LEN-40 分支验证 Janus 测试、business scan 测试和 workflow YAML。
- Kill switch: 如 CI token 权限不足，可暂时回退对应仓 `.github/workflows/branch-coherence.yml`。
- Rollback steps: revert 各仓 workflow 与 Janus delivery 包变更，保留文档记录后续修正。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| CI token 无法跨私有仓 checkout peer repo | delivery readiness 无法运行 | workflow 使用专用 token fallback，并在证据中记录权限缺口 | Harness Team |
| 本地 Git 无法在 feature branch 删除后证明历史 PR | peer 状态误判 | Janus 支持 merge commit message fallback，后续补 GitHub PR 查询 | Harness Team |
| release-bound artifact 验证凭据缺失 | Formal 证据只能部分验证 | 设计中明确 artifact registry 只读凭据为上线前条件 | Harness Team |
