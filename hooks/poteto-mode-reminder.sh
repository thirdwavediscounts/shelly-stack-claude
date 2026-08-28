#!/usr/bin/env bash
# Reproduces Cursor's sticky `mode: true` + `reminder:` skill frontmatter.
# /poteto-mode touches ~/.claude/poteto-mode/<project basename>; opting out deletes it.
marker="$HOME/.claude/poteto-mode/$(basename "$PWD")"
[ -f "$marker" ] || exit 0
printf '%s' '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"poteto-mode is active for this project (marker ~/.claude/poteto-mode/). New task? Playbook match or rigor needed -> apply /poteto-mode. Casual turn or user opts out -> don'"'"'t; on opt-out delete the marker."}}'
