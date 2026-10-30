---
max_turns: 30
timeout_seconds: 600
runs: 2
model: claude-opus-5-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
tags: [skill-triggers]
---
Create a skill for this repo that writes release notes from the git log since the last tag. This sandbox blocks writes under .claude/, so put it at skills/release-notes/SKILL.md in the repo instead of .claude/skills/.
