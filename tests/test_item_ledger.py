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


class TestCounts(unittest.TestCase):
    def rows(self):
        now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        old = "2026-01-01T00:00:00Z"
        def rec(i, amigo, scope, state, when):
            return {"id": i, "amigo": amigo, "scope": scope, "state": state,
                    "filed_utc": when, "title": i}
        return {r["id"]: r for r in [
            rec("a", "desi", "internal", None, now),
            rec("b", "desi", "external", None, now),
            rec("c", "gemini", "internal", "accomplished", now),
            rec("d", "gemini", "external", "postponed", old),
            rec("e", "tarik", "internal", "rejected", old),
        ]}

    def test_the_identity_holds(self):
        c = il.counts(self.rows(), None)
        self.assertEqual(c["N"]["total"], 5)
        self.assertEqual(c["N"]["total"],
                         c["A"]["total"] + c["P"]["total"] + c["R"]["total"] + c["U"]["total"])

    def test_unreviewed_is_its_own_group_and_not_dropped(self):
        c = il.counts(self.rows(), None)
        self.assertEqual(c["U"]["total"], 2)      # a and b
        self.assertEqual(c["A"]["total"], 1)
        self.assertEqual(c["P"]["total"], 1)
        self.assertEqual(c["R"]["total"], 1)

    def test_internal_and_external_are_split_per_group_and_per_amigo(self):
        c = il.counts(self.rows(), None)
        self.assertEqual((c["N"]["internal"], c["N"]["external"]), (3, 2))
        self.assertEqual(c["N"]["by_amigo"]["desi"], {"total": 2, "internal": 1, "external": 1})
        self.assertEqual((c["P"]["internal"], c["P"]["external"]), (0, 1))

    def test_the_window_excludes_old_items(self):
        c = il.counts(self.rows(), 24)
        self.assertEqual(c["N"]["total"], 3)      # only the three filed "now"
        self.assertEqual(c["P"]["total"], 0)
        self.assertEqual(c["R"]["total"], 0)


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
