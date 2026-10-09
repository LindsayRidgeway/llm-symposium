#!/usr/bin/env python3
"""Tests for the landing preflight (channels/risks.md R-009).

The preflight answers one question before a landing is attempted: would
`land_runs.py` accept it, or refuse it because the shared checkout has *foreign*
dirt? These tests pin the classification (record/generated/foreign) and the exit
codes, on throwaway git work trees, so the check never touches the real checkout.

Run directly:  python3 tests/test_landing_preflight.py
"""
from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "landing_preflight", ROOT / "scripts" / "landing_preflight.py"
)
lp = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(lp)


def _git(cwd, *args):
    return subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
        cwd=cwd, capture_output=True, text=True,
    )


class LandingPreflightTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name) / "shared"
        self.repo.mkdir()
        _git(self.repo, "init", "-q")
        (self.repo / "insights").mkdir()
        (self.repo / "insights" / "note.md").write_text("original\n", encoding="utf-8")
        _git(self.repo, "add", "-A")
        _git(self.repo, "commit", "-q", "-m", "seed")

    def tearDown(self):
        self._tmp.cleanup()

    def test_classify_splits_record_generated_foreign(self):
        groups = lp.classify([
            "channels/telegram/2026-10-09.md",
            "channels/conversation/x.md",
            "channels/agenda.md",
            "scripts/README.md",
            "insights/2026-09-09-rover-build-03-manual-transcription.md",
        ])
        self.assertEqual(groups["record"],
                         ["channels/telegram/2026-10-09.md", "channels/conversation/x.md"])
        self.assertEqual(groups["generated"], ["channels/agenda.md", "scripts/README.md"])
        self.assertEqual(groups["foreign"],
                         ["insights/2026-09-09-rover-build-03-manual-transcription.md"])

    def test_clean_repo_is_accepted(self):
        self.assertEqual(lp.main(["--repo", str(self.repo)]), 0)

    def test_foreign_dirt_is_refused(self):
        (self.repo / "insights" / "note.md").write_text("original\nadded\n", encoding="utf-8")
        self.assertEqual(lp.dirty_paths(self.repo), ["insights/note.md"])
        self.assertEqual(lp.main(["--repo", str(self.repo)]), 1)

    def test_record_dirt_is_tolerated(self):
        (self.repo / "channels" / "telegram").mkdir(parents=True)
        (self.repo / "channels" / "telegram" / "2026-10-09.md").write_text("hi\n", encoding="utf-8")
        self.assertEqual(lp.classify(lp.dirty_paths(self.repo))["foreign"], [])
        self.assertEqual(lp.main(["--repo", str(self.repo)]), 0)

    def test_not_a_work_tree(self):
        plain = Path(self._tmp.name) / "notrepo"
        plain.mkdir()
        self.assertEqual(lp.main(["--repo", str(plain)]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
