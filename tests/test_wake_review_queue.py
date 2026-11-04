#!/usr/bin/env python3
"""Tests for the wake review-queue block — the job a wake opens with.

The block is only honest if three things hold, and each is pinned here:
  1. no item is ever addressed to its own author (nobody reviews their own work);
  2. an item's reviewer does not change between wakes (the assignment is a function of the id);
  3. an item no one can be named for comes back as a hole, not as a silent default.
"""
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts import wake_review_queue as wq  # noqa: E402


def rec(item_id, author, when="2026-09-15T00:00:00Z", title=None, **kw):
    return {"id": item_id, "amigo": author, "scope": "internal", "state": None,
            "filed_utc": when, "title": title or item_id, "evidence": f"{author}-bot run {item_id}",
            **kw}


class TestAssignment(unittest.TestCase):
    def test_no_item_is_ever_addressed_to_its_author(self):
        for author in wq.il.AMIGOS:
            for i in range(50):
                self.assertNotEqual(wq.reviewer_for(f"item-{author}-{i}", author), author)

    def test_the_assignment_is_stable_across_calls(self):
        first = wq.reviewer_for("20260915T051453Z-dddc728b", "desi")
        for _ in range(10):
            self.assertEqual(wq.reviewer_for("20260915T051453Z-dddc728b", "desi"), first)

    def test_the_assignment_spreads_across_the_other_amigos(self):
        # Not a load-balancer, but it must not funnel everything to one neighbour.
        seen = {wq.reviewer_for(f"x{i}", "desi") for i in range(200)}
        self.assertEqual(seen, {"claude", "gemini", "tarik", "dmitri", "gwen"})

    def test_an_unknown_author_has_no_reviewer(self):
        self.assertIsNone(wq.reviewer_for("x", "someone-not-on-the-roster"))


class TestTheQueue(unittest.TestCase):
    def rows(self):
        items = {r["id"]: r for r in [
            rec("a", "gemini", "2026-09-15T00:00:00Z"),
            rec("b", "gemini", "2026-10-01T00:00:00Z"),
            rec("c", "desi", "2026-09-20T00:00:00Z"),
            rec("d", "nobody", "2026-09-01T00:00:00Z"),          # author not on the roster
            rec("e", "tarik", "2026-09-02T00:00:00Z",
                state="accomplished", reason="landed"),          # not waiting — already decided
        ]}
        return items

    def test_a_decided_item_is_not_in_anyones_queue(self):
        mine, _ = wq.assigned_to(self.rows(), "claude")
        self.assertNotIn("e", [r["id"] for r in mine])

    def test_an_unassignable_item_is_a_hole_not_a_default(self):
        _, holes = wq.assigned_to(self.rows(), "claude")
        self.assertEqual([r["id"] for r in holes], ["d"])

    def test_a_reviewer_sees_only_its_own_items_oldest_first(self):
        items = self.rows()
        mine, _ = wq.assigned_to(items, "claude", limit=10)
        for r in mine:
            self.assertEqual(wq.reviewer_for(r["id"], r["amigo"]), "claude")
        self.assertEqual([r["id"] for r in mine],
                         sorted([r["id"] for r in mine],
                                key=lambda i: items[i]["filed_utc"]))

    def test_the_limit_caps_what_is_shown(self):
        mine, _ = wq.assigned_to(self.rows(), "claude", limit=1)
        self.assertLessEqual(len(mine), 1)


class TestFrozenAssignment(unittest.TestCase):
    """Tarik's 2026-10-30 postponement, closed here with its counterexamples as tests.

    The hash was the only rule, so it overruled `assigned_to` — the name `--assign` writes and
    `item_ledger --queue` reads. The item then showed up in one amigo's wake input and not the
    other's, which is a queue that cannot drain because it disagrees with itself.
    """

    def frozen_id(self, author, frozen):
        """An id whose hash names someone other than `frozen`, so the two rules differ."""
        for n in range(10000):
            iid = f"frozen-{n}"
            if wq.reviewer_for(iid, author) != frozen:
                return iid
        raise AssertionError("no id disagreed with the frozen name")

    def test_a_frozen_name_beats_the_hash(self):
        iid = self.frozen_id("gemini", "tarik")
        r = rec(iid, "gemini", assigned_to="tarik")
        self.assertEqual(wq.reviewer_of(r), "tarik")
        mine, _ = wq.assigned_to({iid: r}, "tarik", limit=10)
        self.assertEqual([x["id"] for x in mine], [iid])

    def test_the_frozen_name_is_not_also_shown_to_the_hashed_reviewer(self):
        iid = self.frozen_id("gemini", "tarik")
        hashed = wq.reviewer_for(iid, "gemini")
        mine, _ = wq.assigned_to({iid: rec(iid, "gemini", assigned_to="tarik")}, hashed, limit=10)
        self.assertEqual(mine, [])

    def test_the_frozen_report_matches_the_ledger_queue(self):
        iid = self.frozen_id("gemini", "tarik")
        items = {iid: rec(iid, "gemini", assigned_to="tarik")}
        self.assertEqual([r["id"] for r in wq.il._named(items, "tarik")],
                         [r["id"] for r in wq.assigned_to(items, "tarik", limit=10)[0]])

    def test_a_frozen_name_nobody_knows_is_a_hole(self):
        r = rec("x", "gemini", assigned_to="someone-who-left")
        self.assertIsNone(wq.reviewer_of(r))
        _, holes = wq.assigned_to({"x": r}, "claude")
        self.assertEqual([h["id"] for h in holes], ["x"])


class TestTheSuppliedLedger(unittest.TestCase):
    """The reading block must count the ledger it was handed, not the public one.

    Counterexample from the same review: `--ledger <one-row fixture>` printed "73 delivered
    item(s)" for dmitri, every one of them from `channels/items.jsonl`.
    """

    def count(self, rows, amigo="dmitri"):
        import json
        import subprocess
        import tempfile
        path = Path(tempfile.mkdtemp()) / "ledger.jsonl"
        path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        out = subprocess.run([sys.executable, str(REPO / "scripts" / "wake_review_queue.py"),
                              "--amigo", amigo, "--ledger", str(path)],
                             capture_output=True, text=True, check=True).stdout
        lines = out.splitlines()
        i = next(n for n, l in enumerate(lines) if l.startswith("=== YOUR READING QUEUE"))
        return int(lines[i + 1].split()[0])

    def test_a_fixture_with_no_unread_rows_reports_zero(self):
        self.assertEqual(self.count([rec("a", "gemini", assigned_to="dmitri")]), 0)

    def test_a_fixture_with_one_unread_row_reports_one(self):
        unread = rec("b", "gemini", state="accomplished", reviewer="auto:land",
                     reading_assigned_to="dmitri")
        self.assertEqual(self.count([rec("a", "gemini"), unread]), 1)


class TestTheBlock(unittest.TestCase):
    def test_the_block_names_the_reviewer_and_the_command(self):
        text = wq.block({r["id"]: r for r in [rec("a", "gemini")]}, "claude")
        self.assertIn("addressed to claude", text)
        self.assertIn("--reviewer claude", text)

    def test_the_block_surfaces_holes(self):
        items = {r["id"]: r for r in [rec("d", "nobody"), rec("a", "gemini")]}
        text = wq.block(items, "claude")
        self.assertIn("HOLES", text)
        self.assertIn("  d  ", text)


if __name__ == "__main__":
    unittest.main()
