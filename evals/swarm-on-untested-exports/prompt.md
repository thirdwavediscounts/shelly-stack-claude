---
max_turns: 40
timeout_seconds: 900
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
tags: [skill-triggers]
---
Swarm this: one worker per module in src/, each lists the exported functions that no test calls. Give me one report.
