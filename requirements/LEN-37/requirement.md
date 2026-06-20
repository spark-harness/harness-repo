---
requirement_id: "LEN-37"
owner: "Codex"
status: "approved"
created_at: "2026-06-20"
related_branch: "feature/LEN-37-remove-janus-gate-render"
approved_by: "Forest"
approved_at: "2026-06-20T13:31:36+08:00"
decision: "批准 LEN-37 requirement-review，允许进入设计阶段。"
---

# 移除 Janus gate render 并统一 gate JSON 事实源

## Background

Spark Harness 门禁已经把 `*.gate.json` 作为机器判定事实源，但历史流程仍要求 Janus 渲染 `requirements/{id}/gates/{gate-id}.md`，并在 CI、skills、agents、文档和 Janus CLI 中保留 `gate render` / `render --check`。

先说不是什么：本需求不是改变人工审批规则，不是修改 gate JSON schema，也不是新增另一个 Markdown 报告生成器。它是移除 gate Markdown 渲染能力和强制依赖，使阶段推进、CI 和合并判断只依赖可校验的 gate JSON。

## Goals

- R1: Harness CI 不再执行 `janus gate render --check`。
- R2: Harness 文档、AGENTS、skills 和 agents 不再要求生成 `requirements/{id}/gates/{gate-id}.md`。
- R3: Janus CLI 删除 `janus gate render`，并删除 `render --check` 能力。
- R4: `janus requirement gate-check` 只写入 `*.gate.json`，不再写入 gate Markdown。
- R5: `janus requirement status`、`janus gate verify` 和 `janus requirement verify --target merge` 不再读取或要求 gate Markdown。
- R6: 历史 `requirements/*/gates/*.md` 不批量删除，只视为旧审计快照，不再刷新、不再校验、不再作为事实来源。
- R7: 新需求门禁只需要提交并校验 `*.gate.json`。

## Non-Goals

- 不改变 gate JSON schema。
- 不改变人工审批规则。
- 不改变 `janus gate validate`、`janus gate verify`、`janus requirement verify` 的门禁语义。
- 不引入新的 Markdown 报告生成器。
- 不批量删除历史 `requirements/*/gates/*.md`。
- 不把聊天记录、手写 Markdown 或历史 Markdown 作为阶段推进依据。

## User / Business Scenarios

### Scenario 1: 新需求只提交 gate JSON

Given: 新需求需要完成阶段门禁。

When: Agent 或人员运行 Janus 门禁流程。

Then: 只生成、提交和校验 `requirements/{id}/gates/{gate-id}.gate.json`，不新增 `requirements/{id}/gates/{gate-id}.md`。

### Scenario 2: CI 不再检查 Markdown 漂移

Given: PR 修改了 gate JSON。

When: Harness CI 检查本次变更。

Then: CI 运行 `janus gate validate` 和按需运行 `janus requirement verify --target merge`，不运行 `janus gate render --check`。

### Scenario 3: Janus render 命令不可用

Given: 用户或脚本调用 `janus gate render`。

When: Janus 解析 gate 子命令。

Then: 命令不可用，并按未知 gate 子命令返回错误。

### Scenario 4: 历史 Markdown 不影响判断

Given: 仓库仍存在历史 `requirements/*/gates/*.md`。

When: 运行 `janus requirement status`、`janus gate verify`、`janus requirement verify --target merge` 或 Harness CI。

Then: 历史 Markdown 不影响 CI、阶段推进或合并判断。

## Business Rules

- BR1: `*.gate.json` 是门禁唯一机器事实来源。
- BR2: gate Markdown 不得作为阶段推进、CI 或合并判断依据。
- BR3: Janus 不再生成、刷新或校验 gate Markdown。
- BR4: Harness 文档和协作资产不得要求执行 `janus gate render` 或 `render --check`。
- BR5: 历史 gate Markdown 可以留在仓库中作为旧审计快照，但不得被新流程刷新。
- BR6: 新需求不得新增 gate Markdown。
- BR7: 人工审批仍通过被评审产物的批准字段表达，并由 gate JSON 保存当次检查快照。

## Acceptance Criteria

- AC1: Harness CI 中不存在 `janus gate render --check`。
- AC2: `janus gate render` 命令不可用，相关测试和文档已同步删除或改写。
- AC3: 搜索强制流程文档时，不再出现“必须运行 render / render --check”的要求。
- AC4: 新需求门禁只需要提交 `*.gate.json`。
- AC5: `janus gate validate` 仍可校验 gate JSON。
- AC6: `janus requirement verify --target merge` 仍可用于 merge 级判断。
- AC7: 历史 `*.md` 不影响 CI、不影响阶段推进、不影响合并判断。
- AC8: Janus `gate-check` 只生成 gate JSON，不生成 gate Markdown。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 是否后续单独清理历史 gate Markdown 文件 | Forest | 后续治理 ticket | 本需求不处理 |

## Notes

- 用户已批准一次完成：同时移除 Harness 强制 render 流程和 Janus CLI `gate render` 命令。
- 本需求影响 `harness-repo` 与 `janus`，不涉及 `business-repo`、`idl-repo` 或 generated contracts。
