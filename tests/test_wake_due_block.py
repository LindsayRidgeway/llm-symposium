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


class TheCalendarSurvivesItsOwnList(unittest.TestCase):
    """The repeater that a wholesale rewrite cannot delete.

    Added 2026-11-19, the third time the same loss was found: a wake overwrites to-do-lists/<seat>.md
    from memory, the `repeat:` lines go with it, and the due block truthfully reports that nothing
    repeats. Twice this was restored by hand; a promise that survives only in a file its owner
    rewrites is not a promise, so the machine keeps its own copy in channels/recurring.json.
    """

    def setUp(self):
        import json
        import tempfile
        self.e = load_engine()
        self._amigo = self.e.AMIGO
        self.e.AMIGO = "desi"
        self.dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.dir.name)
        (self.repo / "to-do-lists").mkdir()
        (self.repo / "channels").mkdir()
        self.list = self.repo / "to-do-lists" / "desi.md"
        self.registry = self.repo / "channels" / "recurring.json"
        self.registry.write_text(json.dumps({"desi": [
            {"text": "Weekly: one letter to a stranger.", "repeat": "FREQ=WEEKLY;INTERVAL=1",
             "since": "2026-11-23"}]}), encoding="utf-8")

    def tearDown(self):
        self.e.AMIGO = self._amigo
        self.dir.cleanup()

    def test_a_repeat_the_list_lost_is_still_due(self):
        self.list.write_text("- [ ] 2026-11-01 — something else\n", encoding="utf-8")
        text = self.e.due_block(str(self.repo), amigo="desi")
        self.assertIn("one letter to a stranger", text)
        self.assertIn("from the machine calendar", text)

    def test_a_repeat_the_list_still_carries_is_not_duplicated(self):
        self.list.write_text("- [ ] 2026-11-23 — Weekly: one letter to a stranger.\n"
                             "  repeat: FREQ=WEEKLY;INTERVAL=1\n", encoding="utf-8")
        text = self.e.due_block(str(self.repo), amigo="desi")
        self.assertEqual(text.count("one letter to a stranger"), 1)
        self.assertNotIn("from the machine calendar", text)

    def test_a_bolded_title_is_the_same_promise_not_a_second_one(self):
        """Measured on the live list 2026-11-19: `**Weekly: ...**` and `Weekly: ...` printed twice."""
        self.list.write_text("- [ ] 2026-11-23 — **Weekly: one letter to a stranger.** Text after it.\n"
                             "  repeat: FREQ=WEEKLY;INTERVAL=1\n", encoding="utf-8")
        text = self.e.due_block(str(self.repo), amigo="desi")
        self.assertEqual(text.count("one letter to a stranger"), 1)

    def test_another_seats_calendar_is_not_borrowed(self):
        self.list.write_text("- [ ] 2026-11-01 — something else\n", encoding="utf-8")
        text = self.e.due_block(str(self.repo), amigo="claude")
        self.assertNotIn("one letter to a stranger", text)

    def test_no_registry_changes_nothing(self):
        self.registry.unlink()
        self.list.write_text("- [ ] 2027-03-01 — distant, dated, once\n", encoding="utf-8")
        text = self.e.due_block(str(self.repo), amigo="desi")
        self.assertIn("Nothing on your list repeats", text)


if __name__ == "__main__":
    unittest.main()
