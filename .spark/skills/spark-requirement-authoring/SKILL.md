---
name: spark-requirement-authoring
description: Create or update Harness requirement artifacts for Spark requirements. Use after requirement intake is approved to write requirements/{id}/README.md and requirement.md with goals, non-goals, scenarios, business rules, acceptance criteria, and open questions in Chinese.
---

# Spark Requirement Authoring

Write reviewable Harness requirement files. Do not write design, IDL, or business code in this skill.

## Inputs

- Approved Requirement Brief.
- Current context from `spark-context-scan`.
- Requirement ID.

## Preconditions

Do not write files unless one of these is true:

- the current turn explicitly approves the Requirement Brief and permits requirement document creation
- an existing `requirements/{requirement-id}/requirement.md` is already approved by a prior explicit approval record

Clarifying implementation direction does not satisfy this precondition. If approval is missing, return to `spark-requirement-intake` and produce a chat-only Requirement Brief.

## Files

- `harness-repo/requirements/{requirement-id}/README.md`
- `harness-repo/requirements/{requirement-id}/requirement.md`

## Requirements

- Write team-facing guidance in Chinese.
- Keep sections short and concrete.
- Include Background, Goals, Non-Goals, Scenarios, Business Rules, Acceptance Criteria, Open Questions, and Notes.
- Use Given/When/Then for scenarios.
- Keep Harness docs semantic; do not copy business implementation details.
- If a concept is easy to confuse, state what it is not before what it is.

## Gate

Approval and gate generation are the same stage task. When the requirement
artifact is approved or updated with an approval record, immediately create or
refresh `requirements/{requirement-id}/gates/requirement-review.gate.json`, then
run:

```bash
janus gate validate requirements/{requirement-id}/gates/requirement-review.gate.json
janus gate render --input requirements/{requirement-id}/gates/requirement-review.gate.json --output requirements/{requirement-id}/gates/requirement-review.md
```

If `impact-analysis.md` is not available yet but the gate matrix expects it,
still write the gate report with `result: "BLOCKED"` and a blocking issue that
names the missing impact analysis. Do not leave the gate file absent.

## Output

Summarize changed files, the gate result, and unresolved open questions.
Continue to `spark-impact-analysis` when requirement artifacts are ready.
