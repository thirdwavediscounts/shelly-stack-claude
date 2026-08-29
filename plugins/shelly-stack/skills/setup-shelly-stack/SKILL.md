---
name: setup-shelly-stack
description: Configure which Codex models Shelly Stack uses for implementation, judgment,
  investigation, and review panels.
---

> **Codex runtime:** Read the [Codex runtime adapter](../shelly-mode/references/codex-runtime.md) before following tool, model, configuration, path, transcript, or subagent instructions below. The adapter overrides conflicting Claude Code wording.

# Set up Shelly Stack models for Codex

Write `~/.codex/shelly-stack-models.md`. This is the Codex-only override layer. Never read or change `~/.claude/rules/shelly-stack-models.md` from this skill.

## 1. Detect available models

Read the current native subagent tool schema and enumerate every value accepted by `spawn_agent.model`. This schema is the dependable source. Do not spawn a throwaway agent merely to probe model names.

The alias `inherit` is always valid. It means omit the model override so the subagent uses the parent task's model.

If no native model values can be detected, ask the user to paste the models shown by their Codex installation. Never persist a model that has not been confirmed available.

## 2. Load current choices

If `~/.codex/shelly-stack-models.md` exists, read it and treat its values as the current choices. Otherwise construct a proposed mapping from the detected set:

- Use the strongest reasoning model for bug fixes, performance work, judgment, synthesis, and hardest tasks.
- Use the current balanced model for features, refactoring, exploration, investigation, and swarm workers.
- For panels, propose up to three distinct models. Prefer different model families or generations when available.
- Use `inherit` when the detected set does not support a useful distinction.

The roles are:

```text
feature, refactoring
bug-fix
perf-issue
hillclimb
judgment and prose
hardest tasks
how explorer
how explainer
how critics
why investigators
why synthesizer
reflect tooling
reflect judgment, divergent, synthesizer
arena runners
arena cross-judge pool
swarm workers
architect runners
interrogate reviewers
```

The panel roles `how critics`, `arena runners`, `architect runners`, and `interrogate reviewers` are comma-separated lists. One subagent runs per entry, so list length controls fan-out. `arena cross-judge pool` is also a list, but Arena selects one entry different from the parent when possible.

## 3. Confirm

Show every role with its current or proposed model. Mark any saved value missing from the detected set as invalid. Ask whether to use the proposal or change specific roles. Offer only detected model values plus `inherit`.

Use `request_user_input` when it is available and can express the choice cleanly. Otherwise ask for a compact plain-text reply. Do not write the file before the user confirms.

## 4. Validate and write

Validate every real model against the detected set. Stop and ask again if any value is unavailable. `inherit` always passes.

After validation, overwrite `~/.codex/shelly-stack-models.md` with no frontmatter and exactly one line per role:

```text
# shelly-stack model configuration for Codex. One line per role.
# `inherit` omits the subagent model override. Repeated panel entries still count toward fan-out.
feature, refactoring: <model>
bug-fix: <model>
perf-issue: <model>
hillclimb: <model>
judgment and prose: <model>
hardest tasks: <model>
how explorer: <model>
how explainer: <model>
how critics: <model>, <model>, <model>
why investigators: <model>
why synthesizer: <model>
reflect tooling: <model>
reflect judgment, divergent, synthesizer: <model>
arena runners: <model>, <model>, <model>
arena cross-judge pool: <model>, <model>, <model>
swarm workers: <model>
architect runners: <model>, <model>, <model>
interrogate reviewers: <model>, <model>, <model>
```

Tell the user the Codex rule was written and applies to new tasks. Re-running this skill updates it.

## 5. Optional verification skill

Check whether the current project already has a project-local `verify-*` skill or another harness that drives the real app. If not, offer once to create one with `$shelly-stack:create-verification-skill`. Do not start it without the user's choice.
