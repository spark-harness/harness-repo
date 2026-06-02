---
name: managing-requirement-lifecycle
description: Create, continue, review, gate-check, and advance Harness requirements using the repository process, templates, service matrix, and Janus gate validation.
---

# Managing Requirement Lifecycle

Use this skill when the user wants to create, continue, review, gate-check, advance, or close a requirement in `harness-repo`.

## Goal

把需求从自然语言输入推进为可评审、可追溯、可交付的工程产物。

## Source Of Truth

- Process stages: `context/harness-framework/main-process-numbering.md`
- Gate implementation: `context/harness-framework/gate-implementation.md`
- Template policy: `context/harness-framework/document-template-policy.md`
- Context collection: `context/harness-framework/context-collection.md`
- Service topology: `.service-matrix/dependencies.yaml`
- Requirement templates: `context/harness-framework/templates/`
- Requirement template: `context/harness-framework/templates/requirement.md`
- Impact analysis template: `context/harness-framework/templates/impact-analysis.md`
- Gate report template: `context/harness-framework/templates/gate-report.md`
- Gate report source: `requirements/{requirement-id}/gates/{gate-id}.md`
- Gate CLI: `janus` on PATH.

## Workflow

1. Confirm `janus version` works.
2. Confirm the requirement id and current stage.
3. Read `context/team/INDEX.md`, `context/harness-framework/INDEX.md`, `context/harness-framework/context-collection.md`, and the relevant `context/project/` entry.
4. Use `.service-matrix/dependencies.yaml` to resolve affected services, repo paths, IDL paths, and libraries.
5. Create or update requirement artifacts under `requirements/{requirement-id}/`.
6. For gate checks, write a fixed-format gate report under `requirements/{requirement-id}/gates/`.
7. If Janus provides validation in the local environment, run the matching validation command against the gate report.
8. Use stage advancement checks only when deciding whether the gate can release a stage.
10. Use `janus requirement verify --requirement <id> --target merge` before merge-oriented claims.
11. If a user correction is a reusable lesson, propose updating `context/project/.../experience/` or the relevant team/framework rule.

## Gate Report Requirements

- `Checked At` must be present.
- `Source Files` must include every file used for the gate decision.
- `BLOCKED` must set `Blocks Next Stage: yes` and include blocking issues.
- `WARN` must include warnings with follow-up actions.
- `WAIVED` must include complete waiver fields.
- If IDL impact is absent, record the reason in the checklist or warnings.

## Output

Every lifecycle action must update repository files or state what prevented the update. Do not use chat-only gate decisions.
