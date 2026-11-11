#!/usr/bin/env python3
"""A LAND line that names a directory must not pass for a delivery.

Written 2026-11-11 (Dmitri) after reading three runs in two days that wrote
`LAND: channels/ledger-verdicts/` and landed nothing:

  gemini-bot 20261110T131526Z-61c082dd  cut off; its changed paths live only in that run's
                                       changes.patch; its two verdict files never reached main
  gemini-bot 20261110T171543Z-2a288583  the same two ids again, nothing on disk
  dmitri-bot 20261111T130044Z-9fe1b78a  named by the wake summary as
                                       `CLAIMED, NOT IN ITS DIFF: channels/ledger-verdicts/`

The directory is not merely imprecise, it is invisible to both cheap checks the harness makes:
it is never in the diff (so it lands in `land_missing`, a six-path warning nobody reads) and it
does exist in the checkout (so the wake summary's "NOT IN MAIN" test calls it present). Both
answers are about the string, and the work was in the files.

What these tests pin: a directory claim is resolved from the run's own diff — the one record the
worker cannot write — and a directory claim with nothing under it in the diff stays visible as a
false claim rather than being helpfully erased.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "channels"))

import wake_engine as we  # noqa: E402

MEASURED_DIR = "channels/ledger-verdicts/"
MEASURED_FILES = [
    "channels/items.jsonl",
    "channels/ledger-verdicts/20261110T132117Z-20260926T075812Z-a04cb0cf.json",
    "channels/ledger-verdicts/20261110T132121Z-20260928T165839Z-26d63524.json",
]


class TheMeasuredCase(unittest.TestCase):
    """The report line and the diff are both taken from 20261110T131526Z-61c082dd."""

    def test_the_parser_still_yields_the_directory(self):
        # If this ever stops being a directory claim, the bug it caused has moved.
        self.assertEqual(we.land_claimed("LAND: channels/ledger-verdicts/"), [MEASURED_DIR])

    def test_the_directory_becomes_the_two_verdict_files(self):
        claimed = we.expand_land_claims(we.land_claimed("LAND: channels/ledger-verdicts/"),
                                        MEASURED_FILES)
        self.assertEqual(claimed, [
            "channels/ledger-verdicts/20261110T132117Z-20260926T075812Z-a04cb0cf.json",
            "channels/ledger-verdicts/20261110T132121Z-20260928T165839Z-26d63524.json",
        ])

    def test_land_missing_is_empty_once_the_claim_is_resolved(self):
        claimed = we.expand_land_claims(we.land_claimed("LAND: channels/ledger-verdicts/"),
                                        MEASURED_FILES)
        self.assertEqual([c for c in claimed if c not in MEASURED_FILES], [])

    def test_the_unresolved_directory_would_have_been_reported_missing(self):
        # The old behaviour, kept as the contrast: the directory is in no diff, ever.
        claimed = we.land_claimed("LAND: channels/ledger-verdicts/")
        self.assertEqual([c for c in claimed if c not in MEASURED_FILES], [MEASURED_DIR])


class TheRefusalToHelp(unittest.TestCase):

    def test_a_directory_with_nothing_under_it_stays_visible(self):
        claimed = we.expand_land_claims(["channels/ledger-verdicts/"],
                                        ["channels/items.jsonl", "tests/test_x.py"])
        self.assertEqual(claimed, ["channels/ledger-verdicts/"])
        self.assertEqual([c for c in claimed if c not in
                          ("channels/items.jsonl", "tests/test_x.py")],
                         ["channels/ledger-verdicts/"])

    def test_a_bare_directory_resolves_the_same_way(self):
        self.assertEqual(we.expand_land_claims(["channels/ledger-verdicts"],
                                               MEASURED_FILES),
                         we.expand_land_claims(["channels/ledger-verdicts/"], MEASURED_FILES))

    def test_a_prefix_is_not_a_parent(self):
        # 'channels/ledger' must not swallow 'channels/ledger-verdicts/x.json'.
        claimed = we.expand_land_claims(["channels/ledger"],
                                        ["channels/ledger-verdicts/x.json"])
        self.assertEqual(claimed, ["channels/ledger"])


class NothingElseMoves(unittest.TestCase):

    def test_file_claims_pass_through_in_order(self):
        files = ["tests/b.py", "channels/items.jsonl", "work/logo.svg"]
        self.assertEqual(we.expand_land_claims(files, MEASURED_FILES + files), files)

    def test_a_file_claim_that_names_no_change_is_not_quietly_dropped(self):
        self.assertEqual(we.expand_land_claims(["tests/never_written.py"], MEASURED_FILES),
                         ["tests/never_written.py"])

    def test_a_directory_claim_duplicating_a_file_claim_collapses(self):
        claimed = we.expand_land_claims(
            ["channels/ledger-verdicts/20261110T132117Z-20260926T075812Z-a04cb0cf.json",
             "channels/ledger-verdicts/"],
            MEASURED_FILES)
        self.assertEqual(len(claimed), 2)
        self.assertEqual(len(set(claimed)), 2)

    def test_both_directories_in_one_line(self):
        claimed = we.expand_land_claims(["channels/ledger-verdicts/", "work/"],
                                        ["work/logo.svg"] + MEASURED_FILES)
        self.assertIn("work/logo.svg", claimed)
        self.assertEqual(len([c for c in claimed if c.startswith("channels/ledger-verdicts/")]), 2)

    def test_an_empty_claim_list_stays_empty(self):
        self.assertEqual(we.expand_land_claims([], MEASURED_FILES), [])


if __name__ == "__main__":
    unittest.main()
