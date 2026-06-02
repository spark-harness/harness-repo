---
name: janus-gate-workflow
description: Generate, validate, render, and verify Harness gate reports using Janus gate JSON as the machine-readable source of truth.
---

# Janus Gate Workflow

Use this skill when producing or validating a Harness gate result.

## Files

- Machine source: `requirements/{requirement-id}/gates/{gate-id}.gate.json`
- Audit view: `requirements/{requirement-id}/gates/{gate-id}.md`
- CLI: `janus` on PATH.

Check environment:

```sh
janus version
```

## Required Commands

Validate gate JSON:

```sh
janus gate validate requirements/{requirement-id}/gates/{gate-id}.gate.json
```

Render Markdown:

```sh
janus gate render \
  --input requirements/{requirement-id}/gates/{gate-id}.gate.json \
  --output requirements/{requirement-id}/gates/{gate-id}.md
```

Check Markdown drift:

```sh
janus gate render --check \
  --input requirements/{requirement-id}/gates/{gate-id}.gate.json \
  --output requirements/{requirement-id}/gates/{gate-id}.md
```

Verify stage release:

```sh
janus gate verify --input requirements/{requirement-id}/gates/{gate-id}.gate.json
```

## Rules

- Generate or edit JSON first, then render Markdown.
- Do not hand-edit generated blocking fields in Markdown.
- If `gate verify` returns a non-zero exit code, report the exact gate state and do not claim the stage is released.
- When input files change, old gate JSON is stale until regenerated with new hashes.
