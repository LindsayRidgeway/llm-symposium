#!/usr/bin/env python3
"""Tests for the item ledger — the register behind the human's daily report.

The three things that would make the report a lie, and are therefore pinned here:
  1. an item is derived from the run's changed paths, so a run that changed nothing is not an item;
  2. internal/external is decided by whether the work could have reached the world, not by which
     amigo did it or how it was described;
  3. a postponed or rejected item must carry a reason — an item filed as "postponed" with no
     reason is indistinguishable from one that was quietly dropped.
"""
import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from channels import item_ledger as il  # noqa: E402


def make_run(root: Path, run_id: str, changed: list[str], report: str) -> Path:
    d = root / run_id
    d.mkdir(parents=True)
    (d / "result.json").write_text(json.dumps({
        "run_id": run_id, "status": "awaiting_review", "changed_paths": changed,
    }), encoding="utf-8")
    (d / "report.txt").write_text(report, encoding="utf-8")
    return d


class TestDerivation(unittest.TestCase):
    def test_a_run_that_changed_nothing_is_not_an_item(self):
        with tempfile.TemporaryDirectory() as t:
            d = make_run(Path(t), "20261006T082758Z-245fa706", [], "I did nothing.")
            self.assertEqual(il.run_to_items("desi", d), [])

    def test_a_run_that_changed_files_is_one_item(self):
        with tempfile.TemporaryDirectory() as t:
            d = make_run(Path(t), "20261006T082758Z-245fa706",
                         ["scripts/x.py", "tests/test_x.py"],
                         "I built the thing that was missing.")
            items = il.run_to_items("desi", d)
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0]["amigo"], "desi")
            self.assertEqual(items[0]["filed_utc"], "2026-10-06T08:27:58Z")
            self.assertEqual(items[0]["state"] if "state" in items[0] else None, None)
            self.assertEqual(items[0]["source"], "derived")

    def test_declared_items_override_the_derivation(self):
        with tempfile.TemporaryDirectory() as t:
            d = make_run(Path(t), "20261006T082758Z-245fa706", ["a.py", "docs/index.html"],
                         "Two things got done.\n"
                         "ITEM: [internal] fixed the lander\n"
                         "ITEM: [external] published the magazine page\n")
            items = il.run_to_items("desi", d)
            self.assertEqual([i["title"] for i in items],
                             ["fixed the lander", "published the magazine page"])
            self.assertEqual([i["scope"] for i in items], ["internal", "external"])


class TestScope(unittest.TestCase):
    def test_mail_and_magazine_are_external(self):
        for path in ("channels/sent/x.md", "channels/outbound/y.md",
                     "channels/outreach/z.md", "docs/index.html"):
            self.assertEqual(il.scope_for_paths([path]), "external", path)

    def test_repository_work_is_internal(self):
        for path in ("scripts/x.py", "channels/risks.md", "to-do-lists/desi.md"):
            self.assertEqual(il.scope_for_paths([path]), "internal", path)

    def test_one_external_path_makes_the_item_external(self):
        self.assertEqual(
            il.scope_for_paths(["scripts/x.py", "channels/sent/letter.md"]), "external")


class TestTitle(unittest.TestCase):
    def test_intent_lines_are_skipped_in_favour_of_the_summary(self):
        report = ("Starting: orienting from the to-do list.\n"
                  "Intending to: pick an item and deliver an artefact.\n"
                  "Area this wake: the lander.\n"
                  "I fixed the refusal loop that stopped a day and a half of work reaching main.\n")
        self.assertEqual(
            il.best_title(report),
            "I fixed the refusal loop that stopped a day and a half of work reaching main.")

    def test_the_summary_line_wins(self):
        report = ("Starting: orienting from the to-do list.\n"
                  "I found why nothing has landed for a day and a half.\n")
        self.assertEqual(il.best_title(report), "I found why nothing has landed for a day and a half.")

    def test_a_report_that_is_only_an_intent_is_returned_rather_than_invented(self):
        report = "Intending to: take the next item in turn and review the reject queue, properly.\n"
        self.assertEqual(il.best_title(report), report.strip())


class TestLetters(unittest.TestCase):
    """The classifier of the human's second scheme (2026-10-07). Two rules, both his, both pinned:
    an unwritten postponement is *waiting*, not postponed; and an exemption from review must be
    claimed in writing or the item reads as needing review."""

    def test_the_letters_follow_the_decision_on_disk(self):
        self.assertEqual(il.letter_for({"state": "accomplished"}), "A")
        self.assertEqual(il.letter_for({"state": "rejected"}), "R")
        self.assertEqual(il.letter_for({"state": "postponed", "reason": "no access"}), "P")

    def test_a_postponement_with_no_written_reason_is_waiting(self):
        # The point of the split: a decision nobody recorded is not a decision. W, not P.
        self.assertEqual(il.letter_for({"state": "postponed"}), "W")
        self.assertEqual(il.letter_for({"state": "postponed", "reason": "   "}), "W")

    def test_no_decision_at_all_is_waiting(self):
        self.assertEqual(il.letter_for({"state": None}), "W")

    def test_an_exemption_must_be_written_down(self):
        self.assertFalse(il.is_exempt({}))
        self.assertFalse(il.is_exempt({"no_review_reason": "  "}))
        self.assertTrue(il.is_exempt({"no_review_reason": "a ledger row, nothing to review"}))


class TestCounts(unittest.TestCase):
    def rows(self):
        now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        old = "2026-01-01T00:00:00Z"

        def rec(i, amigo, scope, state=None, when=now, **kw):
            return {"id": i, "amigo": amigo, "scope": scope, "state": state,
                    "filed_utc": when, "title": i, **kw}

        return {r["id"]: r for r in [
            rec("a", "desi", "internal"),                                     # filed, nobody looked
            rec("b", "desi", "external"),                                     # ditto
            rec("c", "gemini", "internal", "accomplished", now, state_utc=now,
                reviewer="auto:land", reason="landed on main (lander's test gate passed)"),
            rec("d", "gemini", "external", "postponed", old),                 # put off, no reason
            rec("e", "tarik", "internal", "rejected", old, state_utc=old,
                reviewer="desi", reason="the source does not exist"),
            rec("f", "tarik", "internal", "postponed", old, state_utc=old,
                reviewer="desi", reason="needs library access"),              # a real decision
        ]}

    def test_the_identity_is_the_two_axes_added_up(self):
        # N+V = A+P+W+R, his equation of 2026-10-07. It holds because each item gets exactly one
        # letter from each axis, which is what makes it a check rather than a tautology.
        c = il.counts(self.rows(), None)
        self.assertEqual(c["N"]["total"] + c["V"]["total"],
                         c["A"]["total"] + c["P"]["total"] + c["W"]["total"] + c["R"]["total"])
        self.assertEqual(c["N"]["total"] + c["V"]["total"], 6)
        self.assertNotIn("U", c)          # the letter he retired, 2026-10-06

    def test_nothing_is_exempt_without_saying_so(self):
        c = il.counts(self.rows(), None)
        self.assertEqual(c["N"]["total"], 0)     # nobody has ever claimed an exemption
        self.assertEqual(c["V"]["total"], 6)
        rows = self.rows()
        rows["g"] = {"id": "g", "amigo": "desi", "scope": "internal", "state": None,
                     "filed_utc": "2026-01-01T00:00:00Z", "title": "g",
                     "no_review_reason": "a ledger row; nothing in it to review"}
        c = il.counts(rows, None)
        self.assertEqual(c["N"]["total"], 1)
        self.assertEqual(c["V"]["total"], 6)

    def test_the_postponed_letter_is_only_written_decisions(self):
        c = il.counts(self.rows(), None)
        self.assertEqual(c["P"]["total"], 1)     # f, the one with a reason on disk
        self.assertEqual(c["W"]["total"], 3)     # a, b, d — nobody has looked, or nobody wrote it
        self.assertNotIn("undecided", c["P"])    # that split is now the W letter itself

    def test_accomplished_says_whether_a_review_or_the_lander_did_it(self):
        c = il.counts(self.rows(), None)
        self.assertEqual(c["A"]["total"], 1)
        self.assertEqual(c["A"]["by_gate"], 1)
        self.assertEqual(c["A"]["by_review"], 0)
        rows = self.rows()
        rows["h"] = {"id": "h", "amigo": "desi", "scope": "internal", "state": "accomplished",
                     "filed_utc": "2026-01-01T00:00:00Z", "reviewer": "gemini",
                     "reason": "reviewed, kept"}
        c = il.counts(rows, None)
        self.assertEqual((c["A"]["by_review"], c["A"]["by_gate"]), (1, 1))

    def test_decisions_counts_what_left_waiting(self):
        # Δ(V−W) is derived, not stored: every written decision takes exactly one item out of W.
        c = il.counts(self.rows(), None)
        self.assertEqual(c["decisions"], 3)      # c, e, f — old ones still carry a state_utc

    def test_internal_and_external_are_split_per_letter_and_per_amigo(self):
        c = il.counts(self.rows(), None)
        self.assertEqual((c["V"]["internal"], c["V"]["external"]), (4, 2))
        self.assertEqual(c["V"]["by_amigo"]["desi"], {"total": 2, "internal": 1, "external": 1})
        self.assertEqual((c["W"]["internal"], c["W"]["external"]), (1, 2))
        self.assertEqual(c["W"]["by_amigo"]["gemini"]["total"], 1)     # d, not c

    def test_the_window_excludes_old_items(self):
        c = il.counts(self.rows(), 24)
        self.assertEqual(c["N"]["total"] + c["V"]["total"], 3)   # a, b, c — filed today
        self.assertEqual(c["A"]["total"], 1)                     # c
        self.assertEqual(c["W"]["total"], 2)                     # a, b
        self.assertEqual(c["P"]["total"], 0)                     # f is old
        self.assertEqual(c["R"]["total"], 0)                     # e is old
        self.assertEqual(c["decisions"], 1)                      # c, decided today


class TestTheReviewQueue(unittest.TestCase):
    """Nothing in the commons has ever reviewed a wake's work, which is why every count of A is 0
    and W is 203. This queue is the drain: oldest first, and never your own work."""

    def setUp(self):
        self.rows = {
            "old": {"id": "old", "amigo": "gemini", "scope": "internal", "state": None,
                    "filed_utc": "2026-09-15T00:00:00Z", "title": "old"},
            "new": {"id": "new", "amigo": "dmitri", "scope": "internal", "state": None,
                    "filed_utc": "2026-10-01T00:00:00Z", "title": "new"},
            "mine": {"id": "mine", "amigo": "desi", "scope": "internal", "state": None,
                     "filed_utc": "2026-09-01T00:00:00Z", "title": "mine"},
            "put_off": {"id": "put_off", "amigo": "gemini", "scope": "internal",
                        "state": "postponed", "reason": "needs access",
                        "filed_utc": "2026-09-02T00:00:00Z", "title": "put off"},
        }

    def test_the_oldest_waiting_item_comes_first(self):
        self.assertEqual([r["id"] for r in il.waiting(self.rows, 5)], ["mine", "old", "new"])

    def test_your_own_work_is_not_in_your_queue(self):
        self.assertEqual([r["id"] for r in il.waiting(self.rows, 5, not_mine="desi")],
                         ["old", "new"])

    def test_an_item_that_already_carries_a_decision_is_not_waiting(self):
        self.assertNotIn("put_off", [r["id"] for r in il.waiting(self.rows, 5)])

    def test_the_queue_is_capped(self):
        self.assertEqual(len(il.waiting(self.rows, 1)), 1)


class TestReview(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "items.jsonl"
        il.append([{"id": "a", "amigo": "desi", "scope": "internal", "title": "t",
                    "state": None, "filed_utc": "2026-10-06T00:00:00Z"}], self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_reason_is_required(self):
        with self.assertRaises(ValueError):
            il.review(path=self.path, item_id="a", state="postponed", reason="  ")

    def test_an_unknown_state_is_refused(self):
        with self.assertRaises(ValueError):
            il.review(path=self.path, item_id="a", state="maybe", reason="why")

    def test_state_changes_append_and_take_effect(self):
        il.review(path=self.path, item_id="a", state="postponed", reason="needs library access")
        rec = il.load(self.path)["a"]
        self.assertEqual(rec["state"], "postponed")
        self.assertEqual(rec["reason"], "needs library access")

    def test_the_ledger_is_append_only(self):
        il.review(path=self.path, item_id="a", state="postponed", reason="first")
        il.review(path=self.path, item_id="a", state="accomplished", reason="done: docs/x.html")
        lines = self.path.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(lines), 3)          # one filing, two state changes
        self.assertEqual(il.load(self.path)["a"]["state"], "accomplished")

    def test_a_stamp_is_not_an_accomplished_exit(self):
        """The researcher's rule (2026-10-09): A means the work is done, not that someone looked."""
        with self.assertRaises(ValueError):
            il.review(path=self.path, item_id="a", state="accomplished", reason="looked fine")

    def test_the_accomplished_reason_has_to_name_the_work(self):
        for reason in ("did it — docs/fiction/dead-band.html",
                       "finished in run 20261009T030000Z-abc12345",
                       "shipped: https://example.org/thing"):
            with self.subTest(reason=reason):
                il.review(path=self.path, item_id="a", state="accomplished", reason=reason)
                self.assertEqual(il.load(self.path)["a"]["state"], "accomplished")


class TestAssignment(unittest.TestCase):
    """Who looks. The human's algorithm, 2026-10-09: name the best suited, else draw cheap."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.path = root / "items.jsonl"
        self.band_dir = root / "usage"
        self.band_dir.mkdir()
        (self.band_dir / "price-band-2026-10.json").write_text(json.dumps({
            "as_of": "2026-08-25", "band": ["desi", "dmitri"], "cheapest": "desi",
            "rates_usd_per_million": {"desi": 0.01, "dmitri": 0.01, "gemini": 0.59,
                                      "claude": 1.15, "tarik": 1.86},
        }), encoding="utf-8")
        il.append([
            {"id": "by-desi", "amigo": "desi", "scope": "internal", "title": "d",
             "state": None, "filed_utc": "2026-10-01T00:00:00Z"},
            {"id": "by-dmitri", "amigo": "dmitri", "scope": "internal", "title": "m",
             "state": None, "filed_utc": "2026-10-02T00:00:00Z"},
            {"id": "by-gemini", "amigo": "gemini", "scope": "internal", "title": "g",
             "state": None, "filed_utc": "2026-10-03T00:00:00Z"},
        ], self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_the_author_is_never_the_reviewer(self):
        with self.assertRaises(ValueError) as caught:
            il.assign(path=self.path, item_id="by-desi", to="desi", reason="best suited")
        self.assertIn("author is never", str(caught.exception))

    def test_a_name_needs_its_one_line_reason(self):
        with self.assertRaises(ValueError):
            il.assign(path=self.path, item_id="by-desi", to="gemini", reason="   ")

    def test_only_a_waiting_item_is_assigned(self):
        il.review(path=self.path, item_id="by-desi", state="rejected", reason="superseded")
        with self.assertRaises(ValueError) as caught:
            il.assign(path=self.path, item_id="by-desi", to="gemini", reason="why")
        self.assertIn("not waiting", str(caught.exception))

    def test_an_unknown_amigo_is_refused(self):
        with self.assertRaises(ValueError):
            il.assign(path=self.path, item_id="by-desi", to="nobody", reason="why")

    def test_the_draw_names_every_unassigned_item_and_records_the_band(self):
        made = il.draw(path=self.path, dir_=self.band_dir, by="desi")
        self.assertEqual(len(made), 3)
        for rec in made:
            self.assertIn(rec["assigned_to"], ("desi", "dmitri"))
            self.assertIn("2026-08-25", rec["assign_reason"])
            self.assertEqual(rec["assign_kind"], "draw")
            self.assertNotEqual(rec["assigned_to"], rec["amigo"])

    def test_the_draw_does_not_re_roll(self):
        il.draw(path=self.path, dir_=self.band_dir, by="desi")
        first = {k: v["assigned_to"] for k, v in il.load(self.path).items()}
        il.draw(path=self.path, dir_=self.band_dir, by="desi")
        second = {k: v["assigned_to"] for k, v in il.load(self.path).items()}
        self.assertEqual(first, second)

    def test_a_frozen_draw_only_moves_with_a_reason_and_force(self):
        made = il.draw(path=self.path, dir_=self.band_dir, only="by-gemini", by="desi")
        current = made[0]["assigned_to"]
        other = "dmitri" if current == "desi" else "desi"
        with self.assertRaises(ValueError):
            il.assign(path=self.path, item_id="by-gemini", to=other, reason="changed my mind")
        moved = il.assign(path=self.path, item_id="by-gemini", to=other, force=True,
                          reason="the first reviewer is away")
        self.assertEqual(moved["assigned_to"], other)

    def test_the_queue_is_what_carries_your_name(self):
        il.assign(path=self.path, item_id="by-desi", to="gemini", reason="gallery owner")
        items = il.load(self.path)
        self.assertEqual([r["id"] for r in il.assigned(items, "gemini")], ["by-desi"])
        self.assertEqual(il.assigned(items, "tarik"), [])

    def test_a_hole_is_a_waiting_item_with_no_name(self):
        items = il.load(self.path)
        self.assertEqual(len(il.holes(items)), 3)
        il.draw(path=self.path, dir_=self.band_dir, by="desi")
        self.assertEqual(il.holes(il.load(self.path)), [])

    def test_no_band_is_an_error_not_a_default(self):
        empty = Path(self.tmp.name) / "nothing"
        empty.mkdir()
        with self.assertRaises(FileNotFoundError):
            il.draw(path=self.path, dir_=empty, by="desi")

    def test_the_band_widens_rather_than_stranding_an_item(self):
        """A one-member band that wrote the item would be a permanent hole; widen, and say so."""
        narrow = Path(self.tmp.name) / "narrow"
        narrow.mkdir()
        (narrow / "price-band-2026-10.json").write_text(json.dumps({
            "as_of": "2026-08-25", "band": ["desi"], "cheapest": "desi",
            "rates_usd_per_million": {"desi": 0.01, "dmitri": 0.01, "gemini": 0.59,
                                      "claude": 1.15, "tarik": 1.86},
        }), encoding="utf-8")
        made = il.draw(path=self.path, dir_=narrow, by="desi")
        by_id = {r["id"]: r for r in made}
        self.assertEqual(by_id["by-desi"]["assigned_to"], "dmitri")
        self.assertIn("widened", by_id["by-desi"]["assign_reason"])
        self.assertEqual(by_id["by-dmitri"]["assigned_to"], "desi")
        self.assertEqual(il.holes(il.load(self.path)), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
