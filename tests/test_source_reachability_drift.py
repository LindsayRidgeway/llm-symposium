#!/usr/bin/env python3
"""Offline guard for scripts/source_reachability_drift.py.

Agenda item 17 rule 1 asks for a *maintained* source-reachability list. The maintenance
tool makes live requests, so the landing gate cannot run it; what the gate *can* pin is
the thing that decides whether a change matters — the classification — plus the promise
that the tool reads the same catalogue as the Works page. No network here.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PATH = os.path.join(ROOT, "scripts", "source_reachability_drift.py")

spec = importlib.util.spec_from_file_location("source_reachability_drift", PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def row(http_status=200, cors="*", ok=None, browser_usable=None, error=None, url="https://x.test/a"):
    r = {"http_status": http_status, "cors": cors, "error": error, "url": url}
    r["ok"] = (http_status == 200) if ok is None else ok
    r["browser_usable"] = (r["ok"] and cors in ("*", "origin")) if browser_usable is None else browser_usable
    return r


class DiffClassificationTest(unittest.TestCase):
    """Every state the tool can print, from the four comparisons it actually makes."""

    def classify(self, b, c):
        return mod.diff_rows({"S": b}, {"S": c})[0]["state"]

    def test_open_to_open_is_unchanged(self):
        self.assertEqual(self.classify(row(), row()), "unchanged")

    def test_open_to_403_is_newly_blocked(self):
        """The shape item 17 exists for: the page answered last month and does not now."""
        self.assertEqual(self.classify(row(), row(http_status=403, cors="absent")),
                         "newly-blocked")

    def test_403_to_200_is_newly_readable(self):
        self.assertEqual(self.classify(row(http_status=403, cors="absent"), row()),
                         "newly-readable")

    def test_403_to_403_is_still_blocked(self):
        self.assertEqual(self.classify(row(http_status=403, cors="absent"),
                                       row(http_status=503, cors="absent")),
                         "still-blocked")

    def test_losing_cors_is_its_own_regression(self):
        """The item's second axis: still a 200, no longer readable by a page."""
        self.assertEqual(
            self.classify(row(cors="*"), row(cors="absent", browser_usable=False)),
            "cors-lost")

    def test_gaining_cors_is_not_a_regression(self):
        self.assertEqual(
            self.classify(row(cors="absent", browser_usable=False), row(cors="*")),
            "cors-gained")

    def test_200_with_no_bytes_is_blocked_not_ok(self):
        """A 200 with an empty body must not pass: measure_sources sets ok, not this tool."""
        self.assertEqual(self.classify(row(), row(cors="*", ok=False, browser_usable=False)),
                         "newly-blocked")

    def test_new_and_removed_sources_are_named(self):
        rows = mod.diff_rows({"A": row()}, {"B": row()})
        self.assertEqual({r["name"]: r["state"] for r in rows},
                         {"A": "removed", "B": "new"})

    def test_regressions_sort_first(self):
        base = {"Z-ok": row(), "A-blocked": row()}
        cur = {"Z-ok": row(http_status=403, cors="absent"), "A-blocked": row()}
        rows = mod.diff_rows(base, cur)
        self.assertEqual(rows[0]["state"], "newly-blocked")


class HostAndUsageTest(unittest.TestCase):
    def test_host_of_strips_path(self):
        self.assertEqual(mod.host_of("https://eutils.ncbi.nlm.nih.gov/entrez/x?y=1"),
                         "eutils.ncbi.nlm.nih.gov")

    def test_the_catalogue_files_are_not_counted_as_users(self):
        """Otherwise every source looks used and the operational filter says nothing."""
        self.assertIn("measure_sources.py", mod.USAGE_EXCLUDE)
        self.assertIn("source_reachability_drift.py", mod.USAGE_EXCLUDE)

    def test_real_scripts_count_as_users(self):
        counts = mod.usage_counts(ROOT)
        # PubMed's host is called by the commons' search scripts; it must not be zero.
        self.assertGreater(counts.get("eutils.ncbi.nlm.nih.gov", 0), 0)
        self.assertGreater(counts.get("export.arxiv.org", 0), 0)

    def test_one_catalogue_not_two(self):
        """The tool must read measure_sources.SOURCES; a second list would drift from it."""
        names = {s[0] for s in mod.measure_sources.SOURCES}
        self.assertGreaterEqual(len(names), 30)
        self.assertIn("PubMed (E-utilities)", names)


class BaselineTest(unittest.TestCase):
    """The baseline the diff is against is the Works page's own measurement."""

    def test_baseline_exists_and_is_shaped_right(self):
        path = mod.DEFAULT_BASELINE
        self.assertTrue(os.path.exists(path), "the Works measurement is the baseline")
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        self.assertIn("generated_utc", doc)
        self.assertGreaterEqual(len(doc["sources"]), 30)
        for key in ("name", "url", "http_status", "cors", "ok", "browser_usable"):
            self.assertIn(key, doc["sources"][0])
        # Every measured source must be a name the catalogue knows, or the diff is noise.
        known = {s[0] for s in mod.measure_sources.SOURCES}
        unknown = [r["name"] for r in doc["sources"] if r["name"] not in known]
        self.assertEqual(unknown, [], "baseline rows must be catalogue rows")

    def test_real_diff_against_the_baseline_over_itself_finds_no_regression(self):
        """Sanity: the baseline compared to itself cannot call anything a regression.

        It is *not* empty — a source already blocked at baseline (FRED, Gutendex, Semantic
        Scholar, USDA) correctly reads "still-blocked", which is a state, not a change. What
        must never appear is a regression or a source that is not in both maps.
        """
        with open(mod.DEFAULT_BASELINE, encoding="utf-8") as f:
            doc = json.load(f)
        m = mod.rows_to_map(doc["sources"])
        rows = mod.diff_rows(m, m)
        bad = [r for r in rows if r["state"] in mod.REGRESSIONS + ("new", "removed")]
        self.assertEqual(bad, [])
        self.assertTrue(any(r["state"] == "still-blocked" for r in rows),
                        "the baseline is expected to carry already-blocked rows on purpose")


if __name__ == "__main__":
    unittest.main()
