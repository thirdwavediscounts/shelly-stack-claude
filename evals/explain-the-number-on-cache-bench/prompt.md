---
max_turns: 40
timeout_seconds: 600
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
tags: [principles]
---
/shelly-stack:shelly-mode I added a cache to parse() in src/parse.mjs and node bench.mjs says it's way faster. Is that number good enough to put in the PR? Commit on a new branch. Do not push.
