---
name: spark-worktree-isolation
description: Use when Spark workspace work needs Git isolation, branch setup, multi-repo worktrees, or a decision about whether to work in the current checkout before editing files.
---

# Spark Worktree Isolation

Use this before creating branches or editing files when Spark work needs an
isolated Git workspace.

## Rule

`/Users/forest/Code/spark` is a multi-repo workspace, not a Git repository.
Worktree decisions are made per affected subrepo:

- `harness-repo`: requirements, gates, context, templates, Spark skills, agents, commands, and rules.
- `business-repo`: services, frontend apps, libraries, tests, and runtime config.
- `idl-repo`: protobuf contracts and Buf configuration.
- `idl-java-repo`: generated Java contracts only when a task explicitly requires generated-contract changes.
- `learning-docs-repo`: training or learning material.
- `janus`: Janus CLI or gate engine changes.

Prefer platform-native worktree tools. Use `git worktree` only as a fallback.
Never create a nested worktree inside an already isolated subrepo.

## Preconditions

- `spark-workspace-scan` has captured repo branch and dirty state.
- `spark-harness-context-loading` has loaded `context/team/git.md`,
  `context/team/git-workflow.md`, and relevant service-matrix context.
- The current lifecycle stage allows file edits. During intake, only report the
  isolation plan; do not create a branch or worktree.

## Step 1: Resolve Affected Repos

Use the requirement, design, task plan, service matrix, and user request to list
only repos that need changes.

For multi-repo requirements:

- Use the same branch name in every affected repo.
- Include the requirement ID or ticket ID in the branch name.
- Do not create worktrees for cleanly unaffected repos.
- Do not include `idl-java-repo` just because `idl-repo` changes; include it
  only when generated Java contract changes are part of the requested work.

## Step 2: Detect Current State

Run this from `/Users/forest/Code/spark` for every affected repo:

```bash
repo=harness-repo
git -C "$repo" status --short --branch
git -C "$repo" branch --show-current
GIT_DIR=$(git -C "$repo" rev-parse --absolute-git-dir)
GIT_COMMON=$(git -C "$repo" rev-parse --path-format=absolute --git-common-dir)
git -C "$repo" rev-parse --show-superproject-working-tree 2>/dev/null
```

Interpretation:

- `GIT_DIR != GIT_COMMON` and no superproject path: already in a linked worktree.
  Use it; do not create another one.
- `GIT_DIR == GIT_COMMON`: normal checkout. It may need isolation before edits.
- A superproject path means submodule behavior, not Spark worktree isolation.
- Dirty target files block worktree setup until the user decides whether to keep,
  commit, stash, or move those changes.

## Step 3: Prefer Native Isolation

If the host provides a native worktree or thread-worktree tool, use it before
manual Git commands. Native tools own directory placement, lifecycle, cleanup,
and app state.

After native setup, re-run Step 2 for affected repos and report which repos are
isolated. If the native tool isolated only one repo, do not assume the other
Spark repos moved with it.

## Step 4: Git Worktree Fallback

Use this only when no native tool is available.

Default to a workspace-level directory so worktree contents cannot be committed
inside any Spark subrepo:

```bash
WORKSPACE=/Users/forest/Code/spark
BRANCH=feature/workstream/TICKET-123
SLUG=$(printf '%s' "$BRANCH" | sed 's#[^A-Za-z0-9._-]#-#g')
BASE="$WORKSPACE/.worktrees/$SLUG"
mkdir -p "$BASE"
```

For each affected repo, create or attach the matching branch:

```bash
repo=harness-repo
target="$BASE/$repo"

if git -C "$repo" show-ref --verify --quiet "refs/heads/$BRANCH"; then
  git -C "$repo" worktree add "$target" "$BRANCH"
elif git -C "$repo" ls-remote --exit-code --heads origin "$BRANCH" >/dev/null 2>&1; then
  git -C "$repo" fetch origin "$BRANCH"
  git -C "$repo" worktree add "$target" -b "$BRANCH" "origin/$BRANCH"
else
  git -C "$repo" worktree add "$target" -b "$BRANCH"
fi
```

Only use repo-local `.worktrees/` or `worktrees/` when the user or repo rules
explicitly require it. Before creating repo-local worktrees, verify the chosen
directory is ignored in that repo:

```bash
git -C "$repo" check-ignore -q .worktrees
```

If it is not ignored, stop and ask before editing `.gitignore` or committing a
repository-maintenance change.

## Step 5: Baseline And Handoff

After isolation exists:

- Run `git -C <worktree-path> status --short --branch` for every affected repo.
- Run the narrow baseline command required by the next Spark skill. Examples:
  `janus version` for Harness workflow work, `buf lint` for IDL work, or the
  service-specific test command from project context for business code.
- Record the new repo paths in the next plan, implementation note, or final
  response.
- Do not copy uncommitted changes into the worktree without explicit user
  approval.

## Report

Include:

- affected repos
- branch name
- whether each repo is normal checkout, native worktree, existing linked
  worktree, or git fallback worktree
- worktree paths
- dirty-state blockers
- baseline commands run
- next Spark workflow skill

## Stop Conditions

Stop before creating or using a worktree when:

- affected repos are unclear
- requirement ID or branch name is missing for requirement work
- current dirty changes overlap target files
- the lifecycle stage does not allow edits
- a native worktree tool is available but cannot cover the needed repo set
- branch names would diverge across affected repos
- the fallback path already exists and is not clearly the same requested branch
