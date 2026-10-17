#!/usr/bin/env python3
"""Tests for `scripts/source_drift.py`. Offline — canned records shaped like the real ones.

Why these exist. The tool's whole job is to say *what changed*, and the two ways to get that
wrong are both silent: calling a flake a regression, and calling an error page an answer. So the
fixtures here are not invented; they are the shapes the catalogue actually stored on 2026-09-16:

  - `US Census (ACS)` — HTTP 200, `cors: *`, and a body whose title is "Missing Key". The
    published catalogue counts it as reachable. The tool must keep that verdict and *say* the
    answer is not data.
  - `REST Countries` — HTTP 200 and the body is `{"success": false, ... "errors": [...]}`.
  - `GDELT` — HTTP 429 with "please limit requests to one every 5 seconds": a speed wall.
  - `Gutendex` — HTTP 403 with a Cloudflare interstitial: a bot wall, not a content wall and not
    an outage.
  - `FRED` — HTTP 400; the key is the problem, so it reads as a key wall.

The network path is deliberately untested: a test that needs 35 public servers to be up fails for
reasons that have nothing to do with the code it is guarding.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import source_drift as sd  # noqa: E402


def rec(**kw):
    base = {"http_status": 200, "cors": "*", "content_type": "application/json", "bytes": 100,
            "witness": '{"ok": true}', "error": None, "advertised_key": False,
            "ok": True, "browser_usable": True}
    base.update(kw)
    return base


MISSING_KEY = rec(witness='<html> <head> <title>Missing Key</title> <body>Missing Key</body>',
                  content_type="text/html")
REST_COUNTRIES = rec(witness='{ "success": false, "data": null, "errors": [ { "message": '
                             '"Invalid request" } ] }')
GDELT_429 = rec(http_status=429, cors="absent", bytes=0, witness="", error="HTTP 429", ok=False,
                browser_usable=False)
GUTENDEX_403 = rec(http_status=403, cors="absent", bytes=60, ok=False, browser_usable=False,
                   witness="Just a moment... enable JavaScript and cookies to continue",
                   error="HTTP 403")
FRED_400 = rec(http_status=400, cors="absent", bytes=0, ok=False, browser_usable=False,
               advertised_key=True, error="HTTP 400")


class KindTest(unittest.TestCase):
    def test_a_200_is_answered(self):
        self.assertEqual(sd.kind(rec()), "answered")

    def test_429_is_a_speed_wall_not_an_outage(self):
        self.assertEqual(sd.kind(GDELT_429), "speed wall")

    def test_cloudflare_403_is_a_bot_wall(self):
        self.assertEqual(sd.kind(GUTENDEX_403), "bot wall")

    def test_403_without_a_challenge_and_with_a_key_is_a_key_wall(self):
        self.assertEqual(sd.kind(rec(http_status=403, ok=False, browser_usable=False,
                                     advertised_key=True, error="HTTP 403")), "key wall")

    def test_403_with_neither_is_plainly_refused(self):
        self.assertEqual(sd.kind(rec(http_status=403, ok=False, browser_usable=False,
                                     error="HTTP 403")), "refused")

    def test_400_on_a_keyed_source_reads_as_a_key_wall(self):
        self.assertEqual(sd.kind(FRED_400), "key wall")

    def test_5xx_is_a_server_error(self):
        self.assertEqual(sd.kind(rec(http_status=503, ok=False, browser_usable=False,
                                     error="HTTP 503")), "server error")

    def test_no_status_at_all_is_unreachable(self):
        self.assertEqual(sd.kind(rec(http_status=None, ok=False, browser_usable=False,
                                     error="URLError: timed out")), "unreachable")

    def test_every_record_has_a_kind(self):
        for r in (rec(), MISSING_KEY, REST_COUNTRIES, GDELT_429, GUTENDEX_403, FRED_400):
            self.assertIsInstance(sd.kind(r), str)


class ClaimsDataTest(unittest.TestCase):
    def test_200_missing_key_page_is_not_data(self):
        # The finding this tool was written to surface: ok=True, and nothing to read.
        self.assertTrue(MISSING_KEY["ok"])
        data, why = sd.claims_data(MISSING_KEY)
        self.assertFalse(data)
        self.assertIn("missing key", why)

    def test_success_false_body_is_not_data(self):
        data, why = sd.claims_data(REST_COUNTRIES)
        self.assertFalse(data)
        self.assertIn('"success": false', why)

    def test_a_real_body_is_data(self):
        data, why = sd.claims_data(rec())
        self.assertTrue(data)
        self.assertEqual(why, "")

    def test_a_source_that_did_not_answer_claims_nothing(self):
        data, why = sd.claims_data(GUTENDEX_403)
        self.assertFalse(data)
        self.assertEqual(why, "did not answer")


class DriftTest(unittest.TestCase):
    def test_answered_then_403_is_a_regression(self):
        self.assertEqual(sd.drift(rec(), GUTENDEX_403)["verdict"], "regressed")

    def test_browser_readable_then_server_only_is_a_regression(self):
        # Same status, same body — but a page can no longer read it. Item 17's second axis.
        now = rec(cors="absent", browser_usable=False)
        self.assertEqual(sd.drift(rec(), now)["verdict"], "regressed")

    def test_cors_appearing_is_an_improvement(self):
        before = rec(cors="absent", browser_usable=False)
        self.assertEqual(sd.drift(before, rec())["verdict"], "improved")

    def test_refused_then_answered_is_an_improvement(self):
        self.assertEqual(sd.drift(GUTENDEX_403, rec())["verdict"], "improved")

    def test_same_answers_different_reason_is_changed(self):
        before = rec(http_status=403, ok=False, browser_usable=False, error="HTTP 403")
        self.assertEqual(sd.drift(before, FRED_400)["verdict"], "changed")

    def test_identical_readings_are_unchanged(self):
        self.assertEqual(sd.drift(rec(), dict(rec()))["verdict"], "unchanged")

    def test_regression_beats_unchanged_kind(self):
        # A 200 that stops carrying data still answers, so assess it on the axes, not the kind.
        self.assertEqual(sd.drift(rec(), MISSING_KEY)["verdict"], "unchanged")
        self.assertFalse(sd.reading(MISSING_KEY)["claims_data"])


class SummariseTest(unittest.TestCase):
    def test_counts_every_row_and_both_axes(self):
        rows = [
            {"drift": sd.drift(rec(), rec())},
            {"drift": sd.drift(rec(), GUTENDEX_403)},
            {"drift": sd.drift(GUTENDEX_403, rec())},
            {"drift": sd.drift(GDELT_429, rec(cors="absent", browser_usable=False))},
        ]
        c = sd.summarise(rows)
        self.assertEqual(c["sources"], 4)
        self.assertEqual(c["unchanged"], 1)
        self.assertEqual(c["regressed"], 1)
        self.assertEqual(c["improved"], 2)
        self.assertEqual(c["answered_then"], 2)
        self.assertEqual(c["answered_now"], 3)
        self.assertEqual(c["browser_now"], 2)


class MarkdownTest(unittest.TestCase):
    def test_no_change_says_so_in_words(self):
        doc = {"run_utc": "2026-10-17T12:00:00Z", "baseline_utc": "2026-09-16T18:56:34Z",
               "baseline_path": "docs/works/fetchable-sources.json",
               "origin_sent": "https://example.org", "days_since_baseline": 31,
               "snapshot": "research/source-drift/x.json",
               "counts": sd.summarise([{"drift": sd.drift(rec(), rec())}]),
               "sources": [{"name": "X", "drift": sd.drift(rec(), rec())}]}
        md = sd.render_markdown(doc)
        self.assertIn("No source changed", md)
        self.assertIn("31 days", md)

    def test_a_regression_gets_a_row_with_its_confirmation(self):
        row = {"name": "Gutendex", "confirmation": "reproduced (403 then 403)",
               "drift": sd.drift(rec(), GUTENDEX_403)}
        doc = {"run_utc": "2026-10-17T12:00:00Z", "baseline_utc": "2026-09-16T18:56:34Z",
               "baseline_path": "docs/works/fetchable-sources.json",
               "origin_sent": "https://example.org", "days_since_baseline": 31,
               "snapshot": "research/source-drift/x.json",
               "counts": sd.summarise([row]), "sources": [row]}
        md = sd.render_markdown(doc)
        self.assertIn("| Gutendex |", md)
        self.assertIn("reproduced (403 then 403)", md)
        self.assertIn("regressed", md)

    def test_an_unusable_answer_is_listed_with_its_witness(self):
        row = {"name": "US Census (ACS)", "confirmation": None,
               "drift": sd.drift(MISSING_KEY, MISSING_KEY)}
        doc = {"run_utc": "2026-10-17T12:00:00Z", "baseline_utc": "2026-09-16T18:56:34Z",
               "baseline_path": "docs/works/fetchable-sources.json",
               "origin_sent": "https://example.org", "days_since_baseline": 31,
               "snapshot": "research/source-drift/x.json",
               "counts": sd.summarise([row]), "sources": [row]}
        md = sd.render_markdown(doc)
        self.assertIn("Answered, but the answer is not data", md)
        self.assertIn("missing key", md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
