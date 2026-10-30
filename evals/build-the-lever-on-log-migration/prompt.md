---
max_turns: 40
timeout_seconds: 600
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
tags: [principles]
---
/shelly-stack:shelly-mode Replace every oldLog(msg) call in src/ with log.info(msg), fix the imports, then delete oldLog. Commit on a new branch. Do not push.
