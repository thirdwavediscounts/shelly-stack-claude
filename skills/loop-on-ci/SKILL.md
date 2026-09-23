---
name: loop-on-ci
description: Watch the current PR's checks and fix failures until every required check is green. Use when asked to monitor, babysit, or loop on CI for a branch or pull request, including pending checks that have not finished.
disable-model-invocation: true
---

Read the [runtime contract](../../references/runtime.md) before using this skill.

# Loop on CI

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

# GitHub Actions logs, when the failing check links to a GHA run
gh run view <run-id> --log-failed
```

## Guardrails

- Keep each fix scoped to a single failure cause when possible.
- Do not bypass hooks (`--no-verify`) to force progress.
- If the failure is outside the diff, check whether the base is stale. Reconcile with the current base only within the authorized history operations.
- If failures are flaky, retry once and report flake evidence.

## Output

- Current CI status
- Failure summary and fixes applied
- PR URL once checks are green
