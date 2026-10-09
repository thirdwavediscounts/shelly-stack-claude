# Set up shelly-stack

In this page you install the plugin, pick which models shelly-stack uses, and run your first task. Setup is one command plus a short conversation.

## Install the plugin

In a Claude Code session, run:

```text
/plugin marketplace add thirdwavediscounts/shelly-stack-claude
/plugin install shelly-stack@shelly-stack
```

Claude Code confirms the plugin is installed. For Codex, install the separate Codex plugin from the `shelly-stack-codex` repository.

## Pick your models

Run:

```text
/setup-shelly-stack
```

[`/setup-shelly-stack`](../../skills/setup-shelly-stack/SKILL.md) detects the models you have access to, shows you each role (code delegates, judgment, the review panels), and asks what you want. It writes `~/.claude/rules/shelly-stack-models.md`.

You only override what you care about. A role with no line in the rule keeps the skill's default. To restore a default later, delete that role's line, or just run `/setup-shelly-stack` again.

To keep a role on the model your session already runs, set the role to `inherit`. shelly-stack then omits the subagent `model` field, so the subagent uses your parent session's model. `inherit` is not a model value. For a panel role the value is a list, and one subagent runs per entry, so the list length sets the panel size. A role can also name a pinned agent that ships with the plugin, such as `shelly-stack:shelly-opus-high`. That is how you pin a full model ID or an effort level. The plugin ships opus at low, medium, high, and xhigh, fable at low, medium, high, and xhigh, and sonnet at low, medium, and high. Setup also configures `swarm workers`, the default model for every `/swarm` worker unless a race names a model for each arm.

## Accept the verification offer, or don't

At the end of setup, `/setup-shelly-stack` looks for a way to prove app behavior in your project, either a `verify-*` skill or an existing harness. If it finds neither, it offers once to generate one with [`/create-verification-skill`](../../skills/create-verification-skill/SKILL.md).

Say yes and it writes a project-local verification skill: `.claude/skills/verify-<app>/`. It teaches agents to drive your app the way a user does and proves the skill works once before handoff. Say no and setup moves on. You can run the create-verification skill yourself any time. [Verify and ship](./06-verify-and-ship.md#create-a-project-verification-skill) covers when it earns its place.

After setup, start a new chat. The model rule applies to new sessions.

## Run your first task

Pick something real but small, and describe it the way you'd describe it to a colleague:

```text
/shelly-mode add a --json flag to this command. text output stays byte-identical. verify both.
```

Watch the todo list. Its first items are the matched playbook's steps copied in, the Feature playbook for this prompt. If `/shelly-mode` skips a step, the step stays in the list with `skip: <reason>`, so you can see what it chose not to do.

From here you can type normal follow-ups. `/shelly-mode` stays in effect for the rest of the session. When you switch subjects, say "new task" so it re-matches the playbook. If a long session drifts, invoke it again.

Next: [Route work through `/shelly-mode`](./02-shelly-mode.md).
