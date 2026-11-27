#!/usr/bin/env python3
"""The mutation log records a path checkout, so a lost edit can name what took it.

On 2026-11-27 four edited files in the shared checkout were destroyed between `git add` and
`git commit`, and two committed blocks were reverted out of the working tree an hour later. Nothing
logged either event, so the only version of the story was mine. This test pins the log that would
have answered it: `git checkout -- <path>` must leave a line, and the line must be distinguishable
from a branch switch, because they are different acts and only one of them is silent.

Run directly: python3 tests/test_git_mutation_log.py
"""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install_git_mutation_log.sh"


def git(repo, *args, env=None):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          env=env or dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                                          GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t"))


class TheLogNamesAPathCheckout(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.repo = Path(self._td.name)
        git(self.repo, "init", "-q", "-b", "main")
        (self.repo / "f.txt").write_text("one\n", encoding="utf-8")
        git(self.repo, "add", "f.txt")
        git(self.repo, "commit", "-q", "-m", "one")
        self.log = self.repo / ".git" / "mutation.log"

    def tearDown(self):
        self._td.cleanup()

    def install(self):
        self.assertEqual(subprocess.run(["sh", str(INSTALLER), str(self.repo)],
                                        capture_output=True, text=True).returncode, 0,
                         "the installer failed")

    def test_a_path_checkout_is_logged_and_marked_as_one(self):
        self.install()
        (self.repo / "f.txt").write_text("two\n", encoding="utf-8")
        git(self.repo, "checkout", "--", "f.txt")
        self.assertTrue(self.log.is_file(), "a path checkout left no line in the mutation log")
        line = self.log.read_text(encoding="utf-8").strip().splitlines()[-1]
        self.assertIn("checkout", line)
        self.assertIn("branch=0", line, "a path checkout must be distinguishable from a branch switch")

    def test_a_branch_switch_is_logged_as_one(self):
        self.install()
        git(self.repo, "checkout", "-q", "-b", "other")
        line = self.log.read_text(encoding="utf-8").strip().splitlines()[-1]
        self.assertIn("branch=1", line)

    def test_the_log_never_dirties_the_tree(self):
        self.install()
        git(self.repo, "checkout", "-q", "-b", "other")
        status = git(self.repo, "status", "--porcelain").stdout.strip()
        self.assertEqual(status, "", "the hook wrote into the working tree: %r" % status)

    def test_the_installer_is_idempotent(self):
        self.install()
        self.install()
        hook = (self.repo / ".git" / "hooks" / "post-checkout").read_text(encoding="utf-8")
        self.assertEqual(hook.count("install_git_mutation_log"), 1, "the hook was appended twice")

    def test_the_real_clone_has_it_installed(self):
        """A guard that is not installed protects nothing — the lesson of the runnerless test file."""
        hook = ROOT / ".git" / "hooks" / "post-checkout"
        if not hook.is_file():
            self.skipTest("the shared clone has not run scripts/install_git_mutation_log.sh")
        self.assertIn("mutation.log", hook.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
