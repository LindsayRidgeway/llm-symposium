#!/usr/bin/env python3
"""Tests for the waiting-pile measurement (`scripts/waiting_pile.py`).

What would make this number a lie, and is therefore pinned:
  1. a non-waiting item is counted — the measurement is *W*, not the whole ledger;
  2. path presence is read from the wrong root, so every path reads missing;
  3. the pipeline floor counts the wrong side of the date, which would turn a
     delivery fact back into a review backlog — the exact confusion the script exists
     to remove.
"""
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts import waiting_pile as wp  # noqa: E402


def item(i, *, assigned=None, author="desi", filed="2026-09-15T00:00:00Z", paths=(), state=None):
    return {
        "id": i, "assigned_to": assigned, "amigo": author, "filed_utc": filed,
        "paths": list(paths), "state": state,
    }


class TestPathStatus(unittest.TestCase):
    def test_all_some_none_and_empty(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "a.md").write_text("x", encoding="utf-8")
            self.assertEqual(wp.path_status(["a.md"], root), "all_present")
            self.assertEqual(wp.path_status(["a.md", "gone.md"], root), "some_present")
            self.assertEqual(wp.path_status(["gone.md"], root), "none_present")
            self.assertEqual(wp.path_status([], root), "no_paths")
            self.assertEqual(wp.path_status(None, root), "no_paths")

    def test_junk_entries_do_not_raise(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "a.md").write_text("x", encoding="utf-8")
            self.assertEqual(wp.path_status([None, "", "a.md"], root), "all_present")


class TestSummarize(unittest.TestCase):
    def _items(self):
        return {
            # waiting, named, pre-pipeline, delivered
            "i1": item("i1", assigned="dmitri", filed="2026-09-15T00:00:00Z", paths=["a.md"]),
            # waiting, named, pre-pipeline, not delivered
            "i2": item("i2", assigned="desi", filed="2026-09-16T00:00:00Z", paths=["gone.md"]),
            # waiting, hole (no name), pipeline era
            "i3": item("i3", assigned=None, filed="2026-10-01T00:00:00Z", paths=["a.md"]),
            # already accomplished — must NOT be counted
            "i4": item("i4", assigned="dmitri", filed="2026-10-01T00:00:00Z",
                       paths=["a.md"], state="accomplished"),
        }

    def test_only_waiting_items_are_counted(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "a.md").write_text("x", encoding="utf-8")
            s = wp.summarize(self._items(), "2026-09-25T12:27:01-04:00", root)
            self.assertEqual(s["waiting"], 3)
            self.assertEqual(s["named"], {"dmitri": 1, "desi": 1})
            self.assertEqual(s["holes"], 1)
            self.assertEqual(s["by_path_status"]["all_present"], 2)
            self.assertEqual(s["by_path_status"]["none_present"], 1)
            self.assertEqual(s["floor_pre_pipeline"], 2)
            self.assertEqual(s["pipeline_era"], 1)

    def test_no_pipeline_start_means_no_floor_split(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "a.md").write_text("x", encoding="utf-8")
            s = wp.summarize(self._items(), None, root)
            self.assertEqual(s["pipeline_start"], None)
            self.assertEqual(s["floor_pre_pipeline"], 0)
            self.assertEqual(s["pipeline_era"], 0)

    def test_render_mentions_the_floor_and_the_totals(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "a.md").write_text("x", encoding="utf-8")
            text = wp.render(wp.summarize(self._items(), "2026-09-25T12:27:01-04:00", root))
            self.assertIn("**3**", text)
            self.assertIn("**2**", text)   # the floor

    def test_render_survives_an_empty_ledger(self):
        text = wp.render(wp.summarize({}, None))
        self.assertIn("Waiting items (W): **0**", text)


class TestPipelineStart(unittest.TestCase):
    def test_no_repo_returns_none(self):
        # a directory that is not a git repo: the git call fails, and the floor must not crash
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(wp.pipeline_start(Path(d)))


if __name__ == "__main__":
    unittest.main()
