---
max_turns: 150
timeout_seconds: 1800
runs: 3
model: claude-opus-5-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, TodoWrite]
tags: [pr-cleanup]
---
/shelly-stack:shelly-mode Add a `--only <pattern>` option to tools/staging/disable-cron-jobs.mjs so I can turn off just the jobs whose name contains the pattern, for example `--only sync-`. Without the option it behaves as today, and `--list` honors it too. Add tests. Then ship it: commit on a new branch, push, and open the PR with `gh pr create`. This sandbox has no GitHub login, so `gh pr create` will fail. Run it anyway, then stop and report.
