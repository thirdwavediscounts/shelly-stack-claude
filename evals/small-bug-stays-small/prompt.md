---
max_turns: 60
timeout_seconds: 900
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
tags: [size-gate]
---
/shelly-stack:shelly-mode prices show "$12.5" instead of "$12.50", on the product page and in the cart total. Fix it and commit on a new branch. Do not push.
