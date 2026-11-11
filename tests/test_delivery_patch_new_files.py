"""The delivery patch carries files a run *created*, and nothing guarded that.

Added 2026-11-11 (Desi), answering a question my own to-do list had carried as an
unmeasured worry: "`--review` now writes its mirror as a *new* untracked file, so if the
delivery diff is computed from tracked changes only, the mirror cannot travel and the
2026-11-09 repair is defeated in transit."

**Measured, not argued.** The diff is taken with `git add -N .` followed by
`git diff <base>` (channels/wake_engine.py, both `_run_standard` and the handoff path).
Intent-to-add is what makes an untracked file appear in `git diff` at all, and the record
shows it working: run 20261111T141644Z-bcfe688e's changes.patch holds five
`new file mode 100644` hunks under channels/ledger-verdicts/, and run
20261111T101614Z-468de618's holds two. So the worry was false: new files travel.

What was missing is a guard. Nothing in the tree would notice if `add -N .` became
`add -u` — every new mirror file, every new screen, every new test would then be written,
reported, and silently left behind, and the run would still look delivered because its
modifications were in the diff. This test is that guard, in the two directions the
property can break:

  1. the code that builds the patch still uses intent-to-add; and
  2. the repository does not ignore the directory the mirrors are written into — because
     `git add -N .` respects .gitignore, and an ignored mirror is the same failure arriving
     by a different door.

The second half is demonstrated rather than asserted: a throwaway repository is built, a
verdict mirror is written into it untracked, and the same command pair the pipeline uses is
run against it. If the patch that comes back does not name the file as a new file, this
fails, whatever the comment in wake_engine.py says.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

WAKE_ENGINE = REPO_ROOT / "channels" / "wake_engine.py"
VERDICT_DIR = "channels/ledger-verdicts"
# The directory `item_ledger.py --review` and `scripts/ledger_verdict_mirror.py` write into.


def _git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=True,
    ).stdout


class ThePatchCommand(unittest.TestCase):
    def test_every_patch_is_taken_with_intent_to_add(self):
        """`add -N` before `git diff`, at every place the pipeline takes a run's diff.

        A plain `git diff` reports modifications to tracked files only. `add -N` marks an
        untracked path as intent-to-add so the diff includes it as `new file mode`; `add -u`
        would stage the tracked ones and still leave every new file out.
        """
        source = WAKE_ENGINE.read_text(encoding="utf-8")
        adds = re.findall(r"\['git', '-C', str\(repo\), 'add', ([^\]]*)\]", source)
        self.assertTrue(adds, "no git add call found in wake_engine.py — did it move?")
        for args in adds:
            self.assertIn("'-N'", args, f"a diff is taken after `git add {args}` — not intent-to-add")

    def test_the_mirror_directory_is_not_ignored(self):
        """Intent-to-add does not override .gitignore — an ignored mirror would still travel nowhere."""
        proc = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "check-ignore", "-q", VERDICT_DIR],
            capture_output=True, text=True,
        )
        self.assertEqual(
            proc.returncode, 1,
            f"{VERDICT_DIR} is ignored by .gitignore: `git add -N .` will skip it, so verdict "
            "mirrors are written and then lost. Fix .gitignore, not the mirror writer.",
        )


class TheDemoRepository(unittest.TestCase):
    """The property, demonstrated on a real git repository rather than asserted in prose."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        _git(self.repo, "init", "--quiet")
        _git(self.repo, "config", "user.email", "test@example.invalid")
        _git(self.repo, "config", "user.name", "test")
        (self.repo / "channels").mkdir()
        (self.repo / "channels" / "items.jsonl").write_text("", encoding="utf-8")
        _git(self.repo, "add", ".")
        _git(self.repo, "commit", "--quiet", "-m", "base")
        self.base = _git(self.repo, "rev-parse", "HEAD").strip()

    def tearDown(self):
        self.tmp.cleanup()

    def _patch(self):
        _git(self.repo, "add", "-N", ".")
        return _git(self.repo, "diff", "--no-ext-diff", "--no-textconv", "--binary", self.base)

    def test_a_new_verdict_mirror_is_in_the_patch_as_a_new_file(self):
        target = self.repo / VERDICT_DIR / "20261111T201722Z-20261110T065635Z-8a64f8e4.json"
        target.parent.mkdir(parents=True)
        target.write_text('{"state": "accomplished", "reviewer": "desi"}\n', encoding="utf-8")

        patch = self._patch()
        self.assertIn(f"b/{VERDICT_DIR}/20261111T201722Z-20261110T065635Z-8a64f8e4.json", patch)
        self.assertIn("new file mode 100644", patch)
        self.assertIn("--- /dev/null", patch)

    def test_a_new_mirror_under_an_ignored_directory_is_not_in_the_patch(self):
        """The negative case, so the test above cannot pass for the wrong reason.

        If this ever stops being true, `git add -N` has begun overriding .gitignore and the
        guard in ThePatchCommand.test_the_mirror_directory_is_not_ignored needs rethinking.
        Both directions are recorded because a guard that only ever sees the passing case
        proves nothing about which line is doing the work.
        """
        (self.repo / ".gitignore").write_text("channels/ledger-verdicts/\n", encoding="utf-8")
        target = self.repo / VERDICT_DIR / "ignored.json"
        target.parent.mkdir(parents=True)
        target.write_text("{}\n", encoding="utf-8")

        patch = self._patch()
        self.assertNotIn(f"b/{VERDICT_DIR}/ignored.json", patch)


if __name__ == "__main__":
    unittest.main()
