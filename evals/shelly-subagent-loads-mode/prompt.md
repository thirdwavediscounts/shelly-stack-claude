---
max_turns: 20
timeout_seconds: 600
runs: 3
model: claude-opus-5-5
allowed_tools: [Bash, Read, Glob, Grep, Skill, Agent]
tags: [shelly-agents]
---
Spawn one `shelly-stack:shelly-sonnet-low` agent and have it answer this: which cron jobs in jobs.json are active, and what does tools/staging/disable-cron-jobs.mjs do with them? Do not read any files yourself. Relay its answer.
