---
max_turns: 20
timeout_seconds: 240
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Glob, Grep, Skill]
tags: [turn-state]
---
/shelly-stack:shelly-mode start ./backfill.sh in the background. It takes about 20 minutes. Once it is going, tell me where things stand.
