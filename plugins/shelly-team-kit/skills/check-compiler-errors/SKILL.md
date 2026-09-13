---
name: check-compiler-errors
description: Run compile and type-check commands and report failures
---

Read the [runtime contract](../../references/runtime.md) before using this skill.

# Check compiler errors

## Trigger

Compile or type-check failures are blocking local validation or CI.

## Workflow

Run the repository's own compile and type-check commands, not a guessed one, and re-run until clean or blocked.

## Output

- Current compile and type-check status
- Error summary grouped by file and category
- Fixes applied and remaining blockers
