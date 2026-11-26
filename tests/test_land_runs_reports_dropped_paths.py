#!/usr/bin/env python3
"""A landing that does not carry a path it claims must say so (Desi, 2026-11-26).

Measured that day: Gwen's 11:09Z run changed 28 paths; her landing commit carried 27. The
missing one was a *deletion* (`tests/test_ledger_watch.py.new`, a tracked 0-byte leftover), so
the tree she left behind was the one her own page had recorded as cleaned, and the leftover she
meant to remove was still tracked. `land_runs.py` printed `landed`, which was true of the push and
false of the work.

The mechanism is *unproven* — two attempts to reproduce a refused staging `git add` failed, and
the page that describes the loss says so. What this file pins is the part that is provable and
that would have ended the silence either way: the lander asks the worktree, after the commit,
whether the paths it claimed are still dirty there. If they are, it writes them to
`land_missing.json` beside `result.json`, where the wake prompt's `land_missing` column reads them.

The claim is executed against the lander as installed rather than restated. When there is no
installed lander, or an older one without the helper, every case skips with its reason in the
message: a test that cannot run is not a pass. pytest is not installed on the wake machines, so
this runs directly (`python3 tests/test_land_runs_reports_dropped_paths.py`) and through the
landing gate, which executes every `tests/test_*.py`.
"""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

LANDER = Path.home() / "LLM" / "desi-bot" / "land_runs.py"


def load_lander():
    spec = importlib.util.spec_from_file_location("land_runs_under_test", LANDER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


class DroppedPaths(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not LANDER.is_file():
            raise unittest.SkipTest("no lander installed at %s" % LANDER)
        cls.lr = load_lander()
        if not hasattr(cls.lr, "_land_missing"):
            raise unittest.SkipTest(
                "the installed lander predates `_land_missing` (%s); the repair is not deployed "
                "to this machine" % LANDER)

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.wt = Path(self._tmp.name)
        git(self.wt, "init", "-q", ".")
        git(self.wt, "config", "user.email", "wake@example.invalid")
        git(self.wt, "config", "user.name", "wake")
        (self.wt / "keep.txt").write_text("x\n", encoding="utf-8")
        (self.wt / "drop.txt").write_text("gone\n", encoding="utf-8")
        git(self.wt, "add", "-A")
        git(self.wt, "commit", "-qm", "init")
        self.paths = ["drop.txt", "keep.txt"]

    def tearDown(self):
        self._tmp.cleanup()

    def test_a_deletion_the_commit_did_not_carry_is_reported(self):
        # The 2026-11-26 shape: gone from the worktree, still in HEAD.
        (self.wt / "drop.txt").unlink()
        missing = self.lr._land_missing(self.paths, self.wt, 0)
        self.assertEqual(len(missing), 1, missing)
        self.assertIn("drop.txt", missing[0])
        self.assertTrue(missing[0].startswith("D ") or missing[0].startswith(" D"), missing[0])

    def test_a_deletion_the_commit_carried_is_not_reported(self):
        git(self.wt, "rm", "-q", "drop.txt")
        git(self.wt, "commit", "-qm", "rm")
        self.assertEqual(self.lr._land_missing(self.paths, self.wt, 0), [])

    def test_a_change_the_commit_carried_is_not_reported(self):
        (self.wt / "keep.txt").write_text("y\n", encoding="utf-8")
        git(self.wt, "commit", "-qam", "change")
        self.assertEqual(self.lr._land_missing(self.paths, self.wt, 0), [])

    def test_a_refused_staging_step_is_reported_even_when_the_tree_is_clean(self):
        missing = self.lr._land_missing(["keep.txt"], self.wt, 128)
        self.assertEqual(len(missing), 1, missing)
        self.assertIn("128", missing[0])

    def test_nothing_claimed_reports_nothing(self):
        self.assertEqual(self.lr._land_missing([], self.wt, 1), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
