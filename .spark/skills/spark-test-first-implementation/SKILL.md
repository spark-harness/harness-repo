---
name: spark-test-first-implementation
description: Use before implementing Spark behavior changes, bug fixes, refactors, adapters, use cases, repositories, generated-contract consumers, or frontend flows. Establishes the failing test, characterization test, baseline command, or explicit exception required before production edits.
---

# Spark Test-First Implementation

Create executable expectations before production edits.

## Principle

Behavior changes and bug fixes need a failing or characterization test before
implementation. Tests should prove business behavior, contract behavior, or
failure semantics, not internal call order.

## Preconditions

- Requirement intent is approved, or the user explicitly requested a narrow bugfix.
- `spark-workspace-scan` has checked dirty state.
- `spark-harness-context-loading` has loaded relevant testing, contract, service, and project context.
- Target task or bug scope is known.

## Classify The Change

| Change type | Required before production edit |
| --- | --- |
| New business behavior | Add a test that fails for the missing behavior. |
| Bug fix | Add or expose a test that fails for the bug. |
| Refactor | Run a passing baseline; add characterization tests for risky behavior. |
| Contract adapter | Add contract-facing or service-facing test coverage where feasible. |
| Frontend behavior | Add component, integration, or e2e coverage for user-visible behavior where feasible. |
| Docs, templates, generated code, config-only | Record an explicit exception and verification command. |

## Rules

- Run the new or changed test and confirm it fails for the expected reason before production edits.
- Keep tests focused on business results, stable contracts, and failure semantics.
- Do not lock tests to private implementation details unless no better seam exists.
- Do not manually edit generated code to satisfy a test.
- Do not delete user or existing work just to satisfy test-first discipline. If code already exists, add the missing test and verify against a clean baseline when feasible.
- If a test-first exception is needed, state why and name the verification command that replaces it.

## Test Selection

Prefer the narrowest test that proves the risk:

- domain or use-case unit test for pure business rules
- adapter or integration test for API, repository, config, transaction, or generated-contract behavior
- frontend component or e2e test for user-visible behavior
- Buf and generated-contract checks for protobuf-only work

## Output

Before implementation, report:

- selected test level
- test file or planned test file
- failing command and result, or explicit exception
- expected behavior being proven
- follow-up verification after implementation
