---
name: setup-shelly-stack
description: Configure the native Codex model and reasoning-effort pairs Shelly Stack
  uses for implementation, judgment, investigation, and review panels.
---

> **Codex runtime:** Follow the [native runtime contract](../shelly-mode/references/codex-runtime.md) for model selection, subagents, planning, review, waits, and Codex paths.

# Set up Shelly Stack roles for Codex

Write `~/.codex/shelly-stack-models.md`. This is the Codex-only override layer. Never read or change `~/.claude/rules/shelly-stack-models.md` from this skill.

## 1. Detect native model pairs

Read the current native subagent tool schema. Enumerate every model accepted by `spawn_agent.model`, every effort accepted by `spawn_agent.reasoning_effort`, and any documented model-specific effort limits. The schema is the dependable source. Do not spawn a throwaway agent merely to probe values.

The pair `inherit@inherit` is always valid. It means omit both overrides so the subagent inherits the parent task's settings.

If no native values can be detected, ask the user to paste the models and reasoning efforts shown by their Codex installation. Never persist an unconfirmed pair.

## 2. Load current choices

If `~/.codex/shelly-stack-models.md` exists, read it and treat its values as the current choices. Each value uses `<model>@<reasoning_effort>`. Otherwise construct a proposed mapping from the detected set:

- Use a strong reasoning pair for bug fixes, performance work, judgment, synthesis, review, and hardest tasks.
- Use a balanced pair for features, refactoring, exploration, investigation, and swarm workers.
- Use a faster pair for broad read-only scans when speed matters more than depth.
- For panels, propose up to three distinct valid pairs. Prefer useful model or reasoning-effort diversity.
- Use `inherit@inherit` when the detected set does not support a useful distinction.

The roles are:

```text
feature, refactoring
bug-fix
perf-issue
hillclimb
judgment and prose
hardest tasks
code review
how explorer
how explainer
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

The panel roles `arena runners`, `architect runners`, and `interrogate reviewers` are comma-separated pair lists. One subagent runs per pair, so list length controls fan-out. `arena cross-judge pool` is also a list, but Arena selects one pair different from the parent when possible.

## 3. Confirm

Show every role with its current or proposed pair. Mark an unavailable model, effort, or combination as invalid. Ask whether to use the proposal or change specific roles. Offer only accepted pairs plus `inherit@inherit`.

Use `request_user_input` when it is available and can express the choice cleanly. Otherwise ask for a compact plain-text reply. Do not write the file before the user confirms.

## 4. Validate and write

Validate every real pair against the detected schema. Stop and ask again if any model, effort, or combination is unavailable. `inherit@inherit` always passes.

After validation, overwrite `~/.codex/shelly-stack-models.md` with no frontmatter and exactly one line per role:

```text
# shelly-stack native Codex role configuration. One line per role.
# Format: model@reasoning_effort. `inherit@inherit` omits both native spawn overrides.
feature, refactoring: <model>@<effort>
bug-fix: <model>@<effort>
perf-issue: <model>@<effort>
hillclimb: <model>@<effort>
judgment and prose: <model>@<effort>
hardest tasks: <model>@<effort>
code review: <model>@<effort>
how explorer: <model>@<effort>
how explainer: <model>@<effort>
why investigators: <model>@<effort>
why synthesizer: <model>@<effort>
reflect tooling: <model>@<effort>
reflect judgment, divergent, synthesizer: <model>@<effort>
arena runners: <model>@<effort>, <model>@<effort>, <model>@<effort>
arena cross-judge pool: <model>@<effort>, <model>@<effort>, <model>@<effort>
swarm workers: <model>@<effort>
architect runners: <model>@<effort>, <model>@<effort>, <model>@<effort>
interrogate reviewers: <model>@<effort>, <model>@<effort>, <model>@<effort>
```

Tell the user the Codex role file was written and applies to new tasks. Re-running this skill updates it.

## 5. Optional verification skill

Check whether the current project already has a project-local `verify-*` skill or another harness that drives the real app. If not, offer once to create one with `$shelly-stack:create-verification-skill`. Do not start it without the user's choice.

When updating an existing configuration, remove the retired `how critics` role. How now produces explanations only.
