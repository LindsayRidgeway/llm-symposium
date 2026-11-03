#!/usr/bin/env python3
"""A scheduled job may not commit a deletion outside the sweep fence.

Why this file exists (2026-11-02). `channel-poll.yml` stages all of `channels/` and commits it about
twelve times a day. Until today the risk sweep rebuilt `channels/tasks.md` wholesale, so any of those
commits could carry the deletion of every section below the Open Risks heading — 53,793 characters of
the live file — under the message "feat(channels): frequent poll — mail + telegram". No conflict, no
failing test, no name against the act.

`scripts/sweep_risks.py` now owns a fenced block. `scripts/check_sweep_fence_only.py` is the belt to
that braces, and these tests are the proof that the belt is a belt: it must pass a change that stays
inside the fence, and refuse one that removes a line outside it.

Run: python3 tests/test_check_sweep_fence_only.py
"""
import pathlib
import subprocess
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
CHECK = REPO / "scripts" / "check_sweep_fence_only.py"

BEFORE = """# Commons tasks

## Filed from the chat with the human

- [ ] a request from the human

<!-- sweep-risks:begin -->
## Open Risks (from channels/risks.md)

- [2026-10-01] **R-001** (Desi): an old row
  Fix, then mark Done in channels/risks.md.
<!-- sweep-risks:end -->

## A section below the block

- [ ] the founder's volume rule
"""

INSIDE_ONLY = BEFORE.replace("- [2026-10-01] **R-001** (Desi): an old row",
                             "- [2026-11-02] **R-002** (Gemini): a newer row")
# A rewrite that loses work on BOTH sides of the fence: above it, the human's filed item; below it,
# a section. The old sweep managed the lower half on its own.
WHOLESALE = """# Commons tasks

<!-- sweep-risks:begin -->
## Open Risks (from channels/risks.md)

*(No open risks in ledger)*
<!-- sweep-risks:end -->
"""


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


class FenceCheck(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.td.name)
        git(self.root, "init", "-q", "-b", "main")
        git(self.root, "config", "user.email", "t@example.invalid")
        git(self.root, "config", "user.name", "t")
        (self.root / "channels").mkdir()
        (self.root / "channels" / "tasks.md").write_text(BEFORE, encoding="utf-8")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-qm", "base")
        # Run the real script against this repository by pointing it at it with -C.
        self.script = self.root / "check.py"
        self.script.write_text(
            CHECK.read_text(encoding="utf-8").replace(
                'REPO = Path(__file__).resolve().parent.parent',
                'REPO = Path(%r)' % str(self.root)),
            encoding="utf-8")

    def tearDown(self):
        self.td.cleanup()

    def run_check(self, after_text=None):
        if after_text is not None:
            path = self.root / "after.md"
            path.write_text(after_text, encoding="utf-8")
            return subprocess.run([sys.executable, str(self.script), "--after", str(path)],
                                  capture_output=True, text=True)
        return subprocess.run([sys.executable, str(self.script)], capture_output=True, text=True)

    def test_a_change_inside_the_fence_passes(self):
        r = self.run_check(INSIDE_ONLY)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("confined to the fenced risk block", r.stdout)

    def test_a_wholesale_rewrite_is_refused_and_names_the_lines(self):
        r = self.run_check(WHOLESALE)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("REFUSED", r.stdout)
        self.assertIn("the founder's volume rule", r.stdout)
        self.assertIn("a request from the human", r.stdout)

    def test_an_untouched_file_passes_silently(self):
        r = self.run_check(BEFORE)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(r.stdout.strip(), "")

    def test_the_real_repository_passes_its_own_check(self):
        """The guard must not refuse the live tree, or it will be switched off within a day."""
        r = subprocess.run([sys.executable, str(CHECK)], capture_output=True, text=True, cwd=REPO)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
