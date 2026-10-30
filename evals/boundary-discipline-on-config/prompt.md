---
max_turns: 40
timeout_seconds: 600
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
tags: [principles]
---
/shelly-stack:shelly-mode Add a maxRetries setting to config.json (default 3) and make importOrders retry a failed batch up to that many times. Commit on a new branch. Do not push.
