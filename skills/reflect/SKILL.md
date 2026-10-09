---
name: reflect
description: Spawn three parallel review subagents over the active transcript, surface learnings, and route each to a concrete edit on an existing skill. Use when the user says reflect.
disable-model-invocation: true
---

# Reflect

Mine the current conversation for durable learnings, then route them into skill edits.

## When to invoke

Invoke when the user says "reflect" or "/reflect". Skip when the conversation is trivial, off-topic, or already covered by an existing skill the parent followed correctly. One-offs are not learnings.

## Process

### 1. Locate the active transcript

The parent finds its own transcript file before fanning out. Run `scripts/find-transcript.sh "$PWD" "<opening words of this conversation's first user prompt>"`. It derives the workspace's transcript directory (`~/.claude/projects/<slug>/`, never another project's, since those hold private chats) and prints the newest transcript whose first user message contains that prompt. It checks session transcripts before subagent transcripts. If it prints nothing, write a tight digest of the session and pass that instead.

### 2. Spawn three reviewers in parallel

One message, three `Agent` calls, `subagent_type: general-purpose`, explicit `model:` on each (or `subagent_type` when the configured value is an agent name; see below). Reviewers use MCP tools for context lookups (tickets, chat threads, observability traces referenced in the transcript). The prompt forbids file writes; the parent applies edits.

A configured role value is either an Agent `model` alias (`fable`, `opus`, `sonnet`, `haiku`) or a pinned agent name. The plugin ships pinned agents named `shelly-stack:shelly-<model>-<effort>`, for example `shelly-stack:shelly-opus-high`. Each is shelly-agent's body with a pinned model and effort. A user agent of the same shape under `~/.claude/agents/` also works. Use its bare name. An alias goes in `model`. An agent name goes in `subagent_type` with `model` omitted; it already carries the shelly-agent body, so it replaces `shelly-stack:shelly-agent` and `general-purpose` for that spawn.

| Lens | Value | Prompt template |
|---|---|---|
| Judgment | your configured reflect-judgment model (default `fable`) | `references/judgment-reviewer.md` |
| Tooling | your configured reflect-tooling model (default `opus`) | `references/tooling-reviewer.md` |
| Divergent | your configured reflect-judgment model (default `fable`) | `references/divergent-reviewer.md` |

Pass each template verbatim, substituting the transcript path or digest where marked. Reviewers return findings in the `Agent` response body.

### 3. Synthesize

One `Agent` call, `subagent_type: general-purpose`, using your configured reflect-judgment model (default `fable`). The synthesizer's quality check spot-verifies citations through MCP tools. Use `references/synthesizer.md` verbatim, with each reviewer's full output inlined where marked. The synthesizer returns a structured Accepted / Rejected / Backlog list.

### 4. Structural enforcement check

Sanity-check the synthesizer's Accepted list. For any item that would be enforced more reliably by a lint rule, script, metadata flag, or runtime check, move it from Accepted to Backlog. See the **encode-lessons-in-structure** principle (Read `../principle-encode-lessons-in-structure/SKILL.md`).

### 5. Apply

Before applying any Accepted edit, present the synthesizer's full Accepted/Rejected/Backlog output to the user and wait for explicit approval. The user picks which subset to apply and may redirect routings. Skill changes affect every future agent in the org. Do not auto-apply.

Backlog items file to whatever devex / backlog tracker your team uses automatically. Only the Accepted list waits for approval.

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
- Backlog filed to the devex tracker: `<issue title>` (`<tags>`). One line each.
- Dropped: one line per rejected finding + reason from the synthesizer.
