#!/usr/bin/env python3
"""Tests for the D letter — "delivered, not read" — added 2026-10-25.

The problem it answers, measured the hour it was written: of 492 items in A, 263 had been closed
by a machine (195 by the lander's test gate, 68 by the path check) and never by a reader; of the
306 items ever machine-closed, only 38 — 12% — were opened by a model afterwards. So `accomplished`
carried two incompatible claims, and the review rate could not be read from it.

Three things are pinned here, because each is a way the fix can silently stop working:

  1. the letter and the reading queue are the same predicate (`is_unread`), so they cannot drift;
  2. `collect` names every machine-closed-but-unread item the moment it exists — routing by code,
     not by anybody remembering to run `--name-unread`;
  3. an append can never un-decide an item: a later row that carries no state inherits the
     decision already on the record and says where it came from. Silence is not a reversal.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from channels import item_ledger as il  # noqa: E402


def row(item_id: str, *, state=None, reviewer=None, reason=None, amigo="desi", filed=None,
        **kw) -> dict:
    rec = {
        "id": item_id, "amigo": amigo, "scope": "internal", "source": "derived",
        "filed_utc": filed or "2026-10-25T00:00:00Z", "title": item_id,
        "paths": [f"docs/works/{item_id}.html"], "state": state, "state_utc": None,
        "reviewer": reviewer, "reason": reason,
    }
    rec.update(kw)
    return rec


class Letters(unittest.TestCase):
    def test_a_machine_closure_is_d_and_a_reader_is_a(self):
        self.assertEqual(il.letter_for(row("x", state="accomplished", reviewer="auto:land")), "D")
        self.assertEqual(il.letter_for(row("x", state="accomplished", reviewer="auto:path")), "D")
        self.assertEqual(il.letter_for(row("x", state="accomplished", reviewer="dmitri")), "A")

    def test_the_letter_and_the_reading_queue_are_one_predicate(self):
        for rec in [row("x", state="accomplished", reviewer="auto:land"),
                    row("x", state="accomplished", reviewer="auto:path"),
                    row("x", state="accomplished", reviewer="desi"),
                    row("x", state="postponed", reviewer="desi", reason="not now"),
                    row("x")]:
            self.assertEqual(il.letter_for(rec) == "D", il.is_unread(rec), rec)

    def test_a_reader_who_opens_a_delivered_item_turns_it_into_an_a(self):
        """The pile can drain: nothing refuses a verdict on a D item."""
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "items.jsonl"
            il.append([row("x", state="accomplished", reviewer="auto:path",
                           reason="delivered: every path is on main")], path)
            self.assertEqual(il.letter_for(il.load(path)["x"]), "D")
            il.review(path=path, item_id="x", state="accomplished", reviewer="tarik",
                      reason="read it; the work is in docs/works/x.html and it is finished")
            self.assertEqual(il.letter_for(il.load(path)["x"]), "A")


class Routing(unittest.TestCase):
    def test_collect_names_every_unread_item_so_it_is_in_a_queue(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "items.jsonl"
            il.append([row("a", state="accomplished", reviewer="auto:land",
                           reason="landed on main (lander's test gate passed)"),
                       row("b", state="accomplished", reviewer="desi", reason="read and kept")], path)
            self.assertIsNone(il.load(path)["a"].get("reading_assigned_to"))
            # collect() is the writer that runs on every wake; naming happens there, not by hand
            il.name_unread(path=path, by="collect")
            rec = il.load(path)["a"]
            self.assertIn(rec.get("reading_assigned_to"), il.AMIGOS)
            self.assertNotEqual(rec.get("reading_assigned_to"), rec.get("amigo"))  # never its author
            self.assertIsNone(il.load(path)["b"].get("reading_assigned_to"))       # already read

    def test_naming_is_stable_and_never_names_the_author(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "items.jsonl"
            il.append([row("a", state="accomplished", reviewer="auto:land",
                           reason="landed on main (lander's test gate passed)")], path)
            first = il.name_unread(path=path, by="collect")[0]["reading_assigned_to"]
            self.assertEqual(il.name_unread(path=path, by="collect"), [])   # idempotent
            self.assertNotEqual(first, "desi")

    def test_an_assignment_cannot_erase_a_decision(self):
        """The 2026-10-25 damage: a null-state row between two closures read as 'waiting'."""
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "items.jsonl"
            il.append([row("x", state="accomplished", reviewer="auto:path",
                           reason="delivered: every path is present on main",
                           state_utc="2026-10-24T11:45:05Z")], path)
            il.append([row("x", assigned_to="dmitri", assign_kind="draw",
                           assigned_utc="2026-10-25T11:45:06Z",
                           assign_reason="drawn at random")], path)
            rec = il.load(path)["x"]
            self.assertEqual(rec["state"], "accomplished")     # kept
            self.assertEqual(rec["reviewer"], "auto:path")     # kept
            self.assertEqual(rec["reason"], "delivered: every path is present on main")
            self.assertEqual(rec["decision_preserved_from"], "2026-10-24T11:45:05Z")
            self.assertEqual(rec["assigned_to"], "dmitri")     # the new fact still lands
            self.assertEqual(il.letter_for(rec), "D")

    def test_a_real_decision_still_overwrites(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "items.jsonl"
            il.append([row("x", state="postponed", reviewer="desi", reason="needs a key")], path)
            il.append([row("x", state="accomplished", reviewer="tarik",
                           reason="the key arrived; docs/works/x.html is done")], path)
            self.assertEqual(il.load(path)["x"]["reviewer"], "tarik")


class Quota(unittest.TestCase):
    """2026-10-29: the quota was written on 10-25 into scripts/wake_review_queue.py — a block that
    prints only when a person runs it by hand, which nothing does. So the number reached no wake,
    and ledger_watch.py called the silence "the quota being ignored". These tests exist so the
    number cannot go unreachable again: it is printed by the command the wake opens with."""

    def test_two_reads_while_the_pile_is_over_the_target(self):
        self.assertEqual(il.quota(il.PILE_TARGET + 1), 2)
        self.assertEqual(il.quota(10_000), 2)

    def test_one_read_once_the_pile_is_under_the_target(self):
        self.assertEqual(il.quota(il.PILE_TARGET), 1)
        self.assertEqual(il.quota(0), 1)

    def test_the_reading_queue_command_prints_the_quota(self):
        """The whole point: the number appears where a wake actually looks, not in a helper."""
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "items.jsonl"
            il.append([row(f"x{i}", state="accomplished", reviewer="auto:land",
                           reason="landed on main (lander's test gate passed)") for i in range(3)],
                      path)
            il.name_unread(path=path, by="collect")
            out = io.StringIO()
            real_queue = il.reading_queue
            argv = sys.argv[:]

            def on_the_temp_ledger(path_=None, who=""):   # defaults bind the real LEDGER at def time
                return real_queue(path_ or path, who=who)

            try:
                il.reading_queue = on_the_temp_ledger
                sys.argv = ["item_ledger.py", "--reading-queue", "dmitri"]
                with contextlib.redirect_stdout(out):
                    il._cli()
            finally:
                il.reading_queue = real_queue
                sys.argv = argv
            text = out.getvalue()
            self.assertIn("quota", text)
            self.assertIn("read 1", text)          # pile is 3, under the target
            self.assertIn("never-read item(s) carry dmitri", text)

    def test_the_failure_line_reports_the_measurement_not_a_guess(self):
        """ledger_watch's reason must name what it counted. It cannot know why nobody read."""
        sys.path.insert(0, str(REPO / "scripts"))
        import ledger_watch as lw
        now = {"queue": 12, "arrivals_24h": 27, "pile": 201, "pile_read_24h": 10,
               "model_decisions_24h": 12}
        passes, reasons = lw.verdict(now, {"queue": 12, "pile": 195})
        self.assertFalse(passes)
        first = reasons[0]
        self.assertIn("201", first)
        self.assertIn("195", first)          # what it was, not just what it is
        self.assertIn("10 were read in 24h", first)
        self.assertIn("quota is 2", first)   # and where the number comes from
        self.assertNotIn("being ignored", first)   # the guess that was wrong
        self.assertNotIn("wake block", first)      # the place that never carried it

    def test_an_append_cannot_take_an_item_away_from_its_reviewer(self):
        """Found 2026-11-11 building the assignment census: item 20261101T054704Z-cdd6c59d was
        drawn to gemini, and a later append carrying no assignment fields dropped the name, so the
        record read as never assigned to anybody. A name is as erasable as a decision."""
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "items.jsonl"
            il.append([row("x", assigned_to="gemini", assigned_utc="2026-11-01T06:00:00Z",
                           assigned_by="draw", assign_kind="draw",
                           assign_reason="drawn at random")], path)
            il.append([row("x", state="accomplished", reviewer="tarik",
                           reason="read it and kept it")], path)
            rec = il.load(path)["x"]
            self.assertEqual(rec["assigned_to"], "gemini")
            self.assertEqual(rec["assign_reason"], "drawn at random")
            self.assertEqual(rec["assignment_preserved_from"], "2026-11-01T06:00:00Z")
            self.assertEqual(rec["state"], "accomplished")      # the real decision still lands

    def test_a_redraw_still_moves_the_item(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "items.jsonl"
            il.append([row("x", assigned_to="gemini", assigned_utc="2026-11-01T06:00:00Z")], path)
            il.append([row("x", assigned_to="desi", assigned_utc="2026-11-05T06:00:00Z")], path)
            self.assertEqual(il.load(path)["x"]["assigned_to"], "desi")


class SelfSigned(unittest.TestCase):
    """The author is never the reviewer — a rule that had no enforcement point until 2026-11-13.

    It had been stated in `item_ledger`'s docstring since 2026-10-18 and only ever applied to the
    *draw*: an item the draw named went to somebody else, but a verdict typed by hand walked past
    the rule entirely. Measured that day: 24 of the 410 model verdicts written since 11-01 were
    signed by the body that filed the item. Nothing noticed, because nothing was measuring.
    """

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "items.jsonl"

    def tearDown(self):
        self.dir.cleanup()

    def test_a_verdict_signed_by_the_filer_is_listed(self):
        il.append([row("mine", state="accomplished", reviewer="desi",
                       reason="docs/works/mine.html")], self.path)
        got = il.self_signed(il.load(self.path))
        self.assertEqual([r["id"] for r in got], ["mine"])
        self.assertEqual(got[0]["reviewer"], "desi")

    def test_a_machine_closure_and_another_body_are_not_self_review(self):
        il.append([row("landed", state="accomplished", reviewer="auto:land",
                       reason="landed on main (lander's test gate passed)"),
                   row("theirs", state="accomplished", reviewer="dmitri",
                       reason="docs/works/theirs.html")], self.path)
        self.assertEqual(il.self_signed(il.load(self.path)), [])

    def test_the_ledger_refuses_to_write_one(self):
        real = il.LEDGER
        il.LEDGER = self.path
        try:
            il.append([row("mine")], self.path)
            with self.assertRaises(ValueError) as caught:
                il.review(item_id="mine", state="postponed", reason="not now",
                          reviewer="desi", path=self.path)
            self.assertIn("author is never the reviewer", str(caught.exception))
            self.assertEqual(il.load(self.path)["mine"]["state"], None)
        finally:
            il.LEDGER = real

    def test_another_body_may_still_close_it(self):
        il.append([row("mine")], self.path)
        rec = il.review(item_id="mine", state="postponed", reason="not now",
                        reviewer="gemini", path=self.path)
        self.assertEqual(rec["reviewer"], "gemini")

    def test_the_daily_check_prints_the_number(self):
        """Wired, not merely available: the count is in the message the human reads every day."""
        sys.path.insert(0, str(REPO / "scripts"))
        import ledger_watch as lw
        import datetime as dt
        m = lw.measure(dt.datetime.now(dt.timezone.utc))
        self.assertIn("self_signed_all", m)
        text = lw.message(m, None, "yesterday", {}, True, ["nothing to explain"], "test")
        self.assertIn("signed by the body that filed the item", text)
        self.assertIn(str(m["self_signed_all"]), text)


if __name__ == "__main__":
    unittest.main()


