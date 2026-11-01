#!/usr/bin/env python3
"""The secscan patch is applied to a private copy and RUN, not merely read (Dmitri, 2026-11-01).

`scripts/patches/secscan-working-dir-like.patch` adds `--working-dir-like` to `~/LLM/tools/secscan.py`,
the credential sweeper outside this repository. The 2026-10-30 report claimed the four lines would
reach the wake runs; nobody ran them afterwards, and a patch nobody applies is a paragraph.

So these tests do three things and refuse to fake any of them:

  1. the patch file parses as a diff and names the selector it claims to add;
  2. it applies — `patch -p1` — to the tool as it is actually installed on this machine;
  3. the *patched* tool, run against a synthetic session store, selects sessions by working
     directory only, redacts only those, and leaves another participant's rows untouched.

Test 3 rewrites the two paths the tool hardcodes (the store and the credential file) to point at
temp fixtures, so no real session store is opened and no real credential is loaded. When the tool
is not installed at all — as on CI — every test that needs it skips, with the reason in the skip
message, rather than passing silently on nothing.

Run directly (`python3 tests/test_secscan_working_dir_patch.py`); pytest is not installed.
"""

import hashlib
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "scripts" / "patches" / "secscan-working-dir-like.patch"
TOOL = Path.home() / "LLM" / "tools" / "secscan.py"

DB_LINE = 'DB = f"{HOME}/.local/share/goose/sessions/sessions.db"'
ENV_LINE = 'for line in open(f"{HOME}/LLM/desi-bot/bot.env")'


def have_tool():
    return TOOL.is_file() and "ttyd" not in ""  # presence only; content checked where it matters


def apply_patch(src_text, workdir):
    """Apply PATCH to `src_text` placed at workdir/secscan.py. Returns (ok, text, message)."""
    target = Path(workdir) / "secscan.py"
    target.write_text(src_text)
    proc = subprocess.run(["patch", "-p1", "-i", str(PATCH)], cwd=workdir,
                          capture_output=True, text=True)
    return proc.returncode == 0, target.read_text(), (proc.stdout + proc.stderr).strip()


class PatchFileTest(unittest.TestCase):
    def test_the_patch_is_a_diff_that_adds_the_wake_selector(self):
        text = PATCH.read_text()
        self.assertIn("--- a/secscan.py", text)
        self.assertIn("+++ b/secscan.py", text)
        self.assertIn('ap.add_argument("--working-dir-like"', text)
        self.assertIn("sessions WHERE working_dir LIKE ?", text)
        # the guard must learn the new selector too, or the tool exits "nothing to do" on it
        self.assertIn("a.working_dir_like or a.rotating_logs", text)

    def test_the_patch_records_the_base_it_was_cut_against(self):
        header = PATCH.read_text().split("--- a/")[0]
        self.assertRegex(header, r"Base-sha256: [0-9a-f]{64}")
        self.assertIn("Apply:", header)


@unittest.skipUnless(TOOL.is_file(), f"not installed on this machine: {TOOL}")
class AppliesToInstalledToolTest(unittest.TestCase):
    def setUp(self):
        self.installed = TOOL.read_text()

    def test_it_applies_or_is_already_applied(self):
        if "--working-dir-like" in self.installed:
            self.skipTest("the installed tool already carries --working-dir-like; patch is spent")
        with tempfile.TemporaryDirectory() as d:
            ok, text, msg = apply_patch(self.installed, d)
            self.assertTrue(ok, msg)
            self.assertIn("--working-dir-like", text)

    def test_drift_is_named_not_silently_tolerated(self):
        """A stale base must fail loudly here: a patch that no longer applies is a dead instruction."""
        header = PATCH.read_text().split("--- a/")[0]
        recorded = re.search(r"Base-sha256: ([0-9a-f]{64})", header).group(1)
        if "--working-dir-like" in self.installed:
            self.skipTest("already applied; there is no base left to compare")
        actual = hashlib.sha256(self.installed.encode()).hexdigest()
        self.assertEqual(recorded, actual,
                         "~/LLM/tools/secscan.py has changed since the patch was cut; "
                         "re-cut scripts/patches/secscan-working-dir-like.patch against the new base")


@unittest.skipUnless(TOOL.is_file(), f"not installed on this machine: {TOOL}")
class PatchedToolRunsTest(unittest.TestCase):
    """Run the patched tool on a synthetic store: does the selector do what the report said?"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        installed = TOOL.read_text()
        if DB_LINE not in installed or ENV_LINE not in installed:
            self.skipTest("the tool no longer hardcodes the store/credential paths this fixture rewrites")
        # the example the patch's own docstring prints: the fixture must be reachable by it,
        # or the instruction and the code disagree and one of them is wrong.
        self.pattern = re.search(r"--working-dir-like '([^']+)'", PATCH.read_text()).group(1)
        self.assertTrue(self.pattern.startswith("%") and self.pattern.endswith("%"), self.pattern)
        if "--working-dir-like" in installed:
            self.patched = installed
        else:
            ok, text, msg = apply_patch(installed, self.tmp)
            self.assertTrue(ok, msg)
            self.patched = text

        # --- fixtures: a store with a named session, a CLI Session wake run, and another amigo
        self.db = Path(self.tmp) / "sessions.db"
        con = sqlite3.connect(self.db)
        con.execute("CREATE TABLE sessions (id TEXT, name TEXT, working_dir TEXT)")
        con.execute("CREATE TABLE messages (session_id TEXT, content_json TEXT)")
        secret = "sk-fixture-0123456789"
        rows = [
            ("20261013_4", "Dmitri #03", "/Users/x/LLM/dmitri-bot", secret),           # named, mine
            ("20261012_33", "CLI Session",
             "/Users/x/LLM/dmitri-bot/tick-state/runs/20261012T0459Z-aa", secret),     # a wake, mine
            ("20261029_24", "Gwen #01", "/Users/x/LLM/gwen-bot", secret),              # NOT mine
        ]
        for sid, name, wd, s in rows:
            con.execute("INSERT INTO sessions VALUES (?,?,?)", (sid, name, wd))
            con.execute("INSERT INTO messages VALUES (?,?)",
                        (sid, '{"content": "export DEEPSEEK_API_KEY=' + s + '"}'))
        con.commit()
        con.close()

        env = Path(self.tmp) / "bot.env"
        env.write_text("DEEPSEEK_API_KEY=sk-fixture-0123456789\n")

        self.tool = Path(self.tmp) / "scan.py"
        self.tool.write_text(
            self.patched
            .replace(DB_LINE, f'DB = "{self.db}"')
            .replace(ENV_LINE, f'for line in open("{env}")')
        )

    def run_tool(self, *args):
        return subprocess.run([sys.executable, str(self.tool)] + list(args),
                              capture_output=True, text=True)

    def test_a_working_dir_pattern_reaches_the_wake_run(self):
        r = self.run_tool("scan", "--working-dir-like", self.pattern)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("2 session(s) selected", r.stdout, r.stdout)
        self.assertIn("total message rows with a literal: 2", r.stdout, r.stdout)
        self.assertNotIn("Gwen", r.stdout, "the selector reached a session that is not mine")

    def test_the_name_pattern_alone_misses_the_wake_run(self):
        """The defect the patch exists for, reproduced: by name, one session; by dir, two."""
        r = self.run_tool("scan", "--name-like", "Dmitri%")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("1 session(s) selected", r.stdout, r.stdout)

    def test_redact_clears_mine_and_leaves_another_amigos_rows_alone(self):
        r = self.run_tool("redact", "--working-dir-like", self.pattern)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("rows still containing a literal: 0", r.stdout, r.stdout)
        con = sqlite3.connect(self.db)
        gwen = con.execute("SELECT count(*) FROM messages WHERE session_id='20261029_24' "
                           "AND instr(content_json,'sk-fixture-0123456789')>0").fetchone()[0]
        con.close()
        self.assertEqual(gwen, 1, "redaction touched a session it was not pointed at")

    def test_the_patched_tool_still_refuses_to_scan_nothing(self):
        r = self.run_tool("scan")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--working-dir-like", r.stderr, r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
