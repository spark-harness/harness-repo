---
name: spark-jira-ticket-authoring
description: Author or refine JIRA work items (Epic / Story / Sub-task) for Spark/Lendora at the correct altitude. Use when creating or editing JIRA tickets (e.g. via acli) so business intent stays in Epic/Story and technical detail lives in Sub-tasks, with Given/When/Then acceptance and cross-level traceability.
---

# Spark JIRA Ticket Authoring

Write JIRA work items where each level speaks a different language and stays traceable.
Epic = why, Story = user-observable behavior, Sub-task = technical contract.

## When to use

- Creating or restructuring a JIRA Epic, Story, or Sub-task for Spark/Lendora work.
- A reviewer flags that a Story is full of technical detail (status codes, endpoints, tokens).
- Splitting a capability into BE/FE sub-tasks.

This skill governs JIRA work items only. It does NOT replace the Harness requirement
lifecycle docs (`requirement.md`, `design.md`, `tasks.json`), which have their own skills
and gates. When both exist, the JIRA Story should read like the requirement, the Sub-task
like the design/task.

## Altitude model (who writes what)

| Level | Author | Altitude | Answers the one question | Never contains |
|---|---|---|---|---|
| Epic | Product owner | business / strategy | why, for whom, when it is done | per-feature acceptance, any tech |
| Story | Product / BA | user-observable behavior | what the user can do, which business rules hold, how to verify | endpoints, status codes, DB, tokens, implementation steps |
| Sub-task | Engineer / Tech Lead | technical | how this slice is built, the contract, the done bar | restating business motivation (link to Story) |

Smell test: read the Story to a teammate who does not know HTTP. If `429`, `accessToken`,
or `Idempotency-Key` appears, technical detail has leaked up from a Sub-task.

If there is no dedicated product owner, the same person switches hats — the Story still uses
business language, technical detail still sinks to Sub-tasks.

## Skeletons

Keep ticket content in Chinese, team-facing. When a concept is confusable, say what it is
NOT before what it is.

Epic:
```
# [Epic] <标题>
## 背景与问题       为什么现在做（业务问题，不是功能清单）
## 业务目标 / 价值   期望的结果 outcome（可衡量，不是 output）
## 范围             做 / 不做（不做 → 指向接手的 Epic，避免蔓延）
## 成功指标         怎么判定这个 Epic 交付了（端到端、可验证）
## 包含 Story        索引 + 建议交付顺序
## 跨 Story 风险 / 依赖
```

Story (属于 <Epic 链接>):
```
## 用户故事    作为 <角色>，我要 <能力>，以便 <价值>
## 背景        这条能力在流程里的位置；先说「不是什么」再说「是什么」
## 业务规则    BR1.. 领域语言，无 HTTP / 无实现细节
## 验收标准    表格：每行一条 AC（编号 | Given | When | Then），结果须「用户可观察」
## 范围        做 / 不做（本能力边界）
## 依赖 / 待确认  Blocked by；未决问题挂 Owner + 截止
```

Acceptance criteria use a table — one AC per row:

| AC | Given | When | Then |
|----|-------|------|------|
| AC1 | <前置状态> | <用户动作> | <用户可观察的结果> |

Never put endpoints, status codes, DB, token types, or implementation steps in a Story.

Sub-task (属于 <Story 链接>):
```
## 技术范围    本子任务负责 Story 的哪一片
## 接口 / 契约  端点 / 出入参 / 错误码用表格（固定格式优先表格）
## 实现要点    存储、第三方、桩、边界条件、幂等
## DoD         覆盖父 Story 的哪几条 AC（写 AC 编号）；契约符合哪份文档
## 依赖        其他子任务 / 外部
```

In 接口 / 契约, express fixed-format detail as tables, not codeBlock. Endpoints and error
codes are tables; reserve codeBlock for free-form snippets (e.g. a sample payload).

| 端点 | 请求 | 响应 |
|------|------|------|
| METHOD /path | { req } | { resp } |

| HTTP | code | 触发 |
|------|------|------|
| 4xx | error_code | <触发条件> |

Never restate business motivation in a Sub-task; link back to the Story.

## Traceability

```
Epic.成功指标  ⟵ sum of Story.AC
Story.AC#      ⟵ realized & verified by Sub-task.DoD (DoD names the AC numbers it covers)
Story.BR#      ⟵ realized by the Sub-task contract / implementation
```

Iron rule: one fact is defined at exactly one level; other levels reference it by ID or link.
Never duplicate — otherwise edits to a Story AC drift from the Sub-task DoD.

## Worked examples

Filled-in examples live in `references/`, one file per level:

- `references/epic-example.md` — Epic (LEN-1), business only.
- `references/story-example.md` — Story (LEN-2), AC as a table.
- `references/subtask-example.md` — Sub-task (LEN-12), contract as tables.

Read the matching file before authoring that level.

## Tooling: scripts/adf.py

This skill ships `scripts/adf.py`. It turns a compact block spec into ADF JSON for
`acli ... --description-file`. Workflow:

```bash
# 1) write a spec (list of [kind, payload]) to spec.json, e.g.
#    [["h","接口 / 契约"], ["table", [["端点","请求","响应"], ["POST /...","{..}","{..}"]]]]
# 2) build ADF
python3 <skill-dir>/scripts/adf.py spec.json > out.json
# 3) apply
acli jira workitem edit --key LEN-2 --description-file out.json --yes
```

Spec blocks: `["h", s]` heading · `["p", s]` paragraph · `["ul", [..]]` bullet list ·
`["table", [header_row, ...data_rows]]` table · `["code", s]` code block (snippets only).

## Notes & pitfalls

- ADF, not plain text. `\n` inside a paragraph will not render; headings / lists / tables /
  code must be real ADF nodes. Use `scripts/adf.py`; never hand `acli` a multi-line plain string.
- AC → table (编号 | Given | When | Then); contract → tables (端点表 + 错误码表). `codeBlock`
  only for free-form snippets such as a sample payload.
- One project per product (Lendora = `LEN`); organize the backlog by Epic = roadmap phase.
  FE/BE are labels (`backend` / `frontend` / `platform`), not separate projects.
- Hierarchy via `--parent`. Issue-type names may be localized — this project: Epic=长篇故事,
  Story=故事, Sub-task=Subtask. Confirm against the target project before bulk-creating.
- Edit descriptions with `--description-file <adf.json> --yes`.
- Renaming a project key re-keys every issue; JIRA keeps old-key redirects automatically and
  the redirect cannot be disabled.
- One fact lives at one level — when you edit a Story AC, update the Sub-task DoD that cites it.

## Rules

- Keep Epic and Story in business language; sink all technical detail to Sub-tasks.
- Write Story acceptance criteria as a table (编号 | Given | When | Then), one AC per row.
- In Sub-task 接口 / 契约, express fixed-format detail (endpoints, request/response, error codes) as tables; reserve codeBlock for free-form snippets.
- Every Sub-task DoD must cite the parent Story AC numbers it covers.
- Make Non-Goals explicit at both Epic and Story.
- Prefer vertical-slice Stories (one user capability) with BE/FE Sub-tasks over discipline-split Stories.

## Output

Report created or updated work item keys and the Epic → Story → Sub-task tree.
Flag any Story AC not yet mapped to a Sub-task DoD.
