import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OTHER_RUNTIME = r"spawn_agent|request_user_input|\$shelly-stack:[a-z]|~/\.codex/"
INVOCATION = r"/shelly-stack:([a-z][a-z-]*)"


def tracked(pattern: str) -> list[Path]:
    return [p for p in ROOT.rglob(pattern) if not {"node_modules", ".git"} & set(p.parts)]


def frontmatter(path: Path) -> dict:
    return yaml.safe_load(path.read_text().split("---", 2)[1])


def skill_names() -> set[str]:
    return {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}


class PluginTests(unittest.TestCase):
    def test_marketplace_serves_this_directory(self):
        entries = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())["plugins"]
        self.assertEqual([e["name"] for e in entries], ["shelly-stack"])
        self.assertEqual((ROOT / entries[0]["source"]).resolve(), ROOT)

    def test_manifest_names_the_plugin(self):
        self.assertEqual(json.loads((ROOT / '.claude-plugin/plugin.json').read_text())["name"], "shelly-stack")

    def test_skill_names_match_directories(self):
        for skill in tracked("skills/*/SKILL.md"):
            self.assertEqual(frontmatter(skill)["name"], skill.parent.name, str(skill))

    def test_relative_links_resolve(self):
        for path in tracked("*.md"):
            for link in re.findall(r"\]\(([^)\s]+)\)", path.read_text()):
                if "://" in link or link.startswith(("#", "mailto:")) or "<" in link or not re.search(r"[./]", link):
                    continue
                self.assertTrue((path.parent / link.split("#")[0]).exists(), f"{path}: {link}")

    def test_other_runtime_vocabulary_is_absent(self):
        for path in (*tracked("skills/**/*.md"), *tracked("agents/*.md"), *tracked("references/*.md")):
            self.assertNotRegex(path.read_text(), OTHER_RUNTIME, str(path))

    def test_skill_invocations_name_real_skills(self):
        names = skill_names()
        for path in tracked("skills/**/*.md"):
            for name in re.findall(INVOCATION, path.read_text()):
                self.assertIn(name, names, str(path))


class PrReviewCanvasTests(unittest.TestCase):
    def test_recipe_preserves_script_terminators_and_path_keys(self):
        for root in (ROOT,):
            skill = root / "skills/pr-review-canvas"
            recipe = re.search(r"```python\n(.*?)\n```", (skill / "SKILL.md").read_text(), re.S)[1]
            patches = {"a-b.js": '+const x = "</script><script>alert(1)</script>";', "a_b.js": '+const y = "quote\\\\value";'}
            with tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                (output / "patches.json").write_text(json.dumps(patches))
                (output / "body.html").write_text('<div data-diff="a-b.js"></div>')
                recipe = recipe.replace("<absolute skill directory>", str(skill)).replace("<task artifact directory>", directory)
                exec(compile(recipe, "canvas-recipe", "exec"), {})
                rendered = (output / "review.html").read_text()
                data = re.search(r'<script id="pr-diffs-json"[^>]*>(.*?)</script>', rendered, re.S)[1]
                self.assertEqual(json.loads(data), patches)
                self.assertNotIn("</script>", data)
                self.assertNotIn("INJECT_", rendered)

    def test_renderer_keeps_import_line_numbers_and_escapes_code(self):
        script = r'''
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const context = {document: {addEventListener() {}}, console};
vm.createContext(context);
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), context);
const target = {innerHTML: ''};
context.renderDiff(target, '@@ -1,2 +1,2 @@\n-import old from "old";\n+import next from "next";\n+<script>alert(1)</script>');
assert.ok(target.innerHTML.includes('import next'));
assert.ok(target.innerHTML.includes('<td class="diff-ln">2</td><td class="diff-code">&lt;script&gt;'));
assert.ok(!target.innerHTML.includes('<script>'));
'''
        for root in (ROOT,):
            subprocess.run(["node", "-e", script, str(root / "skills/pr-review-canvas/renderer.js")], check=True)


if __name__ == "__main__":
    unittest.main()
