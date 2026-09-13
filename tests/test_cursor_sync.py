"""Protect the principle inventory and workflow removals from the upstream sync."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRINCIPLES = {
    'attack-the-premise', 'boundary-discipline', 'build-the-lever',
    'encode-lessons-in-structure', 'exhaust-the-design-space', 'experience-first',
    'fix-root-causes', 'foundational-thinking', 'guard-the-context-window',
    'laziness-protocol', 'make-operations-idempotent',
    'migrate-callers-then-delete-legacy-apis', 'minimize-reader-load',
    'model-the-domain', 'never-block-on-the-human', 'outcome-oriented-execution',
    'prove-it-works', 'redesign-from-first-principles',
    'separate-before-serializing-shared-state', 'sequence-verifiable-units',
    'subtract-before-you-add', 'test-behavior-not-implementation',
    'type-system-discipline',
}


class CursorSyncTests(unittest.TestCase):
    def test_all_upstream_principles_are_delivered_and_routed(self):
        for root in (ROOT, ROOT / 'plugins/shelly-stack'):
            skills = root / 'skills'
            actual = {p.parent.name.removeprefix('principle-')
                      for p in skills.glob('principle-*/SKILL.md')}
            self.assertEqual(actual, PRINCIPLES)
            mode = (skills / 'shelly-mode/SKILL.md').read_text()
            for name in PRINCIPLES:
                self.assertIn('principle-' + name, mode)
        routes = ROOT / 'plugins/shelly-stack/skills/shelly-mode/references/routed'
        for name in PRINCIPLES:
            self.assertTrue((routes / ('principle-' + name) / 'workflow.md').is_file())

    def test_explanation_uses_current_templates_without_retired_critique(self):
        for root in (ROOT, ROOT / 'plugins/shelly-stack'):
            skill = root / 'skills/how'
            body = (skill / 'SKILL.md').read_text()
            self.assertEqual(body.count('## Step 2a.'), 1)
            self.assertEqual(body.count('## Step 2b.'), 1)
            self.assertIn('sections defined in `references/explainer-prompt.md`', body)
            self.assertFalse((skill / 'references/critic-prompt.md').exists())
            self.assertFalse((skill / 'references/critique-rubric.md').exists())

    def test_merged_playbooks_have_one_copy_of_each_instruction(self):
        for root in (ROOT, ROOT / 'plugins/shelly-stack'):
            playbooks = root / 'skills/shelly-mode/playbooks'
            self.assertEqual((playbooks / 'babysit.md').read_text().count('1. **Declare'), 1)
            self.assertEqual((playbooks / 'opening-a-pr.md').read_text().count('- `## Why`'), 1)
