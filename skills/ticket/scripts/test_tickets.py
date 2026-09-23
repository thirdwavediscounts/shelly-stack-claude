#!/usr/bin/env python3
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent / "tickets.py"
BODY = "Partial refunds are booked as full returns, so the returns queue overcounts. Fix the classifier.\n\n## Acceptance\n\n- [ ] A partial refund stays in sales.\n"


def git(cwd, *args):
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True)


def run(cwd, *args, stdin=BODY):
    env = {k: v for k, v in os.environ.items() if k != "TICKETS_ROOT"}
    return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=cwd, input=stdin, capture_output=True, text=True, env=env)


class TicketsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        git(self.repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "init")

    def tearDown(self):
        self.tmp.cleanup()

    def ignore(self):
        (self.repo / ".gitignore").write_text("tickets/\n")

    def test_refuses_when_tickets_would_be_tracked(self):
        r = run(self.repo, "new", "--title", "Partial refunds")
        self.assertEqual(r.returncode, 1)
        self.assertIn("would be tracked by git", r.stderr)
        self.assertFalse((self.repo / "tickets").exists())

    def test_ids_subtickets_index_and_log(self):
        self.ignore()
        (self.repo / "tickets" / "DEV-182").mkdir(parents=True)
        r = run(self.repo, "new", "--title", "Partial refunds", "--app", "ccg", "--type", "Bug")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(r.stdout.startswith("DEV-183 "))
        self.assertEqual(run(self.repo, "new", "--title", "Classifier", "--parent", "DEV-183").stdout.split()[0], "DEV-183-1")
        self.assertEqual(run(self.repo, "new", "--title", "Backfill", "--parent", "DEV-183").stdout.split()[0], "DEV-183-2")

        self.assertEqual(run(self.repo, "status", "DEV-183", "In Progress", "--why", "build started").returncode, 0)
        self.assertEqual(run(self.repo, "set", "DEV-183", "branch=sean/partial-refunds", "pr=https://github.com/o/r/pull/7").returncode, 0)

        index = (self.repo / "tickets" / "index.tsv").read_text().splitlines()
        self.assertEqual(index[0], "id\ttitle\tstatus\tparent\tapp\tbranch\tpr\tupdated")
        self.assertEqual([row.split("\t")[:7] for row in index[1:]], [
            ["DEV-183", "Partial refunds", "In Progress", "", "ccg", "sean/partial-refunds", "https://github.com/o/r/pull/7"],
            ["DEV-183-1", "Classifier", "Triage", "DEV-183", "", "", ""],
            ["DEV-183-2", "Backfill", "Triage", "DEV-183", "", "", ""],
        ])

        log = (self.repo / "tickets" / "DEV-183" / "DEV-183.tsv").read_text().splitlines()
        self.assertEqual(log[0], "ts\tphase\tdecision\twhy\tevidence\tresult")
        self.assertEqual([row.split("\t")[1:3] for row in log[1:]], [
            ["Triage", "created"],
            ["In Progress", "moved Triage to In Progress"],
            ["In Progress", "set branch"],
            ["In Progress", "set pr"],
        ])
        self.assertTrue((self.repo / "tickets" / "DEV-183" / "DEV-183-1.tsv").exists())

    def test_first_ticket_is_dev_1(self):
        self.ignore()
        self.assertEqual(run(self.repo, "new", "--title", "First").stdout.split()[0], "DEV-1")

    def test_rejects_bad_status_and_lint_failures(self):
        self.ignore()
        run(self.repo, "new", "--title", "Partial refunds")
        r = run(self.repo, "status", "DEV-1", "Doing", "--why", "x")
        self.assertEqual(r.returncode, 1)
        self.assertIn("unknown status", r.stderr)
        r = run(self.repo, "comment", "DEV-1", stdin="Fixed it — done.")
        self.assertEqual(r.returncode, 1)
        self.assertIn("em or en dash", r.stderr)
        self.assertNotIn("Fixed it", (self.repo / "tickets" / "DEV-1" / "DEV-1.md").read_text())

    def test_comment_lands_in_log_section(self):
        self.ignore()
        run(self.repo, "new", "--title", "Partial refunds")
        self.assertEqual(run(self.repo, "comment", "DEV-1", stdin="Reproduced on staging with order 42.").returncode, 0)
        text = (self.repo / "tickets" / "DEV-1" / "DEV-1.md").read_text()
        log_section = text.split("\n## Log\n", 1)[1]
        self.assertIn("Reproduced on staging with order 42.", log_section)
        self.assertEqual(run(self.repo, "check", "DEV-1").returncode, 0)

    def test_worktree_writes_to_main_checkout(self):
        self.ignore()
        wt = Path(self.tmp.name) / "wt"
        git(self.repo, "worktree", "add", "-q", "-b", "sean/x", str(wt))
        r = run(wt, "new", "--title", "From a worktree")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.repo / "tickets" / "DEV-1" / "DEV-1.md").exists())
        self.assertFalse((wt / "tickets").exists())


if __name__ == "__main__":
    unittest.main()
