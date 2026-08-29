# Codex runtime adapter

This file overrides conflicting Claude Code wording in the shared Shelly Stack skill that linked here. Follow the shared workflow, but use Codex-native tools and paths below.

## Skills and questions

- A shared `/name` skill reference means the installed `$shelly-stack:name` skill in Codex.
- Use `request_user_input` for structured questions only when it is available. Otherwise ask one concise plain-text question in the final response.
- Ignore Claude-only variables such as `$ARGUMENTS`. Read the current user request and conversation instead.

## Subagents

- `Agent`, `Task`, teammates, and panes mean Codex native collaboration subagents. Use `spawn_agent`, `send_message`, `followup_task`, `wait_agent`, and `interrupt_agent` as appropriate.
- Do not create a user-visible Codex task as a substitute for a subagent. Use `create_thread` only when the user explicitly asks for a separate task.
- `general-purpose` means an ordinary native subagent with a concrete task name and prompt.
- A `shelly-stack:shelly-agent` request means a native subagent whose prompt tells it to read `$shelly-stack:shelly-mode` completely before it works.
- A `shelly-stack:comment-sicko` request means a native read-only review subagent using the bundled `agents/comment-sicko.md` prompt. Prompt it not to edit files because Codex collaboration does not enforce Claude tool allowlists.
- Launch independent subagents in parallel when the shared skill calls for a panel. Codex has no Claude `isolation: remote` or `environment: cloud` field. Put concurrent writers in separate Git worktrees or give them non-overlapping outputs.
- Model names come from the current `spawn_agent` schema. Never pass Claude aliases such as `fable`, `opus`, `sonnet`, or `haiku` to Codex.

## Model configuration

Read `~/.codex/shelly-stack-models.md` before choosing a Shelly Stack subagent model. The Codex setup skill owns that file. Never read or overwrite `~/.claude/rules/shelly-stack-models.md` from Codex.

If the Codex file is absent or a role is missing, choose from the model values exposed by the current `spawn_agent` schema:

- Use the strongest available reasoning model for bug fixes, performance work, judgment, synthesis, and the hardest tasks.
- Use the current balanced model for feature work, refactoring, exploration, investigation, and swarm workers.
- For panels, choose up to three distinct available models. Prefer different model families or generations when available. If only one model is available, use `inherit` for each required seat.
- `inherit` means omit the subagent model override. It is not a model name.

If a configured model is no longer available, use the closest current model for that run and tell the user to rerun `$shelly-stack:setup-shelly-stack`. Do not silently rewrite their configuration.

## Codex paths and state

- Project skills belong under `.agents/skills/<name>/` when they should travel with the repository.
- Personal Codex skills belong under `~/.codex/skills/<name>/`.
- Codex skill frontmatter contains `name` and `description`. Do not emit Claude-only `disable-model-invocation`, `user-invocable`, or `argument-hint` fields. Put explicit-only policy in `agents/openai.yaml` as `policy.allow_implicit_invocation: false`.
- Prefer Codex thread-history tools for the current task. When a skill needs a local transcript and no thread tool is available, restrict any `~/.codex/sessions/` lookup to the current thread ID or exact working-directory metadata. Never scan unrelated sessions.
- Claude hooks do not run in a native Codex plugin. Shelly mode applies to the turn where the skill is invoked unless the user explicitly asks for a recurring Codex heartbeat automation.
- Claude routines under `automations/` are not included in the Codex build.

## Planning and long-running work

- `TodoWrite` or Claude task-list instructions mean `update_plan` in Codex.
- Claude `/loop` instructions mean a native wait for active subagents during the current turn, or a Codex heartbeat automation when the user asks for recurring future checks.
- Preserve every authorization boundary in the shared skill. Runtime translation does not grant permission to push, merge, deploy, message people, or mutate external systems.
