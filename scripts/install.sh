#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

copy_dir() {
  local target="$1"
  mkdir -p "$ROOT/$target"
  rsync -a --delete "$ROOT/.spark/skills/" "$ROOT/$target/skills/"
  rsync -a --delete "$ROOT/.spark/agents/" "$ROOT/$target/agents/"
  rsync -a --delete "$ROOT/.spark/commands/" "$ROOT/$target/commands/"
  rsync -a --delete "$ROOT/.spark/rules/" "$ROOT/$target/rules/"
}

copy_skills_dir() {
  local target="$1"
  mkdir -p "$ROOT/$target/skills"
  rsync -a --delete "$ROOT/.spark/skills/" "$ROOT/$target/skills/"
}

copy_dir ".codex"
copy_dir ".claude"
copy_dir ".gemini"
copy_skills_dir ".agent"

echo "installed Spark Harness assets"
