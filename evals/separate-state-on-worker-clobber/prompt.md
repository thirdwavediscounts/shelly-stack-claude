---
max_turns: 40
timeout_seconds: 600
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
tags: [principles]
---
/shelly-stack:shelly-mode The indexer and metrics workers run at the same time and keep wiping each other's fields in state.json. Run node run-both.mjs to see it. Fix it. Commit on a new branch. Do not push.
