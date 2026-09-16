import importlib.util
import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("team_kit_builder", ROOT / "scripts/build_team_kit_plugin.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class TeamKitTests(unittest.TestCase):
    def test_distribution_matches_source_and_preserves_policies(self):
        before = builder.snapshot(builder.SOURCE)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            builder.populate(output)
            self.assertEqual(builder.snapshot(output), builder.snapshot(builder.OUTPUT))
            self.assertEqual(before, builder.snapshot(builder.SOURCE))
            self.assertFalse((output / "agents").exists())
            for skill in (output / "skills").glob("*/SKILL.md"):
                front = yaml.safe_load(skill.read_text().split("---", 2)[1])
                self.assertEqual(set(front), {"name", "description"})
                self.assertEqual(front["name"], skill.parent.name)
                source = builder.SOURCE / skill.relative_to(output)
                source_front = yaml.safe_load(source.read_text().split("---", 2)[1])
                policy = skill.parent / "agents/openai.yaml"
                self.assertEqual(policy.exists(), bool(source_front.get("disable-model-invocation")))
                if policy.exists():
                    self.assertFalse(yaml.safe_load(policy.read_text())["policy"]["allow_implicit_invocation"])

    def test_skill_inventory_and_links(self):
        expected = {
            "check-compiler-errors", "control-cli", "control-ui", "deslop", "fix-ci",
            "fix-merge-conflicts", "get-pr-comments", "loop-on-ci", "make-pr-easy-to-review",
            "new-branch-and-pr", "pr-review-canvas", "review-and-ship", "run-smoke-tests",
            "thermo-nuclear-code-quality-review", "verify-this", "weekly-review",
            "what-did-i-get-done", "workflow-from-chats", "typescript-conventions",
        }
        for root in (builder.SOURCE, builder.OUTPUT):
            self.assertEqual({p.parent.name for p in (root / "skills").glob("*/SKILL.md")}, expected)
            for path in root.rglob("*.md"):
                for link in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                    if "://" not in link and not link.startswith("#"):
                        self.assertTrue((path.parent / link.split("#")[0]).exists(), f"{path}: {link}")
            for path in (root / "skills").rglob("*.md"):
                self.assertNotRegex(path.read_text(), r"\.cursor/|AskQuestion|review-bugbot|review-security|cloud_base_branch|run_in_background|\bTask tool\b")
        for root in (ROOT / "skills", ROOT / "plugins/shelly-stack/skills"):
            for path in root.rglob("*.md"):
                for name in re.findall(r"[/$]shelly-team-kit:([a-z-]+)", path.read_text()):
                    self.assertIn(name, expected, str(path))
        codex = (builder.OUTPUT / "references/runtime.md").read_text()
        self.assertNotIn("~/.claude/", codex)
        self.assertIn("enforced read-only", codex)
        self.assertIn("explicit request", codex)

    def test_marketplaces_resolve_both_packages(self):
        for relative, source in ((".claude-plugin/marketplace.json", "./team-kit"), (".agents/plugins/marketplace.json", {"source": "local", "path": "./plugins/shelly-team-kit"})):
            entries = json.loads((ROOT / relative).read_text())["plugins"]
            kit = [entry for entry in entries if entry["name"] == "shelly-team-kit"]
            self.assertEqual(len(kit), 1)
            self.assertEqual(kit[0]["source"], source)

    def test_canvas_recipe_preserves_script_terminators_and_path_keys(self):
        skill = builder.SOURCE / "skills/pr-review-canvas"
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

    def test_canvas_renderer_keeps_import_line_numbers_and_escapes_code(self):
        renderer = builder.SOURCE / "skills/pr-review-canvas/renderer.js"
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
        subprocess.run(["node", "-e", script, str(renderer)], check=True)


if __name__ == "__main__":
    unittest.main()
