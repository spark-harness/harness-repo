---
name: spark-using-workflow
description: Top-level router for Spark workspace development. Use at the start of any real development, bugfix, IDL, Harness requirement, gate, documentation-governance, refactor, or multi-repo task in /Users/forest/Code/spark to choose the right Spark workflow skills before editing files.
---

# Spark Using Workflow

Use this before acting on Spark workspace tasks. It routes work to the right Spark skill and prevents jumping from vague requests directly into code, IDL, or gate edits.

## Priority

1. Explicit user instructions and `AGENTS.md`.
2. This router and selected Spark skills.
3. Default coding behavior.

## Rule

If a Spark workflow skill might apply, use the relevant process skill before any edit, side-effect command, or implementation decision.

User answers define requirements, constraints, and direction. They do not grant lifecycle approval unless they explicitly approve the current Requirement Brief or the current lifecycle stage.

Process skills run before production skills:

1. `spark-requirement-intake`
2. `spark-workspace-scan`
3. `spark-harness-context-loading`
4. `spark-worktree-isolation`
5. `spark-requirement-authoring`
6. `spark-impact-analysis`
7. `spark-design-authoring`
8. `spark-task-planning`
9. `spark-idl-change-protocol`
10. `spark-test-first-implementation`
11. `spark-implementation-execution`
12. `spark-debugging-root-cause`
13. `spark-code-review`
14. `spark-self-refinement`
15. `spark-evidence-gate-completion`

## Routing

- New feature or behavior change: intake -> workspace scan -> harness context loading -> worktree isolation before approved file edits -> requirement authoring -> impact -> design -> tasks -> test-first -> IDL protocol when needed -> implementation -> code review -> evidence/gates -> self-refinement when reusable lessons appear.
- IDL or contract change: intake -> workspace scan -> harness context loading -> worktree isolation before approved file edits -> impact -> design -> tasks -> IDL protocol -> test-first for consumers when needed -> implementation -> code review -> evidence/gates.
- Bugfix: intake enough to define expected behavior -> workspace scan -> harness context loading -> root cause debugging -> worktree isolation before production edits -> test-first -> implementation -> code review -> evidence/gates -> self-refinement when the root cause is reusable.
- Harness documentation or process change: intake -> workspace scan -> harness context loading -> worktree isolation when edits are requested -> authoring or impact/design as needed -> evidence/gates if gate-linked files change.
- Gate-only work: workspace scan -> harness context loading -> root cause debugging if the gate failure is unclear -> evidence/gates.
- Code review request: workspace scan -> harness context loading -> code review; do not edit unless the user asks for fixes.
- Repeated correction, reusable lesson, or context gap: workspace scan -> harness context loading -> self-refinement; do not edit durable assets without explicit approval.
- Branch, worktree, or isolated workspace setup: workspace scan -> harness context loading -> worktree isolation.
- User explicitly asks for analysis only: workspace scan -> harness context loading when semantic context matters -> answer; do not edit.

## Stage Lock

When a requirement is new, missing, unclear, or not explicitly approved, the active stage is intake.

In intake stage:

- Allowed side effects: none.
- Allowed commands: read-only workspace scan and Harness context loading commands only.
- Allowed output: questions, analysis, and a chat-only Requirement Brief.
- Forbidden file edits:
  - `requirements/{requirement-id}/`
  - `.proto`
  - generated contracts
  - business code
  - gate JSON, rendered gate Markdown, evidence, or task files

Do not create draft lifecycle artifacts just to make progress. Wait for explicit approval first.

## Stop Conditions

Stop and ask before editing when:

- Requirement ID or target repo is unclear.
- The task appears to involve IDL but the change type is unclear.
- Branch name and requirement ID conflict.
- Dirty worktree changes may be overwritten.
- User asks to demonstrate, discuss, review, or plan rather than implement.
- The user has clarified an implementation direction but has not explicitly approved the Requirement Brief.
- The next step would set `status: approved`, `approved_by`, or `approved_at` without a user approval message for that exact brief or stage.
- A behavior change would start production edits without `spark-test-first-implementation` evidence or an explicit exception.

## Red Flags

If you think any of these, stop and return to intake:

- "The user confirmed the interface direction, so the requirement is approved."
- "I can write the requirement files first and ask later."
- "Harness lifecycle files are documentation, not real edits."
- "I can update IDL first and backfill the brief."
- "`status: approved` is only a placeholder."

## Output

State which Spark skill is being used and why. Keep the router response short, then follow the selected workflow.
