---
name: spark-impact-analysis
description: Analyze Spark requirement impact across service matrix, repos, IDL, generated contracts, upstream consumers, data, config, permissions, observability, rollout, and rollback. Use before design or implementation for cross-repo, service, IDL, or gate-linked changes.
---

# Spark Impact Analysis

Create or update the requirement impact analysis from actual service topology.

## Source Of Truth

- `harness-repo/.service-matrix/dependencies.yaml`
- `harness-repo/context/project/`
- Context Pack from `spark-harness-context-loading`
- `idl-repo/buf.yaml`
- affected service code and existing requirements

## Preconditions

Do not write `impact-analysis.md` unless `requirements/{requirement-id}/requirement.md` exists and is approved from an explicit Requirement Brief approval.

If the requirement artifact is missing, draft, or approval is ambiguous, return to `spark-requirement-intake` or `spark-requirement-authoring` before continuing.

## File

Write `harness-repo/requirements/{requirement-id}/impact-analysis.md`.

## Required Coverage

- summary
- affected domains
- affected services and repos
- upstream/downstream consumers
- API and protobuf contract impact
- generated contract impact
- data, migration, cache, and runtime storage impact
- config, permission, observability, logs, tracing, events
- rollout and rollback
- risks and mitigations

## IDL Rules

For IDL work, explicitly state:

- `.proto` files
- Buf module/config
- required checks
- breaking baseline
- compatibility risk

Do not proceed to design if IDL impact is unclear.

## Gate

Impact approval is part of the requirement-review gate stage. When
`impact-analysis.md` is approved or updated after approval, create or refresh
`requirements/{requirement-id}/gates/requirement-review.gate.json` with current
SHA-256 inputs for `requirement.md` and `impact-analysis.md`, then run:

```bash
janus gate validate requirements/{requirement-id}/gates/requirement-review.gate.json
```

Do not create `requirement-review` before `impact-analysis.md` exists. If the
requirement or impact approval record is missing after both files exist, the
gate may be generated as `BLOCKED` with a human-approval blocking issue.
