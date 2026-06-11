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

Four dimensions are delegated to independent checker agents and run in
parallel, each in its own context:

| Dimension | Checker agent |
|---|---|
| Requirement/design/task traceability and task-slice scope | `code_review_traceability_checker` |
| Protobuf, HTTP, error-code, event, and generated-contract compatibility | `code_review_contract_checker` |
| Data, transaction, concurrency, retry, idempotency, and rollback behavior | `code_review_data_concurrency_checker` |
| Security, error handling, logging, metrics, and tracing | `code_review_security_error_checker` |

When the diff touches backend services, also dispatch
`backend_architecture_reviewer` for architecture boundaries and dependency
direction.

The remaining dimensions are checked by the aggregation step, not delegated:

- Test value, failure-path assertions, and evidence quality.
- Complexity, duplicated logic, reviewability, and build artifacts.

Do not approve a lifecycle gate. A review can say the changes are ready for the
next gate, but Janus gate state and human approval remain separate.

## Process

1. Establish the exact diff, base revision, and task ID.
2. Dispatch the four checker agents in parallel with the same diff scope.
   Include `backend_architecture_reviewer` when backend services change.
3. Each checker returns fixed-format findings (severity, file:line, issue,
   impact, required fix) for its dimension only, or an explicit no-findings
   result with the checked scope.
4. Run the aggregation step via `code_review_reporter`: merge all checker
   findings verbatim, add the non-delegated dimension checks, and write the
   report to `requirements/{requirement-id}/reviews/{task-id}.md` using
   `context/harness-framework/templates/review-report.md`.
5. A checker that did not run must appear in the report as `skipped` with a
   reason. Never treat a skipped dimension as passed.
6. If findings conflict with existing context, cite the source file and line.
7. If the review finds a reusable lesson, hand off to `spark-self-refinement`
   after the review result is reported.

## Output

The persisted report at `requirements/{requirement-id}/reviews/{task-id}.md`
is the review record. A spoken summary in conversation never replaces it.

Findings are ordered by severity:

- `P0`: correctness, data loss, security, or contract break.
- `P1`: likely production bug, missing required evidence, or gate blocker.
- `P2`: maintainability, test, observability, or rollout risk.
- `P3`: minor cleanup that should not block.

For each finding include:

- source dimension and checker
- file and tight line reference when available
- issue
- impact
- required fix or decision

The report conclusion is `not-ready` while any P0 or P1 finding is open, and
`ready-for-gate` otherwise. Then include open questions, tests inspected or
run, and residual risk. If no issues are found, say so and still report test
or evidence gaps.

In conversation, reply with a one-line summary pointing to the report file.
