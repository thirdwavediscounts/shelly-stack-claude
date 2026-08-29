#!/usr/bin/env python3
"""Validate Shelly Stack's single-source Claude Code and Codex contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLUGIN_NAME = "shelly-stack"


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def skill_names(root: Path) -> set[str]:
    return {path.parent.name for path in root.glob("*/SKILL.md")}


def main() -> None:
    claude_manifest = load_json(ROOT / ".claude-plugin" / "plugin.json")
    codex_manifest = load_json(
        ROOT / "plugins" / PLUGIN_NAME / ".codex-plugin" / "plugin.json"
    )
    require(claude_manifest.get("name") == PLUGIN_NAME, "unexpected Claude plugin name")
    require(codex_manifest.get("name") == PLUGIN_NAME, "unexpected Codex plugin name")
    require(
        claude_manifest.get("version") == codex_manifest.get("version"),
        "Claude and Codex plugin versions must match",
    )

    claude_marketplace = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    codex_marketplace = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
    for client, marketplace in (
        ("Claude", claude_marketplace),
        ("Codex", codex_marketplace),
    ):
        require(marketplace.get("name") == PLUGIN_NAME, f"{client} marketplace name must match")
        plugins = marketplace.get("plugins")
        require(
            isinstance(plugins, list) and len(plugins) == 1,
            f"{client} marketplace must contain one plugin",
        )
        require(plugins[0].get("name") == PLUGIN_NAME, f"{client} plugin entry must match")

    codex_source = codex_marketplace["plugins"][0].get("source")
    require(
        codex_source == {"source": "local", "path": "./plugins/shelly-stack"},
        "Codex marketplace must point at the generated runtime projection",
    )

    shared_skills = skill_names(ROOT / "skills")
    codex_skills = skill_names(ROOT / "plugins" / PLUGIN_NAME / "skills")
    require(shared_skills == codex_skills, "Claude and Codex skill inventories differ")

    runtime_notice = "> **Codex runtime:** Read the [Codex runtime adapter]"
    for skill_path in sorted((ROOT / "plugins" / PLUGIN_NAME / "skills").glob("*/SKILL.md")):
        require(
            runtime_notice in skill_path.read_text(encoding="utf-8"),
            f"generated skill lacks the Codex runtime adapter: {skill_path}",
        )

    claude_setup = (ROOT / "skills" / "setup-shelly-stack" / "SKILL.md").read_text(encoding="utf-8")
    codex_setup = (
        ROOT / "plugins" / PLUGIN_NAME / "skills" / "setup-shelly-stack" / "SKILL.md"
    ).read_text(encoding="utf-8")
    require(
        "~/.claude/rules/shelly-stack-models.md" in claude_setup,
        "Claude setup path is missing",
    )
    require("~/.codex/shelly-stack-models.md" in codex_setup, "Codex setup path is missing")
    require(
        "never read or change" in codex_setup.lower(),
        "Codex setup must protect Claude configuration",
    )

    print(
        f"Validated {len(shared_skills)} shared skills for Claude Code and Codex "
        f"at version {claude_manifest['version']}"
    )


if __name__ == "__main__":
    main()
