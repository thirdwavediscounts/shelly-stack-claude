---
max_turns: 50
timeout_seconds: 900
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
tags: [skill-triggers]
---
Agents in this repo keep formatting prices with toFixed instead of formatPrice. I've corrected it twice already. Make it so the next agent can't do it.
