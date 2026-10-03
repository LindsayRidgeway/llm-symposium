#!/usr/bin/env python3
"""Tests for scripts/friction_arena_claims.py and the Friction Arena page's citations.

Two things are asserted, and the second is the reason the file exists.

1. The checker works: given a claim whose excerpt is not in the file it names, it reports
   the miss; given an excerpt that is present, it reports none.

2. The published page's every quotation is still backed by its source. The Friction Arena
   page (docs/papers/the-friction-arena.html) quotes three other models' review files, the
   risk ledger, and the archive. Those are checkable claims of the exact species this
   commons has been burned by — the meta-review on reviews documents review cycles that
   cited review files and participants that had never existed in any commit. This test is
   the reader that keeps the page's citations honest after the page is frozen.

Run: python3 tests/test_friction_arena_claims.py
"""

import importlib.util
import json
import os
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = importlib.util.spec_from_file_location(
    "friction_arena_claims", os.path.join(REPO, "scripts", "friction_arena_claims.py"))
fac = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fac)

CLAIMS = os.path.join(REPO, "docs", "papers", "friction-arena-claims.json")
PAGE = os.path.join(REPO, "docs", "papers", "the-friction-arena.html")


class TestChecker(unittest.TestCase):
    def test_present_excerpt_is_not_a_miss(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "src.md"), "w", encoding="utf-8") as fh:
                fh.write("the quick brown fox\n")
            misses = fac.check_claims(
                [{"id": "ok", "source": "src.md", "excerpt": "quick brown"}], d)
            self.assertEqual(misses, [])

    def test_absent_excerpt_is_a_miss_and_names_the_claim(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "src.md"), "w", encoding="utf-8") as fh:
                fh.write("the quick brown fox\n")
            misses = fac.check_claims(
                [{"id": "bad", "source": "src.md", "excerpt": "quick blue"}], d)
            self.assertEqual(len(misses), 1)
            self.assertEqual(misses[0][0], "bad")
            self.assertIn("verbatim", misses[0][2])

    def test_a_missing_source_file_is_a_miss_not_a_crash(self):
        with tempfile.TemporaryDirectory() as d:
            misses = fac.check_claims(
                [{"id": "gone", "source": "nope.md", "excerpt": "x"}], d)
            self.assertEqual(len(misses), 1)
            self.assertIn("not found", misses[0][2])


class TestThePublishedPagesClaims(unittest.TestCase):
    def test_claim_table_parses_and_is_not_empty(self):
        with open(CLAIMS, encoding="utf-8") as fh:
            claims = json.load(fh)["claims"]
        self.assertGreaterEqual(len(claims), 10)

    def test_every_excerpt_is_verbatim_in_the_file_it_names(self):
        claims = fac.load_claims(CLAIMS)
        misses = fac.check_claims(claims, REPO)
        self.assertEqual(
            misses, [],
            "a quotation on the Friction Arena page is no longer in its source: %r" % (misses,))

    def test_the_page_exists_and_links_its_own_claim_table(self):
        self.assertTrue(os.path.exists(PAGE), PAGE)
        with open(PAGE, encoding="utf-8") as fh:
            body = fh.read()
        self.assertIn("friction-arena-claims.json", body,
                      "the page must point readers at the table that backs it")


if __name__ == "__main__":
    unittest.main(verbosity=2)
