#!/usr/bin/env python3
import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from harness import FakeGhCase  # noqa: E402

BODY = "Partial refunds are booked as full returns, so the returns queue overcounts. Fix the classifier.\n\n## Acceptance\n\n- [ ] A partial refund stays in sales.\n"


class TicketsTest(FakeGhCase):
    def tickets(self, *args, stdin=BODY, **kw):
        return self.run_script("tickets.py", *args, stdin=stdin, **kw)

    def new(self, title, *args):
        r = self.tickets("new", "--title", title, *args)
        self.assertEqual(r.returncode, 0, r.stderr)
        return int(r.stdout.split()[0].lstrip("#"))

    def test_new_sub_issue_gets_labels_attachment_and_parent_link(self):
        parent = self.new("Partial refunds are booked as full returns", "--type", "Bug", "--priority", "High")
        report = self.dir / "plan.txt"
        report.write_text("step 1 ```sql``` inside\nstep 2\n")
        r = self.tickets("new", "--title", "Classifier keeps partial refunds in sales", "--parent", f"#{parent}", "--app", "ccg",
                         "--type", "bug", "--priority", "medium", "--labels", "area:database", "--status", "Ready", "--attach", str(report))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, "#2 https://github.com/acme/widgets/issues/2\n")
        child = self.issue(2)
        self.assertEqual(child["labels"], ["sean", "status:ready", "app:ccg", "type:bug", "priority:medium", "area:database"])
        self.assertEqual(child["body"], BODY.strip() + "\n\n<details><summary>plan.txt</summary>\n\n````\nstep 1 ```sql``` inside\nstep 2\n````\n\n</details>\n")
        self.assertEqual(self.issue(parent)["subs"], [2])
        self.assertEqual(child["parent"], parent)

    def test_new_refuses_binary_attachment_and_lint_failures_without_writing(self):
        png = self.dir / "shot.png"
        png.write_bytes(b"\x89PNG\r\n\x1a\n\0\0")
        r = self.tickets("new", "--title", "Shot", "--attach", str(png))
        self.assertEqual(r.returncode, 1)
        self.assertIn("Commit it to a branch and link it", r.stderr)
        r = self.tickets("new", "--title", "Dashy", stdin=BODY + "\nBlocked by DEV-7 — for now.\n")
        self.assertEqual(r.returncode, 1)
        self.assertIn("em or en dash", r.stderr)
        self.assertIn("ticket reference DEV-7", r.stderr)
        self.assertEqual(self.writes(), [])

    def test_status_moves_swap_one_label_close_and_reopen(self):
        n = self.new("Partial refunds", "--app", "ccg")
        self.assertEqual(self.tickets("status", str(n), "In Progress", "--why", "build started").returncode, 0)
        self.assertEqual(self.issue(n)["labels"], ["sean", "app:ccg", "status:in-progress"])
        r = self.tickets("status", str(n), "done", "--why", "merged", "--evidence", "merge commit abc123")
        self.assertEqual(r.stdout, "#1 In Progress -> Done\n")
        self.assertEqual((self.issue(n)["state"], self.issue(n)["state_reason"], self.issue(n)["labels"]), ("closed", "completed", ["sean", "app:ccg"]))
        self.tickets("status", str(n), "Canceled", "--why", "duplicate of #9")
        self.assertEqual(self.issue(n)["state_reason"], "not_planned")
        self.tickets("status", str(n), "status:triage", "--why", "reopened by Sean")
        self.assertEqual((self.issue(n)["state"], self.issue(n)["labels"]), ("open", ["sean", "app:ccg", "status:triage"]))
        self.assertEqual(self.issue(n)["comments"], [
            "**Status** · Triage → In Progress\n- Why: build started",
            "**Status** · In Progress → Done\n- Why: merged\n- Evidence: merge commit abc123",
            "**Status** · Done → Canceled\n- Why: duplicate of #9",
            "**Status** · Canceled → Triage\n- Why: reopened by Sean",
        ])
        r = self.tickets("status", str(n), "Doing", "--why", "x")
        self.assertIn("unknown status 'Doing'", r.stderr)

    def test_set_comments_branch_and_pr_and_edits_fields(self):
        n = self.new("Partial refunds", "--app", "ccg", "--priority", "low")
        r = self.tickets("set", str(n), "branch=sean/partial-refunds", "pr=https://github.com/acme/widgets/pull/7",
                         "app=home", "priority=Urgent", "labels=area:database", "title=Partial refunds stay in sales")
        self.assertEqual(r.returncode, 0, r.stderr)
        issue = self.issue(n)
        self.assertEqual(issue["title"], "Partial refunds stay in sales")
        self.assertEqual(issue["labels"], ["sean", "status:triage", "app:home", "priority:urgent", "area:database"])
        self.assertEqual(issue["comments"], ["**Branch** · `sean/partial-refunds`\n**PR** · https://github.com/acme/widgets/pull/7"])
        self.assertIn("bad field", self.tickets("set", str(n), "owner=me").stderr)

    def test_log_and_comment(self):
        n = self.new("Partial refunds")
        self.tickets("status", str(n), "In Progress", "--why", "build started")
        r = self.tickets("log", str(n), "--decision", "Classify by refund_price, not refund count", "--why", "counts miss partials",
                         "--evidence", "order 42 on staging", "--result", "classifier rewritten")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.tickets("comment", str(n), stdin="Reproduced on staging with order 42.\n").returncode, 0)
        r = self.tickets("comment", str(n), stdin="Fixed it — done.")
        self.assertIn("em or en dash", r.stderr)
        self.assertEqual(self.issue(n)["comments"][1:], [
            "**Decision** · status In Progress\nClassify by refund_price, not refund count\n- Why: counts miss partials\n- Evidence: order 42 on staging\n- Result: classifier rewritten",
            "Reproduced on staging with order 42.",
        ])

    def test_show_prints_body_comments_subs_parent_and_prs(self):
        parent = self.new("Refund tracker")
        child = self.new("Classifier", "--parent", str(parent), "--status", "In Review")
        self.new("Backfill", "--parent", str(parent))
        self.tickets("status", "3", "Done", "--why", "merged")
        state = self.github()
        state["issues"][str(parent)]["prs"] = [55]
        self.state.write_text(json.dumps(state))
        out = self.tickets("show", f"#{parent}").stdout
        self.assertEqual(out.splitlines()[:8], [
            "#1 Refund tracker",
            "status: Triage",
            "labels: sean, status:triage",
            "url: https://github.com/acme/widgets/issues/1",
            "parent: none",
            "pr: #55 https://github.com/acme/widgets/pull/55",
            "sub-issue: #2\tIn Review\tClassifier",
            "sub-issue: #3\tDone\tBackfill",
        ])
        self.assertIn("Partial refunds are booked as full returns", out)
        self.assertIn("parent: #1 Refund tracker", self.tickets("show", str(child)).stdout)
        self.assertIn("**Status** · Triage → Done", self.tickets("show", "3").stdout)

    def test_list_filters_open_sean_issues_by_status_and_app(self):
        self.new("One", "--app", "ccg", "--priority", "high")
        self.new("Two", "--app", "home", "--status", "Ready")
        self.new("Three", "--app", "ccg")
        self.tickets("status", "3", "Done", "--why", "merged")
        state = self.github()
        state["issues"]["4"] = {**state["issues"]["1"], "number": 4, "id": 9004, "title": "Someone else", "labels": ["status:triage"]}
        self.state.write_text(json.dumps(state))
        self.assertEqual(self.tickets("list").stdout.splitlines(), [
            "number\tstatus\tapp\tpriority\ttitle", "#1\tTriage\tccg\thigh\tOne", "#2\tReady\thome\t\tTwo"])
        self.assertEqual(self.tickets("list", "--status", "Ready", "--status", "Done").stdout.splitlines()[1:], [
            "#2\tReady\thome\t\tTwo", "#3\tDone\tccg\t\tThree"])
        self.assertEqual(self.tickets("list", "--app", "ccg").stdout.splitlines()[1:], ["#1\tTriage\tccg\thigh\tOne"])

    def test_check_lints_the_live_body_and_status_labels(self):
        n = self.new("Partial refunds")
        self.assertEqual(self.tickets("check", str(n)).stdout, "#1 clean\n")
        state = self.github()
        state["issues"]["1"]["body"] += "\nSee DEV-12 for the backfill.\n"
        self.state.write_text(json.dumps(state))
        r = self.tickets("check", str(n))
        self.assertEqual(r.returncode, 1)
        self.assertIn("ticket reference DEV-12", r.stderr)
        state["issues"]["1"]["body"] = BODY
        state["issues"]["1"]["labels"] += ["status:ready"]
        self.state.write_text(json.dumps(state))
        self.assertIn("needs exactly one", self.tickets("check", str(n)).stderr)

    def test_labels_ensure_creates_only_missing_and_is_idempotent(self):
        repo = self.dir / "repo"
        (repo / "apps" / "ccg").mkdir(parents=True)
        (repo / "apps" / "home").mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        self.state.write_text('{"repo": "", "next": 1, "issues": {}, "labels": ["sean", "bug"], "writes": 0}')
        first = self.tickets("labels", "--ensure", cwd=repo)
        self.assertEqual(first.stdout, "19 missing, 1 already present\n")
        labels = self.github()["labels"]
        self.assertIn("status:verifying-live", labels)
        self.assertIn("app:home", labels)
        self.assertIn("area:database", labels)
        self.assertEqual(self.tickets("labels", "--ensure", cwd=repo).stdout, "0 missing, 20 already present\n")

    def test_dry_run_prints_calls_and_writes_nothing(self):
        n = self.new("Partial refunds")
        before = len(self.writes())
        r = self.tickets("new", "--title", "Child", "--parent", str(n), "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("gh api -X POST repos/acme/widgets/issues --input - <<'JSON'", r.stdout)
        self.assertIn('"title": "Child"', r.stdout)
        self.assertIn('gh api -X POST repos/acme/widgets/issues/1/sub_issues --input -', r.stdout)
        self.assertIn('"sub_issue_id": "<id of the new issue>"', r.stdout)
        r = self.tickets("status", str(n), "Done", "--why", "merged", "--dry-run")
        self.assertIn('"state_reason": "completed"', r.stdout)
        self.assertIn("gh api -X POST repos/acme/widgets/issues/1/comments", r.stdout)
        self.tickets("set", str(n), "pr=https://x/pull/1", "--dry-run")
        self.tickets("log", str(n), "--decision", "d", "--why", "w", "--dry-run")
        self.tickets("comment", str(n), "--dry-run", stdin="Seen on staging.")
        self.tickets("labels", "--ensure", "--dry-run")
        self.assertEqual(len(self.writes()), before)
        self.assertEqual(self.issue(n)["comments"], [])

    def test_repo_comes_from_flag_then_env_then_origin_remote(self):
        repo = self.dir / "clone"
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "remote", "add", "origin", "git@github.com:thirdwave/monorepo.git"], check=True)
        del self.env["TICKETS_REPO"]
        r = self.tickets("list", cwd=self.dir)
        self.assertEqual(r.returncode, 1)
        self.assertIn("no --repo, no TICKETS_REPO", r.stderr)
        dry = [self.tickets("new", "--title", "A", "--dry-run", cwd=repo, env=e).stdout for e in ({}, {"TICKETS_REPO": "env/repo"})]
        self.assertIn("repos/thirdwave/monorepo/issues", dry[0])
        self.assertIn("repos/env/repo/issues", dry[1])
        flagged = self.tickets("new", "--title", "A", "--dry-run", "--repo", "flag/repo", cwd=repo, env={"TICKETS_REPO": "env/repo"})
        self.assertIn("repos/flag/repo/issues", flagged.stdout)


if __name__ == "__main__":
    unittest.main()
