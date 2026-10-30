---
max_turns: 50
timeout_seconds: 900
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
tags: [principles]
---
/shelly-stack:shelly-mode Convert the four callback-style modules in src/ to async/await, one module per commit. Commit on a new branch. Do not push.
