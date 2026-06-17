# LEN-31

## Title

[FE] Clean Architecture 脚手架 + dependency-cruiser 门禁

## Source

- JIRA: LEN-31（Subtask）← LEN-4（前端骨架与流程编排）← LEN-1。
- 承接父票 LEN-4 的 AC6（违规被门禁拦截并指出文件）、AC5（CI 含 lint:deps、可一键运行）。

## Status

- Requirement Brief: approved（会话批准，2026-06-14）
- requirement.md / impact-analysis.md / design.md / tasks.json: authored & approved
- requirement-review / design-review / dev-entry / service-repo-check: PASS
- merge-readiness: BLOCKED（等待人工合并批准）

## Scope

新建前端独立应用 **fides**（`business-repo/services/frontend/fides`，Next.js 16 App Router + TS + Tailwind v4），并在其中建立 Clean Architecture 分层骨架与 `dependency-cruiser` 静态依赖门禁，作为所有前端屏/子任务的结构与质量地基。空骨架即可跑通 `pnpm lint:deps`，应用外壳可 `dev/build`，门禁接入 CI。本票只立「应用外壳 + 结构 + 门禁」，不实现任何业务屏。

> 注：现有 `aegis` 应用不在本票范围、保持不动；fides 是本工作流的新前端项目（用户 2026-06-14 明确）。

## Affected

- 服务：新增 `fides`（module `frontend`，`idl_required: false`，无 IDL）；`aegis` 不改。
- 仓库：`business-repo`（fides 应用 + 门禁 + CI）、`harness-repo`（生命周期产物 + 服务矩阵新增 fides）。
- 分支/隔离：`feature/LEN-31-fe-clean-arch-scaffold`（harness-repo + business-repo 同名），在工作区级 git worktree `.worktrees/feature-LEN-31-fe-clean-arch-scaffold/` 内开发，主检出保持 master 干净。

## Traceability

| 类别 | 位置 |
|---|---|
| 需求 | `requirement.md` |
| 影响分析 | `impact-analysis.md` |
| 设计 | `design.md` |
| 任务 | `tasks.json` |
| 门禁 | `gates/` |
| 证据 | `evidence/lint-deps-redline.md` |
| 评审 | `reviews/implementation.md` |
