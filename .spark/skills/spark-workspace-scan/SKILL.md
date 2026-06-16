---
name: spark-workspace-scan
description: Read-only workspace scan for Spark multi-repo work. Use before creating or modifying Harness requirements, IDL, generated contracts, business services, gates, or commits to inspect repo state, branches, dirty changes, service matrix, related requirement files, IDL paths, and service entry points.
---

# Spark Workspace Scan

Build a current Workspace Pack. This skill is read-only.

This skill captures repository and topology facts. It does not load the full
Harness semantic context; use `spark-harness-context-loading` after this skill
when a task needs framework, team, project, or service knowledge.

## Commands

Prefer these checks from `$SPARK_WORKSPACE` (the multi-repo workspace root, i.e.
the parent of `harness-repo`; resolve it at runtime, do not hard-code a machine
path):

```bash
janus version
git -C harness-repo status --short --branch
git -C idl-repo status --short --branch
git -C idl-java-repo status --short --branch
git -C business-repo status --short --branch
sed -n '1,220p' harness-repo/.service-matrix/dependencies.yaml
```

Read only relevant requirement, IDL, and service entry-point files. Use `rg` and
`find`; do not scan entire generated trees unless needed.

## Workspace Pack

Report:

- repo branches and dirty state
- requirement ID and branch alignment
- affected services and repos from service matrix
- relevant requirement, design, task, evidence, and gate files
- relevant `.proto` paths and generated contract repos
- relevant service and test entry points
- context roots that should be loaded next by `spark-harness-context-loading`
- blockers before editing

## Stop Conditions

Stop before edit if:

- dirty changes are unrelated and overlap target files
- branch mismatch may fail Janus branch policy
- baseline tests already fail and the failure matters to the task
- required repo or source-of-truth file is missing
