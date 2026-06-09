---
name: spark-task-planning
description: Create traceable Spark implementation task plans. Use after requirement, impact, and design are ready to write or update requirements/{id}/tasks.json with verifiable slices mapped to requirement items, design decisions, affected services, acceptance criteria, and status.
---

# Spark Task Planning

Split approved design into implementation slices that can be verified and committed independently.

## File

Write `harness-repo/requirements/{requirement-id}/tasks.json`.

## Preconditions

Do not write `tasks.json` unless:

- the requirement is approved
- `design.md` exists
- the task slices can be traced to requirement items and design decisions

If any precondition is missing, stop and return to the earlier lifecycle skill.

## Task Shape

Each task must include:

- `id`
- `title`
- `scope`
- `trace.requirement_items`
- `trace.design_decisions`
- `affected_services`
- `acceptance`
- `status`

## Typical Slices

- Harness artifacts
- IDL contract
- generated contracts
- application tests
- implementation
- evidence and gates

## Rules

- Keep tasks small enough to verify locally.
- Do not hide IDL and business implementation in one task.
- Do not create tasks with vague scopes like "handle errors" or "add tests" without concrete acceptance links.
