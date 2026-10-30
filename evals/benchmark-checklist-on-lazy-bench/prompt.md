---
max_turns: 30
timeout_seconds: 600
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
tags: [skill-triggers]
---
I rewrote the sum as fastSum in src/sum.mjs. Run node bench.mjs and tell me how much faster it is. Vet the number before you tell me.
