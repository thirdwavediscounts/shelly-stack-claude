#!/usr/bin/env bash
# Reproduces Cursor's sticky `mode: true` + `reminder:` skill frontmatter.
# /shelly-mode touches ~/.claude/shelly-mode/<project basename>; opting out deletes it.
marker="$HOME/.claude/shelly-mode/$(basename "$PWD")"
[ -f "$marker" ] || exit 0
printf '%s' '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"shelly-mode is active for this project (marker ~/.claude/shelly-mode/). New task? Playbook match or rigor needed -> apply /shelly-mode. Casual turn or user opts out -> don'"'"'t; on opt-out delete the marker."}}'
