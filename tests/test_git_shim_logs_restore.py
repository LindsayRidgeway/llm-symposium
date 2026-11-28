#!/usr/bin/env python3
"""`git restore` leaves a line naming the process, which no hook could ever do.

The hook installer (scripts/install_git_mutation_log.sh) covers checkouts, merges and rewrites, and
on 2026-11-27 the live clone's mutation log showed it firing — yet the sweep at 20:51:25Z that put
six tracked files back to older content left no line of any kind. The reason is structural, not an
oversight: `git restore`, `git reset --hard` outside the lander, `git read-tree -u` and
`git checkout-index -f -a` run no hook, so no hook can be extended to catch them. Dmitri's report
(channels/reports/2026-11-27-dmitri-the-2051-sweep-has-no-author-because-nothing-logs-restore.md)
names the one instrument that stands where the mutation happens: a `git` shim earlier on PATH.

This test pins that shim, and deliberately pins the two things that make such shims fiction:
it must not exec itself, and it must not log commands that mutate nothing.

Run directly: python3 tests/test_git_shim_logs_restore.py
"""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install_git_shim.sh"

CLEAN_ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                 GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")


class TheShimNamesTheAuthorOfAHooklessRestore(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.repo = Path(self._td.name)
        self.run_git("init", "-q", "-b", "main")
        (self.repo / "f.txt").write_text("one\n", encoding="utf-8")
        self.run_git("add", "f.txt")
        self.run_git("commit", "-q", "-m", "one")
        self.log = self.repo / ".git" / "mutation.log"
        self.shimdir = self.repo / ".git" / "shim"

    def tearDown(self):
        self._td.cleanup()

    def run_git(self, *args, env=None):
        return subprocess.run(["git", "-C", str(self.repo), *args], capture_output=True,
                              text=True, env=env or CLEAN_ENV)

    def install(self):
        r = subprocess.run(["sh", str(INSTALLER), str(self.repo)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, "the installer failed: %s%s" % (r.stdout, r.stderr))
        self.assertTrue((self.shimdir / "git").is_file(), "the installer wrote no shim")

    def shim_env(self):
        """PATH with the shim first — what a launcher must do for the instrument to bind."""
        return dict(CLEAN_ENV, PATH=str(self.shimdir) + os.pathsep + CLEAN_ENV["PATH"])

    def shimmed(self, *args, cwd=None):
        """Run the shim as git, with a hard timeout: a shim that execs itself hangs, not fails."""
        try:
            return subprocess.run(["git", *args], cwd=cwd or str(self.repo), capture_output=True,
                                  text=True, env=self.shim_env(), timeout=15)
        except subprocess.TimeoutExpired:
            self.fail("git %r hung for 15s under the shim — the classic exec-itself bug"
                      % (args,))

    def lines(self):
        if not self.log.is_file():
            return []
        return [l for l in self.log.read_text(encoding="utf-8").splitlines() if l.strip()]

    def test_restore_is_logged_with_pid_cwd_and_argv(self):
        """The closing condition of the item: which process, and with what command."""
        self.install()
        (self.repo / "f.txt").write_text("two\n", encoding="utf-8")
        r = self.shimmed("restore", "f.txt")
        self.assertEqual(r.returncode, 0, "the shim broke a working git command: " + r.stderr)
        self.assertEqual((self.repo / "f.txt").read_text(encoding="utf-8"), "one\n",
                         "the shim logged the restore but did not perform it")
        lines = self.lines()
        self.assertTrue(lines, "git restore left no line — the hookless write is still invisible")
        line = lines[-1]
        self.assertIn("verb=restore", line)
        self.assertRegex(line, r"pid=\d+", "no pid: this is the field the item asks for")
        self.assertRegex(line, r"ppid=\d+")
        self.assertIn("argv=restore f.txt", line, "the argv is what tells a sweep from a stray restore")
        self.assertIn("cwd=", line)

    def test_reset_hard_is_logged(self):
        self.install()
        (self.repo / "f.txt").write_text("two\n", encoding="utf-8")
        self.shimmed("reset", "-q", "--hard", "HEAD")
        self.assertIn("verb=reset", self.lines()[-1])
        self.assertIn("--hard", self.lines()[-1])

    def test_the_verb_is_found_after_value_taking_global_options(self):
        """`git -C <dir> restore f` is how every script here calls git; the shim must not miss it."""
        self.install()
        (self.repo / "f.txt").write_text("two\n", encoding="utf-8")
        self.shimmed("-C", str(self.repo), "restore", "f.txt", cwd=str(ROOT))
        self.assertIn("verb=restore", self.lines()[-1],
                      "an option with a value shadowed the verb, so the shim logged nothing")

    def test_a_read_only_command_logs_nothing(self):
        """The 33-line log Dmitri read is worth reading only if it is not mostly `git status`."""
        self.install()
        for args in (("status", "--porcelain"), ("log", "-1", "--oneline"), ("diff",)):
            self.shimmed(*args)
        self.assertEqual(self.lines(), [], "a read-only git command wrote a mutation-log line")

    def test_the_shim_does_not_exec_itself(self):
        """An exec loop hangs the machine and looks like a slow disk. It is the classic shim bug."""
        self.install()
        try:
            r = subprocess.run(["git", "--version"], cwd=str(self.repo), capture_output=True,
                               text=True, env=self.shim_env(), timeout=20)
        except subprocess.TimeoutExpired:
            self.fail("the shim exec'd itself instead of the real git")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("git version", r.stdout)

    def test_the_check_mode_says_whether_the_instrument_binds_this_process(self):
        self.install()
        bound = subprocess.run(["sh", str(INSTALLER), "--check", str(self.repo)],
                               capture_output=True, text=True, env=self.shim_env())
        self.assertEqual(bound.returncode, 0, "the shim is installed and first on PATH: " + bound.stdout)
        self.assertIn("BOUND", bound.stdout)
        unbound = dict(CLEAN_ENV, PATH="/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin")
        r = subprocess.run(["sh", str(INSTALLER), "--check", str(self.repo)],
                           capture_output=True, text=True, env=unbound)
        self.assertNotEqual(r.returncode, 0,
                            "a check that passes when the shim is not on PATH is the decoration this "
                            "repository already shipped once")

    def test_the_installer_is_idempotent_and_leaves_the_tree_clean(self):
        self.install()
        self.install()
        body = (self.shimdir / "git").read_text(encoding="utf-8")
        self.assertEqual(body.count("installed by scripts/install_git_shim.sh"), 1)
        status = self.run_git("status", "--porcelain").stdout.strip()
        self.assertEqual(status, "", "installing the shim dirtied the working tree: %r" % status)


if __name__ == "__main__":
    unittest.main(verbosity=2)
