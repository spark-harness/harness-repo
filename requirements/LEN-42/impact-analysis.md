---
requirement_id: "LEN-42"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-21"
approved_by: "Forest"
approved_at: "2026-06-21T13:14:40+08:00"
decision: "批准 LEN-42 service repo readiness；本票无业务服务影响，涉及仓库为 harness-repo 与 idl-repo。"
idl_impact: "yes"
idl_impact_reason: "本需求不修改 .proto，但修改 IDL 仓 Buf 生成配置，影响 generated contract 的生成输入可复现性。"
---

# Impact Analysis

## Summary

LEN-42 只影响 `idl-repo` 的 Buf 生成配置和 `harness-repo` 的追溯文档；不影响业务服务运行时、不修改 protobuf schema、不新增外部 proto deps。

## Affected Domains

- IDL / generated contract 生成治理。
- Harness requirement lifecycle 追溯。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| IDL generation config | `idl-repo` | 锁定 `buf.gen.yaml` 与 `buf.gen.go.yaml` 中的 remote plugin version | No schema change |
| Harness lifecycle | `harness-repo` | 记录需求、影响、设计、任务和证据 | No |

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: Yes, config-only。修改生成配置，不修改 proto schema。
- Contract repo: `idl-repo`。
- Proto files: none changed。
- Buf module: local workspace module in `idl-repo/buf.yaml`。
- Buf config version: v2。
- Required buf checks: `buf lint` / `buf generate` / `buf breaking`。
- Breaking baseline: `origin/master` for this worktree; local main checkout may be stale.
- Compatibility risk: Low。插件版本从 implicit latest 固定为当前 latest，不改变 proto schema。风险在于生成器输出可能与未来 latest 不同，这是本需求希望消除的漂移。

## Data Impact

- Database schema: none。
- Data migration: none。
- Backfill: none。
- Cache: none。

## Config / Permission / Observability Impact

- Config: `idl-repo/buf.gen.yaml`、`idl-repo/buf.gen.go.yaml`。
- Permission: none。
- Metrics: none。
- Logs: none。
- Tracing: none。
- Events: none。

## Rollout And Rollback

- Gray release: not applicable。该变更随 IDL 仓配置合并生效。
- Kill switch: not required。
- Rollback steps: revert the `remote:<version>` changes in `buf.gen.yaml` and `buf.gen.go.yaml` if a locked plugin version is proven unusable.

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| 锁定版本后 `buf generate` 产生生成物漂移 | 可能影响 generated contract 消费者 | 运行生成命令并记录输出范围；本票不提交 generated contract 仓库变更 | Platform |
| 误把 `buf.lock` 当成插件锁定机制 | 未来治理文档和实现方向错误 | 在 requirement/design/evidence 中明确边界 | Platform |
| 本地 `master` checkout 落后导致 breaking check 误判 | 误报已有历史差异 | 使用 worktree 基于 `origin/master` 的 baseline，并在证据中记录命令与原因 | Platform |
