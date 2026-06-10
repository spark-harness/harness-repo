---
name: spark-harness-context-loading
description: Load the minimal Harness semantic context for Spark tasks after workspace state is known. Use after spark-workspace-scan and before requirement authoring, impact analysis, design, task planning, IDL changes, implementation, gate work, or documentation-governance decisions.
---

# Spark Harness Context Loading

Load the smallest set of Harness context files that can change the decision,
design, implementation, or gate result.

This skill is read-only. It does not edit context files. If required context is
missing, report a context gap instead of guessing from chats, paths, or memory.

## Inputs

- Task type.
- Requirement ID or ticket ID, if known.
- Workspace Pack from `spark-workspace-scan`.
- Affected service, library, module, project, or domain, if known.

## Fixed Entry Points

Read these first:

```text
AGENTS.md
harness-repo/context/README.md
harness-repo/context/team/INDEX.md
harness-repo/context/harness-framework/INDEX.md
harness-repo/context/harness-framework/context-collection.md
```

If the task involves services, modules, repo paths, IDL, generated contracts, or
cross-service dependencies, also read:

```text
harness-repo/.service-matrix/dependencies.yaml
harness-repo/context/project/INDEX.md
```

Use the service matrix to resolve project, module, service, repo path, IDL repo,
and proto path. Do not infer service paths from directory names when the matrix
has an entry.

If project or service context exists, read the nearest relevant `INDEX.md`, for
example:

```text
harness-repo/context/project/{project}/{domain}/INDEX.md
harness-repo/context/project/{project}/{domain}/{service}/INDEX.md
```

If it does not exist, report a context gap with the minimal suggested location.

## Task-Specific Context

Load only files relevant to the task:

| Task type | Required context |
| --- | --- |
| Requirement intake or authoring | `main-process-numbering.md`, `document-template-policy.md`, related project context |
| Impact analysis | `.service-matrix/dependencies.yaml`, related project context, `contract-compatibility.md` when IDL/API may change |
| Design | `main-process-numbering.md`, `document-template-policy.md`, relevant team architecture/testing/observability/security rules |
| Task planning | `main-process-numbering.md`, `document-template-policy.md`, approved requirement, impact, and design |
| IDL or generated contracts | `contract-compatibility.md`, service matrix proto path, relevant `.proto` files, Buf config |
| Backend implementation | `backend-clean-architecture.md`, `testing.md`, `logging.md`, `metrics.md`, `tracing.md`, `security.md`, relevant project context |
| Frontend implementation | `frontend-clean-architecture.md`, `testing.md`, `security.md`, relevant project context |
| Money or currency work | `money.md`, service or library entry points, related tests |
| Gate work | `gate-policy.md`, `gate-implementation.md`, gate inputs, relevant team rules |
| Git, merge, or delivery | `git.md`, `git-workflow.md`, related gate and evidence files |
| Context or process governance | `context-collection.md`, affected `INDEX.md`, affected skills, agents, commands, and rules |

## Context Pack

Report:

- task type and requirement ID
- affected services, libraries, modules, and repos
- service matrix facts used
- context files loaded
- requirement lifecycle artifacts loaded
- code, IDL, or evidence entry points loaded
- context gaps and minimal suggested files
- whether the loaded context is sufficient for the next workflow skill

## Stop Conditions

Stop before editing if:

- service matrix facts conflict with project context
- required project or service context is missing and affects the decision
- a lifecycle source of truth is missing
- loaded context contradicts the requested change
- required approval or gate state cannot be established from files

## Rules

- Read entry files before detail files.
- Prefer `INDEX.md` files over broad directory scans.
- Use `rg` and `find` to locate targeted files; do not load entire generated trees.
- Record context gaps explicitly.
- Do not treat memory or chat history as a replacement for Harness source files.
