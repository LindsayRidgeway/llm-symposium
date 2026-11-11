#!/usr/bin/env python3
"""Tests for scripts/assignment_report.py — the page the human asked for on 2026-11-11.

What can silently go wrong with a report like this, and is pinned here:

  1. a letter the ledger can produce but the legend does not explain — the page would then be
     unreadable in exactly the place it claims to be readable;
  2. a re-drawn name hiding the first name (the item appears under only one member);
  3. an item with no members quietly vanishing instead of appearing in the unassigned group;
  4. a date invented for an item that has none, which would make old work look new;
  5. a sort that is claimed but not performed.
"""
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "channels"))
sys.path.insert(0, str(REPO / "scripts"))

import item_ledger as il                      # noqa: E402
from scripts import assignment_report as ar   # noqa: E402


def item(item_id: str, **kw) -> dict:
    rec = {
        "id": item_id, "amigo": "desi", "scope": "internal", "source": "derived",
        "filed_utc": "2026-10-20T04:00:00Z", "title": f"title of {item_id}",
        "paths": [f"docs/{item_id}.html"], "state": None, "state_utc": None,
        "reviewer": None, "reason": None,
    }
    rec.update(kw)
    return rec


class Report(unittest.TestCase):
    def setUp(self):
        self.items: dict[str, dict] = {}
        self.rows: dict[str, list[dict]] = {}
        self._real_load = il.load
        il.load = lambda path=None: self.items     # the report reads the ledger through il.load

    def tearDown(self):
        il.load = self._real_load

    def add(self, record: dict, *history: dict):
        self.items[record["id"]] = record
        self.rows[record["id"]] = [record, *history]

    def page(self) -> str:
        return ar.render(self.rows, "2026-11-11 00:00 UTC")

    def test_the_legend_explains_every_letter_the_ledger_can_produce(self):
        self.add(item("a", state="accomplished", reviewer="auto:land", reason="landed"))
        self.add(item("b", state="accomplished", reviewer="dmitri", reason="read it"))
        self.add(item("c", state="postponed", reviewer="desi", reason="needs a key"))
        self.add(item("d", state="rejected", reviewer="desi", reason="not worth doing"))
        self.add(item("e"))
        text = self.page()
        produced = {il.letter_for(r) for r in self.items.values()}
        self.assertEqual(produced, {"A", "D", "P", "R", "W"})
        for letter, _ in ar.LEGEND:
            self.assertIn(f"| **{letter}** |", text, letter)

    def test_an_item_redrawn_to_another_member_appears_under_both(self):
        """A re-draw cannot launder who had it first."""
        self.add(item("x", assigned_to="desi", assigned_utc="2026-10-21T06:00:00Z"),
                 item("x", assigned_to="dmitri", assigned_utc="2026-10-22T06:00:00Z"))
        text = self.page()
        desi_block = text.split("## Assigned to desi")[1].split("## Assigned to")[0]
        dmitri_block = text.split("## Assigned to dmitri")[1].split("## ")[0]
        self.assertIn("title of x", desi_block)
        self.assertIn("title of x", dmitri_block)

    def test_an_unassigned_item_lands_in_the_last_group_not_under_a_member(self):
        self.add(item("named", assigned_to="desi"))
        self.add(item("orphan"))
        text = self.page()
        self.assertIn("## Never assigned to anyone", text)
        tail = text.split("## Never assigned to anyone")[1].split("## Reading assignments")[0]
        self.assertIn("title of orphan", tail)
        self.assertNotIn("title of orphan", text.split("## Never assigned")[0])

    def test_a_missing_date_says_undated_rather_than_inventing_one(self):
        self.add(item("old", filed_utc=None, assigned_to="desi",
                      assigned_utc="2026-10-19T02:00:00Z"))
        self.add(item("none", filed_utc=None, assigned_to="desi"))
        text = self.page()
        self.assertIn("undated", text.lower(), "the page must not print today's date")
        self.assertNotIn("2026-11-11 |", text.split("## Assigned to desi")[1].split("##")[0])

    def test_the_date_falls_back_to_the_next_significant_date_before_giving_up(self):
        rec = {"id": "d1", "amigo": "desi", "title": "t", "filed_utc": None}
        self.add(rec, {"id": "d1", "assigned_utc": "2026-10-19T02:00:00Z"})
        self.items["d1"]["assigned_to"] = "desi"
        self.assertIn("| 2026-10-19 |", self.page())

    def test_items_are_sorted_by_date_then_status_then_title(self):
        self.add(item("i1", filed_utc="2026-10-22T00:00:00Z", title="zeta", assigned_to="desi"))
        self.add(item("i2", filed_utc="2026-10-22T00:00:00Z", title="alpha", assigned_to="desi"))
        self.add(item("i3", filed_utc="2026-10-21T00:00:00Z", title="beta", assigned_to="desi"))
        self.add(item("i4", filed_utc=None, title="gamma", assigned_to="desi",
                      state="rejected", reviewer="tarik", reason="no"))
        block = self.page().split("## Assigned to desi")[1].split("## ")[0]
        order = [(ln.split("|")[1].strip(), ln.split("|")[2].strip())
                 for ln in block.splitlines()
                 if ln.startswith("| 2026") or ln.startswith("| undated")]
        # date, then status, then title: two items on 10-22 sort alpha before zeta; an item with
        # no date sorts to the end of its group rather than pretending to be new.
        self.assertEqual(order, [("2026-10-21", "W — waiting"),
                                 ("2026-10-22", "W — waiting"),
                                 ("2026-10-22", "W — waiting"),
                                 ("undated", "R — rejected")])

    def test_the_status_column_is_the_code_and_one_word(self):
        """His rule of 2026-11-11: no parentheticals in the status column."""
        self.add(item("p1", state="accomplished", reviewer="dmitri", reason="read", assigned_to="desi"))
        text = self.page().split("## Assigned to desi")[1].split("## ")[0]
        self.assertIn("| A — accomplished |", text)
        self.assertNotIn("(a model read it)", text)
        self.assertNotIn("waiting for review", text)

    def test_the_full_title_is_shown_not_the_truncated_queue_title(self):
        self.add(item("t1", title="A long title that says what the work actually was",
                      short_title="A long title that says,", assigned_to="desi"))
        self.assertIn("A long title that says what the work actually was", self.page())


class HtmlPage(unittest.TestCase):
    """The HTML is for reading: a 2,300-row page needs an index, and an index that points at a
    heading which does not exist is worse than no index."""

    def setUp(self):
        self.items = {"a": item("a", assigned_to="desi", reading_assigned_to="desi"),
                      "b": item("b", title="An <unsafe> & unescaped title")}
        self.rows = {k: [v] for k, v in self.items.items()}
        self._real = il.load
        il.load = lambda path=None: self.items

    def tearDown(self):
        il.load = self._real

    def page(self) -> str:
        return ar.to_html(ar.render(self.rows, "2026-11-11 00:00 UTC"), "Every assignment, by member")

    def test_every_nav_link_points_at_a_heading_that_exists(self):
        import re
        text = self.page()
        hrefs = re.findall(r'<a href="#([^"]+)"', text)
        ids = set(re.findall(r'<h[123] id="([^"]+)"', text))
        self.assertTrue(hrefs)
        self.assertEqual([h for h in hrefs if h not in ids], [])

    def test_the_member_sections_are_in_the_index(self):
        text = self.page()
        self.assertIn('href="#assigned-to-desi"', text)
        self.assertIn('href="#never-assigned-to-anyone"', text)
        self.assertIn('href="#reader-desi"', text)

    def test_tables_render_as_tables_and_titles_are_escaped(self):
        text = self.page()
        self.assertIn("<table>", text)
        self.assertIn("<th>origin date</th>", text)
        self.assertIn("An &lt;unsafe&gt; &amp; unescaped title", text)
        self.assertNotIn("An <unsafe>", text)


if __name__ == "__main__":
    unittest.main()
