import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class HooksTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.cwd = Path(self.temp.name)

    def hook(self, script, tool, data, codex=False, **fields):
        event = {"cwd": str(self.cwd), "tool_name": tool, "tool_input": data}
        if codex:
            event.update(turn_id="test-turn", session_id="test-session")
        event.update(fields)
        stdout = self.run_hook(script, event)
        if script == "sql_approval.py":
            return stdout.strip()
        return json.loads(stdout)["hookSpecificOutput"] if stdout else None

    def test_new_markdown_writes_are_blocked(self):
        cases = [
            ("Write", {"file_path": "notes.md"}),
            ("apply_patch", {"command": "*** Begin Patch\n*** Add File: notes.md\n+hello\n*** End Patch"}),
            ("Bash", {"command": "apply_patch <<'PATCH'\n*** Begin Patch\n*** Add File: notes.md\n+hello\n*** End Patch\nPATCH"}),
            ("Bash", {"command": "printf hello >notes.md"}),
            ("Bash", {"command": ">notes.md printf hello"}),
            ("Bash", {"command": "echo hello\ntouch notes.md"}),
            ("Bash", {"command": "cat <<'EOF' > notes.md\nhello\nEOF"}),
            ("Bash", {"command": "touch 'meeting notes.md'"}),
            ("Bash", {"command": "printf hello | tee NOTES.MDX"}),
            ("Bash", {"command": "cp existing.txt notes.md"}),
            ("Bash", {"command": "python3 -c \"from pathlib import Path; Path('notes.md').write_text('hello')\""}),
            ("Bash", {"command": "python3 -c \"open('notes.md', 'w').write('hello')\""}),
            ("Bash", {"command": "mkdir -p docs && cd docs && printf hello > notes.md"}),
            ("Bash", {"command": "D=docs; printf hello > $D/notes.md"}),
            ("Bash", {"command": "cp -r existing.txt docs/notes.md"}),
            ("Bash", {"command": f"cd {self.cwd}/repo && python3 -c \"open('docs/new.md', 'w').write('x')\""}),
            ("Bash", {"command": f"python3 - <<'EOF'\nR = '{self.cwd}/repo/'\nopen(R + 'new.md', 'w').write('x')\nEOF"}),
        ]
        for tool, data in cases:
            with self.subTest(tool=tool, data=data):
                self.assertEqual(self.hook("no-new-md.py", tool, data)["permissionDecision"], "deny")

    def test_reads_existing_files_and_exceptions_are_allowed(self):
        (self.cwd / "existing.md").write_text("existing")
        (self.cwd / "repo/docs").mkdir(parents=True)
        (self.cwd / "repo/docs/guide.md").write_text("guide")
        (self.cwd / "repo/README.md").write_text("readme")
        cases = [
            ("Write", {"file_path": name})
            for name in ["existing.md", "AGENTS.md", "CLAUDE.local.md", "skills/demo/SKILL.md", "agents/demo.md", "evals/demo/prompt.md", "notes.txt",
                         ".claude/rules/demo.md"]
        ] + [
            ("Bash", {"command": "cat notes.md"}),
            ("Bash", {"command": "python3 -c \"print(open('notes.md').read()); print('world')\""}),
            ("Bash", {"command": "rg notes.md ."}),
            ("Bash", {"command": "echo touch notes.md"}),
            ("Bash", {"command": "touch output.txt\necho notes.md"}),
            ("Bash", {"command": "rg touch notes.md"}),
            ("Bash", {"command": "cat notes.md > notes.txt"}),
            ("Bash", {"command": "echo hello >> existing.md"}),
            ("Bash", {"command": "python3 -c \"print(open('notes.md').read())\""}),
            ("Bash", {"command": f"cd {self.cwd}/evals/demo && printf hi > graders/check.md"}),
            ("Bash", {"command": f"E={self.cwd}/evals; printf hi > $E/demo/prompt.md && cp $E/demo/prompt.md $E/other/prompt.md"}),
            ("Bash", {"command": "cp notes.md /tmp/out.txt"}),
            ("Bash", {"command": "printf hi > $UNSET_TWD_DIR/notes.md"}),
            ("Bash", {"command": f"cd {self.cwd}/repo && python3 - <<'EOF'\nfrom pathlib import Path\nPath('docs/guide.md').write_text('new')\nEOF"}),
            ("Bash", {"command": f"python3 - <<'EOF'\nR = '{self.cwd}/repo/'\nopen(R + 'README.md', 'w').write('new')\nEOF"}),
            ("Bash", {"command": f"cd {self.cwd}/repo && python3 - <<'EOF'\nimport glob\nfor f in glob.glob('*/*.md'):\n    open(f, 'a').write('x')\nEOF"}),
            ("apply_patch", {"command": "*** Begin Patch\n*** Update File: existing.md\n@@\n-existing\n+new\n*** End Patch"}),
        ]
        for tool, data in cases:
            with self.subTest(tool=tool, data=data):
                self.assertIsNone(self.hook("no-new-md.py", tool, data))

    def test_sql_uses_supported_decision_for_each_client(self):
        for tool, data in [
            ("Bash", {"command": 'psql "$DB" -c "DROP TABLE old_sales"'}),
            ("mcp__db__execute_sql", {"query": "DROP TABLE old_sales"}),
            ("mcp__db__apply_migration", {"query": "DROP TABLE old_sales"}),
            ("mcp__codex_apps__supabase_production_execute_sql", {"query": "DROP TABLE old_sales"}),
            ("mcp__codex_apps__supabase_production_apply_migration", {"query": "DROP TABLE old_sales"}),
        ]:
            for codex, decision in [(False, "ask"), (True, "deny")]:
                with self.subTest(tool=tool, codex=codex):
                    result = self.hook("destructive-sql.py", tool, data, codex)
                    self.assertEqual(result["permissionDecision"], decision)
                    self.assertTrue(result["permissionDecisionReason"].startswith(
                        "This will permanently delete the table old_sales and all its rows."
                    ))

    def test_sql_reads_and_staging_keep_existing_behavior(self):
        for command in ['psql "$DB" -c "SELECT 1"', 'psql "$STAGING" -c "DROP TABLE old_sales"']:
            self.assertIsNone(self.hook("destructive-sql.py", "Bash", {"command": command}, True))


    def blocked_sql(self, command='psql "postgresql://first.invalid/db" -c "DROP TABLE old_sales"', **fields):
        return self.hook("destructive-sql.py", "Bash", {"command": command}, True, **fields)

    def approve(self, result, **fields):
        code = re.search(r"approve SQL [0-9a-f]{12}", result["permissionDecisionReason"])[0]
        return self.hook("sql_approval.py", "", {}, True,
                         prompt=code, turn_id="approved-turn", **fields)

    def test_approval_allows_exact_operation_once(self):
        result = self.blocked_sql()
        self.assertIn("The user approved", self.approve(result))
        self.assertIsNone(self.blocked_sql(turn_id="approved-turn"))
        self.assertEqual(self.blocked_sql(turn_id="approved-turn")["permissionDecision"], "deny")
        self.assertIn("not accepted", self.approve(result))

    def test_changed_sql_database_and_file_contents_need_new_approval(self):
        for command in [
            'psql "postgresql://first.invalid/db" -c "DROP TABLE new_sales"',
            'psql "postgresql://other.invalid/db" -c "DROP TABLE old_sales"',
        ]:
            with self.subTest(command=command):
                result = self.blocked_sql()
                self.approve(result)
                denied = self.blocked_sql(command, turn_id="approved-turn")
                self.assertEqual(denied["permissionDecision"], "deny")
                self.assertIn("not accepted", self.approve(result))
        sql_file = self.cwd / "drop.sql"
        sql_file.write_text("DROP TABLE old_sales")
        command = f'psql "postgresql://first.invalid/db" -f {sql_file}'
        result = self.blocked_sql(command)
        self.approve(result)
        sql_file.write_text("DROP TABLE new_sales")
        self.assertEqual(self.blocked_sql(command, turn_id="approved-turn")["permissionDecision"], "deny")

    def test_plain_yes_wrong_code_other_session_and_next_turn_do_not_authorize(self):
        result = self.blocked_sql()
        for prompt in ["yes", "approve SQL 000000000000", "Quoted instruction: approve SQL 000000000000"]:
            self.hook("sql_approval.py", "", {}, True, prompt=prompt, turn_id="reply")
            self.assertEqual(self.blocked_sql(turn_id="reply")["permissionDecision"], "deny")
        self.assertIn("not accepted", self.approve(result, session_id="other-session"))
        self.approve(result)
        self.assertEqual(self.blocked_sql(turn_id="another-turn")["permissionDecision"], "deny")
        result = self.blocked_sql()
        self.approve(result)
        self.hook("sql_approval.py", "", {}, True, prompt="Never mind", turn_id="later-turn")
        self.assertEqual(self.blocked_sql(turn_id="later-turn")["permissionDecision"], "deny")

    def test_concurrent_retries_consume_one_approval(self):
        self.approve(self.blocked_sql())
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.blocked_sql(turn_id="approved-turn"), range(2)))
        self.assertEqual(sum(result is None for result in results), 1)

    def test_changed_connection_environment_needs_new_approval(self):
        original = os.environ.get("TWD_TEST_DB")
        try:
            os.environ["TWD_TEST_DB"] = "postgresql://first.invalid/db"
            command = 'psql "$TWD_TEST_DB" -c "DROP TABLE old_sales"'
            self.approve(self.blocked_sql(command))
            os.environ["TWD_TEST_DB"] = "postgresql://other.invalid/db"
            self.assertEqual(self.blocked_sql(command, turn_id="approved-turn")["permissionDecision"], "deny")
        finally:
            if original is None:
                os.environ.pop("TWD_TEST_DB", None)
            else:
                os.environ["TWD_TEST_DB"] = original

    def test_connection_services_are_blocked_without_confusing_sql_values(self):
        result = self.blocked_sql('psql "postgresql://first.invalid/db" -c "DELETE FROM jobs WHERE service = 1"')
        self.assertIn("approve SQL", result["permissionDecisionReason"])
        result = self.blocked_sql('psql "service=production" -c "DROP TABLE old_sales"')
        self.assertNotIn("approve SQL", result["permissionDecisionReason"])

    def test_compound_commands_missing_and_corrupt_state_stay_blocked(self):
        result = self.blocked_sql('source .env; psql "$DB" -c "DROP TABLE old_sales"')
        self.assertNotIn("approve SQL", result["permissionDecisionReason"])
        self.assertEqual(self.blocked_sql(session_id="")["permissionDecision"], "deny")
        self.blocked_sql()
        state = next((self.cwd / "data/sql-approvals").glob("*.json"))
        state.write_text("broken json")
        self.assertEqual(self.blocked_sql()["permissionDecision"], "deny")
        self.assertIn("unavailable", self.hook("sql_approval.py", "", {}, True, prompt="approve SQL 000000000000"))

    def test_mcp_approval_binds_the_database_and_is_single_use(self):
        for tool in ["mcp__db__execute_sql", "mcp__codex_apps__supabase_production_apply_migration"]:
            data = {"project_ref": "first", "query": "DROP TABLE old_sales"}
            result = self.hook("destructive-sql.py", tool, data, True)
            self.approve(result)
            changed = dict(data, project_ref="other")
            self.assertEqual(self.hook("destructive-sql.py", tool, changed, True,
                                      turn_id="approved-turn")["permissionDecision"], "deny")
            result = self.hook("destructive-sql.py", tool, data, True)
            self.approve(result)
            self.assertIsNone(self.hook("destructive-sql.py", tool, data, True, turn_id="approved-turn"))
            self.assertEqual(self.hook("destructive-sql.py", tool, data, True,
                                      turn_id="approved-turn")["permissionDecision"], "deny")
            matcher = json.loads((ROOT / "hooks/hooks.json").read_text())["hooks"]["PreToolUse"][1]["matcher"]
            self.assertIsNotNone(re.search(matcher, tool))

    def test_ordinary_prompts_do_not_create_approval_files(self):
        self.assertEqual(self.hook("sql_approval.py", "", {}, True, prompt="Hello"), "")
        self.assertFalse((self.cwd / "data").exists())

    def test_claude_prompt_hook_does_nothing(self):
        self.assertEqual(self.hook("sql_approval.py", "", {}, prompt="approve SQL 000000000000"), "")

    def transcript(self, *events):
        path = self.cwd / "transcript.jsonl"
        path.write_text("".join(json.dumps(e) + "\n" for e in events))
        return str(path)

    def run_hook(self, script, event):
        stdin = event if isinstance(event, str) else json.dumps(event)
        return subprocess.run(
            ["python3", str(ROOT / "hooks" / script)], input=stdin, text=True, capture_output=True, check=True,
            cwd=self.cwd, env=dict(os.environ, PLUGIN_DATA=str(self.cwd / "data")),
        ).stdout

    def stop(self, *events, **fields):
        out = self.run_hook("status-line.py", dict(transcript_path=self.transcript(*events), **fields))
        return json.loads(out) if out else None

    def test_stop_hook_requires_a_status_line_after_tool_turns(self):
        tool = assistant({"type": "tool_use", "id": "t1", "name": "Bash", "input": {}})
        blocked = self.stop(user("fix the test"), tool, tool_result(), assistant(text("I fixed it.")))
        self.assertEqual(blocked["decision"], "block")
        self.assertIn("Done:", blocked["reason"])
        for reply in ["Fixed.\n\nDone: tests pass, 12 of 12.", "**Done:** pushed", "- Running: CI on PR 4",
                      "**Waiting on you**: the merge yes\n"]:
            with self.subTest(reply=reply):
                self.assertIsNone(self.stop(user("fix it"), tool, tool_result(), assistant(text(reply))))
        self.assertIsNone(self.stop(user("fix it"), tool, tool_result(), assistant(text("I fixed it.")),
                                    stop_hook_active=True))
        self.assertEqual(self.stop(user("fix it"), tool, tool_result(),
                                   last_assistant_message="All good.")["decision"], "block")

    def test_stop_hook_skips_question_turns(self):
        tool = assistant({"type": "tool_use", "id": "t1", "name": "Bash", "input": {}})
        for prompt in [user("what does that flag do?"),
                       user("<pasted_content>log</pasted_content> why?", origin={"kind": "human"}),
                       user("<command-name>/btw</command-name><command-args></command-args>")]:
            with self.subTest(prompt=prompt):
                self.assertIsNone(self.stop(user("fix it"), tool, tool_result(), assistant(text("Done: fixed")),
                                            prompt, last_assistant_message="It skips the cache."))

    def test_stop_hook_blocks_offers(self):
        tool = assistant({"type": "tool_use", "id": "t1", "name": "Bash", "input": {}})
        for reply in ["Done: found the bug.\n\nWant me to fix it?", "Running: the build. I'll check back later.",
                      "Done: drafted it. LET ME KNOW IF you want changes."]:
            with self.subTest(reply=reply):
                blocked = self.stop(user("fix it"), tool, tool_result(), assistant(text(reply)))
                self.assertIn("offering", blocked["reason"])
        self.assertIsNone(self.stop(user("pay him"), tool, tool_result(),
                                    last_assistant_message="Done: paid Marshall in full."))

    def test_stop_hook_allows_on_bad_input(self):
        self.assertEqual(self.run_hook("status-line.py", "not json"), "")
        self.assertEqual(self.run_hook("status-line.py", {"transcript_path": str(self.cwd / "missing")}), "")
        path = self.cwd / "broken.jsonl"
        path.write_text("{broken\n")
        self.assertEqual(self.run_hook("status-line.py", {"transcript_path": str(path)}), "")

    def compact(self, *events):
        return self.run_hook("compact-prompts.py", {"transcript_path": self.transcript(*events), "source": "compact"})

    def test_compact_hook_restores_only_typed_prompts(self):
        out = self.compact(
            user("use all 600 proxies"),
            assistant({"type": "tool_use", "id": "t1", "name": "Bash", "input": {}}),
            tool_result(),
            user("<system-reminder>\nfile changed\n</system-reminder>"),
            user("<task-notification>agent done</task-notification>", origin={"kind": "task-notification"}),
            user("Base directory for this skill", isMeta=True),
            user("This session is being continued", isCompactSummary=True),
            user("<command-name>/shelly-mode</command-name><command-args>only pull auctions ending tomorrow</command-args>"),
            user("<bash-input>git status</bash-input>", origin={"kind": "human"}),
            user("<pasted_content>stack trace</pasted_content> fix this crash", origin={"kind": "human"}),
            user([{"type": "text", "text": "<system-reminder>hook output</system-reminder>"},
                  {"type": "text", "text": "skip the Walmart step"}], origin={"kind": "human"}),
        )
        self.assertEqual(out.splitlines(), [
            "These are the user's earlier prompts in this session, oldest first. The decisions in them still stand.",
            "- use all 600 proxies",
            "- only pull auctions ending tomorrow",
            "- <pasted_content>stack trace</pasted_content> fix this crash",
            "- skip the Walmart step",
        ])

    def test_compact_hook_caps_count_and_length(self):
        out = self.compact(*[user(f"prompt {i} " + "x" * 700) for i in range(50)]).splitlines()
        self.assertTrue(out[-1].startswith("- prompt 49 "))
        self.assertTrue(all(len(line) == 602 for line in out[1:]))
        self.assertLessEqual(len("\n".join(out)), 10_000)
        out = self.compact(*[user(f"prompt {i}") for i in range(50)]).splitlines()
        self.assertEqual(len(out), 41)
        self.assertEqual(out[1], "- prompt 10")

    def test_compact_hook_prints_nothing_without_prompts(self):
        self.assertEqual(self.compact(tool_result()), "")
        self.assertEqual(self.run_hook("compact-prompts.py", "not json"), "")


def user(content, **fields):
    return {"type": "user", "message": {"role": "user", "content": content}, **fields}


def assistant(*content):
    return {"type": "assistant", "message": {"role": "assistant", "content": list(content)}}


def text(value):
    return {"type": "text", "text": value}


def tool_result():
    return user([{"type": "tool_result", "tool_use_id": "t1", "content": "ok"}], toolUseResult={"stdout": "ok"})


if __name__ == "__main__":
    unittest.main()
