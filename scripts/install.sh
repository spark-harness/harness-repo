#!/usr/bin/env bash
set -euo pipefail

HARNESS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE_ROOT="$(cd "$HARNESS_ROOT/.." && pwd)"

copy_dir() {
  local root="$1"
  local target="$2"

  mkdir -p "$root/$target"
  rsync -a --delete "$HARNESS_ROOT/.spark/skills/" "$root/$target/skills/"
  rsync -a --delete "$HARNESS_ROOT/.spark/agents/" "$root/$target/agents/"
  rsync -a --delete "$HARNESS_ROOT/.spark/commands/" "$root/$target/commands/"
  rsync -a --delete "$HARNESS_ROOT/.spark/rules/" "$root/$target/rules/"
}

copy_dir "$WORKSPACE_ROOT" ".claude"
copy_dir "$WORKSPACE_ROOT" ".gemini"
copy_dir "$WORKSPACE_ROOT" ".codex"

echo "installed Spark Harness assets"
