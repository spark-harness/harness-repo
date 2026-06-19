---
name: spark-git-delivery
description: Use when Spark workspace work needs focused commits, push, PR/MR creation, merge preparation, history cleanup, or delivery reporting after changes already exist in one or more Spark subrepos.
---

# Spark Git Delivery

Use this after Spark changes exist and the user asks to commit, push, open a
PR/MR, prepare for merge, clean up history, or report delivery readiness.

This skill does not create requirements, design docs, code, IDL, gates, or
worktrees. If the affected repo is not isolated when it should be, return to
`spark-worktree-isolation` before continuing.

## Preconditions

- `spark-workspace-scan` has captured every Spark subrepo branch and dirty state.
- `spark-harness-context-loading` has loaded `context/team/git.md`,
  `context/team/git-workflow.md`, and related gate or evidence context.
- Any required code review, gate refresh, or test-first evidence has already run,
  or the missing verification is explicitly reported before delivery.

## Rule

`$SPARK_WORKSPACE` is not a Git repository. Delivery decisions are made per
subrepo:

- `harness-repo`: requirements, gates, context, templates, Spark skills, agents,
  commands, and rules.
- `business-repo`: services, frontend apps, libraries, tests, and runtime config.
- `idl-repo`: protobuf contracts and Buf configuration.
- `idl-java-repo`: generated Java contracts only when explicitly included.
- `learning-docs-repo`: training or learning material.
- `janus`: Janus CLI or gate engine changes.

Never stage, commit, push, or merge by treating the workspace root as one repo.

## Step 1: Re-scan Repo State

Run from `$SPARK_WORKSPACE`:

```bash
for repo in harness-repo business-repo idl-repo idl-java-repo learning-docs-repo janus; do
  [ -d "$repo/.git" ] || [ -d "$repo" ] || continue
  git -C "$repo" status --short --branch
done
```

If the task is being completed from `.worktrees/{ticket-id}/{repo}`, run the
same status command inside those worktree paths. Do not assume the main checkout
contains the active changes.

## Step 2: Classify Changes

For each dirty repo, classify files before staging:

- intended ticket changes
- generated files required by the intended changes
- user WIP unrelated to the current request
- local noise such as `.DS_Store`, `__pycache__/`, `.pyc`, build output, or
  dependency directories

Stop before staging if unrelated user WIP overlaps the target files. Remove only
noise that was produced by the current work and is clearly not meant to be kept.

## Step 3: Stage Narrowly

Stage only the intended slice:

```bash
git -C <repo-or-worktree> add -p
git -C <repo-or-worktree> add <specific-files>
git -C <repo-or-worktree> diff --staged
git -C <repo-or-worktree> status --short
```

Do not include business code, IDL, Harness docs, generated contracts, dependency
updates, formatting-only changes, and learning docs in the same repo-local commit
unless they are inseparable.

## Step 4: Commit Per Repo

Use Conventional Commits:

```text
<type>(<scope>): <summary>
```

Commit examples:

```text
docs(harness): define LEN-34 git delivery workflow
feat(user-api): add registration skeleton
fix(ci): use same-branch IDL checkout
chore(idl): regenerate Java contracts
```

Commit body should include why the change exists and the verification that backs
it. When AI or Agent decisions matter, add factual trailers:

```text
Agent-Task: LEN-34
Agent-Decision: split delivery workflow into spark-git-delivery because commit and PR actions happen after isolation
Agent-Limitation: no business-repo or idl-repo changes included
```

Do not invent ticket IDs, model names, tests, or decisions.

## Step 5: Push

Before pushing:

```bash
git -C <repo-or-worktree> status --short --branch
git -C <repo-or-worktree> log --oneline --decorate -5
git -C <repo-or-worktree> fetch --prune origin
```

If the user has requested rebase-before-push, or the branch is long-running,
rebase onto the target integration branch before pushing:

```bash
git -C <repo-or-worktree> rebase origin/master
```

Push repo by repo:

```bash
git -C <repo-or-worktree> push -u origin <branch>
```

Never push directly to `main`, `master`, or a protected integration branch.

## Step 6: PR / MR

Open one PR/MR per repo unless the platform supports a reviewed multi-repo
change set.

Description must include:

- ticket ID or requirement ID
- changed repos and branches
- what changed
- key decisions
- tests, lint, Janus gates, and requirement verify commands actually run
- skipped validation and why
- risks or follow-up
- review guidance

Use Janus gate reports and requirement verification as the merge-readiness
source of truth for Harness-governed work. Do not invent a second approval model
inside CI or PR text.

## Step 7: History Cleanup

Before PR/MR or handoff, inspect:

```bash
git -C <repo-or-worktree> log --oneline origin/master..HEAD
```

Clean up `[WIP]` checkpoint commits, vague messages, and temporary exploration
commits. If rewriting a shared branch, present the rewrite plan and wait for
explicit confirmation before force-push.

## Report

Include:

- ticket ID
- repos inspected
- branch per repo
- files staged and committed per repo
- commit hashes
- push target
- PR/MR links, if created
- tests and gates run
- skipped verification or residual risk
- remaining uncommitted changes

## Stop Conditions

Stop before commit, push, PR/MR, or merge when:

- repo boundaries are unclear
- current branch does not include the ticket ID for formal work
- dirty changes contain unrelated user WIP
- staged diff includes local noise or unrelated files
- required tests, gates, or review evidence are missing and the user did not
  explicitly accept the risk
- the target branch is `main`, `master`, or another protected integration branch
- push would require force and the user has not approved the exact rewrite plan
- PR/MR description would claim verification that has not actually run
