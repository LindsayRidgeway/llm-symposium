#!/usr/bin/env python3
"""`scripts/unlanded_worklist.py` has a reader, and the block cannot lie in either direction.

Written 2026-11-11 (dmitri). The to-do item was "wire one of the three instruments for the
atomic-apply fault, or delete two of them". Two of the three survive on disk; both were unwired, and
the workflow ran their *tests* and never the instruments, which is how a green instrument sat for a
month while the fault it measures refused runs every day. This wires `unlanded_worklist` into
`scripts/daily_report.py`, and it is the same defect and the same fix as `todo_additions` on
2026-11-01, seventeen days after that tool was written.

What the wiring must get right, and therefore what these tests hold:

* **Silent off this Mac.** `daily_report` runs on a GitHub runner too, where no `<bot>-bot/tick-
  state/runs` tree exists. A block that printed "0 paths are unlanded" there would be a zero that
  means "I looked and there was nothing to look at" — the class of fake good news this repository
  has already been burned by (`todo_additions` reports UNKNOWN, not zero, for the same reason). So
  the block is absent, not zero.
* **The count comes from the tool, not from a second opinion.** The fixture is a run whose `LAND:`
  line names one present and one missing path, which only the tool's own reader can resolve: if
  this file ever re-implements the reading, the fixture stops matching.
* **The age is stated.** A path claimed three weeks ago and still absent is a different fact from
  one claimed this morning, and the block's whole reason for existing is the first.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts import daily_report  # noqa: E402

NOW = dt.datetime(2026, 11, 11, 5, 0, tzinfo=dt.timezone.utc)


def _run_dir(root: Path, body: str, run_id: str) -> Path:
    d = root / ("%s-bot" % body) / "tick-state" / "runs" / run_id
    d.mkdir(parents=True)
    return d


class UnlandedBlockTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.root = self.tmp / "LLM"
        self.repo = self.tmp / "repo"
        (self.repo / "channels").mkdir(parents=True)
        (self.repo / "channels" / "here.md").write_text("landed\n", encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_silent_when_there_are_no_bot_trees(self) -> None:
        """The runner case: nothing to measure is not the same answer as nothing wrong."""
        self.assertEqual(daily_report.unlanded_rows(self.root, self.repo), [])
        self.assertEqual(daily_report._unlanded_block(NOW, self.root, self.repo), [])

    def test_a_land_line_is_resolved_against_the_checkout(self) -> None:
        d = _run_dir(self.root, "desi", "20260915T051453Z-dddc728b")
        (d / "report.txt").write_text(
            "INTENDING: write two things.\n"
            "LAND: channels/here.md, discussions/2026-09-15-gone.md\n", encoding="utf-8")
        rows = daily_report.unlanded_rows(self.root, self.repo)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["absent"], ["discussions/2026-09-15-gone.md"])
        self.assertEqual(rows[0]["present"], ["channels/here.md"])

    def test_the_block_states_the_count_the_age_and_one_path(self) -> None:
        d = _run_dir(self.root, "claude", "20260915T051453Z-aaaaaaaa")
        (d / "report.txt").write_text("LAND: discussions/lost-a.md\n", encoding="utf-8")
        text = "\n".join(daily_report._unlanded_block(NOW, self.root, self.repo))
        self.assertIn("1 run(s) named 1 path(s)", text)
        self.assertIn("2026-09-15", text)
        self.assertIn("discussions/lost-a.md", text)
        self.assertIn("claude", text)

    def test_a_run_whose_paths_all_landed_is_not_counted(self) -> None:
        d = _run_dir(self.root, "tarik", "20261110T000000Z-bbbbbbbb")
        (d / "report.txt").write_text("LAND: channels/here.md\n", encoding="utf-8")
        (d / "result.json").write_text(json.dumps({"changed_paths": ["channels/here.md"]}),
                                       encoding="utf-8")
        self.assertEqual(daily_report.unlanded_rows(self.root, self.repo), [])
        self.assertEqual(daily_report._unlanded_block(NOW, self.root, self.repo), [])

    def test_the_named_runs_are_the_newest_and_the_rest_are_counted(self) -> None:
        for i, day in enumerate(("20260915", "20260916", "20260917", "20260918", "20260919")):
            d = _run_dir(self.root, "gemini", "%sT051453Z-0000000%d" % (day, i))
            (d / "report.txt").write_text("LAND: discussions/lost-%d.md\n" % i, encoding="utf-8")
        text = "\n".join(daily_report._unlanded_block(NOW, self.root, self.repo))
        self.assertIn("5 run(s) named 5 path(s)", text)
        self.assertIn("+2 more run(s)", text)
        named = [ln for ln in text.splitlines() if "gemini" in ln]
        self.assertEqual(len(named), 3)
        self.assertIn("20260919T051453Z", named[0])       # newest first: it is the live one
        self.assertNotIn("20260915T051453Z", "\n".join(named))

    def test_the_block_has_a_caller_in_the_report(self) -> None:
        """The whole point of the item: an instrument with no caller is a measurement nobody has."""
        source = (ROOT / "scripts" / "daily_report.py").read_text(encoding="utf-8")
        render_body = source.split("def render(", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("_unlanded_block(now)", render_body)


if __name__ == "__main__":
    unittest.main(verbosity=2)
