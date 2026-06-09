---
name: spark-implementation-execution
description: Implement Spark business code from approved requirement, design, and tasks. Use when modifying business-repo services, tests, adapters, use cases, repositories, generated-contract consumers, or frontend apps after intake/design/task planning are clear.
---

# Spark Implementation Execution

Implement only the approved task slice.

## Preconditions

- Requirement intent is approved or the user explicitly requested a narrow bugfix.
- Context scan has checked dirty state.
- IDL changes, if any, have passed `spark-idl-change-protocol` or are explicitly deferred.
- Target task from `tasks.json` is known.
- `design.md` exists for feature, behavior, API, or IDL-linked work.

Clarifying an implementation direction is not requirement approval. If the task is not an explicitly narrow bugfix and approval is missing, stop before editing business code.

## Rules

- Prefer tests first for behavior changes.
- Follow existing package, framework, and architecture patterns.
- Keep edits scoped to affected service files.
- Do not overwrite unrelated dirty changes.
- Do not make unrelated refactors.
- Do not silently skip tests.

## Verification

Run the narrowest meaningful test first, then the service-level suite when feasible.

Examples:

```bash
mvn test
go test ./...
npm test
```

Record exact commands and outcomes for evidence.

After running verification commands, immediately inspect `git status --short`
from the affected repo root. If the test/build command created disposable
outputs such as Maven `target/`, Gradle `build/`, Node `.next/`, `dist/`, or
coverage folders, remove those outputs before staging. Do not add repository
ignore rules for one-off verification artifacts unless the user explicitly
asks for repository ignore policy changes.

## Output

Report changed files, tests run, failures, and remaining risks. Continue to `spark-evidence-gate-completion` when implementation is verified.
