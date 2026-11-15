#!/usr/bin/env python3
"""The reset guard: a hook that refuses to throw away the only copy of a run's work.

Written 2026-11-14 because the shared checkout was reset that morning and two commits ceased to
exist — the 07:45 ledger check and the human's daily report — while every later measurement looked
healthy, because the pushed ledger was fine and only the report was missing. A guard that never
fires (the first version filtered on a ref name git does not send) is worse than none, because it is
believed; two of these tests run real `git reset --hard` against a throwaway repository for that
reason.
"""
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

import checkout_guard as cg  # noqa: E402


def git(repo, *args, check=True):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          check=False if not check else True)


class GuardTest(unittest.TestCase):
    def setUp(self):
        import tempfile
        self._dir = tempfile.TemporaryDirectory()
        self.repo = Path(self._dir.name)
        git(self.repo, "init", "-q", "-b", "main", ".")
        git(self.repo, "config", "user.email", "t@example")
        git(self.repo, "config", "user.name", "t")
        (self.repo / "f").write_text("a")
        git(self.repo, "add", "f")
        git(self.repo, "commit", "-qm", "A")
        self.a = git(self.repo, "rev-parse", "HEAD").stdout.strip()
        (self.repo / "f").write_text("b")
        git(self.repo, "commit", "-qam", "B")
        self.b = git(self.repo, "rev-parse", "HEAD").stdout.strip()
        git(self.repo, "update-ref", "refs/remotes/origin/main", self.a)
        cg.install(self.repo)

    def tearDown(self):
        self._dir.cleanup()

    def test_install_is_idempotent_and_checkable(self):
        self.assertTrue(cg.installed(self.repo))
        self.assertIn("already installed", cg.install(self.repo))
        out = subprocess.run([sys.executable, str(REPO / "scripts" / "checkout_guard.py"),
                              "--repo", str(self.repo), "--check"], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)

    def test_check_fails_loudly_when_the_hook_is_gone(self):
        cg.hook_path(self.repo).unlink()
        self.assertFalse(cg.installed(self.repo))
        out = subprocess.run([sys.executable, str(REPO / "scripts" / "checkout_guard.py"),
                              "--repo", str(self.repo), "--check"], capture_output=True, text=True)
        self.assertEqual(out.returncode, 1)
        self.assertIn("MISSING", out.stderr)

    def test_a_reset_that_would_drop_an_unpublished_commit_is_refused(self):
        r = git(self.repo, "reset", "--hard", "origin/main", check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("refusing to move HEAD", r.stderr)
        self.assertEqual(git(self.repo, "rev-parse", "HEAD").stdout.strip(), self.b)

    def test_a_reset_after_publishing_is_allowed(self):
        """The escape is publication, not permission: once the tip is on origin, it may be left."""
        (self.repo / "f").write_text("c")
        git(self.repo, "commit", "-qam", "C")
        c = git(self.repo, "rev-parse", "HEAD").stdout.strip()
        git(self.repo, "update-ref", "refs/remotes/origin/main", c)   # C is published
        r = git(self.repo, "reset", "--hard", self.a, check=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(git(self.repo, "rev-parse", "HEAD").stdout.strip(), self.a)

    def test_ordinary_commits_are_not_touched(self):
        (self.repo / "f").write_text("d")
        git(self.repo, "commit", "-qam", "D")
        head = git(self.repo, "rev-parse", "HEAD").stdout.strip()
        self.assertNotEqual(head, self.b)                      # the commit happened
        self.assertEqual(git(self.repo, "rev-parse", "HEAD^").stdout.strip(), self.b)

    def test_a_fast_forward_merge_is_allowed(self):
        """Landing is a fast-forward; a guard that refuses it would stop every wake in the commons."""
        (self.repo / "f").write_text("e")
        git(self.repo, "commit", "-qam", "E")
        e = git(self.repo, "rev-parse", "HEAD").stdout.strip()
        git(self.repo, "update-ref", "refs/remotes/origin/main", e)
        self.assertEqual(git(self.repo, "reset", "--hard", self.a, check=False).returncode, 0)
        r = git(self.repo, "merge", "--ff-only", "origin/main", check=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(git(self.repo, "rev-parse", "HEAD").stdout.strip(), e)


if __name__ == "__main__":
    unittest.main()
