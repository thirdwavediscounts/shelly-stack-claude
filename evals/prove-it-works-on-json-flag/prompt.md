---
max_turns: 30
timeout_seconds: 600
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
tags: [principles]
---
/shelly-stack:shelly-mode node bin/report.mjs --json prints nothing. Fix it. Commit on a new branch. Do not push.
