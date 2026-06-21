# LEN-45 Buf Checks Evidence

## Scope

- IDL repo: `/Users/forest/Code/spark/.worktrees/LEN-45/idl-repo`
- Deleted source contract path: `vesta/spark/user/v1`
- Retained Lendora contract path: `vesta/lendora/applicant/v1`
- Generated Java / Go contract repositories are out of scope for this ticket.

## Commands

| Command | Result | Notes |
|---|---|---|
| `test ! -e vesta/spark` | PASS | Old Spark source contract tree is removed. |
| `test -e vesta/lendora/applicant/v1` | PASS | Current Lendora applicant source contract remains. |
| `buf lint` | PASS | No lint output. |
| `buf breaking --against .git#branch=master` | EXPECTED BLOCKED | Reports deletion of `vesta/spark/user/v1/{auth,ping,profile}.proto`. |

## Breaking Output

```text
<input>:1:1:Previously present file "vesta/spark/user/v1/auth.proto" was deleted.
<input>:1:1:Previously present file "vesta/spark/user/v1/ping.proto" was deleted.
<input>:1:1:Previously present file "vesta/spark/user/v1/profile.proto" was deleted.
```

## Decision

The breaking result is expected for LEN-45 because the requirement explicitly decommissions the old Spark user source contract. This ticket does not run or commit generated Java / Go contract cleanup; that cleanup remains assigned to the IDL production synchronization flow.
