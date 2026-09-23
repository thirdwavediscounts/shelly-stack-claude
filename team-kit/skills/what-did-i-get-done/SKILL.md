---
name: what-did-i-get-done
description: Summarize the current git user's commits over a stated time window (yesterday, the last three days, last week) into a short status update. Use when asked what was done, finished, or shipped in a period.
---

Read the [runtime contract](../../references/runtime.md) before using this skill.

# What did I get done

## Workflow

1. Resolve the requested time window into concrete dates.
2. Read commits authored by the current git user email within that range.
3. Exclude merge commits and uncommitted changes.
4. Summarize completed changes. Call work shipped only when merge or deployment evidence supports it.
5. Include the actual date range used in the final summary.

## Guardrails

- Write for a status update a manager skims: every sentence carries a shipped change.
- Prioritize substantial behavior or architecture changes.
- Omit cosmetic-only changes (formatting, imports, minor renames).
- Do not infer intent or motivation. Describe changes functionally.

## Output

- One short summary suitable for a status update
- Real date range
- Optional bullets for major changes only
