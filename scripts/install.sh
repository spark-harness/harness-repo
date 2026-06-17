#!/usr/bin/env bash
set -euo pipefail

# Install Spark Harness assets and hooks into the workspace's per-host dirs
# (.claude / .codex / .gemini). Pass --check to verify the installed copies
# match the source without writing anything (exit 1 on drift); used by CI.

HARNESS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE_ROOT="$(cd "$HARNESS_ROOT/.." && pwd)"

CHECK=0
if [ "${1:-}" = "--check" ]; then
  CHECK=1
fi
DRIFT=0

require_jq() {
  if ! command -v jq >/dev/null 2>&1; then
    echo "error: jq is required to install or check hooks" >&2
    exit 2
  fi
}

# --- asset trees: skills / agents / commands / rules ---

sync_dir() {
  local src="$HARNESS_ROOT/.spark/$1/"
  local dst="$2/"
  if [ "$CHECK" -eq 1 ]; then
    if [ ! -d "$dst" ]; then
      echo "drift: missing $dst"
      DRIFT=1
      return
    fi
    local out
    out="$(rsync -ric --delete --dry-run "$src" "$dst" 2>/dev/null | grep -E '^(>|c|\*deleting)' || true)"
    if [ -n "$out" ]; then
      echo "drift: $dst"
      printf '%s\n' "$out" | sed 's/^/  /'
      DRIFT=1
    fi
  else
    mkdir -p "$dst"
    rsync -a --delete "$src" "$dst"
  fi
}

copy_assets() {
  local base="$1"
  local sub
  for sub in skills agents commands rules; do
    sync_dir "$sub" "$base/$sub"
  done
}

# --- hooks (per-host) ---
#
# The deny signal (exit code 2 + stderr) is identical across Claude, Codex and
# Gemini, so only the registration format and tool matcher differ per host.

GUARD_PRE_CLAUDE='[{"matcher":"Write|Edit|MultiEdit","hooks":[{"type":"command","command":"janus hook guard-edit","statusMessage":"Checking lifecycle edit guard"}]}]'
GUARD_PRE_CODEX='[{"matcher":"Write|Edit|MultiEdit|apply_patch","hooks":[{"type":"command","command":"janus hook guard-edit","statusMessage":"Checking lifecycle edit guard"}]}]'
GUARD_BEFORE_GEMINI='[{"matcher":"write_file|replace","hooks":[{"type":"command","command":"janus hook guard-edit","statusMessage":"Checking lifecycle edit guard"}]}]'
DRIFT_STOP='[{"hooks":[{"type":"command","command":"janus hook gate-drift-check","statusMessage":"Checking Janus gate reports"}]}]'

write_or_check() {
  local file="$1"
  local desired="$2"
  if [ "$CHECK" -eq 1 ]; then
    local current='{}'
    [ -f "$file" ] && current="$(cat "$file")"
    if ! diff <(printf '%s' "$current" | jq -S .) <(printf '%s' "$desired" | jq -S .) >/dev/null 2>&1; then
      echo "drift: $file"
      DRIFT=1
    fi
  else
    mkdir -p "$(dirname "$file")"
    printf '%s\n' "$desired" >"$file"
  fi
}

install_claude_hooks() {
  local file="$WORKSPACE_ROOT/.claude/settings.json"
  local base='{}'
  [ -f "$file" ] && base="$(cat "$file")"
  local desired
  desired="$(printf '%s' "$base" | jq --argjson pre "$GUARD_PRE_CLAUDE" --argjson stop "$DRIFT_STOP" '.hooks.PreToolUse=$pre | .hooks.Stop=$stop')"
  write_or_check "$file" "$desired"
}

install_codex_hooks() {
  # Codex reads a standalone hooks.json next to the project .codex layer.
  local file="$WORKSPACE_ROOT/.codex/hooks.json"
  local desired
  desired="$(jq -n --argjson pre "$GUARD_PRE_CODEX" --argjson stop "$DRIFT_STOP" '{hooks:{PreToolUse:$pre,Stop:$stop}}')"
  write_or_check "$file" "$desired"
}

install_gemini_hooks() {
  # Gemini's pre-tool event is BeforeTool. The Stop/drift hook is not wired for
  # Gemini pending confirmation of its session-end event name.
  local file="$WORKSPACE_ROOT/.gemini/settings.json"
  local base='{}'
  [ -f "$file" ] && base="$(cat "$file")"
  local desired
  desired="$(printf '%s' "$base" | jq --argjson before "$GUARD_BEFORE_GEMINI" '.hooks.BeforeTool=$before')"
  write_or_check "$file" "$desired"
}

require_jq

copy_assets "$WORKSPACE_ROOT/.claude"
copy_assets "$WORKSPACE_ROOT/.gemini"
copy_assets "$WORKSPACE_ROOT/.codex"

install_claude_hooks
install_codex_hooks
install_gemini_hooks

if [ "$CHECK" -eq 1 ]; then
  if [ "$DRIFT" -ne 0 ]; then
    echo "install --check: drift detected" >&2
    exit 1
  fi
  echo "install --check: in sync"
else
  echo "installed Spark Harness assets and hooks"
fi
