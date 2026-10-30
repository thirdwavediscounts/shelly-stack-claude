---
max_turns: 40
timeout_seconds: 900
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
tags: [skill-triggers]
---
Architect this: add per-client rate limiting to src/api.mjs, so each clientId gets at most 10 requests per rolling minute, then a 429. Stop and show me the design before implementing.
