# Porting notes

shelly-pstack is a port of [pstack](https://github.com/cursor/plugins/tree/main/pstack) (cursor/plugins @ 397c8660, MIT, Lauren Tan) to a Claude Code plugin. Commit `ef5d652` in this repo is the verbatim upstream import; `git diff ef5d652` is the whole port.

The goal was fidelity. Poteto's voice, skills, playbooks, principles, and file layout are unchanged. Only what Cursor-specific was translated.

## What changed

| Cursor | Claude Code |
|---|---|
| `.cursor-plugin/plugin.json` | `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` (single-plugin repo) |
| `/add-plugin pstack` | `/plugin marketplace add thirdwavediscounts/shelly-pstack`, `/plugin install pstack@shelly-pstack` |
| `Task` tool, `subagent_type: "poteto-agent"` / `"Comment Sicko"` / `generalPurpose` | `Agent` tool, `pstack:poteto-agent` / `pstack:comment-sicko` / `general-purpose` |
| `run_in_background: true`, `readonly:` | dropped; Agent subagents run in the background, access is restricted by tool list |
| `AskQuestion`, `allow_multiple` | `AskUserQuestion`, `multiSelect` |
| Skill frontmatter `mode: true` + `reminder:` (sticky mode) | marker file `~/.claude/poteto-mode/<project>` + `hooks/poteto-mode-reminder.sh` on `UserPromptSubmit` |
| `~/.cursor/rules/pstack-models.mdc` (`alwaysApply`) | `~/.claude/rules/pstack-models.md` (user-level rule, loaded every session) |
| `.cursor/skills/`, `~/.cursor/skills/`, `.cursor/settings.json` | `.claude/skills/`, `~/.claude/skills/`, `.claude/settings.json` |
| Transcripts `~/.cursor/projects/<slug>/agent-transcripts/<uuid>/<uuid>.jsonl` | `~/.claude/projects/<slug>/<uuid>.jsonl` (`<slug>` keeps the leading dash) |
| Cursor built-in `create-skill` | bundled `skills/create-skill` |
| `cursor-team-kit` (`/deslop`, `control-cli`, `control-ui`) | not available; `unslop` over the diff, and the project's `/create-verification-skill` output |
| Cursor Automations (benny), built-in `/automate` | Claude Code routines (`/schedule`, cron only) or Claude in Slack; no message trigger exists |
| Models `grok-4.6-fast-xhigh` / `gpt-5.6-sol-max` / `claude-fable-5-thinking-max` / `claude-opus-5-thinking-xhigh` | `sonnet` / `opus` / `fable` / `opus`; four-seat panels became three (`fable, opus, sonnet`) |
| `inherit-parent` / `auto` | `inherit` (omit `model`) |

## Not ported

- `make-bot-ui` is built on Cursor's Grok Bot stack (webhook routines, `SendToUser` secret-request cards, `[routine]` wakes). No Claude Code analog exists. The original is kept verbatim at `unported/make-bot-ui/` and is not registered as a skill.

## Kept as-is

- Graphite (`gt`) stack workflows, Bugbot triage, the `watch-pr` and `orch` scripts (bun), and every principle skill.
- The watch-pr script still recognizes Bugbot comments by `CURSOR_AUTOMATION_ID`; that is what Bugbot posts on GitHub regardless of editor.
