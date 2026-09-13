# Shelly Stack for Codex

This directory is the source overlay for the native Codex build. The installable plugin is generated at `plugins/shelly-stack`.

Build and validate from the repository root:

```bash
./scripts/build_codex_plugin.py
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/shelly-stack
```

The build requires Bun 1.4.0 to compile shared TypeScript helpers into dependency-free Node scripts. The installed plugin itself does not require Bun or a runtime package install.

Install the local marketplace:

```bash
codex plugin marketplace add /absolute/path/to/shelly-stack
codex plugin add shelly-stack@shelly-stack
```

For an existing local install, refresh the cached marketplace snapshot as well as the plugin:

```bash
codex plugin remove shelly-stack@shelly-stack
codex plugin marketplace remove shelly-stack
codex plugin marketplace add /absolute/path/to/shelly-stack
codex plugin add shelly-stack@shelly-stack
codex plugin list
```

Confirm that the listed version matches `codex/plugin.template.json`.

Start a new Codex task, then run `$shelly-stack:setup-shelly-stack`. The setup writes native model and reasoning-effort pairs to `~/.codex/shelly-stack-models.md` and never changes the Claude Code rule.

The generated plugin includes the shared workflow skills, Codex invocation policies, native runtime contract, and Codex role setup. Shelly Mode carries mode-owned routed copies of the explicit-only principles and specialist workflows it may call. It does not copy Claude agent definitions, guide pages, hooks, or automation routines.

Native workflows inspect the current Codex tool schema before using optional planning, task-history, waiting, review, or heartbeat capabilities. They use the documented fallback when a capability is absent, such as a commentary checklist for planning or one bounded status check when recurring automation is unavailable.

The Codex manifest owns its release version. A Codex-only release does not change the Claude manifest and does not require reinstalling the Claude plugin.

Do not edit the generated package. Change the shared root source or the files under `codex/`, then rebuild. `./scripts/build_codex_plugin.py --check` verifies that the committed Codex projection matches the shared source.
