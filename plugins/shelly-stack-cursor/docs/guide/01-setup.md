# Set up shelly-stack

In this page you install the plugin, pick which models shelly-stack uses, and run your first task. Setup is one command plus a short conversation.

## Install the plugin

From a local checkout of this repository, build the Cursor package and copy it into Cursor's local plugins directory:

```text
./scripts/build_cursor_plugin.py --install
```

The installed copy at `~/.cursor/plugins/local/shelly-stack` is independent of the checkout. Re-run the command after every rebuild. Enable "Include third-party Plugins, Skills, and other configs" in Cursor settings, then start a new chat so it discovers the skills.

## Pick your models

Run:

```text
/setup-shelly-stack
```


[`/setup-shelly-stack`](../../skills/setup-shelly-stack/SKILL.md) detects the models you have access to, shows you each role (code delegates, judgment, the review panels), and asks what you want. Cursor writes `~/.cursor/rules/shelly-stack-models.mdc` and leaves the other clients' configuration untouched.

You only override what you care about. A role with no line in the rule keeps the skill's default. To restore a default later, delete that role's line, or just run `/setup-shelly-stack` again.

You might be wondering how to keep a role on whatever you're already running. Set a role to `inherit-parent` or `auto` and shelly-stack omits the subagent `model` field, so the subagent inherits your parent session's model. Neither alias is a model value. For a panel role the value is a list, and one subagent runs per entry, so the list length sets the panel size. Setup also configures `swarm workers`, the default model for every `/swarm` worker unless a race names a model for each arm.

## Accept the verification offer, or don't

At the end of setup, `/setup-shelly-stack` looks for a way to prove app behavior in your project, either a `verify-*` skill or an existing harness. If it finds neither, it offers once to generate one with [`/create-verification-skill`](../../skills/create-verification-skill/SKILL.md).

Say yes and it writes a project-local verification skill: `.cursor/skills/verify-<app>/`. It teaches agents to drive your app the way a user does and proves the skill works once before handoff. Say no and setup moves on. You can run the create-verification skill yourself any time. [Verify and ship](./06-verify-and-ship.md#create-a-project-verification-skill) covers when it earns its place.

After setup, start a new chat. The model rule applies to new sessions.

## Run your first task

Pick something real but small, and describe it the way you'd describe it to a colleague:

```text
/shelly-mode add a --json flag to this command. text output stays byte-identical. verify both.
```

Watch the todo list. Its first items are the matched playbook's steps copied in, the Feature playbook for this prompt. If `/shelly-mode` skips a step, the step stays in the list with `skip: <reason>`, so you can see what it chose not to do.

From here you can type normal follow-ups. `/shelly-mode` applies to the turn where you invoke it; invoke `/shelly-mode` on each turn where you want it applied.

Next: [Route work through `/shelly-mode`](./02-shelly-mode.md).
