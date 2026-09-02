# Porting notes

shelly-stack began as a port of [pstack](https://github.com/cursor/plugins/tree/main/pstack) (cursor/plugins @ 397c8660, MIT, Lauren Tan). Commit `ef5d652` in this repo is the verbatim upstream import. Since then it has been reshaped into Third Wave Discounts' own workflow for Claude Code and Codex on plain GitHub. The skills, playbooks, principles, guide, and subagent prompts are one shared source. Claude Code consumes that source at the repository root. `scripts/build_codex_plugin.py` adds the Codex runtime adapter and produces the native projection at `plugins/shelly-stack`.

## What changed from upstream

| Upstream | shelly-stack |
|---|---|
| Editor plugin manifest and `/add-plugin` | `.claude-plugin/plugin.json` plus `.claude-plugin/marketplace.json` for Claude Code; `.agents/plugins/marketplace.json` plus `plugins/shelly-stack` for Codex |
| `Task` tool with `shelly-agent`, `Comment Sicko`, `generalPurpose` | Claude Code `Agent` with `shelly-stack:shelly-agent`, `shelly-stack:comment-sicko`, `general-purpose`; Codex native subagents per `codex/runtime-adapter.md` |
| `AskQuestion`, `allow_multiple` | `AskUserQuestion`, `multiSelect` in Claude Code; `request_user_input` in Codex |
| Sticky mode (`mode: true` plus `reminder:` frontmatter) | Removed. `/shelly-mode` applies to the task you invoke it on. |
| Graphite stacks, `gt submit --merge-when-ready`, the `watch-pr` and `orch` bun scripts | Plain GitHub through `gh`. A stack is a chain of PRs based on each other. Shipping merges verified PRs in order on an explicit go. |
| Bugbot triage | Generic review-bot triage in `skills/shelly-mode/references/review-bot-triage.md`, for any automated reviewer |
| Editor cloud agents, `environment: "cloud"` | A fresh subagent, remote (`isolation: "remote"`) when available, local otherwise |
| `cursor-team-kit` (`/deslop`, `control-cli`, `control-ui`) | The **unslop** skill over the diff, and the project's verification skill from `/create-verification-skill` |
| Built-in `create-skill` | Bundled `skills/create-skill` |
| Editor automations (benny), `make-bot-ui` | benny is a dormant Claude routines pack under `automations/benny`. `make-bot-ui` was dropped. |
| Model names (`grok-4.6-fast-xhigh`, `gpt-5.6-sol-max`, `claude-fable-5-thinking-max`, `claude-opus-5-thinking-xhigh`) | Claude aliases `sonnet`, `opus`, `fable` per role from `~/.claude/rules/shelly-stack-models.md`; Codex models from the `spawn_agent` schema; `inherit` omits the override |
| `~/.cursor/rules/shelly-stack-models.mdc`, `.cursor/skills/` | `~/.claude/rules/shelly-stack-models.md`, `.claude/skills/` and `~/.claude/skills/` |
| Transcripts under `~/.cursor/projects/<slug>/agent-transcripts/` | `~/.claude/projects/<slug>/<uuid>.jsonl` (`<slug>` keeps the leading dash) |

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
| Claude routines | excluded, or translated to Codex heartbeat automations |

The Codex build copies the shared `skills`, `docs`, and subagent prompts, overlays Codex-specific skills such as setup, inserts a runtime adapter link into every skill, and translates explicit-only invocation metadata. The generated directory is committed so Codex can install it directly from the repository marketplace.

Both marketplaces expose the identity `shelly-stack@shelly-stack`. The Claude manifest owns the shared release version, and the Codex builder writes that same version into the generated manifest. CI runs the builder in check mode and rejects any stale generated package or client-specific configuration leak.

## Kept as-is

- Every principle skill, the playbook set, the review panels, and the guide structure.
- The benny automation pack, dormant, for a future Claude-native issue-report bot.
