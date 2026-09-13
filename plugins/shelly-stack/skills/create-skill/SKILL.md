---
name: create-skill
description: Author or edit a Codex SKILL.md when the user asks to create a skill,
  turn a workflow into a skill, or update agent instructions.
---

> **Codex runtime:** Follow the [native runtime contract](../shelly-mode/references/codex-runtime.md) for model selection, subagents, planning, review, waits, and Codex paths.

# Create a Codex skill

Create the smallest skill that changes Codex's decisions in the requested workflow. Use the **unslop** and **technical-writing** skills for prose.

## Placement

- Project skill: `.agents/skills/<name>/SKILL.md`. Commit it only when the current request explicitly authorizes commits; otherwise leave the verified skill in the working tree.
- Personal skill: `~/.codex/skills/<name>/SKILL.md`.
- Plugin skill: `<plugin>/skills/<name>/SKILL.md`.

Use lowercase kebab-case for `<name>`. Put optional support files beside `SKILL.md` in `references/`, `scripts/`, or `assets/` only when they have a concrete use.

`agents/openai.yaml` controls a skill's UI metadata and implicit-invocation policy. It is not a custom-agent definition. Native Codex custom agents are TOML files under project `.codex/agents/` or personal `~/.codex/agents/`; create one only when the user asks for a reusable agent role rather than a skill.

## Entrypoint

Use this frontmatter:

```yaml
---
name: <kebab-case, matching the directory>
description: <what the skill does and when it applies>
---
```

Keep the description concise and discriminating because Codex sees it during skill selection. Put detailed steps and examples in the body or a linked reference.

For an explicit-only skill, add `agents/openai.yaml`:

```yaml
interface:
  display_name: "<Display Name>"
  short_description: "<25 to 64 character description>"
policy:
  allow_implicit_invocation: false
```

Do not put Claude-only `disable-model-invocation`, `user-invocable`, or `argument-hint` fields in Codex frontmatter.

## Body

- Lead with the outcome and when the skill applies.
- State non-obvious constraints, authorization boundaries, and stopping conditions.
- Use numbered steps only when order matters. End each ordered step in an observable state.
- Link supporting references from `SKILL.md` and say when to read them.
- Name the expected final output.
- Remove generic advice Codex already follows.

When the workflow delegates, use Codex native subagent terms and a role from `~/.codex/shelly-stack-models.md`. Use `request_user_input` only when available; otherwise ask one concise chat question.

## Validate

Run the installed Codex skill validator:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-directory>
```

Also inspect trigger accuracy, linked references, support scripts, and any authorization boundary the validator cannot prove.

Reply with the path written, the trigger phrases in the description, the validation result, and any required project dependency.
