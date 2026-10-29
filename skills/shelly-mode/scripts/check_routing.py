from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MODE = ROOT / "skills/shelly-mode"
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
DISABLED = re.compile(r"^disable-model-invocation:\s*true\s*$", re.M)
SKILL_REF = re.compile(r"\bshelly-stack:([a-z0-9-]*[a-z0-9])(?![a-z0-9<{-])")
PLAYBOOK_REF = re.compile(r"\bplaybooks/([a-z0-9-]+)\.md\b")
PRINCIPLE_REF = re.compile(r"\bprinciple-([a-z0-9-]+)/SKILL\.md\b")


def text(path: Path) -> str:
    return path.read_text(errors="ignore")


def disabled(body: str) -> bool:
    frontmatter = FRONTMATTER.match(body)
    return bool(frontmatter and DISABLED.search(frontmatter.group(1)))


def main() -> int:
    skills = {p.parent.name: text(p) for p in sorted((ROOT / "skills").glob("*/SKILL.md"))}
    agents = {p.stem for p in (ROOT / "agents").glob("*.md")}
    playbook_files = sorted((MODE / "playbooks").glob("*.md"))
    playbooks = {p.stem for p in playbook_files}
    mode = text(MODE / "SKILL.md")
    mode_triggers = re.sub(r"^## Principles\n.*?(?=^## )", "", mode, flags=re.S | re.M)
    playbook_text = "\n".join(text(p) for p in playbook_files)
    routes = "\n".join([mode, playbook_text])
    problems = []

    for name, body in skills.items():
        if name.startswith("principle-") or disabled(body):
            continue
        if not re.search(rf"(shelly-stack:|\*\*|`/?|(?<![\w/-])/){re.escape(name)}\b(?!-)", routes):
            problems.append(f"skills/{name}: no trigger in shelly-mode or a playbook")

    for name in sorted(playbooks - set(PLAYBOOK_REF.findall(mode))):
        problems.append(f"skills/shelly-mode/playbooks/{name}.md: shelly-mode never routes to it")

    other_skills = "\n".join(body for name, body in skills.items() if not name.startswith("principle-") and name != "shelly-mode")
    reached = set(PRINCIPLE_REF.findall("\n".join([mode_triggers, playbook_text, other_skills])))
    for name in sorted(n for n in skills if n.startswith("principle-")):
        if name.removeprefix("principle-") not in reached:
            problems.append(f"skills/{name}: named only in the Principles index, with no step or trigger that reads it")

    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    for rel in tracked:
        if Path(rel).suffix not in (".md", ".yaml", ".sh", ".py", ".mjs", ".ts"):
            continue
        for n, line in enumerate(text(ROOT / rel).splitlines(), 1):
            for name in SKILL_REF.findall(line):
                if name not in skills and name not in agents:
                    problems.append(f"{rel}:{n}: shelly-stack:{name} is not a skill or agent")
            for name in PLAYBOOK_REF.findall(line):
                if name not in playbooks:
                    problems.append(f"{rel}:{n}: playbooks/{name}.md does not exist")
            for name in PRINCIPLE_REF.findall(line):
                if f"principle-{name}" not in skills:
                    problems.append(f"{rel}:{n}: principle-{name} does not exist")

    print("\n".join(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
