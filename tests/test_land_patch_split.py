"""The splitter earns its keep only if one stale hunk really does not take the good files with it.

Run: python3 tests/test_land_patch_split.py

Everything here happens in a throwaway git repo built in a temp dir, because the property under test
is about `git apply`'s atomicity and nothing about this repository's contents.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import land_patch_split as lp  # noqa: E402


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


class SplitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.email", "t@example.invalid")
        git(self.repo, "config", "user.name", "test")
        (self.repo / "a.txt").write_text("one\ntwo\nthree\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "base")

    def tearDown(self):
        self.tmp.cleanup()

    def _patch(self, text):
        p = self.repo.parent / f"changes-{len(list(self.repo.parent.glob('changes-*')))}.patch"
        p.write_text(text)
        return p

    def test_one_stale_hunk_does_not_discard_the_other_file(self):
        # b.txt is new (always applies); a.txt's hunk expects text that is no longer there.
        patch = self._patch(
            "diff --git a/a.txt b/a.txt\n"
            "--- a/a.txt\n"
            "+++ b/a.txt\n"
            "@@ -1,3 +1,3 @@\n"
            " one\n"
            "-WRONG\n"
            "+TWO\n"
            " three\n"
            "diff --git a/b.txt b/b.txt\n"
            "new file mode 100644\n"
            "--- /dev/null\n"
            "+++ b/b.txt\n"
            "@@ -0,0 +1 @@\n"
            "+new file\n"
        )
        # The whole-patch apply, which is what the lander does today, lands nothing.
        self.assertNotEqual(git(self.repo, "apply", "--check", str(patch)).returncode, 0)

        result = lp.process(patch, self.repo, apply=True, verbose=False)
        status = {f["path"]: f["status"] for f in result["files"]}
        self.assertEqual(status["b.txt"], "applies")
        self.assertEqual(status["a.txt"], "failed")
        self.assertTrue((self.repo / "b.txt").exists(), "the recoverable file was not written")
        self.assertEqual((self.repo / "a.txt").read_text(), "one\ntwo\nthree\n",
                         "the stale file was modified anyway")

    def test_dry_run_writes_nothing(self):
        patch = self._patch(
            "diff --git a/c.txt b/c.txt\n"
            "new file mode 100644\n"
            "--- /dev/null\n"
            "+++ b/c.txt\n"
            "@@ -0,0 +1 @@\n"
            "+dry\n"
        )
        result = lp.process(patch, self.repo, apply=False, verbose=False)
        self.assertEqual(result["files"][0]["status"], "applies")
        self.assertFalse((self.repo / "c.txt").exists())

    def test_ledger_appends_only_ids_it_does_not_hold(self):
        ledger = self.repo / lp.LEDGER
        ledger.parent.mkdir(parents=True)
        first = {"id": "2026-1", "title": "old"}
        ledger.write_text(json.dumps(first) + "\n")
        dup = json.dumps(first)
        new = json.dumps({"id": "2026-2", "title": "new"})
        patch = self._patch(
            f"diff --git a/{lp.LEDGER} b/{lp.LEDGER}\n"
            f"--- a/{lp.LEDGER}\n"
            f"+++ b/{lp.LEDGER}\n"
            "@@ -1,1 +1,3 @@\n"
            f" {dup}\n"
            f"+{dup}\n"
            f"+{new}\n"
        )
        result = lp.process(patch, self.repo, apply=True, verbose=False)
        entry = result["files"][0]
        self.assertEqual(entry["status"], "ledger")
        self.assertEqual(entry["rows_added"], 1)
        self.assertEqual(entry["rows_duplicate"], 1)
        lines = [l for l in ledger.read_text().splitlines() if l.strip()]
        self.assertEqual(len(lines), 2, "the ledger holds a duplicate row after repair")
        self.assertEqual(json.loads(lines[1])["id"], "2026-2")

    def test_ledger_repair_survives_a_missing_trailing_newline(self):
        ledger = self.repo / lp.LEDGER
        ledger.parent.mkdir(parents=True)
        ledger.write_text(json.dumps({"id": "2026-1"}))  # no newline
        row = json.dumps({"id": "2026-2"})
        patch = self._patch(
            f"diff --git a/{lp.LEDGER} b/{lp.LEDGER}\n"
            f"--- a/{lp.LEDGER}\n"
            f"+++ b/{lp.LEDGER}\n"
            "@@ -1,1 +1,2 @@\n"
            "+" + row + "\n"
        )
        lp.process(patch, self.repo, apply=True, verbose=False)
        lines = [l for l in ledger.read_text().splitlines() if l.strip()]
        self.assertEqual([json.loads(l)["id"] for l in lines], ["2026-1", "2026-2"],
                         "a missing trailing newline glued two rows together")

    def test_split_keeps_each_file_whole(self):
        text = (
            "diff --git a/x b/x\n--- a/x\n+++ b/x\n@@ -1 +1 @@\n-a\n+b\n"
            "diff --git a/y b/y\n--- a/y\n+++ b/y\n@@ -1 +1 @@\n-c\n+d\n"
        )
        self.assertEqual([p for p, _ in lp.split_patch(text)], ["x", "y"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
