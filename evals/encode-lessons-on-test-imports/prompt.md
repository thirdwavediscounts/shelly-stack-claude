---
max_turns: 40
timeout_seconds: 600
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
tags: [principles]
---
/shelly-stack:shelly-mode Code in src/ must never import from test/. Every agent keeps doing it. Fix the one that does and make sure it can't happen again. Commit on a new branch. Do not push.
