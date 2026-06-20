---
name: spark-debugging-root-cause
description: Investigate Spark bugs, failing tests, build failures, Buf or generation failures, Janus gate failures, CI failures, runtime errors, and unexpected behavior before proposing fixes. Use when root cause must be proven across requirements, service matrix, IDL, generated contracts, business code, evidence, or gates.
---

# Spark Root Cause Debugging

Find the cause before changing code or lifecycle artifacts.

## Rule

No fix before root cause evidence.

Do not patch symptoms, rerun random commands, or relax gates just to move
forward. A fix is allowed only after the failing behavior is reproduced or a
decisive static cause is proven.

## Preconditions

- Start with `spark-workspace-scan` for repo state, branches, dirty changes, and service matrix.
- Use `spark-harness-context-loading` when the failure touches requirements, gates, services, IDL, tests, or team rules.
- Preserve unrelated dirty changes.

## Process

1. Capture the exact failure: command, repo, exit code, relevant output, and affected files.
2. Reproduce with the narrowest meaningful command, unless the failure is already fully explained by static evidence.
3. Classify the failure:
   - lifecycle or Janus gate
   - protobuf, Buf, generation, or generated-contract consumption
   - build or dependency resolution
   - unit, integration, end-to-end, or frontend test
   - runtime behavior, logs, config, or environment
4. Trace expected behavior back to requirement, design, task, service matrix, and team context.
5. Trace actual behavior through code, contracts, generated artifacts, configuration, and evidence.
6. State the root cause as a falsifiable claim with evidence.
7. Choose the smallest fix that addresses the cause and preserves the approved scope.
8. Verify by rerunning the original failing command and the narrow regression command.

## Failure-Specific Checks

- Gate failure: inspect gate JSON, input hashes, approval source, and `janus` command output.
- IDL failure: inspect `.proto`, `buf.yaml`, `buf.gen.yaml`, generated output, and consuming service dependency.
- Contract consumption failure: confirm generated artifact version, local install or repository auth, package names, and service imports.
- Test failure: inspect the failing assertion and the behavior under test before editing implementation.
- Runtime failure: inspect logs, configuration, process state, ports, and service startup path.

## Stop Conditions

Stop and ask before editing when:

- the failure cannot be reproduced and static evidence is insufficient
- the root cause points outside the approved requirement scope
- fixing requires a breaking contract change
- branch or repo state would overwrite unrelated work
- a gate is blocked only by missing human approval

## Output

Report:

- failure reproduced or static proof used
- root cause
- evidence files or command outputs
- proposed fix
- verification command
- whether `spark-self-refinement` should capture a reusable lesson
