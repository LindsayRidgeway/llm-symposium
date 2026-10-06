#!/usr/bin/env python3
"""The landing-tree report must classify what the lander refuses on, and name a remedy.

Written 2026-10-06 (Desi) with `scripts/landing_tree_report.py`. The tool exists because
the lander's refusal loop (`refused_dirty_tree` for ten days' worth of runs) is only
breakable if the dirty paths are read *by kind*: the obvious cleanup destroys real work.
So the thing worth pinning is the classification itself — generated and record paths are
accounted for, and every other path is blocking with a remedy that is not "revert it".

Offline. Every case is built in a throwaway git repository under a temp directory; the
real checkout is only ever read by the CLI smoke test, and that asserts the tool runs,
not what it finds.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import landing_tree_report as ltr  # noqa: E402


def run(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)


def make_repo(tmp: Path) -> Path:
    repo = tmp / "repo"
    repo.mkdir()
    run(repo, "init", "-q")
    run(repo, "config", "user.email", "t@example.invalid")
    run(repo, "config", "user.name", "Test")
    for rel, body in [
        ("tracked.txt", "one\n"),
        ("channels/agenda.md", "generated index\n"),
        ("channels/telegram/2026-10-06-chat.md", "log\n"),
    ]:
        f = repo / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(body)
    run(repo, "add", "-A")
    run(repo, "commit", "-q", "-m", "seed")
    return repo


class LandingTreeReportTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.repo = make_repo(self.tmp)

    def tearDown(self):
        self._tmp.cleanup()

    def kinds(self):
        accounted, blocking = ltr.classify(self.repo)
        return {r["path"]: r["kind"] for r in accounted + blocking}, blocking

    def test_clean_checkout_nothing_blocking(self):
        accounted, blocking = ltr.classify(self.repo)
        self.assertEqual(blocking, [])
        self.assertEqual(accounted, [])

    def test_modified_tracked_file_blocks_and_is_not_a_revert(self):
        (self.repo / "tracked.txt").write_text("one\ntwo\n")
        _, blocking = self.kinds()
        self.assertEqual([r["path"] for r in blocking], ["tracked.txt"])
        self.assertEqual(blocking[0]["subkind"], "modified")
        self.assertIn("commit", blocking[0]["remedy"])
        self.assertNotIn("checkout", blocking[0]["remedy"])

    def test_deleted_tracked_file_is_restored_not_committed(self):
        (self.repo / "tracked.txt").unlink()
        _, blocking = self.kinds()
        self.assertEqual(len(blocking), 1)
        self.assertEqual(blocking[0]["path"], "tracked.txt")
        self.assertIn("restore", blocking[0]["remedy"])
        self.assertIn("checkout", blocking[0]["remedy"])

    def test_untracked_file_blocks_without_blanket_clean(self):
        (self.repo / "new-mail.md").write_text("hello\n")
        _, blocking = self.kinds()
        self.assertEqual([r["path"] for r in blocking], ["new-mail.md"])
        self.assertIn("clean", blocking[0]["remedy"])
        self.assertIn("do not", blocking[0]["remedy"].lower())

    def test_generated_and_record_paths_are_accounted_not_blocking(self):
        (self.repo / "channels/agenda.md").write_text("regenerated\n")
        (self.repo / "channels/telegram/2026-10-06-chat.md").write_text("more\n")
        kinds, blocking = self.kinds()
        self.assertEqual(blocking, [])
        self.assertEqual(kinds["channels/agenda.md"], "generated")
        self.assertEqual(kinds["channels/telegram/2026-10-06-chat.md"], "record")

    def test_cli_exit_code_is_one_when_blocking_zero_when_clean(self):
        clean = subprocess.run([sys.executable, str(ROOT / "scripts" / "landing_tree_report.py"),
                                "--repo", str(self.repo)], capture_output=True, text=True)
        self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)
        self.assertIn("can accept a landing", clean.stdout)

        (self.repo / "tracked.txt").write_text("dirty\n")
        (self.repo / "litter.md").write_text("x\n")
        dirty = subprocess.run([sys.executable, str(ROOT / "scripts" / "landing_tree_report.py"),
                                "--repo", str(self.repo), "--json"], capture_output=True, text=True)
        self.assertEqual(dirty.returncode, 1, dirty.stdout + dirty.stderr)
        payload = json.loads(dirty.stdout)
        self.assertEqual({r["path"] for r in payload["blocking"]}, {"tracked.txt", "litter.md"})

    def test_cli_on_a_non_repo_reports_rather_than_crashes(self):
        bare = self.tmp / "not-repo"
        bare.mkdir()
        out = subprocess.run([sys.executable, str(ROOT / "scripts" / "landing_tree_report.py"),
                              "--repo", str(bare)], capture_output=True, text=True)
        self.assertEqual(out.returncode, 2)

    def test_cli_smoke_on_the_real_checkout(self):
        """Runs against this checkout. Asserts it completes, not what it finds."""
        out = subprocess.run([sys.executable, str(ROOT / "scripts" / "landing_tree_report.py")],
                             capture_output=True, text=True)
        self.assertIn(out.returncode, (0, 1), out.stdout + out.stderr)
        self.assertIn("landing-tree report", out.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
