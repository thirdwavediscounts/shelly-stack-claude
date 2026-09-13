# How

Explore the codebase to answer "how does X work?" questions. Produce architectural explanations at the level of a senior engineer onboarding onto a subsystem, enough to build a working mental model, not so much that it reads like annotated source code.

A configured Codex role entry is `<model>@<reasoning_effort>`. Pass both values to `spawn_agent` with a non-`all` `fork_turns` when the current native schema supports them. For `inherit@inherit`, omit all three overrides. If a saved pair is unavailable, use the native runtime contract's dynamic fallback for that run and ask the user to rerun `$shelly-stack:setup-shelly-stack`.

## Step 1. Assess Complexity

If the scope is ambiguous, state your interpretation and explore. The user can redirect.

- **Simple** (a single module, a small utility, a narrow question such as "how does function X work"): no explorers. One explainer explores and explains in a single pass. Go to Step 2b.
- **Complex** (a subsystem spanning multiple files or services, a cross-cutting feature, a full architectural overview): spawn parallel explorers first, then hand off to the explainer. Go to Step 2a.

When in doubt, take the simple path.

## Step 2a. Explore (complex questions only)

Decompose the question into 2 to 4 exploration angles, each a distinct slice of the subsystem. Inspect current child capacity. Spawn up to the available slots together, then refill a rolling window:

- native subagent: one concrete brief
- role pair: the configured how-explorer `<model>@<reasoning_effort>` pair, or the native runtime fallback
- boundary: read-only. Dispatch through the native runtime contract's read-only worker branch

Each explorer gets the prompt in `references/explorer-prompt.md` with its angle filled in. Then go to Step 3.

## Step 2b. Direct Explain (simple questions)

Spawn one native subagent that explores and explains in one pass:

- native subagent: one concrete brief
- role pair: the configured how-explainer `<model>@<reasoning_effort>` pair, or the native runtime fallback
- boundary: read-only. Dispatch through the native runtime contract's read-only worker branch

Build its prompt from `references/explainer-prompt.md` without the explorer-findings section. Go to Step 4.

## Step 3. Synthesize (complex questions only)

Once all explorers have returned, spawn one native subagent to synthesize their findings into one explanation:

- native subagent: one concrete brief
- role pair: the configured how-explainer `<model>@<reasoning_effort>` pair, or the native runtime fallback
- boundary: read-only. Dispatch through the native runtime contract's read-only worker branch

Build its prompt from `references/explainer-prompt.md` with every explorer's findings filled in.

## Step 4. Present

Present the explainer's output to the user. Light edits for clarity or context from the conversation are fine. Do not substantially rewrite it.

## Output Format

The explanation uses the sections defined in `references/explainer-prompt.md`, dropping any that do not apply: Overview, Key Concepts, How It Works, Where Things Live, Gotchas.
