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


if __name__ == "__main__":
    unittest.main()
