---
name: self-refinement
description: Capture reusable corrections, lessons, and recurring failure patterns into Harness context so future Codex runs inherit them.
---

# Self Refinement

Use this skill when the user corrects a recurring mistake, when a gate uncovers a repeatable failure mode, or when implementation work reveals durable service knowledge.

## Classification

- Team-wide rule: update `context/team/`.
- Harness process rule: update `context/harness-framework/`.
- Service-specific state, SOP, or experience: update `context/project/{project}/{domain}/{service}/`.
- Tooling behavior: update `.agents/skills/`, `.codex/agents/`, hooks, or Janus documentation.

## Workflow

1. State the observed pattern.
2. Decide whether it is reusable or one-off.
3. Pick the narrowest durable location.
4. Draft the change in Chinese for team-facing documents.
5. If the lesson affects gates, update the relevant gate criteria or agent instructions.
6. If the lesson affects machine validation, update Janus or hook behavior instead of relying on prose.
