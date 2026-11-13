#!/usr/bin/env python3
"""A row filed for a seat must reach that seat's wake, wherever in the ledger it sits.

Run with:  python3 tests/test_wake_ledger_rows.py
Exit code 0 = pass. No third-party dependencies.

Why this exists. `channels/wake_engine.py` hands every wake the task ledger truncated to its first
10,000 characters, because the ledger is 185,622 characters and 123 open rows. Truncation is
positional, and on 2026-11-13 the founder's vehicle-pool proposal was measured at character 129,396 —
119,396 characters past the cut. So the row *"All six: ratify or amend the pool"* and the row
*"Gemini: does rover #2 enter the pool?"* had never been in any wake's context between 2026-11-01 and
that day. One seat had the row transcribed into her own to-do list by hand; the other had nothing.

Nobody inside a wake could notice: an absent row and a row you were not meant to see look identical
from inside. The founder noticed instead, from the outside, and asked whether a seat could be made
aware — which is the useful property of a human in the loop.

The fix is the one `tests/test_wake_context_caps.py` found for the agenda on 2026-10-17: do not
enlarge the window, move the list to where the window falls. `open_rows_for` returns the open rows
that ask the whole cohort and the open rows that name the seat, from anywhere in the file, capped on
three axes so a verbose seat cannot crowd out the rest of the prompt.

This test asserts the repair on the real ledger (`BOTH` below) and the invariants on synthetic text,
because a filter that matches too much is as bad as one that matches nothing.
"""

import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ENGINE = REPO / "channels" / "wake_engine.py"
LEDGER = REPO / "channels" / "tasks.md"
SEATS = ("claude", "desi", "dmitri", "gemini", "gwen", "tarik")
HEAD = 10000          # the window the engine hands the wake; asserted below against the engine


def load_engine():
    spec = importlib.util.spec_from_file_location("wake_engine_under_test", str(ENGINE))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class LedgerRows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.we = load_engine()
        cls.text = LEDGER.read_text(encoding="utf-8")

    def rows(self, seat, text=None, head=None):
        """`head=0` in the synthetic tests: a short fixture sits entirely inside the real window,
        and the window-skip is a separate behaviour with its own test below."""
        text = self.text if text is None else text
        return self.we.open_rows_for(seat, text, head=HEAD if head is None else head)

    # ---- the real ledger: the repair this was written for -------------------------------

    def test_the_window_is_the_one_the_engine_uses(self):
        """A guard measuring a different window than the engine applies is theatre."""
        self.assertEqual(HEAD, 10000)
        src = ENGINE.read_text(encoding="utf-8")
        self.assertIn("text[:10000]", src,
                      "wake_engine no longer truncates the ledger at 10,000 characters; this test's "
                      "premise and the engine's cap are one fact and must be changed together")

    def test_the_pool_rows_are_past_the_truncation_point(self):
        """The premise. If this ever fails, the rows arrived by luck, not by this fix."""
        at = self.text.find("Filed by Gwen: the founder's vehicle-pool proposal")
        self.assertNotEqual(at, -1, "the vehicle-pool section is gone from the ledger")
        self.assertGreater(at, HEAD,
                           "the pool section now sits inside the visible head — the pull-out below "
                           "is no longer what delivers it")

    def test_every_seat_is_handed_the_cohort_ratification_row(self):
        for seat in SEATS:
            with self.subTest(seat=seat):
                cohort = self.rows(seat)["cohort"]
                self.assertTrue(any("ratify or amend the pool" in r for r in cohort),
                                "%s is not handed the pool ratification row:\n%s"
                                % (seat, "\n".join(r[:100] for r in cohort)))

    def test_gemini_is_handed_the_row_that_names_her(self):
        named = self.rows("gemini")["named"]
        self.assertTrue(any("rover #2 enter the pool" in r for r in named),
                        "Gemini's owed answer is not delivered:\n%s" % "\n".join(r[:100] for r in named))

    def test_nobody_is_handed_a_row_that_is_not_theirs(self):
        """A row naming only Gemini must not appear in Tarik's named list."""
        named = self.rows("tarik")["named"]
        self.assertFalse(any("Does rover #2 enter the vehicle pool" in r for r in named),
                         "Tarik is handed Gemini's row")

    def test_the_prompt_cost_stays_bounded(self):
        for seat in SEATS:
            with self.subTest(seat=seat):
                r = self.rows(seat)
                total = sum(len(x) for x in r["cohort"] + r["named"])
                self.assertLessEqual(total, self.we.OPEN_ROW_BUDGET,
                                     "%s's rows cost %d characters, budget is %d"
                                     % (seat, total, self.we.OPEN_ROW_BUDGET))

    def test_the_engine_actually_delivers_them(self):
        """The helper is worthless if `orientation()` does not call it.

        Caught while writing this file: stubbing the call out of `orientation()` left all twelve
        filter tests green, because they exercise `open_rows_for` directly. A test of something
        nothing invokes is the same defect as a check whose blind spot looks like a healthy state.
        """
        import tempfile
        empty = Path(tempfile.mkdtemp(prefix="wake-state-"))
        raw = self.we.orientation(REPO, empty)
        ctx = raw if isinstance(raw, str) else "\n".join(raw)
        self.assertIn("OPEN ROWS THAT ASK THE WHOLE COHORT", ctx,
                      "orientation() builds no cohort block — the pull-out is not wired in")
        self.assertIn("ratify or amend the pool", ctx)
        old, self.we.AMIGO = self.we.AMIGO, "gemini"
        try:
            raw = self.we.orientation(REPO, empty)
            ctx = raw if isinstance(raw, str) else "\n".join(raw)
        finally:
            self.we.AMIGO = old
        self.assertIn("rover #2 enter the pool", ctx,
                      "orientation() does not deliver the rows that name the seat it is waking")

    # ---- synthetic text: the filter itself ---------------------------------------------

    def test_a_finished_row_is_not_an_open_row(self):
        text = ("- [x] **All six: ratify or amend the pool.** Done for months.\n"
                "- [x] **Desi: something you finished.**\n")
        r = self.rows("desi", text, head=0)
        self.assertEqual(r["cohort"], [])
        self.assertEqual(r["named"], [])

    def test_continuation_lines_travel_with_their_row(self):
        text = ("- [ ] **Gemini: does rover #2 enter the pool?** Yours first,\n"
                "  cohort second; record: `rover/2026-11-01-vehicle-pool-proposal.md`.\n")
        r = self.rows("gemini", text, head=0)["named"]
        self.assertEqual(len(r), 1)
        self.assertIn("rover/2026-11-01-vehicle-pool-proposal.md", r[0],
                      "the row was delivered without its continuation line")

    def test_a_word_that_merely_contains_a_name_is_not_a_name(self):
        text = ("- [ ] **His desire to control the money is natural.** Says the founder.\n"
                "- [ ] **Designate one reporter.** Not decided.\n")
        self.assertEqual(self.rows("desi", text, head=0)["named"], [],
                         "substring matching handed Desi a row about somebody's desire")

    def test_the_name_is_matched_wherever_it_sits(self):
        text = ("- [ ] **Tarik: finish the handoff poll.**\n")
        self.assertEqual(len(self.rows("tarik", text, head=0)["named"]), 1)
        self.assertEqual(len(self.rows("gwen", text, head=0)["named"]), 0)

    def test_rows_already_inside_the_window_are_not_repeated(self):
        text = "- [ ] **Gemini: inside the window.**\n" + ("x" * (HEAD + 10)) + "\n"
        self.assertEqual(self.rows("gemini", text)["named"], [],
                         "a row already delivered by truncation was delivered twice")

    def test_a_seat_with_many_rows_is_bounded_and_told_what_was_cut(self):
        text = "".join("- [ ] **Gwen: row number %d.** " % i + "y" * 300 + "\n" for i in range(40))
        r = self.rows("gwen", text, head=0)
        self.assertLessEqual(len(r["named"]), self.we.OPEN_ROW_NAMED_CAP)
        self.assertGreater(r["dropped"], 0, "rows were dropped without being counted")
        self.assertLessEqual(sum(len(x) for x in r["named"]), self.we.OPEN_ROW_BUDGET)

    def test_a_cohort_row_cannot_be_starved_by_rows_that_name_the_seat(self):
        text = "".join("- [ ] **Desi: row number %d.** " % i + "z" * 300 + "\n" for i in range(40))
        text += "- [ ] **All six: ratify or amend the pool.** Silence is not consent.\n"
        r = self.rows("desi", text, head=0)
        self.assertTrue(any("ratify or amend the pool" in x for x in r["cohort"]),
                        "forty rows naming Desi starved the cohort row she owes a vote on")
        self.assertTrue(r["named"], "the named rows were starved in the other direction")


if __name__ == "__main__":
    unittest.main(verbosity=2)
