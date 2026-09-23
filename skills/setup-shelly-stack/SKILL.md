---
name: setup-shelly-stack
description: Configure which models shelly-stack uses per role. Detects your available models and writes a user-level rule that overrides the skill defaults. Use for /setup-shelly-stack, "configure shelly-stack models", or changing shelly-stack's model choices.
---

# Setup shelly-stack

Write `~/.claude/rules/shelly-stack-models.md`, a user-level rule loaded every session that sets shelly-stack's model per role. The skills read it and fall back to their inline defaults when a line is absent, so this is an override layer, not a requirement.

## Steps

### 1. Detect available models

Enumerate the values you can pass as an `Agent` subagent's `model` in this session — `fable`, `opus`, `sonnet`, `haiku` — that is the dependable source; check the valid values in the Agent tool's error message if one is rejected. If you cannot detect any, ask the user to paste the values they have access to. Never write a real value you have not confirmed is available. The alias `inherit` is always valid even though it is not a detected value. Also list the user agents under `~/.claude/agents/` whose frontmatter pins `model` and `effort` (convention `shelly-<model>-<effort>.md`, body copied from `agents/shelly-agent.md`); their names are valid role values too, and they are the only way to pin a full model ID (for example `claude-opus-5-5`) or a per-role effort (`low`, `medium`, `high`, `xhigh`, `max`), since the Agent call's `model` accepts aliases only. Offer to create a missing agent file when the user wants a model or effort no existing agent provides.

### 2. Load current state

The default role-to-model mapping is the rule shape shown in step 5 below. If `~/.claude/rules/shelly-stack-models.md` already exists, read it and treat its values as the current choices. Otherwise start from those defaults.

### 3. Map and confirm

Show every role with its current model, marking any real value not in the detected set as needing a choice. Ask whether to accept as-is or change specific roles, offering the detected models, the detected agent names, and `inherit` (this role runs on the parent chat model) as the options. Prefer AskUserQuestion over free text. For panel roles (arena runners, architect runners, interrogate reviewers) the value is a list, and one subagent runs per entry, alias entries included, so the list length sets the count. `arena cross-judge pool` is also a list, but Arena selects one value from it different from the parent's when possible. `swarm workers` is the default model for every worker unless a race or comparison assigns another model per arm.

### 4. Validate

Every real value written must be in the detected set, either a model alias or an agent file that exists under `~/.claude/agents/`; `inherit` always passes. If a chosen real value is not available, stop and ask again. A rule pointing at a model the user cannot use breaks every delegation that reads it.

### 5. Write the rule

Write `~/.claude/rules/shelly-stack-models.md` with no frontmatter and one line per role, using the same labels shelly-mode uses. Overwrite the whole file so re-runs stay idempotent. Shape:

```
# shelly-stack model configuration. One line per role. Delete a line to fall back to the skill default.
# `inherit` as a value: the role runs on the parent chat model (omit Agent `model`). Alias entries in a panel list still count toward its fan-out.
# A value naming a user agent under ~/.claude/agents (shelly-<model>-<effort>) goes in `subagent_type` with `model` omitted; it pins that agent's model and effort.
feature, refactoring: sonnet
bug-fix: opus
perf-issue: opus
hillclimb: opus
judgment and prose: fable
hardest tasks: fable
how explorer: sonnet
how explainer: fable
why investigators: sonnet
why synthesizer: fable
reflect tooling: opus
reflect judgment, divergent, synthesizer: fable
arena runners: fable, opus, sonnet
arena cross-judge pool: fable, opus, sonnet
swarm workers: sonnet
architect runners: fable, opus, sonnet
interrogate reviewers: fable, opus, sonnet
```

### 6. Confirm

Tell the user the rule was written and that it applies to new sessions. Re-running this skill updates it.

### 7. Offer a verification skill (optional)

Check whether the project has a way to drive the real app for proof (a `verify-*` skill, or an existing harness). If not, offer once: "want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one with /create-verification-skill." On yes, invoke `/create-verification-skill` (resolves wherever shelly-stack is installed — workspace, user, or plugin). On no, move on without pushing.

When updating an existing configuration, drop any role line the shape above does not list. No skill reads it.
