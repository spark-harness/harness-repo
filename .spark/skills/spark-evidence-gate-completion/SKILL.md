---
name: spark-evidence-gate-completion
description: Complete Spark requirement evidence, Janus gates, verification, and optional commits. Use after docs, IDL, generated contracts, or implementation changes to write evidence, refresh gate input hashes, validate/render/verify gates, run requirement verify, and report multi-repo status.
---

# Spark Evidence Gate Completion

Turn work into auditable Harness evidence and Janus gate state.

## Source Of Truth

- Gate JSON: `harness-repo/requirements/{requirement-id}/gates/{gate-id}.gate.json`
- Gate Markdown: `harness-repo/requirements/{requirement-id}/gates/{gate-id}.md`
- Evidence: `harness-repo/requirements/{requirement-id}/evidence/`

## Preconditions

Do not create or update evidence or gate files unless:

- the requirement is approved
- implementation or contract work has produced concrete verification output
- the current stage expects evidence or gate completion

If evidence would be based only on intent, discussion, or unapproved work, stop and return to the earlier lifecycle skill.

## Gate JSON Requirements

- `checked_at` is RFC3339.
- `inputs` include every file used for the decision with current SHA-256.
- `BLOCKED` sets `blocks_next_stage: true` and has `blocking_issues`.
- `WARN` has warnings with follow-up actions.
- `WAIVED` has complete waiver fields and future expiration.
- If IDL impact is absent, set `idl_impact.impact` to `no` and include `na_reason`.
- If IDL impact is `yes`, include evidence.

## Commands

Run from `harness-repo`:

```bash
jq empty requirements/{requirement-id}/gates/{gate-id}.gate.json
janus gate validate requirements/{requirement-id}/gates/{gate-id}.gate.json
janus gate render --input requirements/{requirement-id}/gates/{gate-id}.gate.json --output requirements/{requirement-id}/gates/{gate-id}.md
janus gate verify --input requirements/{requirement-id}/gates/{gate-id}.gate.json
janus requirement verify --requirement {requirement-id} --target merge
```

Use `gate verify` only when deciding whether a stage can release.

## Final Report

Include:

- changed repos
- changed files
- verification commands
- gate status
- IDL breaking status
- branch and dirty state for all Spark repos
- remaining risks or blockers

Only commit when the user asks. Commit per repo with focused staging.
