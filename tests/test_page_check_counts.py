#!/usr/bin/env python3
"""The check counts the Works pages print are re-derived, not inherited (Desi, 2026-11-27).

`docs/works/index.html` tells a stranger "(81 checks)", "(54 checks)", "(60 checks — no, 94)". Those
numbers are the page's evidence that somebody looked. Nothing re-derived them, and on the day this file
was written two were wrong:

    validate_unreported_trials_page.mjs   the page said 50, the harness runs 54
    validate_recalls_page.mjs             the page said 60, the harness runs 94

Both understated. That is the safe direction and still false: a reader who trusts the number has been
told something untrue about this repository, and a reader who distrusts it is right by accident.

Three things are compared here, and each one catches a different drift:

  * the page's printed number against the recorded one — a page edit that changes a number without
    re-deriving it fails by name;
  * the recorded number against the harness's own output, for every harness that runs offline at
    landing time — so a harness that gains checks cannot leave the record stale;
  * the parser — if it stops finding numbers, "no problems" would be the loudest possible lie, so a
    floor is asserted on how many printed numbers were found.

The live harnesses (retraction, unreported trials, recalls, nonreplication, warming, fetchable) cannot
be re-run on the landing machine with confidence about the weather, so their numbers are pinned to the
record with the date they were derived. That split is stated in the page's own amendment paragraphs.

Run directly: `python3 tests/test_page_check_counts.py`
"""

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module():
    spec = importlib.util.spec_from_file_location("pcc", ROOT / "scripts" / "page_check_counts.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pcc = module()
RECORD = ROOT / "tests" / "page-check-counts.json"


class ThePagesDoNotOverstateOrUnderstate(unittest.TestCase):
    def test_every_printed_number_agrees_with_the_record_and_the_harness(self):
        record = json.loads(RECORD.read_text(encoding="utf-8"))
        # Only the harnesses that run offline here: the rest are pinned to the record's date.
        measured = {p.name: n for p in pcc.harnesses()
                    if pcc.runs_offline(p) and (n := pcc.run_count(p)) is not None}
        self.assertEqual(pcc.problems(record, pcc.printed(), measured), [])
        # The index is not the only page that prints a number: `docs/works/trials.html` said "all 33
        # checks pass" while its harness ran 34, because a check had been added that morning. Found by
        # widening the question, so the widening is guarded rather than remembered.
        self.assertEqual(pcc.problems_in_pages(record, ROOT / "docs" / "works"), [])

    def test_the_parser_still_finds_the_numbers(self):
        said = pcc.printed()
        self.assertGreaterEqual(len(said), 5, "fewer printed check counts were found than exist: the "
                                             "index reworded them and this guard went blind")
        for name, number in said.items():
            self.assertRegex(name, r"^validate_[a-z_0-9]+\.mjs$")
            self.assertGreater(number, 10, "%s prints %d checks" % (name, number))

    def test_the_record_says_when_and_how_it_was_derived(self):
        record = json.loads(RECORD.read_text(encoding="utf-8"))
        self.assertRegex(str(record.get("recorded_at")), r"^\d{4}-\d{2}-\d{2}T")
        self.assertIn("ok", str(record.get("method", "")).lower())
        self.assertGreater(len(record.get("harnesses") or {}), 8)


class TheDetectorFiresOnTheRealCase(unittest.TestCase):
    """50 vs 54 and 60 vs 94, the two numbers the index carried wrongly on 2026-11-27."""

    def setUp(self):
        self.record = {"harnesses": {"validate_unreported_trials_page.mjs": 54,
                                     "validate_recalls_page.mjs": 94,
                                     "validate_trials_page.mjs": 34,
                                     "validate_heat_page.mjs": 57}}

    def test_an_understated_count_is_named(self):
        said = {"validate_unreported_trials_page.mjs": 50, "validate_recalls_page.mjs": 60,
                "validate_heat_page.mjs": 57}
        found = pcc.problems(self.record, said)
        self.assertEqual(len(found), 2, found)
        self.assertIn("the page says 50 checks, the harness runs 54", found[0] + found[1])
        self.assertIn("the page says 60 checks, the harness runs 94", found[0] + found[1])

    def test_an_overstated_count_is_named_too(self):
        found = pcc.problems(self.record, {"validate_heat_page.mjs": 60})
        self.assertEqual(len(found), 1, found)
        self.assertIn("says 60", found[0])

    def test_a_harness_the_page_names_but_nobody_measured_is_named(self):
        found = pcc.problems(self.record, {"validate_invented_page.mjs": 12})
        self.assertIn("never measured", found[0])

    def test_a_harness_that_gained_checks_leaves_the_record_stale(self):
        found = pcc.problems(self.record, {}, {"validate_heat_page.mjs": 58})
        self.assertEqual(len(found), 1, found)
        self.assertIn("recorded 57 checks, runs 58 now", found[0])

    def test_a_page_body_that_prints_a_stale_number_is_named(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "somepage.html").write_text(
                "<p>texts/validate_heat_page.mjs</p><p>all 33 checks pass</p>", encoding="utf-8")
            found = pcc.problems_in_pages(self.record, d)
            self.assertEqual(len(found), 1, found)
            self.assertIn("prints 33 checks", found[0])

    def test_a_page_naming_two_harnesses_is_not_guessed_at(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "twopage.html").write_text(
                "tests/validate_heat_page.mjs and tests/validate_recalls_page.mjs: 33 checks",
                encoding="utf-8")
            self.assertEqual(pcc.problems_in_pages(self.record, d), [],
                             "with two harnesses named, a bare number cannot be attributed — saying "
                             "nothing is right, guessing is not")

    def test_the_index_is_checked_card_by_card(self):
        """Two harnesses on one page are two claims, not an unattributable number.

        The page-level rule skipped any file naming two harnesses. The Works index names twelve, so
        every number on the page a stranger actually reads was outside the check — and a card on it
        came to say "is 54, not the 50" about a harness that runs 34 (2026-11-27).
        """
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "index.html").write_text(
                '<div class="card"><p>tests/validate_heat_page.mjs (57 checks)</p></div>\n'
                '<div class="card"><p>tests/validate_recalls_page.mjs (60 checks)</p></div>\n',
                encoding="utf-8")
            found = pcc.problems_in_pages(self.record, d)
        self.assertEqual(len(found), 1, found)
        self.assertIn("validate_recalls_page.mjs", found[0])
        self.assertIn("60", found[0])

    def test_a_number_stated_as_an_amendment_is_checked_too(self):
        """The exact sentence that was wrong, in the form nothing was looking at."""
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "index.html").write_text(
                '<div class="card"><p>tests/validate_trials_page.mjs re-checks the page. Amended: the '
                'count is 54, not the 50 printed before it.</p></div>\n', encoding="utf-8")
            found = pcc.problems_in_pages(self.record, d)
        self.assertEqual(len(found), 1, found)
        self.assertIn("is 54", found[0])
        self.assertIn("which runs 34", found[0])

    def test_no_record_is_not_a_pass(self):
        found = pcc.problems(None, {"validate_heat_page.mjs": 57})
        self.assertTrue(found and "no recorded counts" in found[0])


class ARecorderMustNotLoseAHarness(unittest.TestCase):
    """The 692 → 655 drop: `--write` rebuilt the record from what it could run, and said only a
    smaller total. `validate_nonreplication_page.mjs` (37 checks) vanished at 18:14Z on 2026-11-27 and
    runs fine by hand — one transient fetch reset was enough to delete a number from the record."""

    def test_a_harness_that_could_not_run_keeps_its_number_and_says_why(self):
        merged, carried, unmeasured = pcc.reconcile(
            {"validate_heat_page.mjs": 57},
            {"validate_nonreplication_page.mjs": "exit 1: TypeError: fetch failed"},
            {"validate_nonreplication_page.mjs": 37, "validate_heat_page.mjs": 57},
            "2026-11-27T18:00:59Z")
        self.assertEqual(merged["validate_nonreplication_page.mjs"], 37,
                         "the number was dropped from the record instead of carried")
        self.assertIn("fetch failed", carried["validate_nonreplication_page.mjs"])
        self.assertIn("2026-11-27T18:00:59Z", carried["validate_nonreplication_page.mjs"])
        self.assertEqual(unmeasured, {})

    def test_a_harness_that_never_ran_has_no_number_and_is_named(self):
        merged, carried, unmeasured = pcc.reconcile({}, {"validate_new_page.mjs": "no node"},
                                                    {}, "an earlier run")
        self.assertNotIn("validate_new_page.mjs", merged,
                         "a count was invented for a harness that has never been measured")
        self.assertIn("no node", unmeasured["validate_new_page.mjs"])

    def test_the_write_exits_nonzero_when_something_never_measured(self):
        self.assertEqual(len(pcc.reconcile({}, {"a": "x"}, {})[2]), 1)


class TheOfflineSetIsAskedNotGuessed(unittest.TestCase):
    def test_warming_is_re_derived_at_check_time(self):
        warming = ROOT / "tests" / "validate_warming_page.mjs"
        self.assertTrue(pcc.runs_offline(warming),
                        "warming calls fetch only behind WARMING_LIVE=1; a content scan for "
                        "`await fetch(` misreads it as live and its count goes unchecked forever")

    def test_a_harness_with_a_recorded_response_is_offline(self):
        self.assertTrue(pcc.runs_offline(ROOT / "tests" / "validate_trials_page.mjs"))

    def test_the_partial_one_is_not_counted_as_offline(self):
        """fetchable is the last harness whose live half cannot be replayed.

        The landing gate runs its `--offline` 11, but the number the Works page prints (16) is the
        live total, and pretending to re-derive that here would compare 16 against 11 forever. It is
        excluded on purpose, and this test says so out loud rather than leaving it to a heuristic.
        """
        self.assertFalse(pcc.runs_offline(ROOT / "tests" / "validate_fetchable_page.mjs"))
        self.assertTrue((ROOT / "tests" / "fixtures" / "validate_unreported_trials_page.replay.json").is_file(),
                        "the last networked harness lost its record")


if __name__ == "__main__":
    unittest.main(verbosity=2)
