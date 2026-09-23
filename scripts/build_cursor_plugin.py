#!/usr/bin/env python3
"""Build the Cursor Shelly Stack plugin from shared workflow sources."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "plugins" / "shelly-stack-cursor"
INSTALL_TARGET = Path.home() / ".cursor" / "plugins" / "local" / "shelly-stack"
SKILLS_SOURCE = ROOT / "skills"
OVERRIDES = ROOT / "cursor" / "overrides"
OVERRIDE_FILE_LIST = ROOT / "cursor" / "override-files.txt"
MANIFEST_TEMPLATE = ROOT / "cursor" / "plugin.template.json"
CLAUDE_MANIFEST = ROOT / ".claude-plugin" / "plugin.json"

# Cursor ships a built-in create-skill; bundling a same-named skill would shadow it.
EXCLUDED_SKILLS = {"create-skill"}
# Pinned shelly-<model>-<effort> agents exist because Claude's Agent call takes aliases only.
# Cursor's Task call takes a full model slug, so only the two prompt agents ship.
AGENTS = ("shelly-agent.md", "comment-sicko.md")

MODEL_ALIASES = {
    "fable": "claude-fable-5-1-thinking-high",
    "opus": "claude-opus-5-5-high",
    "sonnet": "cursor-grok-4.6-high-fast",
    "haiku": "claude-4.5-haiku-thinking",
}

PLUGIN_DIR_NOTE = (
    "`<shelly-stack-plugin-dir>` is the installed plugin directory, the one holding "
    "`.cursor-plugin/plugin.json`; resolve it from the path of the SKILL.md you read "
    "(locally `~/.cursor/plugins/local/shelly-stack`)"
)

# Applied in order to every text file. Later entries must not re-match earlier output.
LITERAL_REPLACEMENTS = (
    ('subagent_type: "shelly-stack:shelly-agent"', 'subagent_type: "shelly-agent"'),
    ("shelly-stack:shelly-agent", "shelly-agent"),
    ('subagent_type: "shelly-stack:comment-sicko"', 'subagent_type: "Comment Sicko"'),
    ("shelly-stack:comment-sicko", "Comment Sicko"),
    ("~/.claude/rules/shelly-stack-models.md", "~/.cursor/rules/shelly-stack-models.mdc"),
    ("~/.claude/skills/", "~/.cursor/skills/"),
    ("~/.claude/plugins/", "~/.cursor/plugins/"),
    (".claude/skills/", ".cursor/skills/"),
    (".claude/worktrees/", ".cursor/worktrees/"),
    ("~/.claude/projects/*/", "~/.cursor/projects/*/"),
    ("general-purpose", "generalPurpose"),
    ("AskUserQuestion", "AskQuestion"),
    ("multiSelect: true", "allow_multiple: true"),
    ("3-4 options each (AskQuestion caps at four)", "4-6 options each"),
    ("`Agent` calls", "`Task` calls"),
    ("`Agent` call", "`Task` call"),
    ("`Agent` response body", "`Task` response body"),
    ("`Agent` prompts", "`Task` prompts"),
    ("the Agent tool", "the `Task` tool"),
    ("Agent tool", "`Task` tool"),
    ("an Agent subagent", "a `Task` subagent"),
    ("Agent subagent", "`Task` subagent"),
    ("Agent `model`", "Task `model`"),
    (
        "`tools`: read-only (give it only Read/Grep/Glob/Bash)",
        "read-only posture: the prompt forbids file writes (Cursor's `Task` has no tool allowlist, so MCP stays available)",
    ),
    (
        "Spawn one read-only judge subagent (give it only Read/Grep/Glob/Bash) on that model.",
        "Spawn one judge subagent on that model with a prompt that forbids writes.",
    ),
    (
        "- `tools`: read-write, with the MCP tools left in. **Do not hand these investigators a read-only tool list.** It strips MCP access, which disables MCP-backed investigators entirely. The source control investigator would be safe read-only, but keep the tool list uniform.",
        "- `subagent_type: generalPurpose`, not `explore`. **Do not use the `explore` subagent for these investigators.** It strips MCP access, which disables MCP-backed investigators entirely. The source control investigator would be safe in `explore`, but keep the types uniform.",
    ),
    (
        "- `tools`: read-write, with the MCP tools left in. The synthesizer's quality check spot-verifies citations, which can require MCP access. A read-only tool list strips the MCPs and defeats that.",
        "- `subagent_type: generalPurpose`. The synthesizer's quality check spot-verifies citations, which can require MCP access. The `explore` subagent strips MCPs and defeats that.",
    ),
    ("read-write with the MCP tools left in", "`generalPurpose` with MCP access"),
    ("a read-only tool list strips the MCPs", "the `explore` subagent strips MCPs"),
    ("`/code-review medium`", "`/review-bugbot`"),
    ("`/code-review` findings and review-bot comments", "Bugbot findings and review-bot comments"),
    ("`/code-review` findings triaged", "Bugbot findings triaged"),
    ("Claude Code restart", "Cursor restart"),
    ("restart Claude Code", "restart Cursor"),
    ("Claude Code's `/loop`", "Cursor's `/loop`"),
    ("`$ARGUMENTS`", "the user's request"),
    ("$ARGUMENTS", "the user's request"),
    (
        "the **create-skill** skill (the bundled skill for authoring SKILL.md files)",
        "Cursor's built-in `create-skill` skill",
    ),
    ("the **create-skill** skill", "Cursor's built-in `create-skill` skill"),
    ("per the repo's `CLAUDE.local.md`", "per the repo's `AGENTS.md` and `.cursor/rules/`"),
    (
        'in its own git worktree (`isolation: "worktree"`)',
        "in its own git worktree (`subagent_type: best-of-n-runner`)",
    ),
    (
        'in its own git worktree on this machine (`isolation: "worktree"`)',
        "in its own git worktree on this machine (`subagent_type: best-of-n-runner`)",
    ),
    ("Spawn `Agent` with `subagent_type:", "Spawn a `Task` subagent with `subagent_type:"),
    ('"/code-review flagged regex backtracking', '"Bugbot flagged regex backtracking'),
    (" (or `subagent_type` when the configured value is an agent name; see below)", ""),
    ("`inherit` is valid: omit `model` for it.", "`inherit-parent` and `auto` are valid: omit `model` for them."),
    ("a role line of `inherit` runs", "a role line of `inherit-parent` or `auto` runs"),
    ("Set a role to `inherit` and", "Set a role to `inherit-parent` or `auto` and"),
    ("`inherit` is not a model value", "Neither alias is a model value"),
    ("`inherit` means the session's model", "`inherit-parent` or `auto` means the session's model"),
    ("treating `inherit` as a model name", "treating `inherit-parent` or `auto` as a model name"),
    ("**Treating `inherit` as a model value.** `inherit` means", "**Treating `inherit-parent` or `auto` as a model value.** Each means"),
)

# Global regexes. Applied after the literals.
REGEX_REPLACEMENTS = (
    # The Claude-only "configured role value is an alias or a user agent" paragraph.
    (
        r"\s*A configured role value is either an (?:Agent|Task) `model` alias \(`fable`, `opus`, `sonnet`, `haiku`\) or the name of a user agent under `~/\.claude/agents/`.*?(?:for that spawn\.|gets its own agent file\.)",
        "",
    ),
    (
        r"Transcripts live at `~/\.claude/projects/<slug>/<uuid>\.jsonl`, where `<slug>` is the workspace path with each \"/\" turned into \"-\", including the leading one \(so `/Users/you/proj` becomes `-Users-you-proj`\)\. Subagent transcripts sit beside it in `<uuid>/subagents/` and tool results in `<uuid>/tool-results/`\.",
        "Transcripts live in the active workspace's `agent-transcripts/` directory named in the system prompt, as `<uuid>.jsonl` or `<uuid>/<uuid>.jsonl`. Subagent transcripts sit beside them in `<uuid>/subagents/`.",
    ),
    (
        r"Derive the (?:active workspace's transcript )?directory from the current working directory: `~/\.claude/projects/<slug>/`, where `<slug>` is the workspace path with every `/` turned into `-`, including the leading one \(`/Users/you/proj` → `-Users-you-proj`\)[;.] ?[Uu]se (?:only )?that path\.",
        "The system prompt names the active workspace's `agent-transcripts/` directory; use only that path.",
    ),
    (
        r"A local transcript under the workspace's `~/\.claude/projects/<slug>/` directory \(derive the slug from the working directory, every `/` turned into `-`; do not glob across `~/\.(?:claude|cursor)/projects/\*/`, that crosses workspace boundaries and reads private chats from unrelated projects\)",
        "A local transcript under the workspace's `agent-transcripts/` directory named in the system prompt (do not glob across `~/.cursor/projects/*/`, that crosses workspace boundaries and reads private chats from unrelated projects)",
    ),
    (r"`~/\.claude/projects/<slug>/`", "the workspace's `agent-transcripts/` directory"),
    (r"Two transcript layouts: the session file \(`<id>\.jsonl`\) and subagent", "Three transcript layouts: legacy flat (`<id>.jsonl`), current nested (`<id>/<id>.jsonl`), and subagent"),
    (r"ls -t <transcripts>/\*\.jsonl <transcripts>/\*/subagents/\*\.jsonl", "ls -t <agent-transcripts>/*.jsonl <agent-transcripts>/*/*.jsonl <agent-transcripts>/*/subagents/*.jsonl"),
    (r"Claude Code", "Cursor"),
    (r"\$\{CLAUDE_PLUGIN_ROOT\}", "<shelly-stack-plugin-dir>"),
)

# Per-file regexes. Every pattern must match, so a source rewrite that moves the anchor fails the build.
FILE_REGEX_REPLACEMENTS: dict[str, tuple[tuple[str, str], ...]] = {
    "skills/reflect/SKILL.md": (
        (
            r"The parent finds its own transcript file before fanning out\. Run `scripts/find-transcript\.sh .*?pass that instead\.",
            "The parent finds its own transcript file before fanning out. The system prompt names the active workspace's `agent-transcripts/` directory; use only that path. Do not glob across `~/.cursor/projects/*/`. That crosses workspace boundaries and reads private chats from unrelated projects.\n\n```bash\nls -t <agent-transcripts>/*.jsonl <agent-transcripts>/*/*.jsonl <agent-transcripts>/*/subagents/*.jsonl 2>/dev/null | head -10\n```\n\nThree transcript layouts: legacy flat (`<id>.jsonl`), current nested (`<id>/<id>.jsonl`), and subagent (`<parent>/subagents/<child>.jsonl`).\n\nFor each candidate, read the first JSONL line and check that `message.content[0].text` contains the conversation's opening user prompt. Take the matching path. If no path resolves, write a tight digest of the session and pass that instead.",
        ),
    ),
    "skills/shelly-mode/SKILL.md": (
        (
            r"\A---\nname: shelly-mode\ndescription: (.*?)\ndisable-model-invocation: true\n---\n",
            "---\nname: shelly-mode\ndescription: \\1\ndisable-model-invocation: true\nmode: true\nicon: crown\ncolor: yellow\nreminder: New task? Playbook match or rigor needed -> apply /shelly-mode. Casual turn or user opts out -> don't.\n---\n",
        ),
        (
            r"## Subagents\n.*?\n## Writing the reply",
            """## Subagents

**Use `subagent_type: "shelly-agent"` for any subagent you spawn inside a playbook step** (code-writing delegates, ad-hoc helpers). `/shelly-mode` and `shelly-agent` route through the same wrapper. Routed workflow skills (`how`, `why`, `interrogate`, `reflect`, `swarm`) set their own `subagent_type` for diverse-model review; respect what the skill prescribes, don't override to `shelly-agent`.

**Defaults for every `Task` call.** `run_in_background: true`, agent mode (the `explore` subagent strips MCP), file pointers not inlined context, explicit model per role (configurable via `/setup-shelly-stack`; defaults `cursor-grok-4.6-high-fast` for code, `claude-fable-5-1-thinking-high` for prose and judgment). Code delegates tier by difficulty. The hardest changes (cross-cutting design, gnarly concurrency, subtle algorithms) go to your strongest judgment model (`claude-fable-5-1-thinking-high`) when the task needs judgment or the intent is vague, and to your strongest instruction-following model (`claude-opus-5-5-high`) when the work is a precisely specified sequence of steps to execute to the letter; trivial mechanical edits go to your fast code model. Per-role lines in the `/setup-shelly-stack` rule override these defaults and the model choices in the routed skills (`how`, `why`, `arena`, `swarm`, `architect`, `interrogate`, `reflect`); a role with no line keeps its default, and a role line of `inherit-parent` or `auto` runs that role on the parent chat model (omit Task `model`).

A subagent that writes files in parallel with others runs as `subagent_type: best-of-n-runner`, which gives it its own git worktree and branch. Cursor's `Task` has no tool allowlist; a read-only posture is a prompt that forbids writes, not a sandbox.

You own every subagent's work. Review the diff and write your own summary, don't pass through what it said. Interrupt-chained resumes silently drop directives, so fire a fresh subagent with consolidated scope rather than trusting a "done" summary. A second opinion is the same prompt against a different model. Agreement is high-signal.

## Writing the reply""",
        ),
    ),
    "skills/shelly-guide/SKILL.md": (
        (r"\nargument-hint: [^\n]*\n", "\n"),
        (
            r"The guide lives at `<shelly-stack-plugin-dir>/docs/guide/`\.",
            f"The guide lives at `<shelly-stack-plugin-dir>/docs/guide/`. {PLUGIN_DIR_NOTE}.",
        ),
    ),
    "skills/ticket/SKILL.md": ((r"\nargument-hint: [^\n]*\n", "\n"),),
    "skills/shelly-mode/playbooks/multi-phase-plan.md": (
        (
            r"6\. Run `node <shelly-stack-plugin-dir>/skills/shelly-mode/scripts/check-plan\.mjs <plan\.md>` and",
            f"6. Run `node <shelly-stack-plugin-dir>/skills/shelly-mode/scripts/check-plan.mjs <plan.md>` ({PLUGIN_DIR_NOTE}) and",
        ),
    ),
    "skills/swarm/SKILL.md": (
        (
            r"Fan out N parallel local workers, each in its own worktree when it writes\.",
            "Fan out N parallel cloud workers.",
        ),
        (
            r"N is total workers; size it for one machine\.",
            "N is total workers, not the cloud concurrency limit.",
        ),
        (
            r"Invoking swarm is the user's opt-in to multi-agent orchestration, so run the fan-out with the `Workflow` tool.*?the Workflow runs locally\.",
            "Spawn all N workers in one message with the `Task` tool, `subagent_type: generalPurpose`, `environment: \"cloud\"`, `run_in_background: true`, and the configured model. Use `environment: \"local\"` only when the worker needs access to something on the user's computer; a local worker that writes files runs as `subagent_type: best-of-n-runner`, which gives it its own git worktree and branch. Put the report shape below in every brief and ask for it verbatim so the parent aggregates objects, not prose.",
        ),
        (
            r"When a worker must start from a non-default pushed branch, name that branch in its brief and tell it to check the branch out first\.",
            "When a worker must start from a non-default pushed branch, pass `cloud_base_branch`.",
        ),
    ),
    "skills/shelly-mode/playbooks/orchestrate.md": (
        (r", or through one Workflow-tool script per wave", ""),
        (r"has the full Agent schema including `isolation`\)", "has the full `Task` schema including `environment`)"),
        (r" A wave may also run as one Workflow-tool script, where `pipeline\(\)` gives that rolling window\.", ""),
        (
            r"`Task` subagents \(or Workflow-tool agents\) on this machine, every writer in its own git worktree: `isolation: \"worktree\"` on the `Task` tool, or `opts\.isolation: 'worktree'` in a Workflow script\. They share the laptop with the coordinator, so size the in-flight cap for one machine\. Everything local is reachable: runtime verification through the project's verification skill, transcripts under the workspace's `agent-transcripts/` directory, simulators and IDE state, local auth\. Briefs still inline what a worker needs or point at repo and store paths, because a worker cannot ask\.",
            "Always `environment: \"cloud\"` unless the task needs this machine: runtime verification through the project's verification skill; reading local transcripts under the workspace's `agent-transcripts/` directory; simulators and local IDE state; auth that exists only here. A local writer runs as `subagent_type: best-of-n-runner` for its own git worktree. Cloud agents cannot read the local store, so their briefs inline what they need or point at repo paths.",
        ),
        (
            r"A spawn may reference the standing-orders file by store path\.",
            "A local spawn may reference the standing-orders file by store path; a cloud spawn gets it pasted.",
        ),
        (
            r"its spawn budget sized for one laptop,",
            "its spawn budget with the cloud default and the local exception list,",
        ),
        (
            r"Work that exists only in one worktree when its agent dies was never done\.",
            "Work that exists only on one cloud VM when that VM dies was never done.",
        ),
        (
            r"Probe read-only: the ledger, `units\.tsv`, `gh`, pushed branches\. Transcript mtime is not liveness\.",
            "Probe read-only: the ledger, `units.tsv`, `gh`, pushed branches, the cloud agent's status in the Cursor dashboard. Transcript mtime is not liveness.",
        ),
        (
            r"After a Cursor restart every agent is dead; only pushed branches and PRs survive\. Re-read the standing orders and `units\.tsv`, recompute the frontier, reattach each unit by branch and PR rather than agent id,",
            "After a Cursor restart local agents are dead; cloud work is not. Re-read the standing orders and `units.tsv`, recompute the frontier, reattach cloud work by PR and branch rather than agent id,",
        ),
    ),
    "skills/shelly-mode/scripts/worktree-audit.sh": (
        (
            r"# Transcripts dir: ~/\.claude/projects/<slugified-repo-path>, leading slash included\.\nslug=\$\(printf '%s' \"\$main_wt\" \| sed 's#/#-#g'\)\ntranscripts=\"\$HOME/\.claude/projects/\$slug\"",
            "# Transcripts dir: ~/.cursor/projects/<slugified-repo-path>/agent-transcripts.\nslug=$(printf '%s' \"$main_wt\" | sed 's#^/##; s#/#-#g')\ntranscripts=\"$HOME/.cursor/projects/$slug/agent-transcripts\"",
        ),
    ),
    "agents/shelly-agent.md": (
        (r"Substituting `generalPurpose` skips that read and drifts\.\n---\n", "Substituting `generalPurpose` skips that read and drifts.\nis_background: true\n---\n"),
    ),
    "docs/guide/01-setup.md": (
        (
            r"## Install the plugin\n.*?\n## Pick your models",
            "## Install the plugin\n\nFrom a local checkout of this repository, build the Cursor package and copy it into Cursor's local plugins directory:\n\n```text\n./scripts/build_cursor_plugin.py --install\n```\n\nThe installed copy at `~/.cursor/plugins/local/shelly-stack` is independent of the checkout. Re-run the command after every rebuild. Enable \"Include third-party Plugins, Skills, and other configs\" in Cursor settings, then start a new chat so it discovers the skills.\n\n## Pick your models",
        ),
        (r"\nIn Codex, invoke `\$shelly-stack:setup-shelly-stack` instead\.\n", "\n"),
        (
            r"Cursor writes `~/\.cursor/rules/shelly-stack-models\.mdc`\. Codex writes `~/\.codex/shelly-stack-models\.md`\. Each setup leaves the other client's configuration untouched\.",
            "Cursor writes `~/.cursor/rules/shelly-stack-models.mdc` and leaves the other clients' configuration untouched.",
        ),
        (r"`\.cursor/skills/verify-<app>/` in Cursor or `\.agents/skills/verify-<app>/` in Codex\.", "`.cursor/skills/verify-<app>/`."),
        (r"; in Cursor invoke `/shelly-mode`, in Codex `\$shelly-stack:shelly-mode`, on each turn where you want it applied\.", "; invoke `/shelly-mode` on each turn where you want it applied."),
    ),
}


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_symlink():
        destination.symlink_to(os.readlink(source))
    else:
        shutil.copy2(source, destination)


def git_tracked_files(prefix: str) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", prefix],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    paths = [ROOT / value.decode("utf-8") for value in result.stdout.split(b"\0") if value]
    if not paths:
        raise ValueError(f"no tracked build inputs found under {prefix}")
    return paths


# Claude-only helpers whose skill text this build rewrites for Cursor.
CLAUDE_ONLY_SKILL_FILES = frozenset({"reflect/scripts/find-transcript.sh"})


def copy_shared_sources(output: Path) -> None:
    for source in git_tracked_files("skills"):
        relative = source.relative_to(SKILLS_SOURCE)
        if relative.parts[0] in EXCLUDED_SKILLS or relative.as_posix() in CLAUDE_ONLY_SKILL_FILES:
            continue
        copy_file(source, output / "skills" / relative)
    for source in git_tracked_files("docs/guide"):
        copy_file(source, output / source.relative_to(ROOT))
    for name in AGENTS:
        copy_file(ROOT / "agents" / name, output / "agents" / name)


def copy_overrides(output: Path) -> None:
    declared = [
        line.strip()
        for line in OVERRIDE_FILE_LIST.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    actual = {
        path.relative_to(OVERRIDES).as_posix()
        for path in OVERRIDES.rglob("*")
        if path.is_file()
    }
    if actual != set(declared):
        raise ValueError(
            f"Cursor override inventory mismatch; missing={sorted(set(declared) - actual)}, "
            f"undeclared={sorted(actual - set(declared))}"
        )
    for relative in declared:
        copy_file(OVERRIDES / relative, output / relative)


def rewrite(contents: str, relative_path: str) -> str:
    for old, new in LITERAL_REPLACEMENTS:
        contents = contents.replace(old, new)
    for pattern, replacement in REGEX_REPLACEMENTS:
        contents = re.sub(pattern, replacement, contents, flags=re.DOTALL)
    for pattern, replacement in FILE_REGEX_REPLACEMENTS.get(relative_path, ()):
        contents, count = re.subn(pattern, replacement, contents, flags=re.DOTALL)
        if count == 0:
            raise ValueError(f"Cursor rewrite anchor not found in {relative_path}: {pattern!r}")
    for alias, slug in MODEL_ALIASES.items():
        contents = contents.replace(f"`{alias}`", f"`{slug}`")
    return contents


def is_override(relative_path: str) -> bool:
    return (OVERRIDES / relative_path).is_file()


def rewrite_output(output: Path) -> None:
    for path in sorted(output.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        if path.suffix not in {".md", ".sh"}:
            continue
        relative = path.relative_to(output).as_posix()
        if is_override(relative):
            continue
        path.write_text(rewrite(path.read_text(encoding="utf-8"), relative), encoding="utf-8")
    for relative in FILE_REGEX_REPLACEMENTS:
        if not (output / relative).is_file():
            raise ValueError(f"Cursor rewrite target missing from package: {relative}")


def write_manifest(destination: Path) -> None:
    claude = json.loads(CLAUDE_MANIFEST.read_text(encoding="utf-8"))
    cursor = json.loads(MANIFEST_TEMPLATE.read_text(encoding="utf-8"))
    if claude.get("name") != cursor.get("name"):
        raise ValueError("Claude and Cursor plugin names must match")
    if not isinstance(cursor.get("version"), str) or not cursor["version"]:
        raise ValueError("Cursor plugin template must own a version")
    destination.parent.mkdir(parents=True)
    destination.write_text(json.dumps(cursor, indent="\t") + "\n", encoding="utf-8")


def populate_output(output: Path) -> None:
    output.mkdir(parents=True)
    copy_shared_sources(output)
    copy_overrides(output)
    rewrite_output(output)
    write_manifest(output / ".cursor-plugin" / "plugin.json")
    shutil.copy2(ROOT / "LICENSE", output / "LICENSE")
    shutil.copy2(ROOT / "cursor" / "plugin.README.md", output / "README.md")


def build(output: Path = OUTPUT) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    staging_root = Path(tempfile.mkdtemp(prefix=f".{output.name}-staging-", dir=output.parent))
    staging_output = staging_root / "package"
    try:
        populate_output(staging_output)
        if output.exists():
            shutil.rmtree(output)
        os.replace(staging_output, output)
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)
    print(f"Built Cursor plugin at {output}")


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
    with tempfile.TemporaryDirectory(prefix="shelly-stack-cursor-") as temporary:
        candidate = Path(temporary) / "shelly-stack"
        build(candidate)
        committed = snapshot(OUTPUT)
        generated = snapshot(candidate)
        if committed != generated:
            changed = [p for p in sorted(set(committed) | set(generated)) if committed.get(p) != generated.get(p)]
            details = "\n".join(f"  {path}" for path in changed[:25])
            if len(changed) > 25:
                details += f"\n  ... and {len(changed) - 25} more"
            raise SystemExit(
                "Committed Cursor package is stale. Run ./scripts/build_cursor_plugin.py.\n"
                f"Changed paths:\n{details}"
            )
    print("Cursor package matches the shared source and overlay")


def install(target: Path = INSTALL_TARGET) -> None:
    """Copy the committed package into Cursor's local plugins directory as its own tree."""
    if target.is_symlink():
        raise RuntimeError(f"{target} is a symlink; remove it before installing a copy")
    if target.exists() and not (target / ".cursor-plugin" / "plugin.json").is_file():
        raise RuntimeError(f"refusing to replace {target}: it is not a Cursor plugin directory")
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".shelly-stack-install-", dir=target.parent))
    try:
        shutil.copytree(OUTPUT, staging / "shelly-stack", symlinks=True)
        if target.exists():
            shutil.rmtree(target)
        os.replace(staging / "shelly-stack", target)
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    version = json.loads((target / ".cursor-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
    print(f"Installed shelly-stack {version} for Cursor at {target}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare a fresh build with the committed Cursor package without changing the tree",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help=f"after building, copy the package to {INSTALL_TARGET}",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    if arguments.check:
        check()
    else:
        build()
        if arguments.install:
            install()
