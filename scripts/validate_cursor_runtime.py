#!/usr/bin/env python3
"""Validate that the generated Cursor package speaks only Cursor's runtime."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
PLUGIN_NAME = "shelly-stack"
CURSOR_ROOT = ROOT / "plugins" / "shelly-stack-cursor"
EXCLUDED_SKILLS = {"create-skill"}

# setup-shelly-stack names the sibling clients' config paths on purpose so it never touches them.
PATH_ALLOWLIST = {"skills/setup-shelly-stack/SKILL.md", "README.md"}

FORBIDDEN_PATTERNS = {
    r"~/\.claude/": "Claude user paths",
    r"(?<![\w.-])\.claude/": "Claude project paths",
    r"\bgeneral-purpose\b": "Claude subagent type",
    r"\bshelly-stack:(?:shelly-agent|comment-sicko)\b": "Claude plugin-qualified agent name",
    r"\bshelly-<model>-<effort>\b": "Claude pinned-agent convention",
    r"`(?:fable|opus|sonnet|haiku)`": "Claude model alias",
    r"`inherit`": "Claude inherit alias",
    r"\bAskUserQuestion\b|\bToolSearch\b": "Claude tool names",
    r"`Agent` (?:call|calls|response body|prompts)|\bAgent tool\b|\bAgent subagents?\b|Spawn `Agent`": "Claude Agent tool wording",
    r"\bWorkflow tool\b|Workflow-tool|`Workflow`": "Claude Workflow tool wording",
    r"\bisolation\s*:": "Claude agent isolation option",
    r"Read/Grep/Glob/Bash|read-only tool list|tools left in": "Claude tool allowlist wording",
    r"\bmcp__claude": "Claude-specific connector name",
    r"\bCLAUDE_PLUGIN_ROOT\b|\$\{PLUGIN_ROOT\}": "Claude plugin root variable",
    r"\bCLAUDE\.local\.md\b": "Claude-only repository instructions",
    r"\$ARGUMENTS\b": "Claude command arguments",
    r"(?<![\w.-])/code-review\b": "Claude code-review command",
    r"Claude Code": "Claude lifecycle wording",
    r"multiSelect|caps at four": "Claude AskUserQuestion schema",
    r"\bargument-hint\b": "Claude-only frontmatter",
    r"\bCodex\b|\$shelly-stack:": "Codex runtime wording",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_frontmatter(path: Path) -> dict:
    contents = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", contents, flags=re.DOTALL)
    require(match is not None, f"missing YAML frontmatter: {path}")
    value = yaml.safe_load(match.group(1))
    require(isinstance(value, dict), f"frontmatter must be an object: {path}")
    return value


def text_files() -> list[Path]:
    result = []
    for path in sorted(CURSOR_ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in {".md", ".sh", ".json"}:
            continue
        if "scripts" in path.relative_to(CURSOR_ROOT).parts:
            continue
        result.append(path)
    return result


def validate_structure() -> None:
    manifest = json.loads((CURSOR_ROOT / ".cursor-plugin" / "plugin.json").read_text(encoding="utf-8"))
    template = json.loads((ROOT / "cursor" / "plugin.template.json").read_text(encoding="utf-8"))
    claude = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    require(manifest.get("name") == PLUGIN_NAME == claude.get("name"), "Cursor plugin name must be shelly-stack")
    require(manifest.get("version") == template.get("version"), "generated Cursor version must match the template")
    require(re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"] or ""), "Cursor version must be MAJOR.MINOR.PATCH")
    require(manifest.get("skills") == "./skills/" and manifest.get("agents") == "./agents/", "Cursor manifest must expose ./skills/ and ./agents/")

    top_level = {path.name for path in CURSOR_ROOT.iterdir()}
    require(top_level == {".cursor-plugin", "skills", "agents", "docs", "LICENSE", "README.md"}, f"unexpected Cursor package entries: {sorted(top_level)}")
    for forbidden in (".git", "node_modules", "__pycache__"):
        require(not any(p.name == forbidden for p in CURSOR_ROOT.rglob("*") if p.is_dir()), f"Cursor package leaks {forbidden}")

    shared = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")} - EXCLUDED_SKILLS
    generated = {p.parent.name for p in (CURSOR_ROOT / "skills").glob("*/SKILL.md")}
    require(shared == generated, f"Cursor skill inventory differs: {sorted(shared ^ generated)}")
    require({p.name for p in (CURSOR_ROOT / "agents").iterdir()} == {"shelly-agent.md", "comment-sicko.md"}, "Cursor agents must be shelly-agent and comment-sicko")

    for skill_path in sorted((CURSOR_ROOT / "skills").glob("*/SKILL.md")):
        metadata = load_frontmatter(skill_path)
        require(metadata.get("name") == skill_path.parent.name, f"skill name mismatch: {skill_path}")
        require(isinstance(metadata.get("description"), str) and metadata["description"].strip(), f"skill description missing: {skill_path}")
        require(set(metadata) <= {"name", "description", "disable-model-invocation", "mode", "icon", "color", "reminder"}, f"non-Cursor frontmatter in {skill_path}: {sorted(metadata)}")

    mode = load_frontmatter(CURSOR_ROOT / "skills" / "shelly-mode" / "SKILL.md")
    require(mode.get("mode") is True and mode.get("disable-model-invocation") is True, "shelly-mode must be an explicit-only Cursor mode skill")
    agent = load_frontmatter(CURSOR_ROOT / "agents" / "shelly-agent.md")
    require(agent.get("is_background") is True, "shelly-agent must run in the background")


def validate_text() -> None:
    violations = []
    for path in text_files():
        relative = path.relative_to(CURSOR_ROOT).as_posix()
        if relative in PATH_ALLOWLIST:
            continue
        contents = path.read_text(encoding="utf-8")
        for pattern, label in FORBIDDEN_PATTERNS.items():
            if match := re.search(pattern, contents):
                line = contents.count("\n", 0, match.start()) + 1
                violations.append(f"{relative}:{line}: {label}: {match.group(0)!r}")
    require(not violations, "Cursor package contains non-native runtime instructions:\n  " + "\n  ".join(violations))


def validate_contracts() -> None:
    mode = (CURSOR_ROOT / "skills" / "shelly-mode" / "SKILL.md").read_text(encoding="utf-8")
    for phrase in ('subagent_type: "shelly-agent"', "`run_in_background: true`", "`subagent_type: best-of-n-runner`", "`inherit-parent` or `auto`"):
        require(phrase in mode, f"Cursor shelly-mode lacks {phrase}")
    setup = (CURSOR_ROOT / "skills" / "setup-shelly-stack" / "SKILL.md").read_text(encoding="utf-8")
    require("~/.cursor/rules/shelly-stack-models.mdc" in setup and "alwaysApply: true" in setup, "Cursor setup must write an always-applied .mdc rule")
    require("Never read or change `~/.claude/rules/shelly-stack-models.md`" in setup, "Cursor setup must protect the Claude rule")
    swarm = (CURSOR_ROOT / "skills" / "swarm" / "SKILL.md").read_text(encoding="utf-8")
    require("best-of-n-runner" in swarm and "`Task` tool" in swarm, "Cursor swarm must fan out through Task and best-of-n-runner")
    guide = (CURSOR_ROOT / "skills" / "shelly-guide" / "SKILL.md").read_text(encoding="utf-8")
    require("<shelly-stack-plugin-dir>/docs/guide/" in guide and (CURSOR_ROOT / "docs" / "guide" / "README.md").is_file(), "Cursor shelly-guide must ship and point at docs/guide")
    audit = (CURSOR_ROOT / "skills" / "shelly-mode" / "scripts" / "worktree-audit.sh").read_text(encoding="utf-8")
    require("$HOME/.cursor/projects/$slug/agent-transcripts" in audit, "worktree-audit must read Cursor transcripts")


def main() -> None:
    validate_structure()
    validate_text()
    validate_contracts()
    skills = len(list((CURSOR_ROOT / "skills").glob("*/SKILL.md")))
    version = json.loads((CURSOR_ROOT / ".cursor-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
    print(f"Validated Cursor package: {skills} skills, version {version}")


if __name__ == "__main__":
    main()
