#!/usr/bin/env python3
"""The two records the daily report was missing are readable from git history, and this pins it.

`channels/tasks.md` records why the report was put on hold: two of the human's nine counts (how much
work was *added*, and whether work is *repeatable*) had no record, and the task says the per-amigo
to-do lists cannot supply the first because they are overwritten rather than appended, "so a wholesale
rewrite cannot be told from a rewrite that added something."

That is the claim this test is built around, and it is the one thing `scripts/todo_additions.py`
exists to disprove. A sequence alignment of the file's own committed versions separates an item that
did not exist before (*insert*) from an item whose wording changed (*replace*) from a rewrite that
changed nothing (neither). These tests hold that distinction still, so a later edit cannot quietly
revert the method to a set difference — which is the shape that cannot make it.

The last test builds a throwaway repository, commits three versions of one list and checks the count
is taken from the commit that introduced each item and not again on the rewrites after it.
"""
from __future__ import annotations

import datetime as dt
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import todo_additions as ta  # noqa: E402


def _git(repo: Path, *args: str, env: dict | None = None) -> None:
    environment = dict(os.environ)
    if env:
        environment.update(env)
    subprocess.run(
        ["git", *args], cwd=str(repo), check=True, capture_output=True, text=True, env=environment
    )


class ItemParsingTest(unittest.TestCase):
    def test_only_checkbox_bullets_are_items(self):
        text = (
            "# header\n\n"
            "- [ ] 2026-10-14 — a real item\n"
            "- a prose bullet is not an item\n"
            "  an indented continuation is not an item either\n"
            "- [x] 2026-10-13 — a ticked item is an item\n"
        )
        self.assertEqual(
            ta.item_lines(text),
            ["2026-10-14 — a real item", "2026-10-13 — a ticked item is an item"],
        )

    def test_a_tick_is_not_an_edit(self):
        before = "- [ ] 2026-10-14 — item\n"
        after = "- [x] 2026-10-14 — item\n"
        self.assertEqual(ta.added_items(before, after), [])
        self.assertEqual(ta.reworded_items(before, after), 0)

    def test_an_appended_item_is_an_insertion(self):
        before = "- [ ] 2026-10-14 — one\n"
        after = "- [ ] 2026-10-14 — one\n- [ ] 2026-10-14 — two\n"
        self.assertEqual(ta.added_items(before, after), ["2026-10-14 — two"])

    def test_a_reworded_item_is_not_an_addition(self):
        # The load-bearing case: a wholesale rewrite that keeps an item is not an arrival. A set
        # difference would read "TWO, re-worded" as one added and one removed; the alignment does not.
        before = "- [ ] 2026-10-14 — one\n- [ ] 2026-10-14 — two\n"
        after = "# a new header\n\n- [ ] 2026-10-14 — one\n- [ ] 2026-10-14 — TWO, re-worded\n"
        self.assertEqual(ta.added_items(before, after), [])
        self.assertGreaterEqual(ta.reworded_items(before, after), 1)

    def test_a_reordered_item_is_not_an_addition(self):
        before = "- [ ] 2026-10-14 — one\n- [ ] 2026-10-14 — two\n"
        after = "- [ ] 2026-10-14 — two\n- [ ] 2026-10-14 — one\n"
        self.assertEqual(ta.added_items(before, after), [])

    def test_repeat_marker_is_found(self):
        text = "- [ ] 2026-10-14 — a recurring item\n  repeat: FREQ=WEEKLY;INTERVAL=1\n"
        self.assertEqual(ta.repeat_items(text), ["repeat: FREQ=WEEKLY;INTERVAL=1"])


class ScanFromHistoryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        _git(self.tmp, "init", "-q")
        _git(self.tmp, "config", "user.email", "test@example.invalid")
        _git(self.tmp, "config", "user.name", "Test")
        (self.tmp / "to-do-lists").mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _commit(self, text: str, iso: str) -> None:
        (self.tmp / "to-do-lists" / "desi.md").write_text(text, encoding="utf-8")
        _git(self.tmp, "add", "-A")
        _git(
            self.tmp,
            "commit",
            "-q",
            "-m",
            "snapshot",
            env={"GIT_AUTHOR_DATE": iso, "GIT_COMMITTER_DATE": iso},
        )

    def test_an_item_is_counted_on_the_commit_that_introduces_it_and_once_only(self):
        self._commit("- [ ] 2026-10-01 — one\n", "2026-10-01T00:00:00+00:00")
        self._commit(
            "- [ ] 2026-10-01 — one\n- [ ] 2026-10-01 — two\n",
            "2026-10-01T01:00:00+00:00",
        )
        # a later rewrite adds one item and ticks another; the two existing items must not re-count
        self._commit(
            "# rewritten wholesale\n\n"
            "- [ ] 2026-10-01 — one\n"
            "- [x] 2026-10-01 — two\n"
            "- [ ] 2026-10-01 — three\n",
            "2026-10-01T02:00:00+00:00",
        )
        report = ta.scan(repo=self.tmp, hours=10**6)
        self.assertEqual(report["desi"]["added"], ["2026-10-01 — two", "2026-10-01 — three"])
        self.assertEqual(report["desi"]["net"], 2)

    def test_the_window_excludes_older_additions(self):
        self._commit("- [ ] 2026-09-01 — old\n", "2026-09-01T00:00:00+00:00")
        self._commit(
            "- [ ] 2026-09-01 — old\n- [ ] 2026-09-01 — new\n",
            "2026-09-02T00:00:00+00:00",
        )
        now = dt.datetime(2026, 9, 3, tzinfo=dt.timezone.utc)
        report = ta.scan(repo=self.tmp, hours=24, now=now)
        self.assertEqual(report["desi"]["added"], ["2026-09-01 — new"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
