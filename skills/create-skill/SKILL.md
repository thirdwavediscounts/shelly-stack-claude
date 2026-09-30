---
name: create-skill
description: Author or edit a Claude Code SKILL.md. Use for "create a skill", "write a skill for X", "turn this into a skill", or when another shelly-stack skill (automate-me, reflect, the authoring-a-skill playbook) says to use create-skill. Covers frontmatter, placement, triggering, and the writing rules agents actually follow.
---

# Create skill

shelly-stack bundles this skill because Claude Code has no built-in. It sets the file shape; the **unslop** and **technical-writing** skills set the prose.

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
argument-hint: "<what to pass after /name>"   # optional; shown in autocomplete
allowed-tools: Read, Grep, Glob  # optional; pre-approves these tools for the invoking turn, it restricts nothing
disallowed-tools: AskUserQuestion  # optional; removes tools while the skill is active
---
```

Rules:

- `description` is the only text Claude sees before deciding to load the skill. Put the triggers there ("Use for X, Y, or when the user says Z"), not a summary of the body. Quote it or use `description: >-` when punctuation or wrapping needs it. The skill listing truncates `description` plus `when_to_use` at 1,536 characters, so put the key use case first.
- `disable-model-invocation: true` for mode skills and user-only workflows. Description matching would otherwise fire it on casual turns. The flag also makes the Skill tool refuse the skill, so never set it on a skill that another skill or agent invokes; `scripts/check_invoke_targets.py` fails CI when one does. For a heavy skill that agents invoke, narrow its description to explicit requests and the skills that call it.
- Claude Code ignores a key it does not recognize without an error, so a misspelled key is a silent no-op. Other documented keys (`when_to_use`, `arguments`, `model`, `effort`, `context: fork` with `agent`, `hooks`, `paths`) are for special cases; the full table is at https://code.claude.com/docs/en/skills (checked 2026-09-23).
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
