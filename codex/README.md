# Shelly Stack for Codex

This directory is the source overlay for the native Codex build. The installable plugin is generated at `plugins/shelly-stack`.

Build and validate from the repository root:

```bash
./scripts/build_codex_plugin.py
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/shelly-stack
```

Install the local marketplace:

```bash
codex plugin marketplace add /absolute/path/to/shelly-stack
codex plugin add shelly-stack@shelly-stack
```

Start a new Codex task, then run `$shelly-stack:setup-shelly-stack`. The setup writes `~/.codex/shelly-stack-models.md` and never changes the Claude Code rule.

The generated plugin includes the shared skills, guide, subagent prompts, Codex invocation policies, runtime adapter, and Codex model setup. The benny routines remain in the root Claude Code package and are not copied into the Codex build.

Do not edit the generated package. Change the shared root source or the files under `codex/`, then rebuild. `./scripts/build_codex_plugin.py --check` verifies that the committed Codex projection matches the shared source.
