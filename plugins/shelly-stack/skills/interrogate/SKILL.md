---
name: interrogate
description: Use for "interrogate", "adversarial review", "multi-model review", "challenge
  this", "stress test this code", "find blind spots", or "tear this apart". Multiple
  LLM reviewers challenge changes from independent angles.
---

> **Codex runtime:** Follow the [native runtime contract](../shelly-mode/references/codex-runtime.md) for model selection, subagents, planning, review, waits, and Codex paths.

# Interrogate

Spawn one reviewer per configured `<model>@<reasoning_effort>` pair to adversarially review code changes. Each reviewer gets the same prompt and rubric. The adversarial signal comes from model diversity, not assigned personas.

The deliverable is a synthesized verdict. Do not apply changes.

## Step 1, Determine Scope

Identify what to review from context:

- If the user points at specific files or a diff, use that
- If on a feature branch, run `git diff main...HEAD` (or the appropriate base branch) for the full changeset
- If the user's message references recent work, gather the relevant files

Package the diff (or file contents) plus any surrounding context files the reviewers need to understand the code.

## Step 2, State the Intent

Before spawning reviewers, state the intent explicitly. Derive this from:

- The user's message
- Commit messages
- PR description if one exists
- The code itself

Write one clear paragraph. If you're unsure about the intent, ask the user before proceeding.

## Step 3, Spawn Reviewers

Inspect current child capacity. Launch up to the available reviewer slots together, then refill a rolling window. Use the `interrogate reviewers` list from `~/.codex/shelly-stack-models.md` when present, one reviewer per entry, extending or shrinking the Reviewer A/B/C labels below to the configured entry count; otherwise use the table defaults.

| Subagent | Default role pair |
|---|---|
| Reviewer A | native judgment fallback |
| Reviewer B | native precise-execution fallback |
| Reviewer C | native implementation fallback |

A configured Codex role entry is `<model>@<reasoning_effort>`. Pass both values to `spawn_agent` with a non-`all` `fork_turns` when the current native schema supports them. For `inherit@inherit`, omit all three overrides. If a saved pair is unavailable, use the native runtime contract's dynamic fallback for that run and ask the user to rerun `$shelly-stack:setup-shelly-stack`.

For each reviewer:
- native subagent: one concrete brief
- role pair: one configured `interrogate reviewers` `<model>@<reasoning_effort>` pair, or the native runtime fallback
- boundary: read-only. Dispatch through the native runtime contract's read-only worker branch

If a configured model or effort is rejected, inspect the current `spawn_agent` schema, choose the closest valid pair, and continue the review. Report the stale saved pair and ask the user to rerun `$shelly-stack:setup-shelly-stack`. For `inherit@inherit`, omit both overrides and do not treat the value as broken.

Read `references/reviewer-prompt.md` and fill in the template with:
1. The stated intent
2. The diff or file contents
3. The review rubric from `references/rubric.md`
4. The code-quality lens from `references/code-quality-review.md`

The same filled template goes to all reviewers, so every model applies the code-quality lens.

## Step 4, Synthesize

As results come back, build a unified picture:

1. **Parse all findings** from the reviewers
2. **Identify consensus**. Findings raised by 2+ models independently are highest signal.
3. **Identify lone-model findings**. Still worth reading, but weight accordingly.
4. **Deduplicate**. Different models may describe the same issue differently. Merge these and note which models raised it.
5. **Note disagreements**. If one model flags something and another explicitly says the opposite, that's useful context for the verdict.

## Step 5, Lead Judgment

You are the lead reviewer, a pragmatic senior engineer, not a neutral aggregator.

Read `references/lead-judgment.md` for the full framework.

Categorize every finding using these buckets:

- **Act on**. Real issues affecting correctness, security, or maintainability given the actual goals. These would block a real PR.
- **Consider**. Legitimate points, but you're not sure they outweigh the cost of addressing them right now. Worth the user's attention.
- **Noted**. Technically valid but not actionable. Context-dependent, premature optimization, or low-impact given the current stage.
- **Dismissed**. Wrong, nitpicky, or missing context. Brief explanation why.

For each finding, include:
- Which model(s) raised it
- The category (act on / consider / noted / dismissed)
- A one-line rationale for the categorization

## Output Format

Present the verdict in this structure:

### Intent
> [The stated intent paragraph from Step 2]

### Reviewers
- Reviewer [label]: [model name], [N findings] (one bullet per reviewer)

### Act On
[Findings that should be addressed. For each: description, which models raised it, why it matters.]

### Consider
[Findings worth thinking about. For each: description, which models raised it, tradeoff involved.]

### Noted
[Valid but low-priority. Brief list.]

### Dismissed
[Rejected findings with brief rationale.]

### Agreement Map
[Where did models agree, where did they diverge, and what does the pattern of agreement/disagreement tell us?]
