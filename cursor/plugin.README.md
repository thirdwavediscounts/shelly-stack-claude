# shelly-stack for Cursor

Generated package. Do not edit it here. Edit the shared root `skills/`, `agents/`, and `docs/` or the overlay under `cursor/`, then run `./scripts/build_cursor_plugin.py` from the repository root.

shelly-stack is Sean's fork of [pstack](https://github.com/cursor/plugins/tree/main/pstack) (MIT, by poteto / Lauren Tan) for Third Wave Discounts. This package is the Cursor runtime of the same plugin identity that Claude Code and Codex install as `shelly-stack`.

## Install locally

From the repository root:

```bash
./scripts/build_cursor_plugin.py --install
```

This copies the package to `~/.cursor/plugins/local/shelly-stack` as its own tree. Re-run it after every rebuild. Enable "Include third-party Plugins, Skills, and other configs" in Cursor settings, then start a new chat. Run `/setup-shelly-stack` once to write `~/.cursor/rules/shelly-stack-models.mdc`. Use `/shelly-mode` for any task that needs rigor and `/shelly-guide` when you do not know which skill fits.

Uninstall the marketplace `pstack` plugin so `unslop`, `tdd`, and the other shared skill names do not register twice.
