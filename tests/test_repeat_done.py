#!/usr/bin/env python3
"""A repeat that is done must stop being asked — added 2026-11-19.

The founder's test of the clockwork, in his words: *if a wake finishes the head of its calendar, does
the next wake find the same head?* Measured that evening, yes: a letter was written and sent at 20:43Z
and the next wake's due block still read DUE TODAY, because completion was recorded nowhere the
calendar could read. So these tests pin the three states a machine needs — not due, due, done — and
the two ways the advance can be wrong: by a day instead of a week (re-anchoring the series on the
completion date) and by corrupting the line it rewrites.
"""
import datetime
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import repeat_done as rd  # noqa: E402


def engine():
    spec = importlib.util.spec_from_file_location("we_rd", ROOT / "channels" / "wake_engine.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)                    # type: ignore[union-attr]
    return mod


class RepeatDone(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.dir.name)
        (self.repo / "channels").mkdir()
        (self.repo / "to-do-lists").mkdir()
        self.registry = self.repo / "channels" / "recurring.json"
        self.registry.write_text(json.dumps({"desi": [{
            "text": "Weekly: one letter to a person outside the commons.",
            "repeat": "FREQ=WEEKLY;INTERVAL=1", "since": "2026-11-19"}]}), encoding="utf-8")
        self.list = self.repo / "to-do-lists" / "desi.md"
        self.list.write_text(
            "- [ ] 2026-11-19 — **Weekly: one letter to a person outside the commons.** A letter is a claim.\n"
            "  repeat: FREQ=WEEKLY;INTERVAL=1\n", encoding="utf-8")
        self._repo = rd.REPO
        rd.REPO = self.repo

    def tearDown(self):
        rd.REPO = self._repo
        self.dir.cleanup()

    def done(self, today="2026-11-19"):
        return rd.done("desi", "one letter to a person outside",
                       today=datetime.date.fromisoformat(today),
                       registry=self.registry, lists=self.repo / "to-do-lists")

    def test_a_weekly_promise_done_today_is_next_asked_in_seven_days(self):
        got = self.done()
        self.assertEqual(got["next"], "2026-11-26")

    def test_the_completion_is_recorded_not_just_the_new_date(self):
        self.done()
        ent = json.loads(self.registry.read_text())["desi"][0]
        self.assertEqual(ent["last_done"], "2026-11-19")

    def test_the_list_line_moves_without_doubling_its_dash(self):
        self.done()
        line = self.list.read_text().splitlines()[0]
        self.assertTrue(line.startswith("- [ ] 2026-11-26 — **Weekly:"), line)
        self.assertNotIn("——", line)

    def test_an_unmatched_phrase_is_an_error_not_a_silent_no_op(self):
        with self.assertRaises(LookupError) as caught:
            rd.done("desi", "something nobody promised",
                    today=datetime.date(2026, 11, 19), registry=self.registry,
                    lists=self.repo / "to-do-lists")
        self.assertIn("--list", str(caught.exception))

    def test_the_due_block_stops_asking_once_it_is_done(self):
        we = engine()
        before = we.due_block(str(self.repo), amigo="desi")
        self.assertIn("2026-11-19", before)
        self.done()
        after = we.due_block(str(self.repo), amigo="desi")
        self.assertIn("2026-11-26", after)
        self.assertNotIn("DUE TODAY", after)
        self.assertNotIn("OVERDUE", after)


if __name__ == "__main__":
    unittest.main()
