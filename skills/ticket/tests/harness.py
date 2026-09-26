import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
FAKE_GH_DIR = SKILL / "tests" / "fake_gh"


class FakeGhCase(unittest.TestCase):
    """Each test gets an empty fake GitHub repo and a PATH whose gh is the fake."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.state = self.dir / "gh-state.json"
        self.log = self.dir / "gh-calls.jsonl"
        self.env = {k: v for k, v in os.environ.items() if k != "TICKETS_REPO"}
        self.env.update(PATH=f"{FAKE_GH_DIR}{os.pathsep}{os.environ['PATH']}", FAKE_GH_STATE=str(self.state),
                        FAKE_GH_LOG=str(self.log), TICKETS_REPO="acme/widgets")

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, script, *args, stdin="", cwd=None, env=None):
        return subprocess.run([sys.executable, str(SKILL / "scripts" / script), *args], input=stdin, capture_output=True,
                              text=True, cwd=cwd or self.dir, env={**self.env, **(env or {})})

    def github(self):
        return json.loads(self.state.read_text()) if self.state.exists() else {"issues": {}, "labels": []}

    def issue(self, number):
        return self.github()["issues"][str(number)]

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def writes(self):
        return [c for c in self.calls() if c["args"][0] == "api" and "-X" in c["args"] and c["args"][c["args"].index("-X") + 1] != "GET"]
