---
requirement_id: "LEN-37"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-20"
approved_by: "Forest"
approved_at: "2026-06-20T14:14:53+08:00"
decision: "批准 LEN-37 service-repo-check，允许进入合并就绪验证。"
idl_impact: "no"
idl_impact_reason: "本需求不修改 protobuf IDL、Buf 配置或 generated contracts。"
---

# Impact Analysis

## Summary

本需求移除 Harness 对 gate Markdown render 的强制依赖，并删除 Janus CLI 的 gate render 能力。影响范围集中在 Harness 治理文档、协作资产、CI、Janus CLI、Janus requirement lifecycle 和相关测试。

## Affected Domains

- Harness governance：门禁流程、CI、skills、agents、模板口径和 AGENTS 说明。
- Janus CLI：`gate render` 子命令、Markdown render 实现、gate-check 输出、status 检查和 hook 行为。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| Harness governance | harness-repo | 移除 gate render 强制流程，更新 CI、文档、skills、agents 和 LEN-37 生命周期产物 | No |
| Janus CLI | janus | 删除 `gate render` 命令、Markdown render 实现和相关测试 / 文档 | No |

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: No。
- Contract repo: 不适用。
- Proto files: 不适用。
- Buf module: 不适用。
- Buf config version: 不适用。
- Required buf checks: 不适用。
- Breaking baseline: 不适用。
- Compatibility risk: CLI 行为有意不兼容，`janus gate render` 调用方必须迁移到 `janus gate validate` 或 `janus requirement verify`。

## Generated Contract Impact

- idl-java-repo: 无影响。
- idl-go-repo: 无影响。
- generated contracts: 无影响。

## Data Impact

- Database schema: 无。
- Data migration: 无。
- Backfill: 无。
- Cache: 无。
- Runtime storage: 无。

## Config / Permission / Observability Impact

- Config: Harness CI workflow 去掉 render check，保留 gate JSON validate 和 merge verify。
- Permission: 无新增权限。
- Metrics: 无运行时指标。
- Logs: CI 日志从 render check 输出变为 validate 输出。
- Tracing: 无。
- Events: 无。

## Rollout And Rollback

- Rollout: 同名分支更新 `harness-repo` 与 `janus`；先验证 Janus 单元测试，再用新 Janus 二进制验证 Harness JSON-only 流程。
- Rollback: 回滚 `harness-repo` 和 `janus` 的 LEN-37 分支变更即可恢复 render 命令和旧流程。
- Compatibility note: 历史 gate Markdown 留在仓库中，不影响回滚和审计。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| 文档或 skill 中残留 render 步骤 | Agent 继续执行已删除命令，导致流程失败 | 全文搜索 `gate render`、`render --check`、`门禁审计视图`、`gates/*.md` 并改为 JSON-only | Codex |
| 外部脚本仍调用 `janus gate render` | 脚本在 Janus 升级后失败 | Harness 内部脚本改为 validate-only；Janus 文档明确 render 命令不可用 | Codex |
| status 或 hook 仍把 Markdown 当必需物 | 历史 Markdown 缺失或过期会误阻塞 | Janus status / hook 改为只校验 gate JSON | Codex |
| 历史 Markdown 被误认为最新事实 | 审计时读到过期 Markdown | 文档明确历史 Markdown 只是旧快照，新需求不得新增 gate Markdown | Codex |
