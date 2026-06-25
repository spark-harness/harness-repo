# LEN-113 Implementation Evidence

Checked at: 2026-06-25T21:40:41+08:00

## Harness Template Path

Command:

```bash
rg -n 'harness-repo/templates|根目录 `templates`|└── templates|├── templates' \
  /Users/forest/Code/spark/AGENTS.md \
  /Users/forest/Code/spark/.worktrees/LEN-113/harness-repo/AGENTS.md \
  /Users/forest/Code/spark/.worktrees/LEN-113/harness-repo/README.md \
  /Users/forest/Code/spark/.worktrees/LEN-113/harness-repo/context \
  --glob '!**/.git/**'
```

Result: PASS. No output.

## Runtime Mirror

Command:

```bash
./scripts/install.sh --check
```

Working directory:

```text
/Users/forest/Code/spark/.worktrees/LEN-113/harness-repo
```

Result:

```text
install --check: in sync
```

## business-repo Directory Fact

Commands:

```bash
git -C business-repo status --short --branch
git -C .worktrees/LEN-113/business-repo status --short --branch
find business-repo -maxdepth 2 -type d -name services -print
find .worktrees/LEN-113/business-repo -maxdepth 2 -type d -name services -print
sed -n '35,55p' harness-repo/.service-matrix/dependencies.yaml
```

Results:

```text
## master...origin/master
 M apps/fides-bff/.golangci.yml
## chore/LEN-113-governance-drift
```

The `find ... services` commands returned no output.

The `business-repo` main checkout has an unrelated local modification in `apps/fides-bff/.golangci.yml`; it is not part of LEN-113 and was not touched.

Service matrix paths remain:

```text
fides -> {business-repo}/apps/fides-web
fides-bff -> {business-repo}/apps/fides-bff
applicant-api -> {business-repo}/apps/applicant-api
```

## Janus Verification

Command:

```bash
go test ./...
```

Working directory:

```text
/Users/forest/Code/spark/.worktrees/LEN-113/janus
```

Result:

```text
?   	janus/cmd/janus	[no test files]
ok  	janus/internal/cli	(cached)
ok  	janus/internal/delivery	(cached)
ok  	janus/internal/gate	(cached)
ok  	janus/internal/requirement	(cached)
```

GitHub PR CI for `spark-harness/janus#6` is green across listed build and test jobs at the time of evidence collection.

## Draft PR State

- `spark-harness/harness-repo#21`: Draft, open. `spark/harness-delivery-readiness` still reflects the pre-lifecycle failure from the earlier premature PR.
- `spark-harness/janus#6`: Draft, open, CI green.
