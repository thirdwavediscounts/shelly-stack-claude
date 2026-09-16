---
name: loop-on-ci
description: Monitor PR checks and fix failures until green. Uses gh pr checks as the source of truth for PR-attached checks.
---

Read the [runtime contract](../../references/runtime.md) before using this skill.

# Loop on CI

## Trigger

Need to watch a branch or pull request and iterate on CI failures until all required checks are green.

Use `gh pr checks` as the source of truth. It includes all PR-attached checks, while `gh run list` only covers GitHub Actions.

## Workflow

1. Resolve the PR for the current branch.
2. Inspect current PR checks before waiting.
3. If checks already failed, diagnose those failures first.
4. If checks are pending, follow the runtime contract for bounded current-turn polling. A future recurring monitor requires an explicit request.
5. After each push, re-check the full PR check set and repeat until green.

## Commands

```bash
# Resolve the active PR
gh pr view --json number,url,headRefName

# Inspect all attached checks
gh pr checks --json name,bucket,state,workflow,link

# Re-read pending checks within the current turn
gh pr checks --json name,bucket,state,workflow,link

# GitHub Actions logs, when the failing check links to a GHA run
gh run view <run-id> --log-failed
```

## Guardrails

- Keep each fix scoped to a single failure cause when possible.
- Do not bypass hooks (`--no-verify`) to force progress.
- If the failure is outside the diff, check whether the base is stale. Reconcile with the current base only within the authorized history operations.
- If failures are flaky, retry once and report flake evidence.
- Re-run `gh pr checks --json name,bucket,state,workflow,link` after every push; the check set can change.

## Output

- Current CI status
- Failure summary and fixes applied
- PR URL once checks are green
