#!/usr/bin/env python3
"""The flat item export must not quietly miscount the work it is describing.

This is the list the founder reads when he wants to know what the commons has been *doing*, and it is
read instead of the ledger rather than alongside it. So the two failure modes that matter are both
silent ones: a row whose status disagrees with the ledger's own classifier, and a `kind` that is
decided by bookkeeping files instead of by the run's real footprint.

The `kind_of` tests are written against the defect that existed in the first draft: `channels/
ledger-verdicts/` was listed in NOISE, so the paths were stripped before the vote and 151 review-only
wakes came out "other" — the export was blind to the single most common kind of work in the commons.
"""

import json
import pathlib
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "channels"))

import item_export  # noqa: E402
import item_ledger  # noqa: E402


class KindTests(unittest.TestCase):
    def test_a_verdict_only_run_is_review(self):
        self.assertEqual(item_export.kind_of(["channels/ledger-verdicts/x.md",
                                              "channels/items.jsonl"]), "review")

    def test_a_run_that_wrote_a_report_and_recorded_verdicts_is_not_review(self):
        # Review is last in KINDS: recording verdicts on top of real work does not relabel the work.
        self.assertEqual(item_export.kind_of(["channels/ledger-verdicts/x.md",
                                              "channels/reports/y.md"]), "record")

    def test_the_ledger_itself_does_not_make_a_run_a_record(self):
        self.assertEqual(item_export.kind_of(["channels/items.jsonl"]), "no paths filed")

    def test_a_run_that_filed_no_path_says_so_rather_than_other(self):
        self.assertEqual(item_export.kind_of([]), "no paths filed")
        self.assertEqual(item_export.kind_of(None), "no paths filed")

    def test_research_is_its_own_kind(self):
        self.assertEqual(item_export.kind_of(["research/rt4/x.md"]), "research")

    def test_engineering_wins_over_the_defaults_because_it_is_first(self):
        self.assertEqual(item_export.kind_of(["docs/index.html", "scripts/x.py"]), "engineering")


class TitleTests(unittest.TestCase):
    def test_short_title_is_preferred(self):
        self.assertEqual(item_export.title_of({"short_title": "Fixed the feed",
                                               "title": "A long account of fixing the feed"}),
                         "Fixed the feed")

    def test_no_report_falls_back_to_the_title(self):
        self.assertEqual(item_export.title_of({"short_title": "no report",
                                               "title": "Did a thing"}), "Did a thing")

    def test_a_row_with_neither_says_so(self):
        self.assertEqual(item_export.title_of({}), "(no report written)")

    def test_whitespace_is_flattened_and_long_titles_are_cut_with_an_ellipsis(self):
        self.assertEqual(item_export.title_of({"title": "a\n\n b\tc"}), "a b c")
        cut = item_export.title_of({"title": "x" * 400})
        self.assertEqual(len(cut), 150)
        self.assertTrue(cut.endswith("…"))


class LedgerTests(unittest.TestCase):
    def test_the_last_row_for_an_id_is_the_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "items.jsonl"
            p.write_text("\n".join(json.dumps(r) for r in [
                {"id": "A", "state": "waiting", "paths": ["scripts/x.py"]},
                {"id": "A", "state": "rejected", "paths": ["scripts/x.py"]},
                {"id": "B", "state": "waiting"},
            ]) + "\n", encoding="utf-8")
            old, item_export.LEDGER = item_export.LEDGER, p
            try:
                rows = {r["item_id"]: r for r in item_export.rows_of(item_export.load_items())}
            finally:
                item_export.LEDGER = old
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows["A"]["status"], "rejected")
        self.assertEqual(rows["B"]["status"], "waiting review")
        self.assertEqual(rows["A"]["kind"], "engineering")

    def test_every_real_row_gets_a_status_the_ledger_can_justify(self):
        items = item_export.load_items()
        self.assertGreater(len(items), 1000)
        for row in item_export.rows_of(items):
            self.assertIn(row["status"], item_export.STATUS.values(), row["item_id"])
            self.assertTrue(row["item_id"], "a row with no id cannot be looked up")
            self.assertTrue(row["title"].strip(), "a row with no title is a blank line")

    def test_the_status_column_agrees_with_the_ledger_summary(self):
        # Not a second opinion: the export must call letter_for directly, or the list and the
        # authoritative summary can drift apart one row at a time.
        src = (REPO / "scripts" / "item_export.py").read_text(encoding="utf-8")
        self.assertIn("item_ledger.letter_for(rec)", src)
        self.assertFalse((REPO / "scripts" / "item_export.py").read_text(encoding="utf-8")
                         .count("def letter_for"), "a local copy of the classifier is a fork of it")


if __name__ == "__main__":
    unittest.main(verbosity=2)
