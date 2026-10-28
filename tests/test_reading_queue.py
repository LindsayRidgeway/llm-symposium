"""The second queue: items the landing gate closed and nobody read.

Why this exists as a test at all: on 2026-10-22 there were 252 such items and *no queue contained
them*. `--queue` lists waiting items; these are not waiting, they are finished. So an instruction to
"read one item from your review queue each wake" could be obeyed perfectly, forever, and never touch
one of them. These tests pin the two properties that make them reachable: they can be named, and the
name goes to a body that wakes.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "channels"))
import item_ledger as il  # noqa: E402


def row(item_id: str, **kw) -> dict:
    base = {"id": item_id, "amigo": "desi", "filed_utc": "2026-10-01T00:00:00Z",
            "state": "accomplished", "reviewer": "auto:land", "reason": "landed on main",
            "short_title": "work"}
    base.update(kw)
    return base


class UnreadTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.path = self.dir / "items.jsonl"

    def write(self, rows):
        self.path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    def test_closed_by_the_machine_is_unread(self):
        self.assertTrue(il.is_unread(row("a")))
        self.assertTrue(il.is_unread(row("b", reviewer="auto:path")))

    def test_a_model_that_looked_makes_it_read(self):
        self.assertFalse(il.is_unread(row("c", reviewer="dmitri")))

    def test_a_waiting_item_is_not_in_this_queue(self):
        self.assertFalse(il.is_unread(row("d", state=None, reviewer=None)))

    def test_naming_never_gives_an_item_to_its_author(self):
        self.write([row("x", amigo="desi"), row("y", amigo="dmitri")])
        made = il.name_unread(path=self.path, by="test")
        self.assertEqual(len(made), 2)
        for rec in made:
            self.assertNotEqual(rec["reading_assigned_to"], rec["amigo"])

    def test_naming_twice_names_nothing_the_second_time(self):
        self.write([row("z")])
        first = il.name_unread(path=self.path, by="test")
        second = il.name_unread(path=self.path, by="test")
        self.assertEqual(len(first), 1)
        self.assertEqual(second, [])

    def test_naming_does_not_change_the_state(self):
        self.write([row("q")])
        made = il.name_unread(path=self.path, by="test")
        self.assertEqual(made[0]["state"], "accomplished")
        self.assertIn("reading_assigned_to", made[0])

    def test_the_pick_is_re_derivable_from_the_id(self):
        a = il._capacity_pick("20261001T000000Z-abc123", "desi")
        b = il._capacity_pick("20261001T000000Z-abc123", "desi")
        self.assertEqual(a, b)

    def test_the_reading_queue_is_per_amigo(self):
        self.write([row("m1"), row("m2")])
        il.name_unread(path=self.path, by="test")
        items = il.load(self.path)
        for rec in items.values():
            who = rec["reading_assigned_to"]
            mine = il.reading_queue(path=self.path, who=who)
            self.assertIn(rec["id"], [r["id"] for r in mine])
        total = sum(len(il.reading_queue(path=self.path, who=a)) for a in il.AMIGOS)
        self.assertEqual(total, 2)


class CapacityWeightingTest(unittest.TestCase):
    def test_a_body_that_wakes_hourly_gets_more_of_the_pile_than_one_that_wakes_daily(self):
        ids = [f"2026100{i}T000000Z-{i:04d}" for i in range(400)]
        picks = [il._capacity_pick(i, "nobody") for i in ids]
        counts = {a: picks.count(a) for a in il.AMIGOS}
        self.assertGreater(counts["desi"] + counts["dmitri"], 6 * (counts["claude"] + counts["tarik"]))
        self.assertGreater(counts["gemini"], counts["claude"])

    def test_an_author_excluded_from_the_pool_still_gets_a_name_from_the_rest(self):
        pick = il._capacity_pick("some-id", "desi")
        self.assertNotEqual(pick, "desi")


class ReadingAssignTest(unittest.TestCase):
    """Branch (a) on the second queue: one amigo is plainly the right reader, and says why.

    Written because the rule could not be obeyed. `--assign` refuses anything that is not waiting,
    and the reading queue could only be re-named by a corrected capacity table — so "the author of a
    gate script is not its reviewer, and here is who is" had no command behind it, and a four-wake
    debt stayed unpaid while the draw's name sat on an amigo with 74 unread items.
    """

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.path = self.dir / "items.jsonl"

    def write(self, rows):
        self.path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    def test_a_judged_reader_replaces_the_draw_and_records_why(self):
        self.write([row("a", amigo="desi", reading_assigned_to="dmitri",
                        reading_assign_kind="draw", reading_assign_reason="capacity draw")])
        rec = il.reading_assign(path=self.path, item_id="a", to="tarik",
                                reason="he owns the gate tooling this hooks into", by="desi",
                                force=True)
        self.assertEqual(rec["reading_assigned_to"], "tarik")
        self.assertEqual(rec["reading_assign_kind"], "name")
        self.assertIn("gate tooling", rec["reading_assign_reason"])
        self.assertEqual(rec["reading_assigned_by"], "desi")

    def test_the_author_is_never_the_reader(self):
        self.write([row("b", amigo="desi")])
        with self.assertRaises(ValueError):
            il.reading_assign(path=self.path, item_id="b", to="desi", reason="he wrote it")

    def test_a_name_with_no_reason_is_refused(self):
        self.write([row("c")])
        with self.assertRaises(ValueError):
            il.reading_assign(path=self.path, item_id="c", to="gemini", reason="   ")

    def test_a_frozen_name_does_not_drift_without_force(self):
        self.write([row("d", reading_assigned_to="claude", reading_assign_kind="draw")])
        with self.assertRaises(ValueError):
            il.reading_assign(path=self.path, item_id="d", to="tarik", reason="better suited")

    def test_the_verdict_is_untouched(self):
        """What is being assigned is the reading, not the outcome."""
        self.write([row("e")])
        rec = il.reading_assign(path=self.path, item_id="e", to="gemini", reason="plainly hers")
        self.assertEqual(rec["state"], "accomplished")
        self.assertEqual(rec["reviewer"], "auto:land")
        self.assertTrue(il.is_unread(rec))

    def test_an_item_a_model_has_read_is_not_readable_again(self):
        self.write([row("f", reviewer="gemini")])
        with self.assertRaises(ValueError):
            il.reading_assign(path=self.path, item_id="f", to="tarik", reason="already read")

    def test_a_corrected_table_does_not_overrule_a_judged_name(self):
        """The guard: a draw may be re-rolled for a better table; a reason may not."""
        self.write([row(f"id{i:03d}", amigo="gemini") for i in range(40)])
        il.name_unread(path=self.path, by="test")
        il.reading_assign(path=self.path, item_id="id000", to="tarik",
                          reason="he owns this one's subject", by="desi", force=True)
        il.WAKES_PER_DAY["claude"] = 500
        try:
            il.rebalance_unread(path=self.path, by="test")
        finally:
            il.WAKES_PER_DAY.pop("claude", None)
        rec = il.load(self.path)["id000"]
        self.assertEqual(rec["reading_assigned_to"], "tarik")
        self.assertEqual(rec["reading_assign_kind"], "name")


class RebalanceTest(unittest.TestCase):
    """The one exception to 'a draw does not re-roll': the table was wrong, and it was measurable."""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.path = self.dir / "items.jsonl"
        rows = [row(f"id{i:03d}", amigo="gemini") for i in range(60)]
        self.path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        self.saved = dict(il.WAKES_PER_DAY)

    def tearDown(self):
        il.WAKES_PER_DAY.clear()
        il.WAKES_PER_DAY.update(self.saved)

    def test_a_stale_table_is_corrected_and_the_row_says_why(self):
        il.name_unread(path=self.path, by="test")
        il.WAKES_PER_DAY["tarik"] = 12          # tarik now wakes hourly
        before = sum(1 for r in il.load(self.path).values() if r["reading_assigned_to"] == "tarik")
        made = il.rebalance_unread(path=self.path, by="test")
        after = sum(1 for r in il.load(self.path).values() if r["reading_assigned_to"] == "tarik")
        self.assertGreater(len(made), 0)
        self.assertGreater(after, before)
        self.assertIn("stale", made[0]["reading_assign_reason"])

    def test_the_same_table_rebalances_nothing(self):
        il.name_unread(path=self.path, by="test")
        self.assertEqual(il.rebalance_unread(path=self.path, by="test"), [])

    def test_rebalance_leaves_items_nobody_named_alone(self):
        self.assertEqual(il.rebalance_unread(path=self.path, by="test"), [])


if __name__ == "__main__":
    unittest.main()
