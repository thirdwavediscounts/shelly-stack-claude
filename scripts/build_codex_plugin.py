#!/usr/bin/env python3
"""Build the native Codex Shelly Stack plugin from the shared Claude sources."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "plugins" / "shelly-stack"
SKILLS_SOURCE = ROOT / "skills"
OVERRIDES = ROOT / "codex" / "overrides"
ADAPTER_SOURCE = ROOT / "codex" / "runtime-adapter.md"
MANIFEST_TEMPLATE = ROOT / "codex" / "plugin.template.json"
CLAUDE_MANIFEST = ROOT / ".claude-plugin" / "plugin.json"


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


def runtime_link(skill_dir: Path, output: Path) -> str:
    adapter = output / "skills" / "shelly-mode" / "references" / "codex-runtime.md"
    return Path(os.path.relpath(adapter, skill_dir)).as_posix()


def rewrite_body_for_codex(body: str, skill_name: str) -> str:
    if skill_name != "setup-shelly-stack":
        body = body.replace(
            "~/.claude/rules/shelly-stack-models.md",
            "~/.codex/shelly-stack-models.md",
        )
    body = re.sub(
        r"A configured role value is either an Agent `model` alias.*?for that spawn\.",
        "Codex has no user agent files: treat every configured role value as a model per the Codex runtime adapter.",
        body,
        flags=re.DOTALL,
    )
    body = re.sub(
        r"(or the agent name as `subagent_type`\)) and `isolation: \"remote\"`\. Remote isolation.*?N Agent calls\.",
        r"\1. Codex has no `isolation` field; give each worker its own worktree or branch in the brief.",
        body,
        flags=re.DOTALL,
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


def transform_skill(skill_path: Path, output: Path) -> None:
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

    link = runtime_link(skill_path.parent, output)
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


def write_codex_manifest(destination: Path) -> None:
    claude_manifest = json.loads(CLAUDE_MANIFEST.read_text(encoding="utf-8"))
    codex_manifest = json.loads(MANIFEST_TEMPLATE.read_text(encoding="utf-8"))
    if claude_manifest.get("name") != codex_manifest.get("name"):
        raise ValueError("Claude and Codex plugin names must match")
    codex_manifest = {
        "name": codex_manifest.pop("name"),
        "version": claude_manifest["version"],
        **codex_manifest,
    }
    destination.write_text(json.dumps(codex_manifest, indent=2) + "\n", encoding="utf-8")


def build(output: Path = OUTPUT) -> None:
    output_is_unsafe = output != ROOT / "plugins" / "shelly-stack" or ROOT not in output.parents
    if output == OUTPUT and output_is_unsafe:
        raise RuntimeError(f"refusing to replace unexpected output path: {output}")

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    copy_tree(SKILLS_SOURCE, output / "skills")
    copy_tree(ROOT / "docs", output / "docs")
    copy_tree(ROOT / "agents", output / "agents")
    copy_tree(OVERRIDES / "skills", output / "skills")
    copy_tree(OVERRIDES / "docs", output / "docs")

    adapter_destination = output / "skills" / "shelly-mode" / "references" / "codex-runtime.md"
    adapter_destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ADAPTER_SOURCE, adapter_destination)

    manifest_dir = output / ".codex-plugin"
    manifest_dir.mkdir(parents=True)
    write_codex_manifest(manifest_dir / "plugin.json")
    shutil.copy2(ROOT / "LICENSE", output / "LICENSE")
    shutil.copy2(ROOT / "codex" / "README.md", output / "README.md")

    for skill_path in sorted((output / "skills").glob("*/SKILL.md")):
        transform_skill(skill_path, output)

    print(f"Built Codex plugin at {output}")


def snapshot(root: Path) -> dict[str, tuple[str, int, str]]:
    result: dict[str, tuple[str, int, str]] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        mode = stat.S_IMODE(path.lstat().st_mode)
        if path.is_symlink():
            result[relative] = ("symlink", mode, os.readlink(path))
        elif path.is_file():
            result[relative] = ("file", mode, hashlib.sha256(path.read_bytes()).hexdigest())
    return result


def check() -> None:
    with tempfile.TemporaryDirectory(prefix="shelly-stack-codex-") as temporary:
        candidate = Path(temporary) / "shelly-stack"
        build(candidate)
        committed = snapshot(OUTPUT)
        generated = snapshot(candidate)
        if committed != generated:
            changed = sorted(set(committed) | set(generated))
            changed = [path for path in changed if committed.get(path) != generated.get(path)]
            details = "\n".join(f"  {path}" for path in changed[:25])
            if len(changed) > 25:
                details += f"\n  ... and {len(changed) - 25} more"
            raise SystemExit(
                "Committed Codex package is stale. Run ./scripts/build_codex_plugin.py.\n"
                f"Changed paths:\n{details}"
            )
    print("Codex package matches the shared source and runtime adapter")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare a fresh build with the committed Codex package without changing the tree",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    check() if arguments.check else build()
