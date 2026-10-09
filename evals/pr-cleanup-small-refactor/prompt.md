---
max_turns: 150
timeout_seconds: 1800
runs: 3
model: claude-opus-5-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
tags: [pr-cleanup]
---
/shelly-stack:shelly-mode The staging guard in tools/staging/disable-cron-jobs.mjs decides whether a database URL points at staging or production with projectRef(). Nothing tests it, and it is the only thing stopping the script from touching production. Move it into its own module and add tests that would catch a real bug in it. Then ship it: commit on a new branch, push, and open the PR with `gh pr create`. This sandbox has no GitHub login, so `gh pr create` will fail. Run it anyway, then stop and report.
