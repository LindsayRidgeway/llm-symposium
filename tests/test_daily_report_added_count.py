#!/usr/bin/env python3
"""The daily report has a consumer for count A, and a shallow clone cannot fake a zero.

Count A of the human's nine (2026-10-14) is work *added* to the per-amigo to-do lists in the window.
`channels/tasks.md` declared it impossible on the grounds that the lists are overwritten rather than
appended, and `scripts/todo_additions.py` measured that claim false on 2026-10-15 by aligning the
lists' own committed versions. The tool then had no caller for seventeen days — a green instrument
that nothing runs is a measurement nobody has — so 2026-11-01 wired it into `render()`.

These tests hold the three things that wiring can get wrong:

* the section is rendered at all, and names every amigo in the ledger's roster;
* an unreadable history reports **UNKNOWN**, never a row of zeros — in a shallow clone every list
  looks unchanged, and that is the one failure mode that reads as good news;
* the distinction the count exists for survives the wiring: an inserted item is not a re-worded one
  (that separation is `todo_additions`'s own claim, and the third test proves the wiring carries it
  rather than flattening it to a size difference).
"""
from __future__ import annotations

import datetime as dt
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts import daily_report  # noqa: E402
from scripts import todo_additions  # noqa: E402

ITEM = "- [ ] **{title}** body\n"


class AddedBlockTest(unittest.TestCase):
    def test_the_report_renders_the_section_and_names_every_amigo(self) -> None:
        text = daily_report.render(24, dt.datetime(2026, 11, 1, 22, 0, tzinfo=dt.timezone.utc))
        self.assertIn("### Items added to the work queues", text)
        for who in ("claude", "desi", "dmitri", "gemini", "gwen", "tarik"):
            self.assertIn(who, text)

    def test_a_history_that_cannot_be_read_is_unknown_and_not_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "to-do-lists").mkdir()
            (repo / "to-do-lists" / "dmitri.md").write_text("## Now\n" + ITEM.format(title="x"))
            now = dt.datetime(2026, 11, 1, 22, 0, tzinfo=dt.timezone.utc)
            block = "\n".join(daily_report._added_block(24, now, repo=repo))
        self.assertIn("UNKNOWN", block)
        self.assertIn("unmeasured", block)
        self.assertNotIn("+0 inserted", block)

    def test_inserted_and_reworded_stay_different_through_the_wiring(self) -> None:
        """The count is only worth having if it can tell new work from work said differently."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
            lists = repo / "to-do-lists"
            lists.mkdir()
            queue = lists / "dmitri.md"

            queue.write_text("## Now\n" + ITEM.format(title="first")
                             + ITEM.format(title="anchor a") + ITEM.format(title="anchor b"))
            subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
            # Commit one is dated outside the window on purpose: the tool counts every item of the
            # first IN-WINDOW commit as an arrival (its `previous` is empty), which is right for a
            # real list and would swamp this three-item fixture.
            subprocess.run(["git", "commit", "-qm", "one"], cwd=repo, check=True,
                           env={**os.environ, "GIT_AUTHOR_DATE": "2020-01-01T00:00:00Z",
                                "GIT_COMMITTER_DATE": "2020-01-01T00:00:00Z"})
            # One item re-worded, one genuinely new, two anchors left exactly alone — so the
            # alignment has something to match on and the insertion is visible as an insertion.
            queue.write_text("## Now\n" + ITEM.format(title="first, reworded")
                             + ITEM.format(title="anchor a") + ITEM.format(title="anchor b")
                             + ITEM.format(title="second"))
            subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "two"], cwd=repo, check=True)

            window = 24
            report = todo_additions.scan(repo=repo, hours=window)
            now = dt.datetime.now(dt.timezone.utc)
            block = "\n".join(daily_report._added_block(window, now, repo=repo))

        self.assertEqual(len(report["dmitri"]["added"]), 1, report["dmitri"]["added"])
        self.assertIn("second", report["dmitri"]["added"][0])
        self.assertGreaterEqual(report["dmitri"]["reworded"], 1)
        self.assertIn("1 inserted", block)
        self.assertIn("re-worded", block)


if __name__ == "__main__":
    unittest.main()
