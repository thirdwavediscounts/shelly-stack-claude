---
max_turns: 60
timeout_seconds: 900
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
tags: [skill-triggers]
---
/shelly-stack:shelly-mode Nothing reads legacy_note on orders anymore, so get rid of it with a new migration. Commit on a new branch. Do not push.
