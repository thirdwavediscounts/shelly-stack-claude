#!/bin/sh
# usage: find-transcript.sh <workspace-path> <opening-prompt-substring>
set -eu
slug=$(printf '%s' "$1" | sed 's/[^A-Za-z0-9-]/-/g')
dir="$HOME/.claude/projects/$slug"
[ -d "$dir" ] || { printf 'no transcript directory: %s\n' "$dir" >&2; exit 1; }
newest_sessions() { ls -t "$dir"/*.jsonl 2>/dev/null | head -10; }
newest_subagents() { ls -t "$dir"/*/subagents/*.jsonl 2>/dev/null | head -10; }
match=$({ newest_sessions; newest_subagents; } | while IFS= read -r f; do
  grep -m1 '"type":"user"' "$f" | grep -qF -- "$2" && { printf '%s\n' "$f"; break; }
done)
[ -n "$match" ] || { printf 'no transcript in %s matched the opening prompt\n' "$dir" >&2; exit 1; }
printf '%s\n' "$match"
