# Shelly Team Kit

Companion workflows for Shelly Stack in Claude Code and Codex. The package adapts all 18 skills from Third Wave Discounts' MIT-licensed Team Kit fork and adds `typescript-conventions` for its two former editor rules.

The verification skills reuse available browser and terminal tools. This plugin does not install a browser, a test framework, service credentials, or background monitors.

## Install

Both plugins use the repository's `shelly-stack` marketplace. In Claude Code, install `shelly-team-kit@shelly-stack`. In Codex, install the same identity after adding this repository as a marketplace. Start a new task after installation.

Invoke a skill as `/shelly-team-kit:deslop` in Claude Code or `$shelly-team-kit:deslop` in Codex. The other skills use the same namespace.

## Included workflows

| Work | Skills |
|---|---|
| Code cleanup and review | `deslop`, `thermo-nuclear-code-quality-review`, `typescript-conventions` |
| Evidence and app control | `verify-this`, `control-ui`, `control-cli`, `run-smoke-tests`, `check-compiler-errors` |
| CI and conflicts | `fix-ci`, `loop-on-ci`, `fix-merge-conflicts` |
| PR preparation | `review-and-ship`, `new-branch-and-pr`, `make-pr-easy-to-review`, `get-pr-comments`, `pr-review-canvas` |
| Work history | `weekly-review`, `what-did-i-get-done`, `workflow-from-chats` |

Claude includes two agent entrypoints for CI snapshots and maintainability review. Codex packages their prompts as references and uses the active runtime's reviewer mechanism. Neither entrypoint grants write permission or starts a recurring monitor.

## Build and verify

Edit this directory, then run these commands from the repository root:

```sh
python3 scripts/build_team_kit_plugin.py
python3 scripts/build_team_kit_plugin.py --check
python3 -m unittest discover -s tests -v
```

The generated Codex package lives at `plugins/shelly-team-kit`. It has native invocation syntax, explicit-only policies, and its own runtime contract. Do not edit that generated directory.

Stack uses `deslop` for code cleanup and `control-ui` or `control-cli` to establish a missing verification harness. Existing project verification skills remain the first choice.

## License

MIT. See [LICENSE](LICENSE) for the upstream copyright notice. The adaptation adds no dependency on editor-specific commands, cloud agents, or review services.
