#!/usr/bin/env python3
"""Validate Shelly Stack's single-source Claude Code and Codex contract."""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import NamedTuple

import yaml


ROOT = Path(__file__).resolve().parent.parent
PLUGIN_NAME = "shelly-stack"
CODEX_ROOT = ROOT / "plugins" / PLUGIN_NAME
SHELLY_MODE_ROUTED_SKILLS = frozenset(
    {
        "architect",
        "arena",
        "create-skill",
        "create-verification-skill",
        "figure-it-out",
        "how",
        "interrogate",
        "maintain-verification-skill",
        "no-comments",
        "reflect",
        "show-me-your-work",
        "swarm",
        "tdd",
        "technical-writing",
        "ticket",
        "unslop",
        "why",
    }
)
FORGE_PLAYBOOKS = frozenset(
    {
        "autopilot-full.md",
        "autopilot-stack.md",
        "babysit.md",
        "multi-phase-plan.md",
        "opening-a-pr.md",
        "orchestrate.md",
        "shipping.md",
    }
)


class CompatibilityCase(NamedTuple):
    name: str
    relative_path: str
    required_phrases: tuple[str, ...]
    forbidden_phrases: tuple[str, ...] = ()


CODEX_COMPATIBILITY_CASES = (
    CompatibilityCase(
        name="babysit-current-turn",
        relative_path="skills/shelly-mode/playbooks/babysit.md",
        required_phrases=(
            "`drive` uses current-turn continuation",
            "`drive` does not require a heartbeat",
            "`background` performs one bounded status pass per active coordinator tick",
            "Use the recurring-check branch only for an explicitly requested future or cross-turn follow-up",
            "A request to babysit, get it green, or watch CI does not by itself authorize PR comments",
        ),
        forbidden_phrases=(
            "For an explicitly requested `drive`, `background`, or `watch CI` monitor, use the native runtime contract's recurring-check branch",
            "For `drive`, start a heartbeat before every next status pass",
        ),
    ),
    CompatibilityCase(
        name="multi-phase-plan-scratch-evidence",
        relative_path="skills/shelly-mode/playbooks/multi-phase-plan.md",
        required_phrases=(
            "Keep the scratch path and observed output or screenshots for Appendix A",
            "Do not create a branch or commit the prototype unless the current request explicitly authorizes those history actions",
            "with its scratch path and observed output or artifact links",
            "<shelly-mode-skill-dir>/references/routed/swarm/workflow.md",
        ),
        forbidden_phrases=(
            "Keep the branch, the SHA, and the screenshots for Appendix A",
            "with the branch, the SHA, and the artifact links",
        ),
    ),
    CompatibilityCase(
        name="read-only-reviewer-containment",
        relative_path="skills/shelly-mode/references/codex-runtime.md",
        required_phrases=(
            "## Read-only worker branch",
            "codex --sandbox read-only --ask-for-approval never exec --ignore-user-config --ephemeral",
            "Never treat a no-edit prompt or an after-the-fact snapshot as containment",
            "The filesystem sandbox does not authorize external writes",
            "report the independent reviewer unavailable",
        ),
        forbidden_phrases=(
            "Otherwise state the no-edit boundary in the prompt",
            "`codex --help`",
            "`codex exec --help`",
        ),
    ),
    CompatibilityCase(
        name="shelly-mode-explicit-only-invocation",
        relative_path="skills/shelly-mode/SKILL.md",
        required_phrases=(
            "Use only for an explicit $shelly-stack:shelly-mode invocation",
        ),
        forbidden_phrases=(
            "Use for poteto",
            "requests to work in this style",
        ),
    ),
    CompatibilityCase(
        name="shipping-comment-authority",
        relative_path="skills/shelly-mode/playbooks/shipping.md",
        required_phrases=(
            "Keep the verdict in the current conversation by default",
            "Post it on the PR only when the current request explicitly authorizes PR comments",
            "A request to land or ship does not by itself authorize comments",
            "This verifier is not a read-only reviewer because live checks may create runtime artifacts",
            "reject its result if either check fails",
        ),
        forbidden_phrases=(
            "posts that verdict on its own PR",
            "Always post every verdict as a PR comment",
        ),
    ),
)

READ_ONLY_WORKFLOW_BRANCH_COUNTS = {
    "arena": 1,
    "blast-radius": 1,
    "how": 3,
    "interrogate": 1,
    "no-comments": 1,
    "reflect": 3,
    "show-me-your-work": 1,
    "why": 2,
}

FORBIDDEN_CODEX_PATTERNS = {
    r"~/.claude/(?:agents|plugins|projects|skills)": "Claude user paths",
    r"\.claude/(?:agents|plugins|projects|skills|worktrees)": "Claude project paths",
    r"\b(?:(?:claude-)?(?:fable|opus|sonnet|haiku)|grok-[\w.-]+)(?:-[\w.-]+)?\b": "non-Codex model names",
    r"\bsubagent_type\b": "Claude subagent_type",
    r"\bAgent (?:tool|call|calls)\b": "Claude Agent tool wording",
    r"\bWorkflow tool\b": "Claude Workflow tool wording",
    r"\b(?:AskUserQuestion|TodoWrite|ToolSearch)\b": "Claude tool names",
    r"\$ARGUMENTS\b": "Claude command arguments",
    r"(?<![\w.-])/(?:code-review|goal|loop)\b": "Claude slash commands",
    r"\bisolation\s*:": "Claude agent isolation option",
    r"\bmcp__claude": "Claude-specific connector name",
    r"\bCLAUDE_PLUGIN_ROOT\b|\$\{PLUGIN_ROOT\}": "non-native plugin root variable",
    r"\bCLAUDE\.local\.md\b": "Claude-only repository instructions",
    r"\btodolist\b": "Claude planning vocabulary",
    r"Read/Grep/Glob/Bash": "Claude tool allowlist",
    r"configured value is an agent name": "Claude custom-agent routing",
    r"``create_goal``": "malformed Codex goal reference",
    r"Claude Code restart": "Claude lifecycle wording",
    r"monitored-shell|output-notification sentinel": "Claude wait implementation",
    r"origin pr checks[^\n`]*`?\s*--watch": "unbounded Origin watcher",
    r"continuation branch": "undefined continuation abstraction",
    r"`/<handle>-mode`": "Claude-style generated skill invocation",
    r"git reset --hard": "destructive worktree reset",
    r"spawn_agent.*each get their own worktree": "automatic worktree claim",
    r"Use a worktree, branch, or `/tmp/swarm": "branch mistaken for worker isolation",
    r"tell it to check the branch out first": "parallel checkout in a shared workspace",
    r"git show origin/main:skills/": "consumer-repository lookup for plugin assets",
    r"`(?:Read|Shell|Grep|Glob|Bash)` tool calls|Use Read, Grep|\(Glob, Grep, Read\)|\bUse (?:Glob|Grep|Read) to\b": "Claude tool-name assumptions",
    r"agent store's|current agent's store|path in the system prompt": "unavailable implicit Codex store",
    r"\btask-list\b|\btask-read\b": "invented Codex task-history tool name",
    r"multiSelect|3-4 options": "unsupported request_user_input schema",
    r"scripts/(?:watch-pr/watch-pr|orch/orch\.ts)": "unresolved shared-runtime script path",
    r"git fetch origin main": "mutating fetch inside a read-only audit",
    r"#!/usr/bin/env bun|// @bun|\bBun\.spawn|import\.meta\.dir|install --frozen-lockfile": "Bun runtime dependency",
    r"Invoked at the end of every other playbook": "unconditional PR creation workflow",
    r"safe to drop": "unsafe assumption about untracked files",
    r"disposable untracked scratch": "unsafe assumption about untracked files",
    r"Spawn all N|Launch all reviewers|Spawn all explorers": "fan-out that ignores native capacity",
    r"Launch all matching investigators|three concurrent native `spawn_agent`": "fan-out that ignores native capacity",
    r"findings in the `spawn_agent` response body": "incorrect native spawn result handling",
    r"(?<![\w.-])skills/(?:shelly-mode|swarm|how|interrogate|show-me-your-work)/": "consumer-relative bundled skill path",
    r"Inject instrumentation via CDP|hotfix the live code|Write a script or test that runs the real code|run it as an `arena`": "mutation inside a read-only workflow",
    r"otherwise explicitly forbid (?:file )?edits? and verify the worktree afterward": "prompt-only reviewer containment",
    r"otherwise state that it must not edit files and verify the working tree afterward": "prompt-only reviewer containment",
    r"otherwise prompt it not to edit files": "prompt-only reviewer containment",
    r"For `drive`, (?:start|create|use) (?:a |the )?heartbeat": "heartbeat required for current-turn drive",
    r"(?:Always|must|should) post (?:every|each) verdict (?:as|on) (?:a |the )?PR comment": "unguarded verdict comment",
    r"(?:Create|Keep|Use) (?:a |the )?prototype (?:branch|commit)": "prototype history without an authority gate",
}


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


def text_files(root: Path) -> list[Path]:
    result: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        result.append(path)
    return result


def load_skill_frontmatter(path: Path) -> dict:
    contents = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n?", contents, flags=re.DOTALL)
    require(match is not None, f"generated skill has no YAML frontmatter: {path}")
    value = yaml.safe_load(match.group(1))
    require(isinstance(value, dict), f"generated skill frontmatter must be an object: {path}")
    return value


def explicit_source_skills() -> set[str]:
    result: set[str] = set()
    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        metadata = load_skill_frontmatter(path)
        if metadata.get("disable-model-invocation") or metadata.get("disable_model_invocation"):
            result.add(path.parent.name)
    return result


def validate_codex_structure(shared_skills: set[str]) -> None:
    allowed_top_level = {".codex-plugin", "skills", "LICENSE", "README.md"}
    actual_top_level = {path.name for path in CODEX_ROOT.iterdir()}
    require(
        actual_top_level == allowed_top_level,
        f"unexpected Codex package entries: {sorted(actual_top_level ^ allowed_top_level)}",
    )
    forbidden_directories = {".git", ".mypy_cache", ".pytest_cache", "__pycache__", "node_modules"}
    leaked_directories = sorted(
        path.relative_to(ROOT).as_posix()
        for path in CODEX_ROOT.rglob("*")
        if path.is_dir() and path.name in forbidden_directories
    )
    require(not leaked_directories, f"generated Codex package contains local artifacts: {leaked_directories}")
    runtime_scripts = CODEX_ROOT / "skills" / "shelly-mode" / "scripts"
    actual_runtime_files = {
        path.relative_to(runtime_scripts).as_posix()
        for path in runtime_scripts.rglob("*")
        if path.is_file()
    }
    expected_runtime_files = {
        "bin/orch.mjs",
        "bin/watch-pr.mjs",
        "check-plan.mjs",
        "worktree-audit.sh",
    }
    require(
        actual_runtime_files == expected_runtime_files,
        "Codex runtime helper inventory differs: "
        f"{sorted(actual_runtime_files ^ expected_runtime_files)}",
    )

    explicit_skills = explicit_source_skills()
    for skill_name in sorted(shared_skills):
        skill_dir = CODEX_ROOT / "skills" / skill_name
        metadata = load_skill_frontmatter(skill_dir / "SKILL.md")
        require(metadata.get("name") == skill_name, f"generated skill name mismatch: {skill_name}")
        require(
            isinstance(metadata.get("description"), str) and metadata["description"].strip(),
            f"generated skill description is missing: {skill_name}",
        )
        require(
            set(metadata) <= {"name", "description"},
            f"generated skill has non-native frontmatter fields: {skill_name}: {sorted(set(metadata) - {'name', 'description'})}",
        )

        policy_path = skill_dir / "agents" / "openai.yaml"
        if skill_name in explicit_skills:
            require(policy_path.is_file(), f"explicit-only skill lacks agents/openai.yaml: {skill_name}")
            policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
            require(isinstance(policy, dict), f"invalid agents/openai.yaml: {skill_name}")
            require(
                policy.get("policy", {}).get("allow_implicit_invocation") is False,
                f"explicit-only skill permits implicit invocation: {skill_name}",
            )
            interface = policy.get("interface", {})
            short_description = interface.get("short_description")
            require(
                isinstance(short_description, str)
                and 25 <= len(short_description) <= 64
                and (len(short_description) < 64 or short_description.endswith("Codex")),
                f"generated UI description is clipped or invalid: {skill_name}: {short_description!r}",
            )


def validate_codex_runtime_text(shared_skills: set[str]) -> None:
    violations: list[str] = []
    slash_skill_pattern = re.compile(
        r"(?<![\w$./-])/" + "(?:" + "|".join(map(re.escape, sorted(shared_skills))) + r")\b"
    )
    for path in text_files(CODEX_ROOT):
        contents = path.read_text(encoding="utf-8")
        for pattern, label in FORBIDDEN_CODEX_PATTERNS.items():
            if match := re.search(pattern, contents, flags=re.IGNORECASE):
                line = contents.count("\n", 0, match.start()) + 1
                violations.append(f"{path.relative_to(ROOT)}:{line}: {label}: {match.group(0)!r}")
        if match := slash_skill_pattern.search(contents):
            line = contents.count("\n", 0, match.start()) + 1
            violations.append(
                f"{path.relative_to(ROOT)}:{line}: Claude-style skill invocation: {match.group(0)!r}"
            )
    require(
        not violations,
        "Codex package contains non-native runtime instructions:\n  " + "\n  ".join(violations),
    )


def validate_runtime_tools() -> None:
    mode_root = CODEX_ROOT / "skills" / "shelly-mode"
    scripts = mode_root / "scripts" / "bin"
    for name in ("orch.mjs", "watch-pr.mjs"):
        result = subprocess.run(
            ["node", str(scripts / name), "--help"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        require(result.returncode == 0, f"bundled Node helper failed: {name}: {result.stderr}")
    runtime = (mode_root / "references" / "codex-runtime.md").read_text(encoding="utf-8")
    require(
        "executable Node helpers" in runtime
        and "<shelly-mode-skill-dir>/scripts/bin/" in runtime
        and "other dependency-free helpers live directly under `<shelly-mode-skill-dir>/scripts/`"
        in runtime,
        "Codex runtime contract must describe both helper locations",
    )


def validate_plan_template() -> None:
    playbook = (
        CODEX_ROOT / "skills" / "shelly-mode" / "playbooks" / "multi-phase-plan.md"
    ).read_text(encoding="utf-8")
    match = re.search(r"````markdown\n(.*?)\n````", playbook, flags=re.DOTALL)
    require(match is not None, "Codex multi-phase plan has no fenced plan template")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", encoding="utf-8") as plan:
        plan.write(match.group(1))
        plan.flush()
        result = subprocess.run(
            [
                "node",
                str(CODEX_ROOT / "skills" / "shelly-mode" / "scripts" / "check-plan.mjs"),
                plan.name,
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    require(
        result.returncode == 0,
        "generated Codex plan template fails its checker:\n" + result.stdout + result.stderr,
    )
    template = match.group(1)
    require(
        "../references/routed/" not in template
        and "../references/bugbot-triage.md" not in template
        and "./shipping.md" not in template
        and "$shelly-stack:" not in template
        and not re.search(r"(?<![\w.-])skills/(?:shelly-mode|swarm|how|interrogate|show-me-your-work)/", template),
        "generated Codex plan template contains a route that breaks after the plan is copied",
    )


def validate_codex_compatibility_cases() -> None:
    failures: list[str] = []
    for case in CODEX_COMPATIBILITY_CASES:
        path = CODEX_ROOT / case.relative_path
        contents = path.read_text(encoding="utf-8")
        for phrase in case.required_phrases:
            if phrase not in contents:
                failures.append(f"{case.name}: missing {phrase!r} in {case.relative_path}")
        for phrase in case.forbidden_phrases:
            if phrase in contents:
                failures.append(f"{case.name}: retained {phrase!r} in {case.relative_path}")

    branch_phrase = "native runtime contract's read-only worker branch"
    for skill_name, expected_count in READ_ONLY_WORKFLOW_BRANCH_COUNTS.items():
        path = CODEX_ROOT / "skills" / skill_name / "SKILL.md"
        actual_count = path.read_text(encoding="utf-8").count(branch_phrase)
        if actual_count != expected_count:
            failures.append(
                "read-only-reviewer-containment: "
                f"{skill_name} has {actual_count} enforced routes, expected {expected_count}"
            )

    policy_path = CODEX_ROOT / "skills" / "shelly-mode" / "agents" / "openai.yaml"
    if not policy_path.is_file():
        failures.append(
            "shelly-mode-explicit-only-invocation: missing agents/openai.yaml"
        )
    else:
        policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
        if not isinstance(policy, dict) or policy.get("policy", {}).get("allow_implicit_invocation") is not False:
            failures.append(
                "shelly-mode-explicit-only-invocation: policy does not disable implicit invocation"
            )

    comment_prompt = (
        CODEX_ROOT / "skills" / "no-comments" / "references" / "comment-sicko.md"
    ).read_text(encoding="utf-8")
    if (
        "NEEDS HOW OR WHY PROOF" not in comment_prompt
        or "$shelly-stack:how" in comment_prompt
        or "$shelly-stack:why" in comment_prompt
    ):
        failures.append(
            "read-only-reviewer-containment: Comment Sicko must return nested analysis to the parent"
        )

    require(
        not failures,
        "Codex compatibility contract failed:\n  " + "\n  ".join(failures),
    )


def skill_body_without_runtime_notice(path: Path) -> str:
    contents = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n.*?\n---\n?", contents, flags=re.DOTALL)
    require(match is not None, f"generated skill has no frontmatter: {path}")
    body = contents[match.end() :].lstrip("\n")
    require(body.startswith("> **Codex runtime:**"), f"generated skill lacks runtime notice: {path}")
    _, separator, body = body.partition("\n\n")
    require(bool(separator), f"generated skill has malformed runtime notice: {path}")
    return body.lstrip()


def markdown_without_link_targets(contents: str) -> str:
    return re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", contents)


def routed_workflow_link_for_validation(
    current_path: Path,
    routed_root: Path,
    skill_name: str,
) -> str:
    target = routed_root / skill_name / "workflow.md"
    return Path(os.path.relpath(target, current_path.parent)).as_posix()


def validate_shelly_mode_routes(shared_skills: set[str]) -> None:
    route_names = set(SHELLY_MODE_ROUTED_SKILLS)
    route_names.update(name for name in shared_skills if name.startswith("principle-"))
    missing_sources = sorted(route_names - shared_skills)
    require(not missing_sources, f"Shelly Mode route targets are missing: {missing_sources}")

    mode_root = CODEX_ROOT / "skills" / "shelly-mode"
    routed_root = mode_root / "references" / "routed"
    actual_routes = {path.name for path in routed_root.iterdir() if path.is_dir()}
    require(
        actual_routes == route_names,
        f"Shelly Mode routed workflow inventory differs: {sorted(actual_routes ^ route_names)}",
    )

    mode = (mode_root / "SKILL.md").read_text(encoding="utf-8")
    require(
        "## Internal routing" in mode
        and "Do not depend on sibling-skill discovery" in mode,
        "Shelly Mode must define its explicit umbrella routing contract",
    )

    for name in sorted(route_names):
        source_root = CODEX_ROOT / "skills" / name
        route_root = routed_root / name
        workflow = route_root / "workflow.md"
        require(workflow.is_file(), f"Shelly Mode route lacks workflow.md: {name}")
        require(
            not workflow.read_text(encoding="utf-8").startswith("---\n"),
            f"Shelly Mode route retained nested skill frontmatter: {name}",
        )
        require(
            not (route_root / "agents").exists(),
            f"Shelly Mode route copied standalone invocation policy: {name}",
        )

        expected_support = {
            path.relative_to(source_root).as_posix()
            for path in source_root.rglob("*")
            if path.is_file()
            and path.name != "SKILL.md"
            and path.relative_to(source_root).parts[0] != "agents"
        }
        actual_support = {
            path.relative_to(route_root).as_posix()
            for path in route_root.rglob("*")
            if path.is_file() and path.name != "workflow.md"
        }
        require(
            actual_support == expected_support,
            f"Shelly Mode route support inventory differs for {name}: "
            f"{sorted(actual_support ^ expected_support)}",
        )

        expected_body = markdown_without_link_targets(
            skill_body_without_runtime_notice(source_root / "SKILL.md")
        )
        actual_body = markdown_without_link_targets(
            workflow.read_text(encoding="utf-8")
        )
        require(actual_body == expected_body, f"Shelly Mode route body drifted: {name}")

        for relative in sorted(expected_support):
            source = source_root / relative
            routed = route_root / relative
            if source.suffix == ".md":
                require(
                    markdown_without_link_targets(routed.read_text(encoding="utf-8"))
                    == markdown_without_link_targets(source.read_text(encoding="utf-8")),
                    f"Shelly Mode route reference drifted: {name}/{relative}",
                )
            else:
                require(
                    routed.read_bytes() == source.read_bytes(),
                    f"Shelly Mode route support file drifted: {name}/{relative}",
                )

    principles = sorted(name for name in route_names if name.startswith("principle-"))
    for name in principles:
        require(
            f"references/routed/{name}/workflow.md" in mode,
            f"Shelly Mode principle lacks a direct routed link: {name}",
        )

    mode_markdown_paths = sorted(
        {mode_root / "SKILL.md", *mode_root.rglob("*.md")}
    )
    principle_aliases = {
        name.removeprefix("principle-"): name for name in principles
    }
    for path in mode_markdown_paths:
        contents = path.read_text(encoding="utf-8")
        for alias in sorted(principle_aliases):
            require(
                f"**{alias}**" not in contents,
                f"Shelly Mode contains an unlinked principle route: {path}: {alias}",
            )
        for match in re.finditer(r"`\$shelly-stack:([a-z0-9-]+)[^`]*`", contents):
            name = match.group(1)
            if name not in route_names:
                continue
            expected_link = routed_workflow_link_for_validation(path, routed_root, name)
            require(
                match.start() > 0
                and contents[match.start() - 1] == "["
                and contents.startswith(f"]({expected_link})", match.end()),
                f"Shelly Mode contains an unlinked routed skill invocation: {path}: {name}",
            )
        for label, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", contents):
            local_target = target.split("#", 1)[0]
            if not local_target or "://" in local_target or local_target.startswith(("#", "/", "<")):
                continue
            resolved = (path.parent / local_target).resolve()
            try:
                route_name = resolved.relative_to(routed_root.resolve()).parts[0]
            except (ValueError, IndexError):
                continue
            if route_name not in route_names:
                continue
            try:
                current_route = path.resolve().relative_to(routed_root.resolve()).parts[0]
            except (ValueError, IndexError):
                current_route = None
            if current_route == route_name:
                continue
            route_alias = route_name.removeprefix("principle-")
            normalized_label = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
            require(
                route_name in normalized_label or route_alias in normalized_label,
                f"Shelly Mode routed label points to the wrong workflow: {path}: {label!r} -> {route_name}",
            )

    playbooks = mode_root / "playbooks"
    actual_playbooks = {path.name for path in playbooks.glob("*.md")}
    listed_playbooks = set(re.findall(r"`playbooks/([a-z0-9-]+\.md)`", mode))
    require(
        listed_playbooks == actual_playbooks,
        "Shelly Mode playbook inventory differs from its entrypoint: "
        f"{sorted(listed_playbooks ^ actual_playbooks)}",
    )
    for path in sorted(playbooks.glob("*.md")):
        contents = path.read_text(encoding="utf-8")
        stale = re.findall(r"(?<![/\w.-])playbooks/([a-z0-9-]+\.md)", contents)
        require(not stale, f"playbook contains a broken nested playbook path: {path}: {stale}")
        for target in re.findall(r"`\./([a-z0-9-]+\.md)`", contents):
            require((playbooks / target).is_file(), f"playbook link does not resolve: {path}: {target}")

    for path in mode_markdown_paths:
        contents = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", contents):
            local_target = target.split("#", 1)[0]
            if not local_target or "://" in local_target or local_target.startswith(("#", "/", "<")):
                continue
            if not Path(local_target).suffix:
                continue
            require(
                (path.parent / local_target).resolve().exists(),
                f"local Markdown link does not resolve: {path}: {target}",
            )


def validate_optional_capabilities() -> None:
    runtime_path = CODEX_ROOT / "skills" / "shelly-mode" / "references" / "codex-runtime.md"
    runtime = runtime_path.read_text(encoding="utf-8")
    for phrase in (
        "Inspect the current tool schema before choosing a planning mechanism",
        "If `update_plan` is exposed",
        "numbered checklist in commentary",
        "Never replace an ordinary plan with a persistent goal",
        "call `get_goal` first",
        "call `create_goal`",
        "Call `update_goal` only when the objective is genuinely complete",
        "Use `wait_threads` only when the current schema exposes it",
        "future or cross-turn recurrence requires and authorizes an exposed heartbeat automation",
        "perform one bounded pass and report that persistent monitoring is unavailable",
        "use `create_thread` only if the current schema exposes it",
        "Codex needs no special loop command to continue work in the active turn",
        "poll that session with waits no longer than 60 seconds",
        "rerun a bounded status command instead of inventing a background loop",
    ):
        require(phrase in runtime, f"Codex optional-capability contract is missing: {phrase}")
    require(
        runtime.index("`get_goal`") < runtime.index("`create_goal`") < runtime.index("`update_goal`"),
        "Codex persistent-goal contract must order get, create, then terminal update",
    )

    mode_root = CODEX_ROOT / "skills" / "shelly-mode"
    operational_paths = [
        mode_root / "SKILL.md",
        *sorted((mode_root / "playbooks").glob("*.md")),
        *sorted((mode_root / "references" / "routed").rglob("*.md")),
    ]
    operational_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in operational_paths
    )
    for token in ("`update_plan`", "`create_goal`", "create a Codex heartbeat", "create or update a Codex heartbeat"):
        require(token not in operational_text, f"Shelly Mode bypasses optional-capability contract: {token}")


def validate_external_tool_preflight() -> None:
    runtime = (
        CODEX_ROOT / "skills" / "shelly-mode" / "references" / "codex-runtime.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "Before using an external CLI, MCP connector, or browser driver",
        "confirm that the current session exposes it",
        "Use `gh` or another forge only after its executable, repository access, and authentication pass",
        "Never report `PASS` from a proxy check",
        "Use `codex review` only after `command -v codex` succeeds",
    ):
        require(phrase in runtime, f"Codex external-tool contract is missing: {phrase}")

    playbooks = CODEX_ROOT / "skills" / "shelly-mode" / "playbooks"
    for filename in sorted(FORGE_PLAYBOOKS):
        contents = (playbooks / filename).read_text(encoding="utf-8")
        for phrase in (
            "command -v gh",
            "gh auth status",
            "gh repo view --json nameWithOwner",
            "stop before the first PR operation",
        ):
            require(phrase in contents, f"Codex {filename} lacks forge preflight: {phrase}")
    orchestrate = (playbooks / "orchestrate.md").read_text(encoding="utf-8")
    require(
        "frontier commands are GitHub-only" in orchestrate
        and "Do not substitute Origin until `orch` supports it" in orchestrate,
        "Codex orchestrate must state its GitHub-only forge dependency",
    )

    why = (CODEX_ROOT / "skills" / "why" / "SKILL.md").read_text(encoding="utf-8")
    require(
        "Local `git` history is the baseline" in why
        and "report PR evidence as an unsearched gap" in why
        and "Source control is always available through git and `gh`" not in why,
        "Codex why must degrade to local history when remote forge access is unavailable",
    )
    require(
        "mcp__codex_apps__<connector>_<tool>" in why
        and "Never collapse all `codex_apps` tools into one connector" in why
        and "If the current schema exposes lazy tool discovery" in why
        and "distinct `<server>` segments are the enabled MCP servers" not in why,
        "Codex why must distinguish product connectors that share the codex_apps server",
    )
    why_preflight = "Before pulling PR bodies, require `command -v gh`"
    require(
        why_preflight in why
        and "gh repo view --json nameWithOwner" in why
        and why.index(why_preflight) < why.index("gh pr view <number>"),
        "Codex why must preflight GitHub before its first remote query",
    )
    why_references = CODEX_ROOT / "skills" / "why" / "references"
    code_archaeology = (why_references / "sources" / "code-archaeology.md").read_text(
        encoding="utf-8"
    )
    require(
        "gh repo view --json nameWithOwner" in code_archaeology
        and code_archaeology.index("gh repo view --json nameWithOwner")
        < code_archaeology.index("gh pr view <number>"),
        "Codex why source playbook must preflight GitHub before PR lookup",
    )
    synthesizer = (why_references / "synthesizer-prompt.md").read_text(encoding="utf-8")
    require(
        "git and `gh` are always expected" not in synthesizer
        and "repository-access preflight" in synthesizer,
        "Codex why synthesizer must report unavailable source-control evidence honestly",
    )

    worktree_audit = (
        CODEX_ROOT / "skills" / "shelly-mode" / "scripts" / "worktree-audit.sh"
    ).read_text(encoding="utf-8")
    for phrase in (
        "command -v gh",
        "command -v jq",
        "gh auth status",
        "gh repo view --json nameWithOwner",
        "pr_check=unavailable",
        "no worktree can be classified safe",
        "review-unverified-pr",
    ):
        require(phrase in worktree_audit, f"Codex worktree audit lacks safe PR fallback: {phrase}")
    cleanup = (playbooks / "worktree-cleanup.md").read_text(encoding="utf-8")
    require(
        "If `PR_CHECK` is not `verified`" in cleanup
        and "never propose deletion" in cleanup,
        "Codex worktree cleanup must reject unverified PR evidence",
    )

    ticket = (CODEX_ROOT / "skills" / "ticket" / "SKILL.md").read_text(encoding="utf-8")
    require(
        "If none is available, stop before any Linear-dependent read or write" in ticket,
        "Codex ticket must stop before Linear work when no connector is available",
    )


def validate_authorization_and_runtime_contracts() -> None:
    runtime_contract = (
        CODEX_ROOT / "skills" / "shelly-mode" / "references" / "codex-runtime.md"
    ).read_text(encoding="utf-8")
    require(
        "fork_turns: \"none\"" in runtime_contract
        and "A full-history fork" in runtime_contract,
        "Codex model overrides must require a non-all fork_turns value",
    )
    require(
        "`list_agents`" in runtime_contract
        and "separately delivered terminal or final-status message" in runtime_contract,
        "Codex runtime must define capacity inspection and terminal-result collection",
    )
    require(
        "Local edits do not imply commit authority" in runtime_contract,
        "Codex runtime must separate local edits from commit authority",
    )

    ordinary_workflows = {
        "feature.md": ("explicitly authorizes commits", "explicitly authorizes PR creation"),
        "bug-fix.md": ("commits are explicitly authorized", "explicitly authorizes PR creation"),
        "refactoring.md": ("commits and rebases are explicitly authorized", "PR creation and pushing are explicitly authorized"),
        "hillclimb.md": ("commits are explicitly authorized", "explicitly authorizes PR creation"),
        "autonomous-run.md": ("only when commits are authorized", "explicitly authorizes PR creation"),
        "pause-safely.md": ("If commits are explicitly authorized", "preserve the dirty tree"),
    }
    playbooks = CODEX_ROOT / "skills" / "shelly-mode" / "playbooks"
    for filename, required_phrases in ordinary_workflows.items():
        contents = (playbooks / filename).read_text(encoding="utf-8")
        for phrase in required_phrases:
            require(phrase in contents, f"Codex {filename} lacks authority gate: {phrase}")

    mode = (CODEX_ROOT / "skills" / "shelly-mode" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    require(
        "Local edits do not authorize commits, rebases, or history rewrites" in mode
        and "Include a PR link only when the authorized workflow" in mode,
        "Codex Shelly Mode must gate history writes and conditional PR links",
    )

    for skill_name in (
        "architect",
        "figure-it-out",
        "principle-build-the-lever",
        "principle-prove-it-works",
        "principle-sequence-verifiable-units",
        "show-me-your-work",
    ):
        contents = (CODEX_ROOT / "skills" / skill_name / "SKILL.md").read_text(
            encoding="utf-8"
        )
        require(
            "authoriz" in contents.lower() and "commit" in contents.lower(),
            f"Codex {skill_name} must preserve commit authorization",
        )

    blast_radius = (CODEX_ROOT / "skills" / "blast-radius" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    require(
        "Do not write a script or test during the review" in blast_radius
        and "bounded read-only reviewer subagents" in blast_radius,
        "Codex blast-radius review must remain read-only",
    )
    runtime_forensics = (playbooks / "runtime-forensics.md").read_text(encoding="utf-8")
    require(
        "Do not inject code" in runtime_forensics
        and "mutate runtime state" in runtime_forensics,
        "Codex runtime forensics must remain read-only",
    )

    why = (CODEX_ROOT / "skills" / "why" / "SKILL.md").read_text(encoding="utf-8")
    reflect = (CODEX_ROOT / "skills" / "reflect" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    require(
        "Call `list_agents` before fan-out" in why and "refill a rolling window" in why,
        "Codex why investigators must respect native child capacity",
    )
    require(
        "run three contained reviewer workers in total" in reflect
        and "refill a rolling window" in reflect
        and "initial `spawn_agent` result is only the agent handle" in reflect
        and "native runtime contract's read-only worker branch" in reflect,
        "Codex reflect must use bounded spawns and terminal mailbox results",
    )

    babysit = (playbooks / "babysit.md").read_text(encoding="utf-8")
    require(
        "Always pass `--status-only`" in babysit
        and "explicit positive `--timeout <seconds>`" in babysit
        and "no greater than 60" in babysit
        and "unbounded default timeout" in babysit,
        "Codex PR watcher instructions must require a bounded invocation",
    )
    require(
        "On Origin, do not run the GitHub-only helper" in babysit
        and "origin pr view <pr> --checks --comments" in babysit
        and "origin pr thread list <pr>" in babysit,
        "Codex babysit must use Origin-native status checks when Origin is selected",
    )
    shipping = (playbooks / "shipping.md").read_text(encoding="utf-8")
    require(
        "If a previous agent armed an upstack PR and GitHub is the resolved forge" in shipping
        and "this playbook has no verified Origin disarm command" in shipping
        and "must not fall back to `gh` after selecting Origin" in shipping,
        "Codex shipping must fail closed when Origin cannot disarm an upstack PR",
    )
    require(
        "origin pr thread list <pr>` once per bounded status pass" in shipping
        and "Do not use Origin's unbounded `--watch` mode" in shipping
        and "`--timeout <seconds>` no greater than 60" in shipping,
        "Codex shipping must bound both Origin and GitHub status waits",
    )
    autopilot_stack = (playbooks / "autopilot-stack.md").read_text(encoding="utf-8")
    require(
        "authenticated read-only `origin pr list`" in autopilot_stack
        and "head branch, and head SHA fields" in autopilot_stack
        and "never substitute GitHub state after selecting Origin" in autopilot_stack,
        "Codex autopilot stack must resolve topology through the selected forge",
    )
    orchestrate = (playbooks / "orchestrate.md").read_text(encoding="utf-8")
    require(
        "GitHub or review-thread comment" in orchestrate
        and "GitHub comments, review-thread replies" in orchestrate,
        "Codex orchestrate must gate comments and messages as external writes",
    )
    plan = (playbooks / "multi-phase-plan.md").read_text(encoding="utf-8")
    require(
        "`<shelly-mode-skill-dir>/playbooks/<execution playbook>.md`" in plan
        and "`<shelly-mode-skill-dir>/references/routed/swarm/workflow.md`" in plan
        and "`<shelly-mode-skill-dir>/references/routed/show-me-your-work/workflow.md`" in plan,
        "Codex plan template must resolve installed plugin skills natively",
    )
    ticket = (CODEX_ROOT / "skills" / "ticket" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    require(
        "ending at merge-ready unless the user explicitly asks to merge" in ticket
        and "Run this flow only when the current user request explicitly asks to file follow-ups" in ticket,
        "Codex ticket workflow must gate merge and follow-up issue creation",
    )


def main() -> None:
    claude_manifest = load_json(ROOT / ".claude-plugin" / "plugin.json")
    codex_manifest = load_json(CODEX_ROOT / ".codex-plugin" / "plugin.json")
    codex_template = load_json(ROOT / "codex" / "plugin.template.json")
    require(claude_manifest.get("name") == PLUGIN_NAME, "unexpected Claude plugin name")
    require(codex_manifest.get("name") == PLUGIN_NAME, "unexpected Codex plugin name")
    require(
        codex_template.get("version") == codex_manifest.get("version"),
        "generated Codex version must match the Codex template",
    )
    require(
        isinstance(codex_manifest.get("version"), str)
        and re.fullmatch(
            r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)",
            codex_manifest["version"],
        ),
        "generated Codex version must use strict MAJOR.MINOR.PATCH semver",
    )
    require(codex_manifest.get("skills") == "./skills/", "Codex manifest must expose ./skills/")

    claude_marketplace = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    codex_marketplace = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
    for client, marketplace in (
        ("Claude", claude_marketplace),
        ("Codex", codex_marketplace),
    ):
        require(marketplace.get("name") == PLUGIN_NAME, f"{client} marketplace name must match")
        plugins = marketplace.get("plugins")
        require(
            isinstance(plugins, list) and {entry.get("name") for entry in plugins} == {PLUGIN_NAME, "shelly-team-kit"} and len(plugins) == 2,
            f"{client} marketplace must contain Shelly Stack and Shelly Team Kit once each",
        )
        require(plugins[0].get("name") == PLUGIN_NAME, f"{client} plugin entry must match")

    codex_source = codex_marketplace["plugins"][0].get("source")
    require(
        codex_source == {"source": "local", "path": "./plugins/shelly-stack"},
        "Codex marketplace must point at the generated runtime projection",
    )

    shared_skills = skill_names(ROOT / "skills")
    codex_skills = skill_names(CODEX_ROOT / "skills")
    require(shared_skills == codex_skills, "Claude and Codex skill inventories differ")
    require(not (CODEX_ROOT / "agents").exists(), "Codex package must not copy Claude agents")
    require(not (CODEX_ROOT / "docs").exists(), "Codex package must not copy Claude guide pages")
    validate_codex_structure(shared_skills)

    runtime_notice = "> **Codex runtime:** Follow the [native runtime contract]"
    for skill_path in sorted((CODEX_ROOT / "skills").glob("*/SKILL.md")):
        require(
            runtime_notice in skill_path.read_text(encoding="utf-8"),
            f"generated skill lacks the native Codex runtime contract: {skill_path}",
        )

    claude_setup = (ROOT / "skills" / "setup-shelly-stack" / "SKILL.md").read_text(encoding="utf-8")
    codex_setup = (
        CODEX_ROOT / "skills" / "setup-shelly-stack" / "SKILL.md"
    ).read_text(encoding="utf-8")
    require(
        "~/.claude/rules/shelly-stack-models.md" in claude_setup,
        "Claude setup path is missing",
    )
    require("~/.codex/shelly-stack-models.md" in codex_setup, "Codex setup path is missing")
    require(
        "Never read or change `~/.claude/rules/shelly-stack-models.md`" in codex_setup,
        "Codex setup must protect Claude configuration",
    )
    require(
        "reasoning_effort" in codex_setup,
        "Codex setup must configure native reasoning effort as well as model",
    )

    codex_automate = (CODEX_ROOT / "skills" / "automate-me" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    require(
        "`$<handle>-mode`" in codex_automate,
        "Codex automate-me must teach native dollar-prefixed skill invocation",
    )
    require(
        "agents/openai.yaml" in codex_automate
        and "policy.allow_implicit_invocation: false" in codex_automate,
        "Codex automate-me must teach native explicit-only policy",
    )
    require(
        "Frontmatter `disable-model-invocation" not in codex_automate,
        "Codex automate-me must not teach Claude-only frontmatter",
    )
    require(
        "two or three mutually exclusive options" in codex_automate
        and "has no multi-select field" in codex_automate
        and "If the tool is unavailable" in codex_automate,
        "Codex automate-me must honor request_user_input's schema and availability",
    )

    codex_orchestrate = (
        CODEX_ROOT / "skills" / "shelly-mode" / "playbooks" / "orchestrate.md"
    ).read_text(encoding="utf-8")
    require(
        "--store ~/.codex/shelly-stack/orchestrate/<project-slug>" in codex_orchestrate,
        "Codex orchestrate must pass an explicit durable store path",
    )
    require(
        "Before any push, PR creation or retarget, GitHub or review-thread comment" in codex_orchestrate,
        "Codex orchestrate must preserve external-write authorization",
    )

    codex_mode = (CODEX_ROOT / "skills" / "shelly-mode" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    require(
        "**External writes need authority.**" in codex_mode
        and "These phrases change persistence, not authorization." in codex_mode,
        "Codex Shelly Mode must separate autonomy from authorization",
    )
    require(
        "**Disk usage audit.**" in codex_mode
        and "audit-only mode" in codex_mode
        and "confirmation of the exact targets" in codex_mode,
        "Codex Shelly Mode must separate disk audit from destructive cleanup",
    )

    opening = (
        CODEX_ROOT / "skills" / "shelly-mode" / "playbooks" / "opening-a-pr.md"
    ).read_text(encoding="utf-8")
    require(
        "only when the current user request explicitly authorizes" in opening,
        "Codex PR playbook must require explicit creation and push authority",
    )
    cleanup = (
        CODEX_ROOT / "skills" / "shelly-mode" / "playbooks" / "worktree-cleanup.md"
    ).read_text(encoding="utf-8")
    require(
        "A request such as \"what's using my disk\" is read-only" in cleanup
        and "Never call untracked files throwaway" in cleanup
        and "obtain explicit confirmation of that exact set" in cleanup,
        "Codex cleanup playbook must gate exact destructive targets",
    )

    validate_optional_capabilities()
    validate_external_tool_preflight()
    validate_shelly_mode_routes(shared_skills)
    validate_codex_runtime_text(shared_skills)
    validate_runtime_tools()
    validate_plan_template()
    validate_codex_compatibility_cases()
    validate_authorization_and_runtime_contracts()

    print(
        f"Validated {len(shared_skills)} shared skills: Claude {claude_manifest['version']} "
        f"and native Codex {codex_manifest['version']}"
    )


if __name__ == "__main__":
    main()
