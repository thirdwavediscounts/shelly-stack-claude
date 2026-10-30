---
max_turns: 50
timeout_seconds: 900
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
tags: [skill-triggers]
---
Two sync workers can both end up holding the lease in src/lease.mjs. Model-check this race and leave a skill so the next agent can rerun the check. There is no network in this sandbox.
