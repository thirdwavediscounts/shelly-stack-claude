# Shelly Stack for Codex

This is the installable native Codex runtime for Shelly Stack. It shares workflow intent with the Claude package while using Codex skills, collaboration subagents, model and reasoning-effort overrides, and capability-aware planning, review, wait, and heartbeat branches. When an optional capability is absent, the native runtime contract defines the fallback.

An explicit `$shelly-stack:shelly-mode` invocation can follow its bundled playbooks, principles, and specialist workflows through mode-owned routed references. Standalone explicit-only invocation policies remain unchanged.

Start a new Codex task after installing or updating the plugin. Run `$shelly-stack:setup-shelly-stack` once to save Codex role pairs in `~/.codex/shelly-stack-models.md`. That setup never reads or changes Claude's model configuration.

Bundled operational helpers run as standalone Node scripts. They do not install packages, require Bun, or write dependencies into the plugin cache at runtime.

The Codex manifest has its own release version. Installing or updating this package does not require reinstalling the Claude plugin.
