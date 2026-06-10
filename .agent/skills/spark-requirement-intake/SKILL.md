---
name: spark-requirement-intake
description: Clarify Spark requirements before implementation. Use when a user gives a new feature, behavior change, bugfix with unclear expected behavior, IDL/API change, or cross-repo request and the goal, non-goals, acceptance criteria, affected services, or contract compatibility are not yet explicit.
---

# Spark Requirement Intake

Turn a rough request into an approved Requirement Brief. This is the first real step for development work.

## Hard Gate

Do not modify implementation code, protobuf IDL, generated contracts, gate files, or Harness lifecycle artifacts until the Requirement Brief is approved, unless the user explicitly asks for analysis-only file reads.

Before Requirement Brief approval, do not:

- create or edit `requirements/{requirement-id}/`
- set `status: approved`
- set `approved_by` or `approved_at`
- write requirement, impact-analysis, design, tasks, gates, reviews, or evidence files
- edit `.proto`
- run code generation
- edit generated contracts
- edit business code

## Process

1. Read the minimum current context needed to avoid asking stale questions.
2. Identify task class: feature, bugfix, IDL/API, refactor, documentation governance, gate-only, or operations.
3. Ask one clarifying question at a time. Prefer questions that change implementation direction.
4. For IDL/API work, first clarify the contract change type:
   - additive new service/RPC/message
   - compatible extension
   - replacement
   - deletion or field-number change
   - unknown
5. If the request spans independent subsystems, propose a split before drafting.
6. Produce a Requirement Brief in the chat only and ask for approval.

## Requirement Brief

Include:

- requirement ID or ticket ID
- goal
- non-goals
- affected domain and services
- affected repos
- IDL impact and breaking risk
- business rules
- acceptance criteria
- open questions
- next workflow skills

## Approval

Clarifying an implementation direction is not approval.

Only explicit approval counts, for example:

- "批准这个 Requirement Brief"
- "approved"
- "可以进入下一阶段"
- "按这个 Requirement Brief 继续"
- "可以创建需求文档"

These do not count as approval:

- confirming one field, endpoint, RPC, repo, or technology choice
- answering a clarifying question
- saying "对", "可以", or "就这样" when the object is only a local design choice
- asking for analysis, plan, or discussion

When the brief is ready, end with one direct approval question:

```text
请确认：是否批准这个 Requirement Brief，并允许我创建需求文档进入下一阶段？
```

If approved, continue to `spark-workspace-scan`, then
`spark-harness-context-loading`, or to `spark-requirement-authoring` only when
both workspace facts and Harness context are already current. If not approved,
revise the brief before any production work.
