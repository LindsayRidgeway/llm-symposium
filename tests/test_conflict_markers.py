#!/usr/bin/env python3
"""The conflict-marker guard: markers must not reach `main` again.

Written 2026-10-11 (Dmitri) with `scripts/check_conflict_markers.py`. Two files on
`main` (channels/risks.md, channels/reject-queue.md) were committed carrying
`<<<<<<< ours` / `=======` / `>>>>>>> theirs` by the landing of run
`20261011T144432Z-bf0069ec` (commit `f48356e3`); the lander runs the repository's
tests and sees only *new* failures, so a marker-free test suite let the corruption
through. This test is that missing failure: it asserts the real tree carries no
markers, so a run that lands a conflicted file turns the suite red and the lander
refuses it.

Offline. The detector is exercised on strings and temp files so the *class* is
pinned; the real tree is scanned only as the integration case.
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_conflict_markers as ccm  # noqa: E402


class MarkerDetectionTest(unittest.TestCase):
    def test_detects_a_classic_block(self):
        text = "a\n<<<<<<< ours\nb\n=======\nc\n>>>>>>> theirs\nd\n"
        lines = [ln for ln, _ in ccm.markers_in_text(text)]
        self.assertEqual(lines, [2, 4, 6])

    def test_detects_bare_separator(self):
        self.assertEqual([ln for ln, _ in ccm.markers_in_text("x\n=======\ny\n")], [2])

    def test_detects_diff3_base_row(self):
        text = "<<<<<<< ours\n||||||| base\n=======\n>>>>>>> theirs\n"
        labels = [lab for _, lab in ccm.markers_in_text(text)]
        self.assertIn("|||||||", labels)
        self.assertEqual(len(labels), 4)

    def test_ignores_ruled_divider(self):
        # The manual-transcription log is full of these; they are not markers.
        text = "=" * 80 + "\n" + "=" * 7 + "x\n"
        self.assertEqual(ccm.markers_in_text(text), [])

    def test_ignores_markdown_table_rules(self):
        text = "| a | b |\n|---|---|\n|----|--------|\n"
        self.assertEqual(ccm.markers_in_text(text), [])

    def test_ignores_indented_fake_marker(self):
        # git writes markers at column 0; an indented one is prose, not a conflict.
        self.assertEqual(ccm.markers_in_text("  <<<<<<< not a marker\n"), [])

    def test_ignores_eight_char_rule(self):
        self.assertEqual(ccm.markers_in_text("<<<<<<<<\n>>>>>>>>\n"), [])


class ScannerTest(unittest.TestCase):
    def test_scan_names_file_and_line(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "f.md"
            p.write_text("ok\n<<<<<<< ours\n=======\n>>>>>>> theirs\n")
            hits = ccm.scan([p], Path(d))
            self.assertEqual(hits, {"f.md": [(2, "<<<<<<<"), (3, "======="), (4, ">>>>>>>")]})

    def test_cli_exit_is_one_when_marker_present(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "f.md"
            p.write_text("=======\n")
            r = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "check_conflict_markers.py"), str(p)],
                capture_output=True, text=True,
            )
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertIn("f.md:1", r.stdout)

    def test_the_real_tree_is_clean(self):
        """The load-bearing case: if this fails, a conflicted file is on disk and
        must not be landed. Repair it, do not excuse it.

        Scans tracked **and** untracked since 2026-10-18: the lander runs this suite between
        `git apply` and `git add`, so a file the landing creates is still untracked here, and a
        guard that reads only `git ls-files` cannot see the case it exists for.
        """
        hits = ccm.scan(ccm.candidate_files(ROOT), ROOT)
        self.assertEqual(hits, {}, f"conflict markers present: {hits}")

    def _repo(self, d):
        root = Path(d) / "r"
        root.mkdir()
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "t@example.com"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "t"], check=True)
        return root

    def test_an_untracked_file_is_scanned(self):
        """The case the guard was blind to: a marker in a file the landing is about to add."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            (root / "base.md").write_text("ok\n")
            subprocess.run(["git", "-C", str(root), "add", "base.md"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "base"], check=True)
            (root / "new-report.md").write_text("ok\n<<<<<<< ours\nx\n=======\ny\n>>>>>>> theirs\n")
            self.assertEqual(ccm.scan(ccm.tracked_files(root), root), {},
                             "fixture is wrong: the untracked file was in the tracked set")
            hits = ccm.scan(ccm.candidate_files(root), root)
            self.assertIn("new-report.md", hits,
                          "an untracked file carrying markers was not scanned -- this is the exact "
                          "case the lander creates between apply and add")

    def test_an_ignored_file_is_not_scanned(self):
        """`.gitignore` must stay honoured, or the guard reads build output and camera rolls."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            (root / ".gitignore").write_text("junk/\n")
            (root / "junk").mkdir()
            (root / "junk" / "f.md").write_text("=======\n")
            self.assertNotIn("junk/f.md", ccm.scan(ccm.candidate_files(root), root),
                             "an ignored file was scanned; pointing this at a live checkout would "
                             "then depend on what happens to be lying in .gitignore'd space")

    def test_an_oversized_file_is_skipped_by_name(self):
        """A skip that says nothing is the defect; a skip that names the file is a record."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            big = root / "big.md"
            big.write_text("=======\n" + "x" * 32)
            old = ccm.MAX_BYTES
            try:
                ccm.MAX_BYTES = 8
                skipped = []
                hits = ccm.scan([big], root, skipped)
            finally:
                ccm.MAX_BYTES = old
            self.assertEqual(hits, {})
            self.assertEqual(skipped, ["big.md"], "an oversized file was skipped silently")


if __name__ == "__main__":
    unittest.main(verbosity=2)
