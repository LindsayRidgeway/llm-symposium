#!/usr/bin/env python3
# Owner: Desi
"""Tests for `scripts/status_census.py --unread` — the view of the pile nobody could see.

Why these exist. Measured 2026-10-21: 225 finished items carry no name, sit in nobody's `--queue`,
and no model has read them — while the two counts that are supposed to control that (`--target`,
`--census`) can only say *how many* there are. A count is not a worklist, so "read before you write"
drained the 43 named items and left the pile alone. The view is the missing half, and it has exactly
one job: hand a wake a specific item it can open.

Three things must be true of it or it is worse than nothing:

  1. **It must not invent readers.** An item a model has already read is not in the view, however
     old it is — otherwise the same work is offered twice and the pile grows while it is "read".
  2. **It must not confuse an undelivered path with an unread one.** An item naming files that are
     not on main is a delivery problem; sending a reader after it wastes the wake that September
     spent ten times over. The two are counted apart, and both are shown.
  3. **It must be bounded.** A 225-row dump is not a worklist either; the default is twelve, and
     `--limit 0` is the deliberate way to ask for everything.
"""
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import status_census as sc  # noqa: E402

WHEN = "2026-10-21T12:00:00Z"


def row(item_id, amigo="gemini", title="t", paths=(), filed="2026-10-01T00:00:00Z",
        state=None, state_utc=None, reviewer=None, assigned_to=None):
    r = {"id": item_id, "amigo": amigo, "title": title, "paths": list(paths),
         "filed_utc": filed, "scope": "internal", "state": state,
         "state_utc": state_utc, "reviewer": reviewer}
    if assigned_to:
        r["assigned_to"] = assigned_to
    return r


class UnreadView(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / "present").mkdir()
        (self.repo / "present" / "a.md").write_text("x", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def landed(self, item_id, **kw):
        kw.setdefault("state", "accomplished")
        kw.setdefault("state_utc", "2026-10-10T00:00:00Z")
        kw.setdefault("reviewer", "auto:land")
        return row(item_id, **kw)

    def test_a_landed_unread_item_is_the_only_kind_in_the_view(self):
        rows = [
            self.landed("20261010T000000Z-aaaaaaaa", paths=["present/a.md"]),   # Status 2 — in
            row("20261010T000000Z-bbbbbbbb", reviewer="desi", state="accomplished",
                state_utc="2026-10-11T00:00:00Z", paths=["present/a.md"]),      # Status 1 — read
            row("20261010T000000Z-cccccccc", paths=["present/a.md"]),            # still waiting
            row("20261010T000000Z-dddddddd", state="postponed",
                state_utc="2026-10-11T00:00:00Z", reviewer="tarik"),            # postponed
        ]
        view = sc.unread_items(rows, WHEN, repo=self.repo)
        self.assertEqual([i["id"] for i in view["shown"]], ["20261010T000000Z-aaaaaaaa"])
        self.assertEqual(view["total"], 1)

    def test_a_read_item_leaves_the_pile(self):
        """The drain has to be visible: same item, before and after a model reads it."""
        before = [self.landed("20261010T000000Z-aaaaaaaa", paths=["present/a.md"])]
        after = before + [row("20261010T000000Z-aaaaaaaa", reviewer="desi", state="accomplished",
                             state_utc="2026-10-20T00:00:00Z", paths=["present/a.md"])]
        self.assertEqual(sc.unread_items(before, WHEN, repo=self.repo)["total"], 1)
        self.assertEqual(sc.unread_items(after, WHEN, repo=self.repo)["total"], 0)

    def test_the_later_event_decides_not_the_line_order(self):
        """The ledger is append-only and its rows are about the *work*, not about the record.

        A row can be appended after another and still describe an earlier minute (`--collect` and
        `--backfill` both do it). So the view must read the timestamps, and the same two rows in
        either file order must give the same answer — otherwise a backfill silently resurrects
        work that was read months ago.
        """
        land = self.landed("20261010T000000Z-aaaaaaaa", state_utc="2026-10-10T00:00:00Z",
                           paths=["present/a.md"], filed="2026-10-09T00:00:00Z")
        read = row("20261010T000000Z-aaaaaaaa", reviewer="desi", state="accomplished",
                   state_utc="2026-10-11T00:00:00Z", paths=["present/a.md"],
                   filed="2026-10-09T00:00:00Z")
        # read after the landing: read, whichever line came first in the file
        self.assertEqual(sc.unread_items([land, read], WHEN, repo=self.repo)["total"], 0)
        self.assertEqual(sc.unread_items([read, land], WHEN, repo=self.repo)["total"], 0)
        # a landing after a read puts the item back in the pile: new work, unread again
        late = self.landed("20261010T000000Z-aaaaaaaa", state_utc="2026-10-12T00:00:00Z",
                           paths=["present/a.md"], filed="2026-10-09T00:00:00Z")
        self.assertEqual(sc.unread_items([read, late], WHEN, repo=self.repo)["total"], 1)
        self.assertEqual(sc.unread_items([late, read], WHEN, repo=self.repo)["total"], 1)

    def test_a_missing_path_is_a_delivery_problem_not_a_reading_one(self):
        rows = [
            self.landed("20261010T000000Z-aaaaaaaa", paths=["present/a.md"]),
            self.landed("20261010T000000Z-bbbbbbbb", paths=["present/a.md", "gone/b.md"]),
            self.landed("20261010T000000Z-cccccccc", paths=["gone/b.md"]),
        ]
        view = sc.unread_items(rows, WHEN, repo=self.repo)
        self.assertEqual(view["total"], 3)
        self.assertEqual(view["readable"], 1)
        self.assertEqual(view["undelivered"], 2)
        by_id = {i["id"]: i for i in view["shown"]}
        self.assertEqual(by_id["20261010T000000Z-bbbbbbbb"]["paths_present"], 1)
        self.assertEqual(by_id["20261010T000000Z-bbbbbbbb"]["paths_missing"], ["gone/b.md"])

    def test_an_item_with_no_paths_is_not_called_undelivered(self):
        """Nothing to check is not the same as something missing — one is noise, one is a fault."""
        rows = [self.landed("20261010T000000Z-aaaaaaaa", paths=[])]
        view = sc.unread_items(rows, WHEN, repo=self.repo)
        self.assertEqual(view["undelivered"], 0)
        self.assertEqual(view["readable"], 0)
        self.assertIn("     -  ", render(view), "the files cell for a pathless item is a dash")

    def test_oldest_landing_first_and_age_is_measured_from_the_landing(self):
        rows = [
            self.landed("20261010T000000Z-bbbbbbbb", state_utc="2026-10-20T00:00:00Z"),
            self.landed("20261010T000000Z-aaaaaaaa", state_utc="2026-10-11T12:00:00Z"),
        ]
        view = sc.unread_items(rows, WHEN, repo=self.repo)
        self.assertEqual([i["id"] for i in view["shown"]],
                         ["20261010T000000Z-aaaaaaaa", "20261010T000000Z-bbbbbbbb"])
        self.assertAlmostEqual(view["shown"][0]["age_hours"], 240.0, places=1)
        self.assertEqual(view["oldest"]["id"], "20261010T000000Z-aaaaaaaa")

    def test_the_default_is_bounded_and_limit_zero_is_all(self):
        rows = [self.landed("2026101%dT000000Z-%s" % (i, "%08x" % i))
                for i in range(20)]
        default = sc.unread_items(rows, WHEN, repo=self.repo)
        self.assertEqual(default["total"], 20)
        self.assertEqual(len(default["shown"]), 12)
        everything = sc.unread_items(rows, WHEN, limit=0, repo=self.repo)
        self.assertEqual(len(everything["shown"]), 20)

    def test_amigo_filter(self):
        rows = [
            self.landed("20261010T000000Z-aaaaaaaa", amigo="gemini"),
            self.landed("20261010T000000Z-bbbbbbbb", amigo="desi"),
        ]
        view = sc.unread_items(rows, WHEN, amigo="gemini", repo=self.repo)
        self.assertEqual([i["id"] for i in view["shown"]], ["20261010T000000Z-aaaaaaaa"])

    def test_a_census_at_an_earlier_time_sees_the_pile_as_it_was(self):
        """The view is derivable, not remembered — so it can be asked about last week."""
        rows = [self.landed("20261010T000000Z-aaaaaaaa", state_utc="2026-10-20T00:00:00Z")]
        self.assertEqual(sc.unread_items(rows, "2026-10-19T00:00:00Z", repo=self.repo)["total"], 0)
        self.assertEqual(sc.unread_items(rows, "2026-10-21T00:00:00Z", repo=self.repo)["total"], 1)

    def test_empty_view_says_so_rather_than_printing_a_header(self):
        view = sc.unread_items([], WHEN, repo=self.repo)
        out = render(view)
        self.assertIn("nothing", out)
        self.assertNotIn("title", out.split("\n")[0])


def render(view):
    buf = io.StringIO()
    with redirect_stdout(buf):
        sc.show_unread(view)
    return buf.getvalue()


class CommandLine(unittest.TestCase):
    """The tool is used from a terminal by a wake, so the terminal path is what is pinned."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        (self.dir / "present").mkdir()
        (self.dir / "present" / "a.md").write_text("x", encoding="utf-8")
        self.ledger = self.dir / "items.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rows):
        self.ledger.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    def run_main(self, *argv):
        buf = io.StringIO()
        old = sys.argv
        sys.argv = ["status_census.py", "--ledger", str(self.ledger), "--repo", str(self.dir)] \
            + list(argv)
        try:
            with redirect_stdout(buf):
                try:
                    code = sc.main()
                except SystemExit as e:          # argparse
                    code = e.code
        finally:
            sys.argv = old
        return code, buf.getvalue()

    def test_the_view_prints_and_names_the_drain_command(self):
        self.write([row("20261010T000000Z-aaaaaaaa", state="accomplished",
                        state_utc="2026-10-10T00:00:00Z", reviewer="auto:land",
                        paths=["present/a.md"], title="Did a thing")])
        code, out = self.run_main("--unread")
        self.assertEqual(code, 0)
        self.assertIn("20261010T000000Z-aaaaaaaa", out)
        self.assertIn("Did a thing", out)
        self.assertIn("--review <id>", out)
        self.assertIn("1 name only files that are still on main", out)

    def test_limit_reaches_the_command_line(self):
        self.write([row("2026101%dT000000Z-%08x" % (i, i), state="accomplished",
                        state_utc="2026-10-1%dT00:00:00Z" % (i % 10), reviewer="auto:land")
                    for i in range(5)])
        _, out = self.run_main("--unread", "--limit", "2")
        self.assertIn("showing 2 of 5", out)

    def test_json_is_the_same_view(self):
        self.write([row("20261010T000000Z-aaaaaaaa", state="accomplished",
                        state_utc="2026-10-10T00:00:00Z", reviewer="auto:land")])
        code, out = self.run_main("--unread", "--json")
        self.assertEqual(code, 0)
        view = json.loads(out)
        self.assertEqual(view["total"], 1)
        self.assertEqual(view["shown"][0]["id"], "20261010T000000Z-aaaaaaaa")

    def test_an_empty_ledger_is_not_an_error(self):
        self.ledger.write_text("", encoding="utf-8")
        code, out = self.run_main("--unread")
        self.assertEqual(code, 0)
        self.assertIn("nothing", out)

    def test_unread_and_the_census_count_the_same_pile(self):
        """Two code paths, one number: if these disagree, one of them is lying about the pile."""
        rows = [row("2026101%dT000000Z-%08x" % (i, i), state="accomplished",
                    state_utc="2026-10-1%dT00:00:00Z" % (i % 10), reviewer="auto:land",
                    paths=["present/a.md"])
                for i in range(4)]
        rows.append(row("20261010T000000Z-ffffffff", reviewer="desi", state="accomplished",
                        state_utc="2026-10-11T00:00:00Z", paths=["present/a.md"]))
        self.write(rows)
        loaded = sc.load(self.ledger)
        census = sc.counts(sc.census(loaded, WHEN))
        view = sc.unread_items(loaded, WHEN, repo=self.dir)
        self.assertEqual(census["2"], 4)
        self.assertEqual(view["total"], census["2"])


class ThePileDoesNotGoBlind(unittest.TestCase):
    """Scale blindness, tested where the input is knowable rather than where the number is meant to fall.

    Added 2026-10-27 (Desi) from Tarik's 2026-10-22 review (finding 2). The guard against a blind view
    used to live in `TheRealLedger` as `assertGreater(view["total"], 100)`, which meant the day the
    pile was actually drained — the outcome the whole view exists for — the suite would go red and
    the next reader would be told to look for a bug that was not there.
    """

    def _pile(self, n):
        return [row("202610%02dT000000Z-%08x" % (i % 28 + 1, i), state="accomplished",
                    state_utc="2026-10-%02dT00:00:00Z" % (i % 28 + 1), reviewer="auto:land",
                    paths=["present/a.md"])
                for i in range(n)]

    def test_a_large_fixture_is_shown_whole(self):
        view = sc.unread_items(self._pile(150), "2999-01-01T00:00:00Z", limit=0, repo=ROOT)
        self.assertEqual(view["total"], 150)
        self.assertEqual(len(view["shown"]), 150)
        self.assertEqual(len({i["id"] for i in view["shown"]}), 150)

    def test_reading_the_pile_empties_it(self):
        """A view whose number cannot reach zero is a floor, not a view."""
        rows = self._pile(150)
        rows += [dict(r, reviewer="desi", state_utc="2026-11-01T00:00:00Z") for r in rows]
        view = sc.unread_items(rows, "2999-01-01T00:00:00Z", limit=0, repo=ROOT)
        self.assertEqual(view["total"], 0)


class TheRealLedger(unittest.TestCase):
    """Checks against the repository itself — a view of an empty file would pass every test above.

    Rewritten 2026-10-27 (Desi) from Tarik's 2026-10-22 review (finding 2). What is left here has to
    be true of a drained ledger as well as a full one: the file still read, the view agreeing with the
    census, and every row shown being a row that exists.
    """

    WHEN_ALL = "2999-01-01T00:00:00Z"

    def test_the_view_agrees_with_the_census_on_the_real_ledger(self):
        """Two code paths over the real file: if these disagree, one of them is lying about the pile."""
        loaded = sc.load(sc.LEDGER)
        self.assertGreater(len(loaded), 500,
                           "the ledger has only ever grown; a short read means this test is "
                           "looking at the wrong file, not that the pile got small")
        view = sc.unread_items(loaded, self.WHEN_ALL, limit=0)
        self.assertEqual(view["total"], sc.counts(sc.census(loaded, self.WHEN_ALL))["2"])

    def test_every_row_shown_is_a_row_that_exists_and_has_a_landing(self):
        loaded = sc.load(sc.LEDGER)
        ids = {r["id"] for r in loaded}
        view = sc.unread_items(loaded, self.WHEN_ALL, limit=0)
        self.assertEqual(view["total"], len(view["shown"]))
        for i in view["shown"]:
            self.assertIn(i["id"], ids)
            self.assertTrue(i["closed_utc"], "a Status 2 item must have a landing time")
            self.assertTrue(i["id"])
        self.assertEqual(view["readable"] + view["undelivered"], view["total"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
