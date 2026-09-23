---
name: new-branch-and-pr
description: Start new work on a fresh branch cut from the default branch, implement
  it, and open a pull request. Use when the work has no branch yet. A branch that
  already carries changes goes through review-and-ship.
---

Read the [runtime contract](../../references/runtime.md) before using this skill.

# New branch and PR

## Workflow

1. Ensure the working tree is clean or explicitly handled.
2. Resolve the repository default branch, fetch it, and create a branch using the repository naming rules. Preserve unrelated working changes in their original checkout.
3. Complete implementation and tests.
4. Run the repository's lint, format, and type gates, the same commands CI runs, then commit focused changes and push.
5. Create a concise PR with summary and test notes.

## Guardrails

- Keep branch scope focused on one change set.
- Include verification notes before requesting review.

## Output

- New branch name
- PR summary and test notes
- PR URL
