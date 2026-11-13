#!/usr/bin/env python3
"""The wake block opens with what is due — added 2026-11-13.

Why this test exists. The founder asked on 2026-11-11 for creative work to repeat monthly and for a
monthly scan for medical opportunities, then asked the question that found the defect: *how does a
member keep looking if it is not a repeating item?* The machinery to declare a repeat already
existed — `to-do-lists/README.md` rule 4, `probes/recurrence_projection.py`, `scripts/todo_due.py` —
and not one list used it, and nothing ran `todo_due`. A repeating marker nobody reads is decoration,
which is the same failure as the reading quota that lived in a script nobody ran.

So `wake_engine.due_block()` computes, per seat, what is overdue, due today, or due within a
fortnight, expanding a repeat to its **next** instance, and `orientation()` puts it in the first
block of the prompt. Pinned here:

  1. a repeat's date is its next instance, not the date it was written;
  2. the three kinds are classified by the calendar, and something far off is not listed as due;
  3. an unreadable rule is reported, never silently dropped;
  4. a seat with nothing due is told so, rather than the block vanishing (a missing block cannot be
     noticed, and cannot fail);
  5. every seat reads its own list.
"""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


def load_engine():
    spec = importlib.util.spec_from_file_location("engine_under_test",
                                                  str(REPO / "channels" / "wake_engine.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Due(unittest.TestCase):
    def setUp(self):
        self.e = load_engine()
        self._amigo = self.e.AMIGO
        self.e.AMIGO = "desi"          # the deployed copies take their seat from the directory name

    def tearDown(self):
        self.e.AMIGO = self._amigo

    def kinds(self, text, today):
        import datetime
        return {t: (k, w) for w, k, t, _r, _n in self.e.due_items(
            text, today=today, repo=str(REPO))}

    def test_a_repeat_is_its_next_instance_not_the_date_it_was_written(self):
        import datetime
        got = self.kinds("- [ ] 2026-11-01 — weekly piece\n  repeat: FREQ=WEEKLY;INTERVAL=1\n",
                         datetime.date(2026, 11, 13))
        kind, when = got["weekly piece"]
        self.assertEqual(when, datetime.date(2026, 11, 15))   # next instance, not 11-01
        self.assertEqual(kind, "soon")
        monthly = self.kinds("- [ ] 2026-11-01 — monthly piece\n  repeat: FREQ=MONTHLY;INTERVAL=1\n",
                             datetime.date(2026, 11, 13))["monthly piece"]
        self.assertEqual(monthly[1], datetime.date(2026, 12, 1))
        self.assertIsNone(monthly[0])          # three weeks out is not "due"

    def test_the_calendar_decides_the_kind_and_far_off_is_not_due(self):
        import datetime
        text = ("- [ ] 2026-11-01 — old promise\n"
                "- [ ] 2026-11-13 — today's\n"
                "- [ ] 2026-11-20 — next week's\n"
                "- [ ] 2027-03-01 — distant\n")
        got = self.kinds(text, datetime.date(2026, 11, 13))
        self.assertEqual(got["old promise"][0], "overdue")
        self.assertEqual(got["today's"][0], "today")
        self.assertEqual(got["next week's"][0], "soon")
        self.assertIsNone(got["distant"][0])

    def test_an_unreadable_rule_is_reported_not_dropped(self):
        import datetime
        got = self.kinds("- [ ] 2026-11-01 — broken\n  repeat: FREQ=FORTNIGHTLY\n",
                         datetime.date(2026, 11, 13))
        self.assertEqual(got["broken"][0], "unreadable-rule")

    def test_a_seat_with_nothing_due_is_told_so(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "to-do-lists").mkdir()
            (root / "to-do-lists" / "desi.md").write_text("# To-do — desi\n\nnothing dated\n",
                                                          encoding="utf-8")
            block = self.e.due_block(str(root), amigo="desi")
        self.assertIn("Nothing is dated today, overdue, or due in the next", block)
        self.assertIn("Nothing on your list repeats", block)
        self.assertTrue(block.startswith("=== WHAT IS DUE"))

    def test_every_seat_reads_its_own_list(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "to-do-lists").mkdir()
            (root / "to-do-lists" / "desi.md").write_text(
                "- [ ] 2026-11-01 — desi's promise\n", encoding="utf-8")
            (root / "to-do-lists" / "gwen.md").write_text(
                "- [ ] 2026-11-02 — gwen's promise\n", encoding="utf-8")
            desi = self.e.due_block(str(root), amigo="desi")
            gwen = self.e.due_block(str(root), amigo="gwen")
        self.assertIn("desi's promise", desi)
        self.assertNotIn("gwen's promise", desi)
        self.assertIn("gwen's promise", gwen)

    def test_the_due_block_is_the_first_thing_a_wake_reads(self):
        """A block that appears after 6,000 characters of to-do list is a block nobody reaches."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "to-do-lists").mkdir()
            (root / "to-do-lists" / "desi.md").write_text(
                "- [ ] 2026-11-01 — overdue promise\n", encoding="utf-8")
            state = root / "state"
            state.mkdir()
            text = self.e.orientation(str(root), str(state), limit=1)
        self.assertTrue(text.startswith("=== WHAT IS DUE"), text[:120])
        self.assertIn("overdue promise", text.split("=== YOUR TO-DO LIST")[0])


if __name__ == "__main__":
    unittest.main()
