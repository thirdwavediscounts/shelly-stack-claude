---
name: what-did-i-get-done
description: Summarize authored commits over a user-specified time period into a concise
  update
---

Read the [runtime contract](../../references/runtime.md) before using this skill.

# What did I get done

## Trigger

Need a short, high-signal summary of work completed in a specific time range (for example: yesterday, last 3 days, or last week).

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
