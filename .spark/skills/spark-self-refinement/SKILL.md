---
name: spark-self-refinement
description: Capture reusable Spark lessons after human corrections, repeated failures, root-cause findings, context gaps, gate drift, service onboarding discoveries, or workflow rule changes. Use to propose and, with explicit approval, update context/team, context/harness-framework, context/project experience, service matrix, templates, skills, agents, or commands.
---

# Spark Self Refinement

Turn repeated lessons into reviewable Harness assets.

## Rule

Do not treat chat memory as a source of truth. Capture only lessons backed by
files, commands, reviewed decisions, or an explicit user correction.

Do not write context, skills, templates, gates, or service matrix changes unless
the user explicitly asks for the update or approves the proposed refinement.

## When To Use

Use after:

- the user corrects a recurring misunderstanding
- a root-cause investigation reveals a reusable failure pattern
- a gate or lifecycle rule drifts from the actual process
- service, module, IDL, or generated-contract knowledge is missing
- a workaround should become a documented SOP
- a skill, command, template, or context file failed to guide the agent correctly

Do not use for one-off implementation details, secrets, credentials, private
production data, or facts that cannot be verified.

## Destination

Choose the smallest durable location:

| Lesson type | Destination |
| --- | --- |
| Cross-project engineering rule | `harness-repo/context/team/` |
| Lifecycle, gate, template, or context protocol | `harness-repo/context/harness-framework/` |
| Project, domain, service, or historical lesson | `harness-repo/context/project/{project}/{domain}/...` |
| Service topology, repo path, IDL path, dependency | `harness-repo/.service-matrix/dependencies.yaml` |
| Agent behavior or workflow gap | `harness-repo/.spark/skills/`, `.spark/agents/`, or `.spark/commands/` |
| Requirement-specific evidence | `harness-repo/requirements/{requirement-id}/evidence/` |

## Process

1. State the reusable lesson in one sentence.
2. Cite the evidence: file, command, gate, test, or user correction.
3. Decide whether it is team, framework, project, service, matrix, or skill knowledge.
4. Read the destination index or existing nearby file first.
5. Propose the minimal change and ask for approval unless approval is already explicit.
6. After approval, edit only the selected asset and required index.
7. Validate the changed asset:
   - skills: `quick_validate.py`
   - gates or requirements: Janus validation or requirement verification
   - service matrix: matrix-specific validator when available
   - docs: link and index consistency checks

## Output

Report:

- lesson captured
- destination chosen
- files changed or proposed
- validation run
- related follow-up if the lesson exposes a larger process gap
