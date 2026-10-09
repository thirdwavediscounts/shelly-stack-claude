---
name: setup-shelly-stack
description: Configure which models shelly-stack uses per role. Detects your available models and writes a user-level rule that overrides the skill defaults. Use for /setup-shelly-stack, "configure shelly-stack models", or changing shelly-stack's model choices.
---

# Setup shelly-stack

Write `~/.claude/rules/shelly-stack-models.md`, a user-level rule loaded every session that sets shelly-stack's model per role. The skills read it and fall back to their inline defaults when a line is absent, so this is an override layer, not a requirement.

## Steps

### 1. Detect available models

Enumerate the values you can pass as an `Agent` subagent's `model` in this session, which are `fable`, `opus`, `sonnet`, and `haiku`. That list is the dependable source. If the Agent tool rejects one, check the valid values in its error message. If you cannot detect any, ask the user to paste the values they have access to. Never write a real value you have not confirmed is available. The alias `inherit` is always valid even though it is not a detected value. Also list the plugin's pinned agents. They are the `shelly-*-*.md` files in the plugin's `agents/` folder, two levels up from this skill's base directory. Each pins a full model ID and an effort. Its role value is `shelly-stack:` plus the file name without `.md`, for example `shelly-stack:shelly-opus-high`. Pinned agents are the only way to pin a full model ID (for example `claude-opus-5-5`) or a per-role effort, because the Agent call's `model` accepts aliases only. A user agent under `~/.claude/agents/` whose frontmatter pins `model` and `effort` is also a valid value. Use its bare name. Do not create user agents. A user agent that points at the plugin by absolute path goes stale, because the install path is a per-session or per-version copy. When the user wants a model and effort that no plugin agent provides, say which one is missing. It belongs as a new file in the plugin's `agents/` folder.

### 2. Load current state

The default role-to-model mapping is the rule shape shown in step 5 below. If `~/.claude/rules/shelly-stack-models.md` already exists, read it and treat its values as the current choices. Otherwise start from those defaults.

### 3. Map and confirm

Show every role with its current model, marking any real value not in the detected set as needing a choice. Ask whether to accept as-is or change specific roles, offering the detected models, the detected agent names (plugin agents first), and `inherit` (this role runs on the parent chat model) as the options. Prefer AskUserQuestion over free text. For panel roles (arena runners, architect runners, interrogate reviewers) the value is a list, and one subagent runs per entry, alias entries included, so the list length sets the count. `arena cross-judge pool` is also a list, but Arena selects one value from it different from the parent's when possible. `swarm workers` is the default model for every worker unless a race or comparison assigns another model per arm.

### 4. Validate

Every real value written must be in the detected set, either a model alias, a `shelly-stack:` agent whose file exists in the plugin's `agents/` folder, or an agent file that exists under `~/.claude/agents/`; `inherit` always passes. If a chosen real value is not available, stop and ask again. A rule pointing at a model the user cannot use breaks every delegation that reads it.

### 5. Write the rule

Write `~/.claude/rules/shelly-stack-models.md` with no frontmatter and one line per role, using the same labels shelly-mode uses. Overwrite the whole file so re-runs stay idempotent. Shape:

```
# shelly-stack model configuration. One line per role. Delete a line to fall back to the skill default.
# `inherit` as a value: the role runs on the parent chat model (omit Agent `model`). Alias entries in a panel list still count toward its fan-out.
# A value naming an agent (shelly-stack:shelly-<model>-<effort>) goes in `subagent_type` with `model` omitted. It pins that agent's model and effort.
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
