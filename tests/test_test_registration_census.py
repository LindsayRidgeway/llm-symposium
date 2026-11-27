#!/usr/bin/env python3
"""The registration census applied to this tree — and red if it ever goes back to naming files only.

WHY THIS EXISTS (measured 2026-11-27, Desi). `.github/workflows/test-and-report.yml` named test files
one per line and stopped at 145 of 252. The other 105 executed nowhere inside this repository: only a
`failing_tests()` glob inside six bot directories outside it ran them, so a clone — CI, a stranger, a
successor — could not run 42% of the suite, and `scripts/unregistered_tests.py --strict` said so and
nothing failed.

The repair is a walk rather than a list: the `walk` job runs `scripts/suite_watch.py`, and the census
learns what a walker covers **by asking it** (`--list`), refusing an answer that is empty or is not
test file names. These tests hold both halves down:

* the real tree has no missing file and no walker claim, and the covered count has a floor;
* deleting the walker line from a copy of the workflows puts ca. 105 files back in MISSING — so the
  line, not a docstring, is what makes the census green;
* a walker that lists nothing is a finding, not coverage, because a runner that collects nothing
  reports success and this repository has been bitten by that twice.

The floor is a count of test files present, not a hash: a test may be added freely, and a file
disappearing is exactly the drop this guard is for.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import unregistered_tests as U  # noqa: E402

REPO = Path(U.REPO)
# 252 test files on 2026-11-27, all 252 walked. A real repair lands files; it does not delete them.
FLOOR = 250


class TheRealTree(unittest.TestCase):
    def test_every_test_file_is_named_or_walked(self):
        r = U.classify()
        self.assertEqual([x["test"] for x in r["missing"]], [])
        self.assertEqual(r["walker_claims"], [])
        self.assertGreaterEqual(len(r["walked"]), FLOOR)

    def test_the_covered_count_has_a_floor(self):
        present = sorted((REPO / "tests").glob("test_*.py"))
        self.assertGreaterEqual(len(present), FLOOR,
                                f"{len(present)} test files, floor {FLOOR}: files went away")

    def test_strict_is_green_on_the_real_tree(self):
        proc = subprocess.run([sys.executable, str(REPO / "scripts" / "unregistered_tests.py"), "--strict"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout[-1200:] + proc.stderr[-400:])


class TheWalkIsTheRegistration(unittest.TestCase):
    def test_removing_the_walk_from_the_workflow_puts_the_files_back_in_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            wf = Path(tmp)
            for src in sorted((REPO / ".github" / "workflows").glob("*.y*ml")):
                kept = [line for line in src.read_text(encoding="utf-8").splitlines(True)
                        if "scripts/suite_watch.py" not in line]
                (wf / src.name).write_text("".join(kept), encoding="utf-8")
            r = U.classify(REPO / "tests", wf, REPO / "scripts")
            self.assertGreaterEqual(len(r["missing"]), 100)
            self.assertFalse([x for x in r["missing"] if x.get("walked_by")])

    def test_a_walker_that_lists_nothing_is_a_finding_not_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for sub in ("tests", "wf", "scripts"):
                (root / sub).mkdir()
            (root / "tests" / "test_a.py").write_text(
                "import sys\nif __name__ == '__main__':\n    sys.exit(0)\n", encoding="utf-8")
            (root / "wf" / "ci.yml").write_text("run: python3 scripts/suite_watch.py\n", encoding="utf-8")
            (root / "scripts" / "suite_watch.py").write_text("print('[]')\n", encoding="utf-8")
            r = U.classify(root / "tests", root / "wf", root / "scripts")
            self.assertEqual([x["test"] for x in r["missing"]], ["test_a.py"])
            self.assertEqual(len(r["walker_claims"]), 1)
            self.assertIn("collects nothing", r["walker_claims"][0]["problem"])
            self.assertEqual(U.main(["--tests", str(root / "tests"), "--workflows", str(root / "wf"),
                                     "--scripts", str(root / "scripts"), "--strict"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
