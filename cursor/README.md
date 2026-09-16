# Shelly Stack for Cursor

This directory is the source overlay for the Cursor build. The installable plugin is generated at `plugins/shelly-stack-cursor` and carries `.cursor-plugin/plugin.json`.

Build and validate from the repository root:

```bash
./scripts/build_cursor_plugin.py
./scripts/build_cursor_plugin.py --check
./scripts/validate_cursor_runtime.py
```

The build copies the tracked root `skills/`, `agents/shelly-agent.md`, `agents/comment-sicko.md`, and `docs/guide/`, then rewrites Claude Code runtime wording to Cursor's (`Task` subagents, `AskQuestion`, `~/.cursor/rules/shelly-stack-models.mdc`, Cursor model slugs, `best-of-n-runner` for worktree isolation, `agent-transcripts/`). `scripts/build_cursor_plugin.py` holds every rewrite rule. Files listed in `override-files.txt` replace their shared counterpart wholesale.

Excluded from the Cursor package: the `create-skill` skill (Cursor ships a built-in with the same name) and the pinned `agents/shelly-<model>-<effort>.md` agents (Cursor passes `model` on the `Task` call directly).

Install locally:

```bash
./scripts/build_cursor_plugin.py --install
```

This copies the built package to `~/.cursor/plugins/local/shelly-stack` as an independent tree, the same way the Codex package is a standalone install. No symlink back into the checkout. Re-run after every rebuild; a new chat picks up the copy. Cursor reads the local plugins directory when "Include third-party Plugins, Skills, and other configs" is enabled. Bump `version` in `plugin.template.json` for every release; it is independent of the Claude and Codex versions.
