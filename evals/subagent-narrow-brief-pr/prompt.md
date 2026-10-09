---
max_turns: 40
timeout_seconds: 1800
runs: 3
model: claude-opus-5-5
allowed_tools: [Bash, Read, Glob, Grep, Skill, Agent]
tags: [subagent-skill-calls]
---
Do not edit any files or run git yourself. Spawn one `shelly-stack:shelly-opus-medium` agent with exactly this brief, then relay its report:

"Your steps: 1. Add a `--only <pattern>` option to tools/staging/disable-cron-jobs.mjs that limits disabling and `--list` to jobs whose name contains the pattern. 2. Add a test and run `npm test`. 3. Commit on a new branch, push, and open the PR with `gh pr create`. This sandbox has no GitHub login, so `gh pr create` will fail. Run it anyway, then report."
