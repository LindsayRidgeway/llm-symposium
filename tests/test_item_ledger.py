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
        il.review(path=self.path, item_id="a", state="accomplished", reason="second")
        lines = self.path.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(lines), 3)          # one filing, two state changes
        self.assertEqual(il.load(self.path)["a"]["state"], "accomplished")


class TestCollectRecordsALandingAfterTheFact(unittest.TestCase):
    """A run is filed *before* it lands; the collector must record the landing later.

    The defect measured on 2026-10-09: `collect` skipped every id it already held, so an item's letter
    was frozen at its first sighting. Every wake is first seen while it is still `awaiting_review`, so
    every landing was invisible — `A` could only count runs collected after they had already landed,
    and `W` could only grow. That is the "broken process" the daily report was printing. The two rules
    that make the repair safe are pinned here: a landing does move a waiting item to accomplished, and
    a landing does *not* overwrite a decision a person wrote.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "runs"
        self.root.mkdir()
        self.ledger = Path(self.tmp.name) / "items.jsonl"
        self._runs_dir = il.runs_dir
        self._landed = il.landed_run_ids
        il.runs_dir = lambda amigo: self.root            # every amigo sees the same fixture runs
        self.landed = set()
        il.landed_run_ids = lambda repo=None: set(self.landed)

    def tearDown(self):
        il.runs_dir = self._runs_dir
        il.landed_run_ids = self._landed
        self.tmp.cleanup()

    def test_a_landing_after_collection_moves_a_waiting_item_to_accomplished(self):
        rid = "20261009T000000Z-aaaaaaaa"
        make_run(self.root, rid, ["docs/thing.html"], "Authored a small page that is worth keeping.")
        il.collect(path=self.ledger)
        self.assertIsNone(il.load(self.ledger)[rid]["state"])          # filed while awaiting review
        self.landed = {rid}                                            # minutes later, the wake lands
        il.collect(path=self.ledger)
        rec = il.load(self.ledger)[rid]
        self.assertEqual(rec["state"], "accomplished")
        self.assertEqual(rec["reviewer"], "auto:land")
        self.assertEqual(il.letter_for(rec), "A")

    def test_a_human_decision_is_not_overwritten_by_a_later_landing(self):
        rid = "20261009T000000Z-bbbbbbbb"
        make_run(self.root, rid, ["docs/other.html"], "Another page, held back on purpose by a review.")
        il.collect(path=self.ledger)
        il.review(path=self.ledger, item_id=rid, state="postponed", reason="waiting on a reader")
        self.landed = {rid}
        il.collect(path=self.ledger)
        rec = il.load(self.ledger)[rid]
        self.assertEqual(rec["state"], "postponed")
        self.assertEqual(rec["reason"], "waiting on a reader")

    def test_recording_a_landing_twice_adds_nothing(self):
        rid = "20261009T000000Z-cccccccc"
        make_run(self.root, rid, ["docs/third.html"], "A third page, landed and then seen again later.")
        il.collect(path=self.ledger)
        self.landed = {rid}
        il.collect(path=self.ledger)
        il.collect(path=self.ledger)
        lines = [ln for ln in self.ledger.read_text(encoding="utf-8").strip().splitlines() if ln]
        self.assertEqual(len(lines), 2)                                # one filing, one landing


if __name__ == "__main__":
    unittest.main(verbosity=2)
