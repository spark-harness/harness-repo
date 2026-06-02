---
name: service-context-loader
description: Load service context for Harness work by resolving a service through the service matrix, then reading team, framework, and project context in order.
---

# Service Context Loader

Use this skill when a task names a service, module, repo path, IDL path, or cross-service dependency.

## Workflow

1. Read `context/harness-framework/context-collection.md`.
2. Read `.service-matrix/dependencies.yaml`.
3. Resolve the active team, module, service, repo path, libraries, upstream, downstream, and IDL requirements.
4. Read `context/team/INDEX.md`.
5. Read `context/harness-framework/INDEX.md` when the task touches lifecycle, gates, templates, or process.
6. Read `context/project/INDEX.md`.
7. If a service-specific `context/project/{project}/{domain}/{service}/INDEX.md` exists, read it before modifying requirement or design artifacts.
8. If the service context is missing, report it as a context gap and suggest the minimal files to add.

## Boundaries

- Use the service matrix as the source of truth for paths.
- Do not infer a service path from directory names when a matrix entry exists.
- Do not copy business implementation details into `context/project/`.
