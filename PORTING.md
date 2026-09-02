# Porting notes

shelly-stack is a port of [pstack](https://github.com/cursor/plugins/tree/main/pstack) (cursor/plugins @ 397c8660, MIT, Lauren Tan) to Claude Code and Codex. Commit `ef5d652` in this repo is the verbatim upstream import. It is one maintained plugin with one skill, guide, and agent source. Claude Code consumes that source at the repository root. `scripts/build_codex_plugin.py` adds the Codex runtime adapter and produces the native projection at `plugins/shelly-stack`.

The goal is fidelity. Poteto's voice, skills, playbooks, and principles stay shared. Each runtime gets a small adapter for its tools, model names, paths, invocation policy, and unsupported features.

## What changed

| Cursor | Claude Code |
|---|---|
| `.cursor-plugin/plugin.json` | `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` (single-plugin repo) |
| `/add-plugin shelly-stack` | `/plugin marketplace add thirdwavediscounts/shelly-stack`, `/plugin install shelly-stack@shelly-stack` |
| `Task` tool, `subagent_type: "shelly-agent"` / `"Comment Sicko"` / `generalPurpose` | `Agent` tool, `shelly-stack:shelly-agent` / `shelly-stack:comment-sicko` / `general-purpose` |
| `run_in_background: true`, `readonly:` | dropped; Agent subagents run in the background, access is restricted by tool list |
| `AskQuestion`, `allow_multiple` | `AskUserQuestion`, `multiSelect` |
| Skill frontmatter `mode: true` + `reminder:` (sticky mode) | dropped; invoke `/shelly-mode` per turn |
| `~/.cursor/rules/shelly-stack-models.mdc` (`alwaysApply`) | `~/.claude/rules/shelly-stack-models.md` (user-level rule, loaded every session) |
| `.cursor/skills/`, `~/.cursor/skills/`, `.cursor/settings.json` | `.claude/skills/`, `~/.claude/skills/`, `.claude/settings.json` |
| Transcripts `~/.cursor/projects/<slug>/agent-transcripts/<uuid>/<uuid>.jsonl` | `~/.claude/projects/<slug>/<uuid>.jsonl` (`<slug>` keeps the leading dash) |
| Cursor built-in `create-skill` | bundled `skills/create-skill` |
| `cursor-team-kit` (`/deslop`, `control-cli`, `control-ui`) | not available; `unslop` over the diff, and the project's `/create-verification-skill` output |
| Cursor Automations (benny), built-in `/automate` | Claude Code routines (`/schedule`, cron only) or Claude in Slack; no message trigger exists |
| Models `grok-4.6-fast-xhigh` / `gpt-5.6-sol-max` / `claude-fable-5-thinking-max` / `claude-opus-5-thinking-xhigh` | `sonnet` / `opus` / `fable` / `opus`; four-seat panels became three (`fable, opus, sonnet`) |
| `inherit-parent` / `auto` | `inherit` (omit `model`) |

## Codex build

| Claude Code source | Native Codex build |
|---|---|
| repository root with `.claude-plugin/plugin.json` | `plugins/shelly-stack` with `.codex-plugin/plugin.json` |
| `.claude-plugin/marketplace.json` | `.agents/plugins/marketplace.json` |
| `disable-model-invocation: true` in skill frontmatter | `agents/openai.yaml` with `policy.allow_implicit_invocation: false` |
| `Agent` and custom `subagent_type` values | native collaboration subagents plus bundled prompt files |
| `AskUserQuestion` | `request_user_input` when available, otherwise a concise chat question |
| `~/.claude/rules/shelly-stack-models.md` | `~/.codex/shelly-stack-models.md` |
| Claude model aliases | values detected from the current `spawn_agent` schema |
| `.claude/skills` and `~/.claude/skills` | `.agents/skills` and `~/.codex/skills` |
| `TodoWrite` | `update_plan` |
| Claude transcript paths | Codex thread tools, with current-thread-only local fallback |
| Claude routines and cloud-agent fields | excluded or translated to native local subagents and Codex heartbeat automations |

The Codex build copies the shared `skills`, `docs`, and subagent prompts, overlays Codex-specific skills such as setup, inserts a runtime adapter link into every skill, and translates explicit-only invocation metadata. The generated directory is committed so Codex can install it directly from the repository marketplace.

Both marketplaces expose the identity `shelly-stack@shelly-stack`. The Claude manifest owns the shared release version, and the Codex builder writes that same version into the generated manifest. CI runs the builder in check mode and rejects any stale generated package or client-specific configuration leak.

## Not ported

- `make-bot-ui` is built on Cursor's Grok Bot stack (webhook routines, `SendToUser` secret-request cards, `[routine]` wakes). No Claude Code analog exists. The original is kept verbatim at `unported/make-bot-ui/` and is not registered as a skill.
- The benny automation pack is not part of the Codex package; it still depends on Claude routines.

## Replaced

- Graphite (`gt`) stack workflows now run on `gh` plus git: topology from `gh pr list`, restacks via `git rebase --update-refs`, sequential landing by arming `gh pr merge --auto` on one PR at a time.
- Cloud and remote execution: every worker runs locally, writers in their own git worktree.

## Kept as-is

- Bugbot triage, the `watch-pr` and `orch` scripts (bun), and every principle skill.
- The watch-pr script still recognizes Bugbot comments by `CURSOR_AUTOMATION_ID`; that is what Bugbot posts on GitHub regardless of editor.
