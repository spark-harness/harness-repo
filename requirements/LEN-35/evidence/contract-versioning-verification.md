# LEN-35 Contract Versioning Verification Evidence

## Scope

- Requirement: LEN-35
- Harness repo branch: feature/LEN-35-contract-versioning
- IDL repo branch: feature/LEN-35-contract-versioning
- Business repo branch: feature/LEN-35-contract-versioning
- Harness base revision: ec5189f
- IDL base revision: 4a589e4
- Business base revision: 9d111cb

## Result

PASS.

## Verified Commands

```text
jq empty requirements/LEN-35/tasks.json
git diff --check
janus requirement gate-check --requirement LEN-35 --gate requirement-review --owner Forest
janus requirement gate-check --requirement LEN-35 --gate design-review --owner Forest
janus requirement gate-check --requirement LEN-35 --gate dev-entry --owner Forest
janus requirement gate-check --requirement LEN-35 --gate service-repo-check --owner Forest
janus gate validate requirements/LEN-35/gates/requirement-review.gate.json
janus gate render --input requirements/LEN-35/gates/requirement-review.gate.json --output requirements/LEN-35/gates/requirement-review.md --check
janus gate validate requirements/LEN-35/gates/design-review.gate.json
janus gate render --input requirements/LEN-35/gates/design-review.gate.json --output requirements/LEN-35/gates/design-review.md --check
janus gate validate requirements/LEN-35/gates/dev-entry.gate.json
janus gate render --input requirements/LEN-35/gates/dev-entry.gate.json --output requirements/LEN-35/gates/dev-entry.md --check
janus gate validate requirements/LEN-35/gates/service-repo-check.gate.json
janus gate render --input requirements/LEN-35/gates/service-repo-check.gate.json --output requirements/LEN-35/gates/service-repo-check.md --check
```

All commands completed successfully.

## Contract / IDL Boundary

- No protobuf file was modified.
- No generated Java or Go contract repository was modified.
- idl-repo was included as the source-of-truth contract repository worktree for service-repo-check readiness only.
- business-repo was included as a read-only worktree so Janus could resolve the service matrix path for user-api; no business files were modified.
- idl-repo contains Buf v2 configuration:
  - buf.yaml: version v2
  - buf.gen.yaml: version v2
- Buf CLI available locally: 1.63.0.

## Covered Acceptance

- AC1: context/team/contract-versioning.md defines development, rc, and formal stages.
- AC2: Java snapshot, RC, and formal SemVer rules are documented.
- AC3: Go generation and self-managed idl-go-repo module tag distribution are documented.
- AC4: Go v2+ module path and tag major matching rules are documented.
- AC5: Formal release is documented as idl-repo SemVer tag driven.
- AC6: Merge-readiness dependency rejection rules are documented.
- AC8: Master-bound business changes must retest after consuming formal versions.
- AC10: idl-java-repo and idl-go-repo are not default worktrees for ordinary IDL changes.

## Notes

No Traceability Manifest was introduced. The required traceability model is the minimal evidence set defined in context/team/contract-versioning.md.
