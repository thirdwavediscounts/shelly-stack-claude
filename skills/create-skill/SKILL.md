---
name: create-skill
description: Author or edit a Claude Code SKILL.md. Use for "create a skill", "write a skill for X", "turn this into a skill", or when another shelly-stack skill (automate-me, reflect, the authoring-a-skill playbook) says to use create-skill. Covers frontmatter, placement, triggering, and the writing rules agents actually follow.
---

# Create skill

Cursor ships `create-skill` as a built-in. Claude Code does not, so shelly-stack bundles this one. It sets the file shape; the **unslop** and **technical-writing** skills set the prose.

## Placement

- Project skill: `.claude/skills/<name>/SKILL.md`. Committed, shared with the team.
- Personal skill: `~/.claude/skills/<name>/SKILL.md`. Just you, every project.
- Plugin skill: `<plugin>/skills/<name>/SKILL.md`. Ships with the plugin.

`<name>` is kebab-case and is the slash command (`/<name>`). Supporting files sit beside `SKILL.md` in `references/`, `scripts/`, or `playbooks/` and are referenced by relative path. A plugin skill that needs an absolute path to its own files uses `${CLAUDE_PLUGIN_ROOT}/skills/<name>/...`.

## Frontmatter

```yaml
---
name: <kebab-case, matches the directory>
description: <one YAML scalar; when to use it, in the user's words, trigger phrases included>
disable-model-invocation: true   # optional; only /name or an explicit request loads it
user-invocable: false            # optional; hides it from the / menu, model-only
argument-hint: "<what to pass after /name>"   # optional
allowed-tools: Read, Grep, Glob  # optional; restricts tools while the skill runs
---
```

Rules:

- `description` is the only text Claude sees before deciding to load the skill. Put the triggers there ("Use for X, Y, or when the user says Z"), not a summary of the body. Quote it or use `description: >-` when punctuation or wrapping needs it. Keep it under ~400 characters.
- `disable-model-invocation: true` for mode skills and anything heavy or opinionated. Description matching would otherwise fire it on casual turns.
- No other keys. Cursor's `mode`, `icon`, `color`, `reminder`, and `alwaysApply` are ignored here. A sticky mode is a marker file plus a `UserPromptSubmit` hook; see `skills/shelly-mode/SKILL.md` for the pattern.
- `$ARGUMENTS` in the body is replaced with whatever the user typed after `/name`.

## Body

Write for an agent that will follow it under load, per the **technical-writing** skill:

- Lead with what the skill does and when. One paragraph.
- Steps as a numbered list, each ending in a checkable state. Name the tool (`Agent`, `AskUserQuestion`, `Bash`) and the model role when a step delegates.
- Reference sibling files by relative path. Reference other skills by bold name ("the **how** skill") so the reader knows to load them, and never paste their contents.
- Say what the reply must contain. A skill that ends without an output contract produces a different reply every run.
- Cut anything the agent already knows. A skill is not a manual.

Every line goes through the **unslop** skill. No long dashes, no colon-as-connector, no "let's", no hedging.

## Check it

1. `/<name>` loads it and the first paragraph tells you what happens next.
2. The description alone, read cold, says when to use it and when not to.
3. A second agent given only the skill produces the same shape of output you did.

Reply: the path written, the trigger phrases in the description, and anything the skill assumes the project provides (a verify skill, an MCP, a script).
