---
name: setup-shelly-stack
description: Configure which models shelly-stack uses per role and at what reasoning budget. Detects your available models and writes a user-level rule that overrides the skill defaults. Use for /setup-shelly-stack, "configure shelly-stack models", "shelly-stack budget", or changing shelly-stack's model choices.
---

# Setup shelly-stack

Write `~/.claude/rules/shelly-stack-models.md`, a user-level rule loaded every session that sets shelly-stack's model per role.

## Steps

### 1. Detect available models

Enumerate the values you can pass as an `Agent` subagent's `model` in this session, which are `fable`, `opus`, `sonnet`, and `haiku`. That list is the dependable source. If the Agent tool rejects one, check the valid values in its error message. If you cannot detect any, ask the user to paste the values they have access to. Never write a real value you have not confirmed is available. The alias `inherit` is always valid even though it is not a detected value. Also list the plugin's pinned agents. They are the `shelly-*-*.md` files in the plugin's `agents/` folder, two levels up from this skill's base directory. Each pins a full model ID and an effort. Its role value is `shelly-stack:` plus the file name without `.md`, for example `shelly-stack:shelly-opus-high`. Pinned agents are the only way to pin a full model ID (for example `claude-opus-5-5`) or a per-role effort, because the Agent call's `model` accepts aliases only. A user agent under `~/.claude/agents/` whose frontmatter pins `model` and `effort` is also a valid value. Use its bare name. Do not create user agents. A user agent that points at the plugin by absolute path goes stale, because the install path is a per-session or per-version copy. When the user wants a model and effort that no plugin agent provides, say which one is missing. It belongs as a new file in the plugin's `agents/` folder.

### 2. Load current state

The default role-to-model mapping is the rule shape shown in step 5 below. If `~/.claude/rules/shelly-stack-models.md` already exists, read it and treat its `# budget` line and its role values as the current choices. Otherwise start from those defaults. A line whose role is not in step 5, such as `how critics`, is from a retired role. Drop it.

### 3. Budget, map, and confirm

**(a) Ask for a budget.** Prefer AskUserQuestion over free text. Offer these four options with these exact labels, and name the current budget when the rule records one. With no rule, say that the defaults are aliases that run at the session's effort.

- `unlimited — max reasoning`
- `large — xhigh reasoning`
- `medium — high reasoning`
- `small — medium reasoning`

**(b) Apply it.** Build the working table from the skill defaults, and on a re-run keep any role the user moved to another model, list, or `inherit`. `unlimited`, `large`, `medium`, and `small` set every real value, panel entries included, to the pinned agent `shelly-stack:shelly-<model>-<effort>` of the same model at `max`, `xhigh`, `high`, or `medium`. An alias such as `opus` counts as its model. The effort ladder is `max` > `xhigh` > `high` > `medium` > `low`. If no agent file pins that model at the target effort, use the same model's pinned agent with the highest effort at or below the target. If there is none, keep the alias and mark the role as needing a choice. `inherit` does not change. So `large` turns `opus` into `shelly-stack:shelly-opus-xhigh` and `sonnet` into `shelly-stack:shelly-sonnet-high`, because no sonnet agent pins `xhigh`. No plugin agent pins `max`, so `unlimited` gives the same result as `large`. `small` turns `opus` into `shelly-stack:shelly-opus-medium`.

**(c) Show the roles and confirm.** Show every role with its value, marking any real value not in the detected set as needing a choice. Also list each line step 2 dropped. Ask whether to accept as-is or change specific roles, offering the detected models, the detected agent names (plugin agents first), and `inherit` (this role runs on the parent chat model) as the options. Prefer AskUserQuestion over free text. For panel roles (arena runners, architect runners, interrogate reviewers) the value is a list, and one subagent runs per entry, alias entries included, so the list length sets the count. `arena cross-judge pool` is also a list, but Arena runs one judge. It tries only values whose model differs from the parent's, in list order, so order it by preference. An `inherit` value never judges. `swarm workers` is the default model for every worker unless a race or comparison assigns another model per arm.

### 4. Validate

Every real value written must be in the detected set, either a model alias, a `shelly-stack:` agent whose file exists in the plugin's `agents/` folder, or an agent file that exists under `~/.claude/agents/`. `inherit` always passes. If a chosen real value is not available, stop and ask again.

### 5. Write the rule

Write `~/.claude/rules/shelly-stack-models.md` with no frontmatter, then the comment lines, a `# budget` line with the chosen label and its target effort, and one line per role, using the same labels shelly-mode uses. Overwrite the whole file so re-runs stay idempotent. Never put the role lines in `CLAUDE.md` or `AGENTS.md`. Shape, shown with the skill defaults before step 3 applies the budget:

```
# shelly-stack model configuration. One line per role. Delete a line to fall back to the skill default.
# `inherit` as a value: the role runs on the parent chat model (omit Agent `model`). Alias entries in a panel list still count toward its fan-out.
# A value naming an agent (shelly-stack:shelly-<model>-<effort>) goes in `subagent_type` with `model` omitted. It pins that agent's model and effort.
# budget: large (xhigh)
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

Check whether the project has a way to drive the real app for proof (a `verify-*` skill, or an existing harness). If not, offer once: "want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one with /create-verification-skill." On yes, run the **create-verification-skill** skill with the Skill tool (`shelly-stack:create-verification-skill`). On no, move on without pushing.

### 8. Offer a formal verification skill (optional)

Check whether the project already has a formal verification skill (a project skill that runs a model checker, a proof, or another verifier against the code). If not, offer once: "want a formal verification skill, so agents can prove a key property of your code holds in every case in scope, not only the cases tests reach? I can generate one with /create-formal-verification-skill." On yes, run the **create-formal-verification-skill** skill with the Skill tool (`shelly-stack:create-formal-verification-skill`). On no, move on without pushing.
