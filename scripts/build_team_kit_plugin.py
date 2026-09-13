#!/usr/bin/env python3
"""Generate the Codex companion package from the Claude Team Kit source."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "team-kit"
OUTPUT = ROOT / "plugins" / "shelly-team-kit"


def populate(output: Path) -> None:
    for name in ("skills", "references"):
        shutil.copytree(SOURCE / name, output / name)
    for name in ("README.md", "LICENSE"):
        shutil.copyfile(SOURCE / name, output / name)
    shutil.copyfile(SOURCE / "references/codex-runtime.md", output / "references/runtime.md")
    (output / "references/codex-runtime.md").unlink()
    names = {path.parent.name for path in (output / "skills").glob("*/SKILL.md")}
    for path in (output / "skills").glob("*/SKILL.md"):
        front, body = path.read_text().removeprefix("---\n").split("---", 1)
        metadata = yaml.safe_load(front)
        if metadata["name"] != path.parent.name or not metadata.get("description"):
            raise ValueError(f"Invalid skill metadata: {path}")
        if metadata.get("disable-model-invocation"):
            policy = path.parent / "agents/openai.yaml"
            policy.parent.mkdir(exist_ok=True)
            policy.write_text(yaml.safe_dump({"interface": {"display_name": metadata["name"].replace("-", " ").title(), "short_description": "Review changes with Shelly Team Kit"}, "policy": {"allow_implicit_invocation": False}}, sort_keys=False))
        path.write_text("---\n" + yaml.safe_dump({key: metadata[key] for key in ("name", "description")}, sort_keys=False) + "---" + body)
    for path in output.rglob("*.md"):
        if path.name == "README.md":
            continue
        text = path.read_text()
        for name in sorted(names, key=len, reverse=True):
            text = text.replace(f"/shelly-team-kit:{name}", f"$shelly-team-kit:{name}")
            text = re.sub(rf"(?<![\w$./:-])/{re.escape(name)}\b", f"$shelly-team-kit:{name}", text)
        path.write_text(text)
    manifest = json.loads((SOURCE / "codex-plugin.template.json").read_text())
    directory = output / ".codex-plugin"
    directory.mkdir()
    (directory / "plugin.json").write_text(json.dumps(manifest, indent=2) + "\n")


def snapshot(directory: Path) -> dict[str, bytes]:
    return {str(path.relative_to(directory)): path.read_bytes() for path in directory.rglob("*") if path.is_file()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="shelly-team-kit-") as directory:
        built = Path(directory) / "shelly-team-kit"
        built.mkdir()
        populate(built)
        expected = snapshot(built)
        actual = snapshot(OUTPUT)
        changed = sorted(name for name in expected.keys() | actual.keys() if expected.get(name) != actual.get(name))
        if args.check:
            if changed:
                raise SystemExit("Team Kit generated files drifted:\n" + "\n".join(changed))
        else:
            # Only generated files belong in OUTPUT. Leave unchanged files untouched.
            for name in changed:
                target = OUTPUT / name
                if name not in expected:
                    target.unlink()
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(expected[name])
        print(f"Shelly Team Kit {'check passed' if args.check else 'built'}: {len(expected)} files")


if __name__ == "__main__":
    main()
