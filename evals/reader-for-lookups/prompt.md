---
max_turns: 30
timeout_seconds: 600
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Glob, Grep, Skill, Agent]
tags: [skill-triggers]
---
/shelly-stack:shelly-mode Have a subagent find every place this repo formats a price and report each as file:line. Do not read the files yourself.
