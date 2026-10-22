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


if __name__ == "__main__":
    unittest.main()
