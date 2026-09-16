from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
BUILD_SCRIPT = ROOT / "scripts" / "build_codex_plugin.py"
VALIDATOR_SCRIPT = ROOT / "scripts" / "validate_dual_runtime.py"
FROZEN_CLAUDE_PATHS = (
    ROOT / ".claude-plugin",
    ROOT / "skills",
    ROOT / "agents",
    ROOT / "docs",
    ROOT / "automations",
)


def load_builder():
    spec = importlib.util.spec_from_file_location("build_codex_plugin", BUILD_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {BUILD_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_dual_runtime", VALIDATOR_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {VALIDATOR_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def frozen_snapshot(builder) -> dict[str, tuple[str, int, str]]:
    result: dict[str, tuple[str, int, str]] = {}
    for root in FROZEN_CLAUDE_PATHS:
        if not root.exists():
            continue
        for relative, value in builder.snapshot(root).items():
            result[f"{root.relative_to(ROOT).as_posix()}/{relative}"] = value
    return result


class CodexDistributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        cls.validator = load_validator()

    def test_build_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shelly-codex-test-") as temporary:
            base = Path(temporary)
            first = base / "first"
            second = base / "second"
            self.builder.build(first)
            self.builder.build(second)
            self.assertEqual(self.builder.snapshot(first), self.builder.snapshot(second))

    def test_committed_distribution_matches_fresh_build(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shelly-codex-test-") as temporary:
            candidate = Path(temporary) / "shelly-stack"
            self.builder.build(candidate)
            self.assertEqual(
                self.builder.snapshot(ROOT / "plugins" / "shelly-stack"),
                self.builder.snapshot(candidate),
            )

    def test_build_does_not_change_claude_runtime(self) -> None:
        before = frozen_snapshot(self.builder)
        with tempfile.TemporaryDirectory(prefix="shelly-codex-test-") as temporary:
            self.builder.build(Path(temporary) / "shelly-stack")
        self.assertEqual(before, frozen_snapshot(self.builder))

    def test_generated_distribution_excludes_local_noise(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shelly-codex-test-") as temporary:
            candidate = Path(temporary) / "shelly-stack"
            self.builder.build(candidate)
            paths = self.builder.snapshot(candidate)
            self.assertFalse(
                any(
                    path.endswith((".pyc", ".pyo", ".DS_Store"))
                    or "/__pycache__/" in f"/{path}/"
                    for path in paths
                )
            )

    def test_build_refuses_an_unapproved_output_root(self) -> None:
        with tempfile.TemporaryDirectory(prefix="unexpected-codex-output-") as temporary:
            with self.assertRaises(RuntimeError):
                self.builder.build(Path(temporary) / "shelly-stack")

    def test_failed_build_preserves_previous_distribution(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shelly-codex-test-") as temporary:
            candidate = Path(temporary) / "shelly-stack"
            candidate.mkdir()
            marker = candidate / "previous-build.txt"
            marker.write_text("keep me\n", encoding="utf-8")

            with mock.patch.object(
                self.builder,
                "bundle_codex_runtime_tools",
                side_effect=RuntimeError("forced bundle failure"),
            ):
                with self.assertRaisesRegex(RuntimeError, "forced bundle failure"):
                    self.builder.build(candidate)

            self.assertEqual(marker.read_text(encoding="utf-8"), "keep me\n")
            self.assertEqual({path.name for path in candidate.iterdir()}, {marker.name})

    def test_runtime_tools_are_bundled_for_node(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shelly-codex-test-") as temporary:
            candidate = Path(temporary) / "shelly-stack"
            self.builder.build(candidate)
            scripts = candidate / "skills" / "shelly-mode" / "scripts"
            self.assertTrue((scripts / "bin" / "orch.mjs").is_file())
            self.assertTrue((scripts / "bin" / "watch-pr.mjs").is_file())
            self.assertFalse((scripts / "node_modules").exists())
            self.assertFalse(any(scripts.rglob("*.ts")))

    def test_generated_ui_descriptions_end_on_a_word(self) -> None:
        for display_name in (
            "TDD",
            "Principle Redesign From First Principles",
            "Principle Migrate Callers Then Delete Legacy APIs",
        ):
            value = self.builder.short_description(display_name)
            self.assertLessEqual(len(value), 64)
            self.assertGreaterEqual(len(value), 25)
            self.assertTrue(value.endswith("Codex"), value)

    def test_runtime_contract_validator_passes(self) -> None:
        result = subprocess.run(
            ["python3", str(ROOT / "scripts" / "validate_dual_runtime.py")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_representative_codex_compatibility_contract_passes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shelly-codex-test-") as temporary:
            candidate = Path(temporary) / "shelly-stack"
            self.builder.build(candidate)
            with mock.patch.object(self.validator, "CODEX_ROOT", candidate):
                self.validator.validate_plan_template()
                self.validator.validate_codex_compatibility_cases()

    def test_compatibility_contract_rejects_each_regression(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shelly-codex-test-") as temporary:
            candidate = Path(temporary) / "shelly-stack"
            self.builder.build(candidate)
            with mock.patch.object(self.validator, "CODEX_ROOT", candidate):
                for case in self.validator.CODEX_COMPATIBILITY_CASES:
                    path = candidate / case.relative_path
                    original = path.read_text(encoding="utf-8")
                    for phrase in case.required_phrases:
                        with self.subTest(case=case.name, mutation="required", phrase=phrase):
                            self.assertIn(phrase, original)
                            path.write_text(original.replace(phrase, "<removed>", 1), encoding="utf-8")
                            with self.assertRaisesRegex(ValueError, case.name):
                                self.validator.validate_codex_compatibility_cases()
                        path.write_text(original, encoding="utf-8")

                    for phrase in case.forbidden_phrases:
                        with self.subTest(case=case.name, mutation="forbidden", phrase=phrase):
                            path.write_text(original + f"\n{phrase}\n", encoding="utf-8")
                            with self.assertRaisesRegex(ValueError, case.name):
                                self.validator.validate_codex_compatibility_cases()
                        path.write_text(original, encoding="utf-8")

    def test_shelly_mode_explicit_policy_is_codex_owned(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shelly-codex-test-") as temporary:
            output = Path(temporary) / "shelly-stack"
            skill = output / "skills" / "shelly-mode" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            contents = (ROOT / "skills" / "shelly-mode" / "SKILL.md").read_text(
                encoding="utf-8"
            )
            skill.write_text(
                contents.replace("disable-model-invocation: true\n", "", 1),
                encoding="utf-8",
            )
            self.builder.transform_skill(skill, output, {"shelly-mode"})
            policy_path = skill.parent / "agents" / "openai.yaml"
            self.assertTrue(policy_path.is_file())
            self.assertIn(
                "allow_implicit_invocation: false",
                policy_path.read_text(encoding="utf-8"),
            )

    def test_compatibility_contract_rejects_missing_shelly_mode_policy(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shelly-codex-test-") as temporary:
            candidate = Path(temporary) / "shelly-stack"
            self.builder.build(candidate)
            (candidate / "skills" / "shelly-mode" / "agents" / "openai.yaml").unlink()
            with mock.patch.object(self.validator, "CODEX_ROOT", candidate):
                with self.assertRaisesRegex(ValueError, "shelly-mode-explicit-only-invocation"):
                    self.validator.validate_codex_compatibility_cases()

    def test_compatibility_contract_rejects_each_unrouted_read_only_workflow(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shelly-codex-test-") as temporary:
            candidate = Path(temporary) / "shelly-stack"
            self.builder.build(candidate)
            branch = "native runtime contract's read-only worker branch"
            with mock.patch.object(self.validator, "CODEX_ROOT", candidate):
                for skill_name in self.validator.READ_ONLY_WORKFLOW_BRANCH_COUNTS:
                    path = candidate / "skills" / skill_name / "SKILL.md"
                    original = path.read_text(encoding="utf-8")
                    with self.subTest(skill=skill_name):
                        self.assertIn(branch, original)
                        path.write_text(original.replace(branch, "<unrouted>", 1), encoding="utf-8")
                        with self.assertRaisesRegex(ValueError, "read-only-reviewer-containment"):
                            self.validator.validate_codex_compatibility_cases()
                    path.write_text(original, encoding="utf-8")

    def test_compatibility_contract_rejects_nested_comment_sicko_work(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shelly-codex-test-") as temporary:
            candidate = Path(temporary) / "shelly-stack"
            self.builder.build(candidate)
            prompt = candidate / "skills" / "no-comments" / "references" / "comment-sicko.md"
            original = prompt.read_text(encoding="utf-8")
            mutations = (
                original.replace("NEEDS HOW OR WHY PROOF", "<removed>", 1),
                original + "\nRun $shelly-stack:how.\n",
                original + "\nRun $shelly-stack:why.\n",
            )
            with mock.patch.object(self.validator, "CODEX_ROOT", candidate):
                for index, contents in enumerate(mutations):
                    with self.subTest(mutation=index):
                        prompt.write_text(contents, encoding="utf-8")
                        with self.assertRaisesRegex(ValueError, "read-only-reviewer-containment"):
                            self.validator.validate_codex_compatibility_cases()
            prompt.write_text(original, encoding="utf-8")

    def test_validator_rejects_a_misdirected_internal_route(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shelly-codex-test-") as temporary:
            candidate = Path(temporary) / "shelly-stack"
            self.builder.build(candidate)
            mode = candidate / "skills" / "shelly-mode" / "SKILL.md"
            contents = mode.read_text(encoding="utf-8").replace(
                "[how](references/routed/how/workflow.md)",
                "[how](references/routed/why/workflow.md)",
                1,
            )
            mode.write_text(contents, encoding="utf-8")
            shared_skills = {
                path.parent.name for path in (candidate / "skills").glob("*/SKILL.md")
            }
            with mock.patch.object(self.validator, "CODEX_ROOT", candidate):
                with self.assertRaisesRegex(ValueError, "points to the wrong workflow"):
                    self.validator.validate_shelly_mode_routes(shared_skills)

    def test_plan_template_rejects_a_copied_relative_route(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shelly-codex-test-") as temporary:
            candidate = Path(temporary) / "shelly-stack"
            self.builder.build(candidate)
            plan = candidate / "skills" / "shelly-mode" / "playbooks" / "multi-phase-plan.md"
            contents = plan.read_text(encoding="utf-8").replace(
                "<shelly-mode-skill-dir>/references/routed/swarm/workflow.md",
                "../references/routed/swarm/workflow.md",
            )
            plan.write_text(contents, encoding="utf-8")
            with mock.patch.object(self.validator, "CODEX_ROOT", candidate):
                with self.assertRaisesRegex(ValueError, "breaks after the plan is copied"):
                    self.validator.validate_plan_template()

    def test_shelly_mode_bundles_internal_routes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shelly-codex-test-") as temporary:
            candidate = Path(temporary) / "shelly-stack"
            self.builder.build(candidate)
            routes = candidate / "skills" / "shelly-mode" / "references" / "routed"
            expected = self.builder.shelly_mode_route_names(
                {path.parent.name for path in (candidate / "skills").glob("*/SKILL.md")}
            )
            self.assertEqual({path.name for path in routes.iterdir()}, expected)
            self.assertFalse(any(routes.rglob("SKILL.md")))
            self.assertFalse(any(routes.rglob("openai.yaml")))

    def test_validator_rejects_an_optional_tool_bypass(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shelly-codex-test-") as temporary:
            candidate = Path(temporary) / "shelly-stack"
            self.builder.build(candidate)
            workflow = (
                candidate
                / "skills"
                / "shelly-mode"
                / "references"
                / "routed"
                / "architect"
                / "workflow.md"
            )
            workflow.write_text(
                workflow.read_text(encoding="utf-8") + "\nUse `update_plan` now.\n",
                encoding="utf-8",
            )
            with mock.patch.object(self.validator, "CODEX_ROOT", candidate):
                with self.assertRaisesRegex(ValueError, "optional-capability contract"):
                    self.validator.validate_optional_capabilities()

    def test_validator_rejects_an_unlinked_principle_alias(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shelly-codex-test-") as temporary:
            candidate = Path(temporary) / "shelly-stack"
            self.builder.build(candidate)
            playbook = candidate / "skills" / "shelly-mode" / "playbooks" / "feature.md"
            playbook.write_text(
                playbook.read_text(encoding="utf-8")
                + "\nUse the **sequence-verifiable-units** principle skill.\n",
                encoding="utf-8",
            )
            shared_skills = {
                path.parent.name for path in (candidate / "skills").glob("*/SKILL.md")
            }
            with mock.patch.object(self.validator, "CODEX_ROOT", candidate):
                with self.assertRaisesRegex(ValueError, "unlinked principle route"):
                    self.validator.validate_shelly_mode_routes(shared_skills)

    def test_validator_rejects_a_missing_internal_route(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shelly-codex-test-") as temporary:
            candidate = Path(temporary) / "shelly-stack"
            self.builder.build(candidate)
            route = (
                candidate
                / "skills"
                / "shelly-mode"
                / "references"
                / "routed"
                / "architect"
                / "workflow.md"
            )
            route.unlink()
            shared_skills = {
                path.parent.name for path in (candidate / "skills").glob("*/SKILL.md")
            }
            with mock.patch.object(self.validator, "CODEX_ROOT", candidate):
                with self.assertRaisesRegex(ValueError, "route lacks workflow.md"):
                    self.validator.validate_shelly_mode_routes(shared_skills)

    def test_validator_rejects_a_missing_linear_fallback(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shelly-codex-test-") as temporary:
            candidate = Path(temporary) / "shelly-stack"
            self.builder.build(candidate)
            ticket = candidate / "skills" / "ticket" / "SKILL.md"
            contents = ticket.read_text(encoding="utf-8").replace(
                "If none is available, stop before any Linear-dependent read or write",
                "If none is available, continue",
            )
            ticket.write_text(contents, encoding="utf-8")
            with mock.patch.object(self.validator, "CODEX_ROOT", candidate):
                with self.assertRaisesRegex(ValueError, "ticket must stop before Linear work"):
                    self.validator.validate_external_tool_preflight()

    def test_validator_rejects_missing_forge_repository_access(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shelly-codex-test-") as temporary:
            candidate = Path(temporary) / "shelly-stack"
            self.builder.build(candidate)
            playbook = (
                candidate
                / "skills"
                / "shelly-mode"
                / "playbooks"
                / "opening-a-pr.md"
            )
            playbook.write_text(
                playbook.read_text(encoding="utf-8").replace(
                    "gh repo view --json nameWithOwner",
                    "gh repo inspect",
                ),
                encoding="utf-8",
            )
            with mock.patch.object(self.validator, "CODEX_ROOT", candidate):
                with self.assertRaisesRegex(ValueError, "lacks forge preflight"):
                    self.validator.validate_external_tool_preflight()

    def test_validator_rejects_collapsed_app_connector_discovery(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shelly-codex-test-") as temporary:
            candidate = Path(temporary) / "shelly-stack"
            self.builder.build(candidate)
            why = candidate / "skills" / "why" / "SKILL.md"
            why.write_text(
                why.read_text(encoding="utf-8").replace(
                    "Never collapse all `codex_apps` tools into one connector",
                    "Collapse all `codex_apps` tools into one connector",
                ),
                encoding="utf-8",
            )
            with mock.patch.object(self.validator, "CODEX_ROOT", candidate):
                with self.assertRaisesRegex(ValueError, "distinguish product connectors"):
                    self.validator.validate_external_tool_preflight()

    def test_validator_rejects_github_watcher_on_origin(self) -> None:
        with tempfile.TemporaryDirectory(prefix="shelly-codex-test-") as temporary:
            candidate = Path(temporary) / "shelly-stack"
            self.builder.build(candidate)
            babysit = candidate / "skills" / "shelly-mode" / "playbooks" / "babysit.md"
            babysit.write_text(
                babysit.read_text(encoding="utf-8").replace(
                    "On Origin, do not run the GitHub-only helper",
                    "On Origin, run the GitHub-only helper",
                ),
                encoding="utf-8",
            )
            with mock.patch.object(self.validator, "CODEX_ROOT", candidate):
                with self.assertRaisesRegex(ValueError, "Origin-native status checks"):
                    self.validator.validate_authorization_and_runtime_contracts()


if __name__ == "__main__":
    unittest.main()
