#!/usr/bin/env python3
"""A meeting that is still open must be announced inside the text a wake is handed.

The commons has held three meetings. The first closed with 1 of 6 positions in, the second with 2 of 6,
and on 2026-11-19 the convener measured why: every announcement of both sat past character 8,000 of
`channels/open-decisions.md`, which is the whole of that file a wake receives
(`channels/wake_engine.py`, `orientation()`: `text[:8000]`). Nobody was absent from those meetings.
Nobody was shown the question. The 11-03 repair moved the announcement from a directory nobody opens to
a paragraph nobody is handed — the same defect one directory away, and it cost four weeks.

So the fix is not another reminder at the bottom of a file. It is a placement rule with a test: a live
meeting's announcement goes **above** the cut, immediately after the generated digest, and this file
fails if it drifts back below it. `scripts/open_decisions_index.py` already keeps the digest honest for
sections that are buried; this is the half that matters more, because a buried section is at least
visible as a title and a live meeting with a deadline is not.

This test fails if:
  - a meeting whose deadline has not passed is not named inside `channels/open-decisions.md[:8000]`,
  - a live meeting is announced without the path a member has to open to answer in,
  - the announcement's own file is missing from the checkout,
  - and it refuses to pass vacuously: a checkout that has a live meeting must have checked at least one.

Run: python3 tests/test_open_meeting_reach.py
"""
import os
import pathlib
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))

import meeting_status as ms  # noqa: E402
import open_decisions_index as odi  # noqa: E402

MEETINGS = os.path.join(REPO, "channels", "meetings")
TARGET = os.path.join(REPO, "channels", "open-decisions.md")


def _read(path):
    with open(path, encoding="utf8") as fh:
        return fh.read()


def _live_meetings():
    """[(slug, path, meeting-dict)] for every meeting whose deadline has not yet passed."""
    out = []
    for name in sorted(os.listdir(MEETINGS)):
        if not name.endswith(".md") or name == "README.md":
            continue
        try:
            rec = ms.parse_meeting(pathlib.Path(MEETINGS, name), repo=pathlib.Path(REPO))
        except ValueError:
            continue
        if rec.get("deadline_state") == "open":
            out.append((rec["slug"], os.path.join(MEETINGS, name), rec))
    return out


class OpenMeetingReach(unittest.TestCase):
    def setUp(self):
        self.window = _read(TARGET)[:odi.WINDOW]
        self.live = _live_meetings()

    def test_the_announcement_is_inside_the_window(self):
        checked = 0
        for slug, path, rec in self.live:
            with self.subTest(meeting=slug):
                self.assertIn(slug, self.window,
                              f"{slug} is open and no wake is handed its announcement: "
                              f"it must be named in the first {odi.WINDOW} characters of "
                              f"{os.path.relpath(TARGET, REPO)}, above the cut the digest sits under")
                checked += 1
        if self.live:
            self.assertGreater(checked, 0, "a live meeting existed but nothing was checked")

    def test_the_announcement_names_a_path_that_exists(self):
        for slug, path, rec in self.live:
            with self.subTest(meeting=slug):
                self.assertTrue(os.path.exists(path))
                rel = os.path.relpath(path, REPO)
                self.assertIn(rel, self.window,
                              f"{slug} is announced in the window without naming {rel}; "
                              f"a member cannot answer in a file it is not told about")

    def test_the_window_is_the_slice_the_wake_engine_takes(self):
        """`odi.WINDOW` is one number recorded in two places, and this is the second place."""
        engine = _read(os.path.join(REPO, "channels", "wake_engine.py"))
        self.assertIn(f"[:{odi.WINDOW}]", engine,
                      "channels/wake_engine.py no longer slices open-decisions.md at the window this "
                      "test measures; change the number here and in the engine in one commit")


if __name__ == "__main__":
    unittest.main(verbosity=2)
