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
2. `spark-context-scan`
3. `spark-requirement-authoring`
4. `spark-impact-analysis`
5. `spark-design-authoring`
6. `spark-task-planning`
7. `spark-idl-change-protocol`
8. `spark-implementation-execution`
9. `spark-evidence-gate-completion`

## Routing

- New feature or behavior change: intake -> context scan -> requirement authoring -> impact -> design -> tasks -> implementation -> evidence/gates.
- IDL or contract change: intake -> context scan -> impact -> design -> tasks -> IDL protocol -> implementation -> evidence/gates.
- Bugfix: intake enough to define expected behavior -> context scan -> design only if behavior or architecture is ambiguous -> implementation -> evidence/gates.
- Harness documentation or process change: intake -> context scan -> authoring or impact/design as needed -> evidence/gates if gate-linked files change.
- Gate-only work: context scan -> evidence/gates.
- User explicitly asks for analysis only: context scan and answer; do not edit.

## Stage Lock

When a requirement is new, missing, unclear, or not explicitly approved, the active stage is intake.

In intake stage:

- Allowed side effects: none.
- Allowed commands: read-only context scan commands only.
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

## Red Flags

If you think any of these, stop and return to intake:

- "The user confirmed the interface direction, so the requirement is approved."
- "I can write the requirement files first and ask later."
- "Harness lifecycle files are documentation, not real edits."
- "I can update IDL first and backfill the brief."
- "`status: approved` is only a placeholder."

## Output

State which Spark skill is being used and why. Keep the router response short, then follow the selected workflow.
