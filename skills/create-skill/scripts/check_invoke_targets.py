#!/usr/bin/env python3
"""Fail when agent-facing prose tells the model to invoke a skill whose frontmatter sets disable-model-invocation.

The Skill tool refuses such a skill and tells the model not to follow its workflow any other way, so the step silently drops.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AGENT_FACING = ("skills", "agents", "references")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
DISABLED = re.compile(r"^disable-model-invocation:\s*true\s*$", re.M)
INVOKE = re.compile(
    r"\b(?:invoke[sd]?|invoking|run|runs|running|call|calls|via|hand(?: it)? to)\s+(?:the\s+)?"
    r"(?:\*\*|`)/?(?:shelly-stack:)?([a-z0-9-]+)(?:\*\*|`)",
    re.I,
)


def disabled_skills() -> set[str]:
    names = set()
    for skill in (ROOT / "skills").glob("*/SKILL.md"):
        match = FRONTMATTER.match(skill.read_text())
        if match and DISABLED.search(match.group(1)):
            names.add(skill.parent.name)
    return names


def main() -> int:
    disabled = disabled_skills()
    violations = []
    for top in AGENT_FACING:
        for path in sorted((ROOT / top).rglob("*.md")):
            rel = path.relative_to(ROOT)
            own = rel.parts[1] if rel.parts[0] == "skills" else None
            for n, line in enumerate(path.read_text().splitlines(), 1):
                for match in INVOKE.finditer(line):
                    name = match.group(1)
                    if name in disabled and name != own:
                        violations.append(f"{rel}:{n}: invokes {name}, which sets disable-model-invocation: true")
    print("\n".join(violations))
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
