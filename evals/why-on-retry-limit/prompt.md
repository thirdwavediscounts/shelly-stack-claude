---
max_turns: 40
timeout_seconds: 900
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Glob, Grep, Skill, Agent]
tags: [skill-triggers]
---
Why is the retry limit 5 in src/fetch-retry.mjs and not 3?
