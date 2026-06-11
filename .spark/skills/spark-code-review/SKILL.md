---
name: spark-code-review
description: Review Spark implementation changes after a task, before evidence or merge, or when the user asks for code review. Use for business-repo, idl-repo, generated-contract consumer, frontend, and Harness workflow changes that must be checked against requirements, design, tasks, service matrix, team rules, tests, security, observability, and contract compatibility.
---

# Spark Code Review

Review Spark changes as an engineering gate, not as a summary pass.

## Preconditions

- `spark-workspace-scan` has checked repo state and dirty changes.
- `spark-harness-context-loading` has loaded relevant team, framework, project, and service context.
- Requirement-linked work has a known requirement ID and relevant lifecycle artifacts.
- The review scope is explicit: repository, base revision, changed files, or task slice.

If the base revision or review scope is unclear, stop and ask before reviewing.

## Inputs

Load only files that can affect the review:

- `requirements/{requirement-id}/requirement.md`
- `requirements/{requirement-id}/impact-analysis.md`
- `requirements/{requirement-id}/design.md`
- `requirements/{requirement-id}/tasks.json`
- `.service-matrix/dependencies.yaml`
- Relevant `context/team/` and `context/project/` files
- Current diff, changed tests, generated-contract usage, and evidence files

## Review Dimensions

Check these dimensions independently:

- Requirement and design traceability.
- Task-slice scope and unrelated changes.
- Architecture boundaries and dependency direction.
- Protobuf, HTTP, error-code, event, and generated-contract compatibility.
- Data, transaction, concurrency, retry, idempotency, and rollback behavior.
- Error handling, logging, metrics, tracing, and security.
- Test value, failure-path assertions, and evidence quality.
- Complexity, duplicated logic, reviewability, and build artifacts.

Do not approve a lifecycle gate. A review can say the changes are ready for the
next gate, but Janus gate state and human approval remain separate.

## Process

1. Establish the exact diff and base revision.
2. Map changed files to requirement items, design decisions, and task IDs.
3. Inspect affected service or IDL entry points before judging behavior.
4. Review each dimension and collect only actionable findings.
5. If findings conflict with existing context, cite the source file and line.
6. If the review finds a reusable lesson, hand off to `spark-self-refinement`
   after the review result is reported.

## Output

Lead with findings ordered by severity:

- `P0`: correctness, data loss, security, or contract break.
- `P1`: likely production bug, missing required evidence, or gate blocker.
- `P2`: maintainability, test, observability, or rollout risk.
- `P3`: minor cleanup that should not block.

For each finding include:

- file and tight line reference when available
- issue
- impact
- required fix or decision

Then include open questions, tests inspected or run, and residual risk. If no
issues are found, say so and still report test or evidence gaps.
