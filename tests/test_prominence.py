"""Tests for scripts/prominence.py — the arithmetic and the honesty rules, with no network.

Added 2026-11-20 (Desi). The instrument exists because a number that cannot be reproduced or that
silently counts an absence as a zero is worse than no number; these tests pin both halves: the sum
over release assets, and the rule that an unread row never renders as 0.
"""

import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("prominence", ROOT / "scripts" / "prominence.py")
prominence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prominence)


class TestSummary(unittest.TestCase):
    def test_no_releases_is_zero_with_a_reason(self):
        got = prominence.summarise_releases([])
        self.assertEqual(got["releases"], 0)
        self.assertEqual(got["downloads"], 0)
        self.assertIn("no release exists", got["empty_reason"])

    def test_release_without_files_says_so(self):
        got = prominence.summarise_releases([{"tag_name": "v0.1", "assets": [], "published_at": "2026-11-01T00:00:00Z"}])
        self.assertEqual(got["downloads"], 0)
        self.assertIn("no file is attached", got["empty_reason"])
        self.assertEqual(got["tags"], ["v0.1"])

    def test_downloads_sum_across_releases_and_assets(self):
        payload = [
            {"tag_name": "v1", "published_at": "2026-01-01T00:00:00Z",
             "assets": [{"download_count": 3}, {"download_count": 4}]},
            {"tag_name": "v2", "published_at": "2026-02-01T00:00:00Z",
             "assets": [{"download_count": 10}]},
        ]
        got = prominence.summarise_releases(payload)
        self.assertEqual(got["downloads"], 17)
        self.assertEqual(got["assets"], 3)
        self.assertEqual(got["releases"], 2)
        self.assertEqual(got["latest_published"], "2026-02-01T00:00:00Z")
        self.assertEqual(got["empty_reason"], "")

    def test_missing_and_null_counts_are_zero_not_an_error(self):
        got = prominence.summarise_releases([{"tag_name": "v1", "assets": [{}, {"download_count": None}]}])
        self.assertEqual(got["downloads"], 0)

    def test_non_list_payload_is_an_error_not_a_zero(self):
        self.assertIn("error", prominence.summarise_releases({"message": "Not Found"}))


class TestRenderNeverDressesAbsenceAsZero(unittest.TestCase):
    def _data(self, downloads):
        return {
            "measured_utc": "2026-11-20T00:00:00Z",
            "repos": [{"repo": "o/r", "role": "test", "status": "200",
                       "releases": 0 if downloads is not None else None,
                       "assets": 0 if downloads is not None else None,
                       "downloads": downloads, "empty_reason": ""}],
            "total_downloads_measured": downloads,
            "all_measured": downloads is not None,
        }

    def test_unread_row_prints_unread_and_no_total(self):
        text = prominence.render(self._data(None))
        self.assertIn("UNREAD", text)
        self.assertIn("Not fully measured", text)
        self.assertIn("unmeasured, not zero", text)

    def test_measured_zero_prints_zero_and_a_total(self):
        text = prominence.render(self._data(0))
        self.assertIn("**0 release-asset downloads", text)
        self.assertNotIn("Not fully measured", text)

    def test_stars_are_labelled_apart(self):
        text = prominence.render(self._data(0))
        self.assertIn("Not prominence", text)


if __name__ == "__main__":
    unittest.main()
