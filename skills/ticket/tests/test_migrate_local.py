#!/usr/bin/env python3
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from harness import FakeGhCase  # noqa: E402

FRONT = "---\nid: {id}\ntitle: {title}\nstatus: {status}\nparent: {parent}\napp: {app}\ntype: Bug\npriority: High\nlabels: {labels}\nbranch:\npr:\ncreated: 2026-09-24\nupdated: 2026-09-24\n---\n"
TSV_HEAD = "ts\tphase\tdecision\twhy\tevidence\tresult\n"


def ticket(folder: Path, ident, title, status, body, parent="", app="ccg", labels="", tsv=""):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{ident}.md").write_text(FRONT.format(id=ident, title=title, status=status, parent=parent, app=app, labels=labels) + body)
    (folder / f"{ident}.tsv").write_text(TSV_HEAD + tsv)


class MigrateTest(FakeGhCase):
    def setUp(self):
        super().setUp()
        root = self.dir / "monorepo"
        (root / "apps" / "ccg").mkdir(parents=True)
        (root / "apps" / "product-research").mkdir()
        t = self.tickets = root / "tickets"
        ticket(t / "DEV-2", "DEV-2", "Every app gets its own role", "Done",
               "\nRoles for each app. Children DEV-2-1 and DEV-2-2 carry the work; DEV-9 is unrelated.\n\n## Log\n\n### 2026-09-24\n\nDecision recorded.\n",
               labels="Database", tsv="2026-09-23T10:00:00Z\tTriage\tmoved Triage to Need Human\tneeds a call\t\tNeed Human\n")
        ticket(t / "DEV-2", "DEV-2-1", "Atlas role", "In Review",
               "\nAtlas uses atlas_app. Blocked on DEV-2-2 and see `DEV-2-2` in code.\n\n## Log\n\n### 2026-09-25\n\nPR opened.\n",
               parent="DEV-2", tsv="2026-09-24T09:00:00Z\tReady for Agents\tmoved Ready for Agents to In Progress\tbuild started\t\tIn Progress\n"
                                   "2026-09-26T09:00:00Z\tIn Progress\tPick BYPASSRLS\tfewer policies\tplan appendix\tadopted\n")
        ticket(t / "DEV-2", "DEV-2-2", "CCG role", "Canceled", "\nNot needed.\n\n## Log\n", parent="DEV-2")
        (t / "DEV-2" / "DEV-2-1.plan.txt").write_text("step one\n")
        (t / "DEV-2" / "DEV-2-wizard.build-report.txt").write_text("wizard ran\n")
        (t / "DEV-2" / "DEV-2-2.plan.txt").write_text("never migrated\n")
        (t / "DEV-2" / "shot.png").write_bytes(b"\x89PNG\0\0")
        ticket(t / "DEV-3", "DEV-3", "Sentry sweep", "Done", "\nAll done.\n\n## Log\n")
        self.linear = self.dir / "linear.json"
        self.linear.write_text(json.dumps([
            {"id": "DEV-48", "title": "AI sheet review", "status": "Done", "statusType": "completed", "priority": "Urgent",
             "labels": ["Product Research", "Feature"], "parentId": None, "url": "https://linear.app/t/issue/DEV-48/ai", "description": "Epic.",
             "comments": []},
            {"id": "DEV-77", "title": "Per-source knowledge", "status": "Backlog", "statusType": "backlog", "priority": "No priority",
             "labels": ["Wave"], "parentId": "DEV-48", "url": "https://linear.app/t/issue/DEV-77/wave",
             "description": 'Part of <issue id="u1" href="https://linear.app/t/issue/DEV-48/ai">DEV-48</issue>, like '
                            '<issue id="u2" href="https://linear.app/t/issue/DEV-60/x">DEV-60</issue> and DEV-61. Built in '
                            '<pull-request id="p" href="https://linear.app/t/review/x">thirdwavediscounts/twd-apps-monorepo#238</pull-request>, '
                            '<pull-request id="q" href="https://github.com/thirdwavediscounts/twd-argus-engine/pull/9">argus 9</pull-request> and '
                            '<pull-request id="r" href="https://example.com/pr">elsewhere</pull-request>.',
             "comments": [{"createdAt": "2026-08-20T00:00:00Z", "author": "Sean", "body": "Second, see DEV-2."},
                          {"createdAt": "2026-08-19T00:00:00Z", "author": "Sean", "body": "First."}]},
            {"id": "DEV-90", "title": "Old", "status": "Canceled", "statusType": "canceled", "priority": "Low", "labels": [],
             "parentId": None, "url": "https://linear.app/t/issue/DEV-90/old", "description": "x", "comments": []},
        ]))
        self.plan_json = self.dir / "plan.json"
        self.mapping = self.dir / "mapping.json"

    def migrate(self, *extra, env=None):
        return self.run_script("migrate_local.py", "--tickets-dir", str(self.tickets), "--linear", str(self.linear),
                               "--repo", "thirdwavediscounts/twd-apps-monorepo", "--plan-json", str(self.plan_json),
                               "--mapping", str(self.mapping), "--pace", "0", *extra, env=env)

    def planned(self):
        return {i["key"]: i for i in json.loads(self.plan_json.read_text())["issues"]}

    def test_dry_run_plans_open_tickets_parents_first_and_writes_nothing(self):
        r = self.migrate()
        self.assertEqual(r.returncode, 0, r.stderr)
        plan = self.planned()
        self.assertEqual(list(plan), ["local:DEV-2", "local:DEV-2-1", "linear:DEV-48", "linear:DEV-77"])
        self.assertEqual(self.writes(), [])
        parent, child, epic, wave = plan.values()
        self.assertEqual((parent["close"], parent["labels"]), ("completed", ["sean", "priority:high", "app:ccg", "type:bug", "area:database"]))
        self.assertEqual((child["parent"], child["labels"][:2]), ("local:DEV-2", ["sean", "status:in-review"]))
        self.assertEqual(parent["body"], "Roles for each app. Children {{ref:local:DEV-2-1}} and DEV-2-2 carry the work; DEV-9 is unrelated.\n\n"
                                         "<sub>Migrated from local ticket DEV-2</sub>\n<!-- migrated:local:DEV-2 -->\n")
        self.assertEqual(parent["refs"]["unresolved"], ["DEV-2-2", "DEV-9"])
        self.assertIn("see `DEV-2-2` in code", child["body"])
        self.assertEqual(child["comments"][:3], [
            "**Status** · Ready → In Progress\n- Why: build started\n\n<sub>Local decision log, 2026-09-24T09:00:00Z</sub>",
            "PR opened.\n\n<sub>Local log entry, 2026-09-25</sub>",
            "**Decision** · status In Progress\nPick BYPASSRLS\n- Why: fewer policies\n- Evidence: plan appendix\n- Result: adopted\n\n<sub>Local decision log, 2026-09-26T09:00:00Z</sub>",
        ])
        self.assertEqual(child["comments"][3], "<details><summary>DEV-2-1.plan.txt</summary>\n\n```\nstep one\n```\n\n</details>")
        self.assertEqual(parent["inlined"], ["DEV-2-wizard.build-report.txt, 0 KB"])
        self.assertEqual(parent["skipped"], ["DEV-2/shot.png, binary, 0 KB"])
        self.assertEqual((epic["close"], epic["labels"], epic["parent"]), ("completed", ["sean", "priority:urgent", "app:product-research", "type:feature"], None))
        self.assertEqual(wave["parent"], "linear:DEV-48")
        self.assertEqual(wave["labels"], ["sean", "status:backlog"])
        self.assertEqual(wave["notes"], ["Linear label 'Wave' has no GitHub mapping"])
        self.assertTrue(wave["body"].startswith(
            "Part of {{ref:linear:DEV-48}}, like [DEV-60](https://linear.app/t/issue/DEV-60/x) and [DEV-61](https://linear.app/t/issue/DEV-61). "
            "Built in #238, thirdwavediscounts/twd-argus-engine#9 and [elsewhere](https://example.com/pr)."))
        self.assertEqual([c.split("\n")[0] for c in wave["comments"]], ["**Linear comment** · Sean · 2026-08-19", "**Linear comment** · Sean · 2026-08-20"])
        self.assertIn("see [DEV-2](https://linear.app/t/issue/DEV-2)", wave["comments"][1])
        self.assertIn("attachments skipped: 1 binary, 1 on closed local tickets", r.stdout)
        self.assertIn("left behind with closed local tickets: DEV-2/DEV-2-2.plan.txt", r.stdout)
        self.assertIn("sub-issues: 2", r.stdout)

    def test_execute_creates_links_resolves_and_resumes_after_a_crash(self):
        crashed = self.migrate("--execute", env={"FAKE_GH_FAIL_WRITE": "7"})
        self.assertEqual(crashed.returncode, 1)
        self.assertIn("injected failure", crashed.stderr)
        self.mapping.unlink()
        lost = self.migrate("--execute", env={"FAKE_GH_LOSE_RESPONSE": "11"})
        self.assertIn("after the write landed", lost.stderr)
        r = self.migrate("--execute")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.migrate("--execute").returncode, 0)
        issues = self.github()["issues"]
        self.assertEqual([(i["number"], i["title"]) for i in issues.values()],
                         [(1, "Every app gets its own role"), (2, "Atlas role"), (3, "AI sheet review"), (4, "Per-source knowledge")])
        self.assertEqual((issues["1"]["subs"], issues["3"]["subs"]), ([2], [4]))
        self.assertTrue(issues["1"]["body"].startswith("Roles for each app. Children #2 and DEV-2-2 carry the work"))
        self.assertTrue(issues["4"]["body"].startswith("Part of #3, like [DEV-60]"))
        self.assertEqual([(i["state"], i["state_reason"]) for i in issues.values()],
                         [("closed", "completed"), ("open", None), ("closed", "completed"), ("open", None)])
        self.assertEqual([len(i["comments"]) for i in issues.values()], [4, 4, 0, 2])
        self.assertEqual(issues["2"]["comments"][0], "**Status** · Ready → In Progress\n- Why: build started\n\n"
                                                     "<sub>Local decision log, 2026-09-24T09:00:00Z</sub>\n\n<!-- migrated:local:DEV-2-1:c0 -->")


if __name__ == "__main__":
    unittest.main()
