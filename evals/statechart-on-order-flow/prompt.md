---
max_turns: 40
timeout_seconds: 900
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
tags: [skill-triggers]
---
/statechart Draw how an order moves between states in src/order.mjs and show me whether an order can ship before it is paid. There is no network in this sandbox.
