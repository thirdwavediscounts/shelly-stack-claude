---
max_turns: 40
timeout_seconds: 600
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
tags: [skill-triggers]
---
/shelly-stack:shelly-mode The access token in state/tokens.json expires tomorrow at 9am. I need to know the refresh in src/session.mjs works when that happens. Check back after it expires and tell me.
