---
name: review-and-ship
description: Review the current branch for bugs, intent fit, and test coverage; run
  or write tests; commit focused work; open or update a PR.
---

Read the [runtime contract](../../references/runtime.md) before using this skill.

# Review and ship

## Trigger

Reviewing changes before shipping. Close key issues, verify behavior, and open or update a PR.

## Workflow

1. Gather context: diff against base branch, uncommitted changes, recent commits, changed files, and user intent from recent relevant chats if useful.
2. Run the repository's lint, format, and type gates, the same commands CI runs, before any review. Read the CI workflow or the root scripts to find them (for example `pnpm ratchet:check`, `pnpm format:check`, `pnpm typecheck`). Fix every red first. A reviewer reading a diff that CI will reject wastes the review.
3. Run targeted tests for changed behavior. If no focused tests exist, decide whether to add them or document the gap.
4. Review for correctness, regressions, security, and intent fit. Use an independent reviewer only when the active delegation rules allow it, following the runtime contract.
5. Fix critical issues before finalizing and re-run affected tests and gates.
6. Commit selective files with a concise message.
7. Push branch and open or update a PR.

## Suggested Checks

```bash
git fetch origin <base-branch>
git diff origin/<base-branch>...HEAD
git status
gh pr checks --json name,bucket,state,workflow,link
```

## Guardrails

- Prioritize correctness, security, and regressions over style-only comments.
- Keep commits focused and avoid unrelated file changes.
- If pre-commit checks fail, fix the issues rather than bypassing hooks.
- Use `gh pr checks` instead of GitHub Actions-only commands when judging PR readiness.

## Output

- Gate commands run and their results
- Findings summary (critical, warning, note)
- Tests run and outcomes
- PR URL
