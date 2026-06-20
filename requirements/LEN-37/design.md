---
requirement_id: "LEN-37"
owner: "Codex"
status: "approved"
updated_at: "2026-06-20"
approved_by: "Forest"
approved_at: "2026-06-20T13:45:46+08:00"
decision: "批准 LEN-37 design-review，允许进入任务拆分。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, AC1 | D1: Harness CI 对变更 gate JSON 只运行 `janus gate validate` | merge PR 仍运行 `janus requirement verify --target merge` |
| R2, R6, R7, AC3, AC4, AC7 | D2: Harness 文档、AGENTS、skills 和 agents 明确 gate JSON 是唯一事实源，历史 Markdown 只是旧快照 | 不批量删除历史 `.md` |
| R3, AC2 | D3: Janus `gate` 子命令只保留 `validate` 与 `verify`，删除 `render` 分支和 usage | `gate render` 返回 unknown subcommand |
| R4, AC8 | D4: `requirement gate-check` 只写 `.gate.json` | 返回输出只展示 Source JSON |
| R5, AC5, AC6, AC7 | D5: `requirement status`、hook 和 requirement verify 只读取 gate JSON、输入 hash、证据 hash 和分支策略 | 不再读取或要求 `.md` |
| R3, AC2 | D6: 删除 Janus Markdown render 实现和 render 单元测试，新增目标行为测试 | 保留非 gate 的模板渲染函数 |

## Summary

本设计把门禁输出收敛到一个可执行事实源：`requirements/{id}/gates/{gate-id}.gate.json`。Harness 负责更新流程口径和 CI；Janus 负责删除 render 命令及所有对 gate Markdown 的机器依赖。

先说不是什么：本设计不改变 gate JSON schema，不改变人工批准字段，不重写 Janus gate verify 语义，也不清理历史 Markdown 文件。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| Harness governance | 更新 CI、AGENTS、framework docs、skills、agents、LEN-37 生命周期产物 | 移除 render 强制依赖 |
| Janus CLI | 删除 gate render 子命令、render 实现、Markdown stale 检查和相关测试 | gate JSON 成为唯一事实源 |

## API / Contract Design

- Protobuf IDL required: No。
- Proto files: 不修改。
- Buf module: 不适用。
- Buf config version: 不适用。
- Generated outputs: 不生成。
- Breaking check baseline: 不适用。
- Compatibility strategy: CLI 层有意删除 `janus gate render`。内部调用方迁移到 `janus gate validate`；合并判断仍使用 `janus requirement verify --target merge`。

## Application Design

### Harness

- `.github/workflows/harness-gates.yml`：
  - 对 changed gate JSON 运行 `janus gate validate "$g"`。
  - 不再计算 `.md` 路径，不再执行 `render --check`。
- `scripts/render-gates.py`：
  - 保留兼容入口，但职责改为 validate gate JSON。
  - `--check` 作为兼容参数保留，不再触发 Markdown 读取。
- `context/harness-framework/*`、`AGENTS.md`：
  - 明确 gate JSON 是唯一机器事实源。
  - 明确历史 gate Markdown 只是旧审计快照，新需求不得新增。
- `.spark/skills`、`.spark/agents`：
  - 删除所有 `janus gate render` 步骤。
  - 门禁流程统一为写 JSON、validate JSON、按需 verify。

### Janus

- `internal/cli/cli.go`：
  - 删除 `runGateRender`。
  - `runGate` 不再接受 `render`。
  - usage 不再展示 `gate render`。
  - `requirement gate-check` 输出只展示 gate JSON Source。
- `internal/requirement/lifecycle.go`：
  - `RunGateCheck` 只写 gate JSON。
  - `Inspect` 不再读取或比较 gate Markdown。
  - `NextAction` 的 stale 提示改为刷新 gate JSON。
- `internal/cli/hook.go`：
  - `gate-drift-check` 保留命令名兼容，但行为改为校验 gate JSON。
  - 缺失或过期 Markdown 不再阻塞。
- `internal/gate/render.go`：
  - 删除 gate Markdown render 实现。
- tests：
  - 删除 render 输出/漂移测试。
  - 新增 `gate render` 不可用测试。
  - 更新 gate-check 和 hook 测试，证明不生成/不要求 Markdown。

## Data / Config / Permission

- Data model: 无。
- Config: Harness CI workflow 变更。
- Permission: 无新增权限。

## Observability

- Logs: CI 输出 `janus gate validate` 分组。
- Metrics: 无。
- Tracing: 无。
- Events: 无。

## Testing Strategy

- Janus: `go test ./...`。
- Janus CLI target behavior:
  - `go run ./cmd/janus gate render --help` 应返回 unknown gate subcommand。
  - `go run ./cmd/janus gate validate <gate-json>` 仍可用。
- Harness:
  - `bash -n scripts/install.sh`。
  - `python3 -m py_compile scripts/render-gates.py`。
  - 搜索 `gate render`、`render --check`、`门禁审计视图`，确认 source 流程没有强制 render。
- Merge-level:
  - 使用 Janus 新二进制运行 `janus requirement verify --requirement LEN-37 --target merge`，前提是 LEN-37 gate JSON 已准备并通过。

## Rollout And Rollback

- Rollout: 同名分支分别提交 `harness-repo` 和 `janus`，PR 描述要求同时评审两个仓库。
- Rollback: 回滚两个仓库的 LEN-37 变更即可恢复旧 render 流程。
- Historical files: 历史 gate Markdown 不删除，避免审计快照丢失。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| 外部调用仍依赖 `janus gate render` | README 和 requirements 明确命令不可用；Harness 内部调用已迁移 | Codex |
| Skill runtime copy 与 `.spark/skills` 漂移 | 变更后运行 `scripts/install.sh` 同步 runtime copies，并运行 `scripts/install.sh --check` | Codex |
| 新 LEN-37 自身 gate 如果使用旧 Janus 会生成 Markdown | 使用 worktree Janus 新二进制执行验证 | Codex |
| 历史 Markdown 误导人工审计 | 文档多处标注历史 Markdown 只是旧快照，新需求不得新增 | Codex |
