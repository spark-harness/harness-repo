---
name: spark-idl-change-protocol
description: Safely change Spark protobuf IDL and generated contracts. Use for any task that creates, updates, replaces, removes, or checks .proto files, Buf config, generated Go output, or idl-java-repo contracts.
---

# Spark IDL Change Protocol

Handle protobuf contract changes without guessing compatibility.

## Hard Gates

- "New IDL" does not mean replacing an existing RPC unless the user explicitly approves replacement.
- If `buf breaking` fails, stop before business implementation unless the user explicitly approves the breaking change.
- Do not edit generated contracts manually; change `.proto` and run generation.
- Do not edit `.proto` or run generation until the requirement is approved and `tasks.json` identifies the IDL task, unless the user explicitly asks for read-only contract analysis.

## Preconditions

Before any IDL edit or generation, confirm:

- `requirements/{requirement-id}/requirement.md` exists and is approved.
- `design.md` exists and classifies the IDL change.
- `tasks.json` contains the IDL task being executed.
- Current repo branches align with the requirement ID, or the mismatch is explicitly approved by the user.

If any item is missing, stop and return to the appropriate lifecycle skill.

## Classify First

Classify the change as:

- additive new service/RPC/message
- compatible message extension
- replacement
- deletion
- field-number or type change
- config-only

## Commands

Run from `idl-repo`:

```bash
buf lint
buf generate
buf breaking --against .git#branch=master
```

If the current baseline cannot support breaking checks because of known structural drift, record the exact failure and treat it as a gate risk.

## Generated Contracts

Check:

```bash
git -C idl-repo status --short --branch
git -C idl-java-repo status --short --branch
find .generated/idl -type f | sort
```

## Evidence

Write or update `harness-repo/requirements/{requirement-id}/evidence/buf-checks.md` with commands, results, timestamps, and any breaking-risk notes.
