---
name: weekly-review
description: Summarize the current git user's commits from the last seven days into a short themed recap classified as bug fixes, tech debt, and net-new work. Use for a weekly status update, retro, or planning recap.
disable-model-invocation: true
---

Read the [runtime contract](../../references/runtime.md) before using this skill.

# Weekly review

## Workflow

1. Determine the current git user email from repo config.
2. Resolve the last seven days into exact dates in the user timezone, unless another range was requested. Collect authored commits reachable from the repository default branch.
3. Exclude merge commits.
4. Group meaningful changes into a few bullets, one theme each.
5. Add a short classification paragraph covering:
   - likely bug fixes
   - likely tech debt work
   - likely net-new functionality

## Guardrails

- Keep the recap short and executive-readable.
- Base claims only on commit history and diffs.
- If git email is missing, use an author identity already provided by the user or ask for it. Do not change git configuration to produce a report.

## Output

- Bullet weekly summary, one theme each
- Brief classification paragraph (bugfix / tech debt / net-new)
