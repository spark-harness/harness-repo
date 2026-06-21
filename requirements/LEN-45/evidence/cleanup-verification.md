# LEN-45 Cleanup Verification

## Run

- Checked at: 2026-06-21T11:35:27Z
- Branch: `feature/LEN-45-cleanup-old-spark-assets`
- Worktrees:
  - `/Users/forest/Code/spark/.worktrees/LEN-45/harness-repo`
  - `/Users/forest/Code/spark/.worktrees/LEN-45/business-repo`
  - `/Users/forest/Code/spark/.worktrees/LEN-45/idl-repo`

## Results

| Check | Command | Result |
|---|---|---|
| Service matrix schema | `python3 scripts/validate-service-matrix.py` | PASS: `service matrix valid` |
| Harness deleted paths | `test` for `requirements/SPARK-{1..5}` and `context/project/spark/user` | PASS: all missing |
| Business deleted paths | `test` for `.github/workflows/user-api-ci.yml`, `services/backend/user-api`, `services/frontend/aegis` | PASS: all missing |
| Business retained paths | `test` for `services/backend/applicant-api`, `services/frontend/fides`, `services/backend/fides-bff` | PASS: all exist |
| IDL deleted path | `test` for `vesta/spark` | PASS: missing |
| IDL retained path | `test` for `vesta/lendora/applicant/v1` | PASS: exists |
| IDL lint | `buf lint` | PASS |
| IDL breaking check | `buf breaking --against .git#branch=master` | EXPECTED BLOCKED: deleted `vesta/spark/user/v1/{auth,ping,profile}.proto` |
| Business active reference scan | `rg "services/(backend/user-api|frontend/aegis)|\\.github/workflows/user-api-ci\\.yml|vesta/spark/user|local/spark-user|com\\.spark\\.user"` | PASS: no active business-repo matches |
| Generated repos excluded | `git -C idl-java-repo status --short --branch`; `git -C idl-go-repo rev-parse --show-toplevel` | PASS: `idl-java-repo` unchanged; `idl-go-repo` is not a git checkout in this workspace and was not edited |
| Learning docs excluded | `git -C learning-docs-repo status --short --branch` | PASS: clean `main` |

## Notes

- `buf breaking` fails because this ticket intentionally deletes the old Spark user source contract. This is the expected contract risk for an explicit decommission.
- Historical LEN requirement files still mention `user-api`, `aegis`, or `vesta/spark/user` as audit records. They are not active service matrix entries, source contract files, business service directories, or CI workflow paths.
- `github.com/go-kratos/aegis` may remain as an indirect Go module dependency in retained Go code. It is not the deleted `services/frontend/aegis` application.
- `idl-java-repo` and `idl-go-repo` generated leftovers remain out of scope and must be handled by the IDL production synchronization flow.
