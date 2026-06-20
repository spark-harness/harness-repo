---
name: spark-design-authoring
description: Write Spark Harness design documents after requirement and impact analysis. Use to create or update design.md with requirement-to-design traceability, architecture boundaries, API/contract design, error handling, testing strategy, rollout, rollback, and risks.
---

# Spark Design Authoring

Turn approved requirements and impact analysis into a focused design.

## File

Write `harness-repo/requirements/{requirement-id}/design.md`.

## Preconditions

Do not write design files unless:

- `requirements/{requirement-id}/requirement.md` exists and is approved
- impact analysis exists or the current workflow explicitly documents why impact analysis is not needed
- Harness context has been loaded with `spark-harness-context-loading`

If approval is missing or inferred only from a technical clarification, stop and return to intake.

## Required Sections

- Requirement Traceability table mapping requirement items to design decisions.
- Summary.
- Affected services.
- API / contract design when relevant.
- Application design.
- Data / config / permission.
- Observability.
- Testing strategy.
- Rollout and rollback.
- Risks.

## Rules

- Do not write code or IDL here.
- Use existing service architecture and local naming.
- Avoid unrelated refactors.
- Make non-goals explicit when they constrain implementation.
- If design cannot resolve a requirement ambiguity, return to `spark-requirement-intake`.

## Gate

Approval and gate generation are the same stage task. When `design.md` is
approved or updated with an approval record, immediately create or refresh
`requirements/{requirement-id}/gates/design-review.gate.json` with current
SHA-256 inputs, then run:

```bash
janus gate validate requirements/{requirement-id}/gates/design-review.gate.json
```

Do not proceed to task planning while the design gate is missing or stale.
