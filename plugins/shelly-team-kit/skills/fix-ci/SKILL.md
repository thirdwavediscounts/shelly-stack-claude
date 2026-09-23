---
name: fix-ci
description: Find the failing checks on the current PR, read their logs or check links,
  and apply one focused fix at a time until the PR is green. Use when a PR's CI is
  red. Pending checks that still need watching belong to loop-on-ci.
---

Read the [runtime contract](../../references/runtime.md) before using this skill.

# Fix CI

## Workflow

1. Resolve the active PR and inspect `gh pr checks --json name,bucket,state,workflow,link`.
2. Inspect failed jobs and extract the first actionable error. Use GitHub Actions logs when available; otherwise use the check link to identify the failing command or service.
3. Apply the smallest safe fix.
4. If commits and pushes are authorized, commit only the fix and push. Re-check the PR at its current head. Otherwise report the verified local fix and remaining CI verification.

## Guardrails

- Fix one actionable failure at a time.
- Prefer minimal, low-risk changes before broader refactors.
- Keep `gh pr checks` as the source of truth for overall PR CI state.

## Output

- Primary failing job and root error
- Fixes applied in iteration order
- Current CI status and next action
