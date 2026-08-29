#!/usr/bin/env python3
"""Build the native Codex Shelly Stack plugin from the shared Claude sources."""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "plugins" / "shelly-stack"
SKILLS_SOURCE = ROOT / "skills"
OVERRIDES = ROOT / "codex" / "overrides"
ADAPTER_SOURCE = ROOT / "codex" / "runtime-adapter.md"
MANIFEST_SOURCE = ROOT / "codex" / "plugin.json"


def copy_tree(source: Path, destination: Path) -> None:
    if source.exists():
        shutil.copytree(source, destination, dirs_exist_ok=True)


def parse_frontmatter(contents: str, skill_path: Path) -> tuple[dict, str]:
    match = re.match(r"\A---\n(.*?)\n---\n?", contents, re.DOTALL)
    if match is None:
        raise ValueError(f"missing YAML frontmatter: {skill_path}")
    metadata = yaml.safe_load(match.group(1))
    if not isinstance(metadata, dict):
        raise ValueError(f"frontmatter must be an object: {skill_path}")
    return metadata, contents[match.end() :]


def display_name(skill_name: str) -> str:
    return " ".join(part.upper() if part in {"tdd"} else part.capitalize() for part in skill_name.split("-"))


def short_description(name: str) -> str:
    value = f"Use the {name} workflow in Codex"
    if len(value) < 25:
        value = f"Run the {name} workflow in Codex"
    return value[:64].rstrip()


def runtime_link(skill_dir: Path) -> str:
    adapter = OUTPUT / "skills" / "shelly-mode" / "references" / "codex-runtime.md"
    return Path(os.path.relpath(adapter, skill_dir)).as_posix()


def rewrite_body_for_codex(body: str, skill_name: str) -> str:
    if skill_name != "setup-shelly-stack":
        body = body.replace(
            "~/.claude/rules/shelly-stack-models.md",
            "~/.codex/shelly-stack-models.md",
        )
    body = body.replace("~/.claude/skills/", "~/.codex/skills/")
    body = body.replace(".claude/skills/", ".agents/skills/")

    if skill_name == "shelly-mode":
        body = re.sub(
            r"## Sticky mode\n\n.*?\n\n## Principles",
            "## Turn-scoped mode\n\n"
            "Codex does not run the Claude `UserPromptSubmit` hook. Apply Shelly mode to "
            "the current turn only. Do not create or delete `~/.claude/shelly-mode` marker "
            "files. If the user explicitly asks for recurring future checks, use a Codex "
            "heartbeat automation.\n\n## Principles",
            body,
            count=1,
            flags=re.DOTALL,
        )
    if skill_name == "arena":
        body = body.replace(
            "Otherwise default to one each on `fable`, `opus`, `sonnet`.",
            "Otherwise choose the panel from the Codex runtime adapter's dynamic fallback.",
        )
        body = body.replace(
            "Otherwise use `fable`, `opus`, `sonnet`.",
            "Otherwise choose from the Codex runtime adapter's dynamic fallback.",
        )
        body = body.replace(
            "Spawn one read-only judge subagent (give it only Read/Grep/Glob/Bash) on that model.",
            "Spawn one judge subagent on that model and prompt it to remain read-only. Codex does not enforce a per-subagent tool allowlist.",
        )
    return body


def transform_skill(skill_path: Path) -> None:
    metadata, body = parse_frontmatter(skill_path.read_text(encoding="utf-8"), skill_path)
    explicit_only = bool(
        metadata.pop("disable-model-invocation", False)
        or metadata.pop("disable_model_invocation", False)
    )
    metadata.pop("argument-hint", None)
    metadata.pop("user-invocable", None)
    name = metadata.get("name")
    if not isinstance(name, str) or not name:
        raise ValueError(f"skill name is missing: {skill_path}")
    body = rewrite_body_for_codex(body, name)

    link = runtime_link(skill_path.parent)
    notice = (
        f"> **Codex runtime:** Read the [Codex runtime adapter]({link}) before following "
        "tool, model, configuration, path, transcript, or subagent instructions below. "
        "The adapter overrides conflicting Claude Code wording.\n\n"
    )
    frontmatter = yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True).rstrip()
    skill_path.write_text(f"---\n{frontmatter}\n---\n\n{notice}{body.lstrip()}", encoding="utf-8")

    if explicit_only:
        agents_dir = skill_path.parent / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        agent_yaml = {
            "interface": {
                "display_name": display_name(name),
                "short_description": short_description(display_name(name)),
            },
            "policy": {"allow_implicit_invocation": False},
        }
        (agents_dir / "openai.yaml").write_text(
            yaml.safe_dump(agent_yaml, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )


def build() -> None:
    expected_output = ROOT / "plugins" / "shelly-stack"
    if OUTPUT != expected_output or ROOT not in OUTPUT.parents:
        raise RuntimeError(f"refusing to replace unexpected output path: {OUTPUT}")

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)

    copy_tree(SKILLS_SOURCE, OUTPUT / "skills")
    copy_tree(ROOT / "docs", OUTPUT / "docs")
    copy_tree(ROOT / "agents", OUTPUT / "agents")
    copy_tree(OVERRIDES / "skills", OUTPUT / "skills")
    copy_tree(OVERRIDES / "docs", OUTPUT / "docs")

    adapter_destination = OUTPUT / "skills" / "shelly-mode" / "references" / "codex-runtime.md"
    adapter_destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ADAPTER_SOURCE, adapter_destination)

    manifest_dir = OUTPUT / ".codex-plugin"
    manifest_dir.mkdir(parents=True)
    shutil.copy2(MANIFEST_SOURCE, manifest_dir / "plugin.json")
    shutil.copy2(ROOT / "LICENSE", OUTPUT / "LICENSE")
    shutil.copy2(ROOT / "codex" / "README.md", OUTPUT / "README.md")

    for skill_path in sorted((OUTPUT / "skills").glob("*/SKILL.md")):
        transform_skill(skill_path)

    print(f"Built Codex plugin at {OUTPUT}")


if __name__ == "__main__":
    build()
