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
        self._real_tree = ar.main_tree_paths
        ar.main_tree_paths = lambda: None          # no repository in a unit test

    def tearDown(self):
        il.load = self._real_load
        ar.main_tree_paths = self._real_tree

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

    def test_a_redrawn_item_appears_once_under_its_current_name(self):
        """His rule of 2026-11-11: "just list the item once under the current assignment"."""
        self.add(item("x", assigned_to="dmitri", assigned_utc="2026-10-22T06:00:00Z"),
                 item("x", assigned_to="desi", assigned_utc="2026-10-21T06:00:00Z"))
        text = self.page()
        self.assertIn("## Assigned to dmitri", text)
        self.assertNotIn("## Assigned to desi", text)
        self.assertEqual(text.count("title of x"), 1)

    def test_an_unassigned_item_lands_in_the_last_group_not_under_a_member(self):
        self.add(item("named", assigned_to="desi"))
        self.add(item("orphan"))
        text = self.page()
        self.assertIn("## Never assigned for review", text)
        tail = text.split("## Never assigned for review")[1]
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


    def test_an_item_whose_named_work_is_absent_from_main_is_marked(self):
        """The one dishonesty this page can catch by itself: recorded, described, never published."""
        self.items.clear()
        self.rows.clear()
        self.add(item("gone", assigned_to="desi", paths=["docs/works/never-landed.html"]))
        self.add(item("here", assigned_to="desi", paths=["docs/index.html"]))
        ar.main_tree_paths = lambda: {"docs/index.html"}
        text = self.page().split("## Assigned to desi")[1].split("## ")[0]
        rows = {ln.split("|")[3].strip(): ln.split("|")[2].strip()
                for ln in text.splitlines() if ln.startswith("| 2026")}
        self.assertIn("work not in the commons", rows["title of gone"])
        self.assertNotIn("work not in the commons", rows["title of here"])

    def test_a_repeating_item_is_marked_after_its_date(self):
        """He asked for the notation on 2026-11-11. No ledger row carries the marker today, so this
        pins the day one does: silently omitting it would be worse than an empty column."""
        self.add(item("r1", assigned_to="desi", repeat="FREQ=WEEKLY;INTERVAL=1"))
        self.add(item("r2", assigned_to="desi"))
        text = self.page().split("## Assigned to desi")[1]
        self.assertIn("2026-10-20 (Repeating)", text)
        self.assertEqual(text.count("(Repeating)"), 1)

    def test_each_item_appears_exactly_once_in_the_whole_page(self):
        self.add(item("a", assigned_to="desi", reading_assigned_to="dmitri"))
        self.add(item("b", reading_assigned_to="tarik"))
        self.add(item("c"))
        text = self.page()
        for title in ("title of a", "title of b", "title of c"):
            self.assertEqual(text.count(title), 1, title)
        self.assertEqual(sum(1 for ln in text.splitlines()
                             if ln.startswith("| 2026") or ln.startswith("| undated")), 3)


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
        self.assertIn('href="#never-assigned-for-review"', text)
        self.assertIn('href="#never-assigned-for-review"', text)

    def test_tables_render_as_tables_and_titles_are_escaped(self):
        text = self.page()
        self.assertIn("<table>", text)
        self.assertIn("<th>origin date</th>", text)
        self.assertIn("An &lt;unsafe&gt; &amp; unescaped title", text)
        self.assertNotIn("An <unsafe>", text)



if __name__ == "__main__":
    unittest.main()
