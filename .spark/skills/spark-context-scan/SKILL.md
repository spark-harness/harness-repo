---
name: spark-context-scan
description: Read-only context scan for Spark multi-repo work. Use before creating or modifying Harness requirements, IDL, generated contracts, business services, gates, or commits to inspect repo state, branches, dirty changes, service matrix, related requirements, docs, code, and IDL.
---

# Spark Context Scan

Build a current Context Pack. This skill is read-only.

## Commands

Prefer these checks from `/Users/forest/Code/spark`:

```bash
janus version
git -C harness-repo status --short --branch
git -C idl-repo status --short --branch
git -C idl-java-repo status --short --branch
git -C business-repo status --short --branch
sed -n '1,220p' harness-repo/.service-matrix/dependencies.yaml
```

Read only relevant requirement, context, IDL, and service files. Use `rg` and `find`; do not scan entire generated trees unless needed.

## Context Pack

Report:

- repo branches and dirty state
- requirement ID and branch alignment
- affected services and repos from service matrix
- relevant requirement/design/gate files
- relevant `.proto` files and generated contract repos
- relevant service code and tests
- blockers before editing

## Stop Conditions

Stop before edit if:

- dirty changes are unrelated and overlap target files
- branch mismatch may fail Janus branch policy
- baseline tests already fail and the failure matters to the task
- required repo or source-of-truth file is missing
