---
name: reflect
description: Spawn three parallel review subagents over the active transcript, surface
  learnings, and route each to a concrete edit on an existing skill. Use when the
  user says reflect.
---

> **Codex runtime:** Follow the [native runtime contract](../shelly-mode/references/codex-runtime.md) for model selection, subagents, planning, review, waits, and Codex paths.

# Reflect

Mine the current conversation for durable learnings, then route them into skill edits.

## When to invoke

Invoke when the user says "reflect" or "$shelly-stack:reflect". Skip when the conversation is trivial, off-topic, or already covered by an existing skill the parent followed correctly. One-offs are not learnings.

## Process

### 1. Locate the active transcript

The parent prepares the current conversation before fanning out. Prefer the current conversation and native `list_threads` and `read_thread` when available. Otherwise write a tight digest, or use an exact session-file path already supplied by the parent or user. Never discover or scan unrelated `~/.codex/sessions/` records.

### 2. Spawn three reviewers in parallel

Load the configured judgment and tooling pairs, then run three contained reviewer workers in total. Dispatch each through the native runtime contract's read-only worker branch. When that branch selects native spawns, call `list_agents`, launch only as many as the available child slots allow, refill a rolling window, and consume each separately delivered terminal result after `wait_agent` reports an update. When it selects bounded CLI workers, collect each command's final output. The parent supplies any required external evidence and applies approved edits.

A configured Codex role is `<model>@<reasoning_effort>`. Pass both values through the native runtime contract's read-only worker branch; for `inherit@inherit`, omit both. If a saved pair is unavailable, use the native runtime contract's fallback for this run and ask the user to rerun `$shelly-stack:setup-shelly-stack`.

| Lens | Role pair | Prompt template |
|---|---|---|
| Judgment | configured reflect judgment pair | `references/judgment-reviewer.md` |
| Tooling | configured reflect tooling pair | `references/tooling-reviewer.md` |
| Divergent | configured reflect judgment pair | `references/divergent-reviewer.md` |

Pass each template verbatim, substituting the transcript path or digest where marked. On the native spawn branch, the initial `spawn_agent` result is only the agent handle and status; wait for completion and consume the separately delivered terminal result. On the CLI branch, consume the command's final output.

### 3. Synthesize

Dispatch one synthesizer with the configured reflect judgment pair and the `references/synthesizer.md` prompt through the native runtime contract's read-only worker branch. Inline the three complete reviewer reports and any parent-collected external evidence where marked, then collect the result through the selected branch. The synthesizer returns a structured Accepted / Rejected / Backlog list.

### 4. Structural enforcement check

Sanity-check the synthesizer's Accepted list. For any item that would be enforced more reliably by a lint rule, script, metadata flag, or runtime check, move it from Accepted to Backlog. See the **encode-lessons-in-structure** principle skill.

### 5. Apply

Before applying any Accepted edit, present the synthesizer's full Accepted/Rejected/Backlog output to the user and wait for explicit approval. The user picks which subset to apply and may redirect routings. Skill changes affect every future agent in the org. Do not auto-apply.

Present Backlog items as proposals. File them in an external tracker only when the user explicitly approves those submissions or already asked this run to file them. Tracker writes and skill edits both wait for the relevant authorization.

For each approved Accepted item, follow the Routing field exactly:

- Trivial existing-skill edit (a one-line bullet, a tightened sentence, a stale fact corrected): parent does directly.
- Substantive existing-skill edit (a new section, a new pattern table, more than ~10 lines): hand to the **create-skill** skill and run its draft / test / iterate loop.
- `tune description: <skill path>` (the skill exists but didn't trigger when it should have): hand to `create-skill` and run its description-optimization loop.
- `new skill via create-skill: <kebab-name>`: hand creation to `create-skill`. Do not invent the shape ad hoc.

If your environment ships a SKILL.md validator, run it on every touched skill before declaring done. Skip this step if it doesn't.

### 6. Summarize for the user

Short list, no preamble:

- Edits applied: `<skill path>`. What changed, one line each.
- New skills created: `<skill path>`. One line each (rare).
- Backlog proposed, or filed with explicit authorization: `<issue title>` (`<tags>`). One line each.
- Dropped: one line per rejected finding + reason from the synthesizer.
