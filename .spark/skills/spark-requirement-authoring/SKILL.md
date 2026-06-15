---
name: spark-requirement-authoring
description: Create or update Harness requirement artifacts for Spark requirements. Use after requirement intake is approved to write requirements/{id}/README.md and requirement.md with goals, non-goals, scenarios, business rules, acceptance criteria, and open questions in Chinese.
---

# Spark Requirement Authoring

Write reviewable Harness requirement files. Do not write design, IDL, or business code in this skill.

## Inputs

- Approved Requirement Brief.
- Current Workspace Pack from `spark-workspace-scan`.
- Current Context Pack from `spark-harness-context-loading`.
- Worktree Isolation Report with an isolated or existing linked `harness-repo`
  path.
- Requirement ID.

## Preconditions

Do not write files unless one of these is true:

- the current turn explicitly approves the Requirement Brief and permits requirement document creation
- an existing `requirements/{requirement-id}/requirement.md` is already approved by a prior explicit approval record

Clarifying implementation direction does not satisfy this precondition. If approval is missing, return to `spark-requirement-intake` and produce a chat-only Requirement Brief.

Do not write requirement files in the main workspace checkout. If the target
path is `$SPARK_WORKSPACE/harness-repo` and it is not an existing linked
worktree, return to `spark-worktree-isolation` first.

## Files

- `{isolated-harness-repo}/requirements/{requirement-id}/README.md`
- `{isolated-harness-repo}/requirements/{requirement-id}/requirement.md`

## Requirements

- Write team-facing guidance in Chinese.
- Keep sections short and concrete.
- Include Background, Goals, Non-Goals, Scenarios, Business Rules, Acceptance Criteria, Open Questions, and Notes.
- Use Given/When/Then for scenarios.
- Keep Harness docs semantic; do not copy business implementation details.
- If a concept is easy to confuse, state what it is not before what it is.

## Gate

`requirement.md` and `impact-analysis.md` are one review stage. Do not create
`requirements/{requirement-id}/gates/requirement-review.gate.json` from this
skill when `impact-analysis.md` is missing. A missing impact analysis means the
stage is still in progress, not a formal gate failure.

After writing `requirement.md`, continue to `spark-impact-analysis`. The
`requirement-review` gate is created or refreshed only after both
`requirement.md` and `impact-analysis.md` exist and the required approval
records are present.

Do not write the approval block (`status: "approved"`, `approved_by`,
`approved_at`, `decision`) yourself. The `janus hook guard-edit` hook blocks any
edit that flips `status` to `approved`. Human approval is recorded only by a
person running `janus requirement approve --requirement <id> --gate <gate> --approved-by <name> --decision <text> --yes`.
The stage-order rules also block `design.md` before `requirement.md` +
`impact-analysis.md` exist, and `requirement-review.gate.json` before
`impact-analysis.md` exists.

## Output

Summarize changed files and unresolved open questions. State that
`requirement-review` is not generated until impact analysis is ready, then
continue to `spark-impact-analysis`.
