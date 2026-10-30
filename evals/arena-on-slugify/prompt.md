---
max_turns: 40
timeout_seconds: 900
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
tags: [skill-triggers]
---
Arena this: write slugify(title) in src/slug.mjs. It turns a product title into a URL slug: lowercase ASCII, words joined by single dashes, no leading or trailing dash, at most 60 characters without cutting a word. Add tests.
