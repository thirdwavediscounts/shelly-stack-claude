#!/bin/sh
# Print the newest transcript in this workspace whose first line contains the opening user prompt.
# usage: find-transcript.sh <workspace-path> <opening-prompt-substring>
set -eu
slug=$(printf '%s' "$1" | tr '/' '-')
dir="$HOME/.claude/projects/$slug"
[ -d "$dir" ] || { printf 'no transcript directory: %s\n' "$dir" >&2; exit 1; }
match=$(ls -t "$dir"/*.jsonl "$dir"/*/subagents/*.jsonl 2>/dev/null | head -10 | while IFS= read -r f; do
  head -1 "$f" | grep -qF -- "$2" && { printf '%s\n' "$f"; break; }
done)
[ -n "$match" ] || { printf 'no transcript in %s matched the opening prompt\n' "$dir" >&2; exit 1; }
printf '%s\n' "$match"
