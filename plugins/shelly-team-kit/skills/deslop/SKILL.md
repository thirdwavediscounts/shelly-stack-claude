---
name: deslop
description: Remove AI-generated code slop and clean up code style
---

Read the [runtime contract](../../references/runtime.md) before using this skill.

# Remove AI code slop

Resolve the PR base or repository default branch and inspect the branch diff plus scoped uncommitted changes. Remove only slop introduced by the requested work. Preserve pre-existing edits from other tasks.

## Focus Areas

- Extra comments that are unnecessary or inconsistent with local style
- Defensive checks or try/catch blocks that are abnormal for trusted code paths
- Casts to `any` used only to bypass type issues
- Deeply nested code that should be simplified with early returns
- Other patterns inconsistent with the file and surrounding codebase

## Guardrails

- Keep behavior unchanged. Report newly discovered bugs separately unless their fix is already in scope.
- Prefer minimal, focused edits over broad rewrites.
- End with a short summary of what was removed.
