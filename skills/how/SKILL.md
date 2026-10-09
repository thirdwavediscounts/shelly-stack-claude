---
name: how
description: "Use for \"how does X work\", code walkthroughs before changing something, and placement / ownership / layering questions (\"where should this live\", \"which package owns this\", \"is this the right layer\"). Explains subsystem architecture, runtime flow, onboarding mental models. Use why for motivation."
---

# How

Explore the codebase to answer "how does X work?" questions. Produce architectural explanations at the level of a senior engineer onboarding onto a subsystem, enough to build a working mental model, not so much that it reads like annotated source code.

A configured role value is either an Agent `model` alias (`fable`, `opus`, `sonnet`, `haiku`) or a pinned agent name. The plugin ships pinned agents named `shelly-stack:shelly-<model>-<effort>`, for example `shelly-stack:shelly-opus-high`. Each is shelly-agent's body with a pinned model and effort. A user agent of the same shape under `~/.claude/agents/` also works. Use its bare name. An alias goes in `model`. An agent name goes in `subagent_type` with `model` omitted; it already carries the shelly-agent body, so it replaces `shelly-stack:shelly-agent` and `general-purpose` for that spawn.

## Step 1. Assess Complexity

If the scope is ambiguous, state your interpretation and explore. The user can redirect.

- **Simple** (a single module, a small utility, a narrow question such as "how does function X work"): no explorers. One explainer explores and explains in a single pass. Go to Step 2b.
- **Complex** (a subsystem spanning multiple files or services, a cross-cutting feature, a full architectural overview): spawn parallel explorers first, then hand off to the explainer. Go to Step 2a.

When in doubt, take the simple path.

## Step 2a. Explore (complex questions only)

Decompose the question into 2 to 4 exploration angles, each a distinct slice of the subsystem. Spawn all explorers in a single message:

- `subagent_type`: `general-purpose`
- `model`: your configured how-explorer model (default `sonnet`)
- Read-only posture stated in the prompt.

Each explorer gets the prompt in `references/explorer-prompt.md` with its angle filled in. Then go to Step 3.

## Step 2b. Direct Explain (simple questions)

Spawn one Agent subagent that explores and explains in one pass:

- `subagent_type`: `general-purpose`
- `model`: your configured how-explainer model (default `fable`)
- Read-only posture stated in the prompt.

Build its prompt from `references/explainer-prompt.md` without the explorer-findings section. Go to Step 4.

## Step 3. Synthesize (complex questions only)

Once all explorers have returned, spawn one Agent subagent to synthesize their findings into one explanation:

- `subagent_type`: `general-purpose`
- `model`: your configured how-explainer model (default `fable`)
- Read-only posture stated in the prompt.

Build its prompt from `references/explainer-prompt.md` with every explorer's findings filled in.

## Step 4. Present

Present the explainer's output to the user. Light edits for clarity or context from the conversation are fine. Do not substantially rewrite it.

## Output Format

The explanation uses the sections defined in `references/explainer-prompt.md`, dropping any that do not apply: Overview, Key Concepts, How It Works, Where Things Live, Gotchas.
