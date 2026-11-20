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



class TestTraffic(unittest.TestCase):
    """The clones-and-views half, added 2026-11-20. Its failure mode is not a wrong sum but a right
    sum read as popularity, so these tests pin the attribution arithmetic, not just the totals."""

    CLONES = {"count": 300, "uniques": 40, "clones": [
        {"timestamp": "2026-11-01T00:00:00Z", "count": 200, "uniques": 30},
        {"timestamp": "2026-11-02T00:00:00Z", "count": 100, "uniques": 10},
    ]}
    VIEWS = {"count": 3, "uniques": 1, "views": [
        {"timestamp": "2026-11-01T00:00:00Z", "count": 2, "uniques": 1},
        {"timestamp": "2026-11-02T00:00:00Z", "count": 1, "uniques": 1},
    ]}

    def test_summary_keeps_the_series_and_the_peak(self):
        got = prominence.summarise_traffic(self.CLONES)
        self.assertEqual(got["count"], 300)
        self.assertEqual(got["uniques"], 40)
        self.assertEqual(got["days"], 2)
        self.assertEqual(got["peak_day"], (200, "2026-11-01"))
        self.assertEqual(got["series"][1], ("2026-11-02", 100, 10))

    def test_views_payload_is_read_by_the_same_function(self):
        got = prominence.summarise_traffic(self.VIEWS)
        self.assertEqual((got["count"], got["days"]), (3, 2))

    def test_non_object_payload_is_an_error_not_a_zero(self):
        self.assertIn("error", prominence.summarise_traffic(["not", "a", "dict"]))

    def test_clones_per_view_is_the_attribution_argument(self):
        self.assertEqual(prominence.clones_per_view(300, 3), 100.0)
        self.assertIsNone(prominence.clones_per_view(300, 0),
                          "no views means the ratio is undefined, which is not zero and not infinite")

    def test_our_own_runs_are_subtracted_and_the_floor_is_zero(self):
        self.assertEqual(prominence.unexplained_clones(300, 296), 4)
        self.assertEqual(prominence.unexplained_clones(300, 900), 0,
                         "an upper bound never goes negative")

    def test_no_token_says_which_binaries_and_which_path_it_looked_at(self):
        """2026-11-20 (Desi): the daily job carries launchd's PATH, and `gh` lives in
        /opt/homebrew/bin — so a scheduled run found no token, printed UNREAD, and looked exactly
        like a host that is not logged in. The search is explicit now and the reason travels with
        the empty token, because an absence that cannot say why is indistinguishable from a fact.
        """
        import os
        from unittest import mock
        real = prominence.traffic_token
        with mock.patch.dict(os.environ, {"PATH": "/usr/bin:/bin"}, clear=False), \
             mock.patch.object(prominence, "GH_CANDIDATES", ("gh", "/nowhere/gh")), \
             mock.patch.object(prominence.subprocess, "run", side_effect=FileNotFoundError()):
            os.environ.pop("GITHUB_TOKEN", None)
            os.environ.pop("GH_TOKEN", None)
            token, why = real()
        self.assertEqual(token, "")
        self.assertIn("/usr/bin:/bin", why)
        self.assertIn("/nowhere/gh", why)

    def test_the_binary_that_is_not_on_path_is_still_tried_by_absolute_path(self):
        """The fix for the launchd PATH, pinned: /opt/homebrew/bin/gh is tried even when PATH lacks it."""
        from unittest import mock
        calls = []

        def fake_run(argv, **kw):
            calls.append(argv[0])
            class R:
                returncode = 0
                stdout = "token-from-absolute-path\n"
            return R() if argv[0].startswith("/") else (_ for _ in ()).throw(FileNotFoundError())

        with mock.patch.object(prominence, "GH_CANDIDATES", ("gh", "/opt/homebrew/bin/gh")), \
             mock.patch.object(prominence.subprocess, "run", side_effect=fake_run):
            token, why = prominence.traffic_token()
        self.assertEqual(token, "token-from-absolute-path")
        self.assertIn("/opt/homebrew/bin/gh", why)
        self.assertEqual(calls, ["gh", "/opt/homebrew/bin/gh"])

    def test_without_a_token_the_section_reads_unread_not_zero(self):
        text = prominence.render_traffic({"traffic": {"token_available": False, "repos": []}})
        self.assertIn("UNREAD", text)
        self.assertIn("push-access token", text)
        self.assertNotIn("0 clones", text)

    def test_a_measured_row_renders_the_ratio_and_the_caveat(self):
        data = {"traffic": {"token_available": True, "repos": [{
            "repo": "LindsayRidgeway/x",
            "clones": prominence.summarise_traffic(self.CLONES),
            "views": prominence.summarise_traffic(self.VIEWS),
            "clones_per_view": 100.0,
            "own_actions_runs": {"2026-11-01": 5, "2026-11-02": 5},
            "own_actions_runs_total": 10,
            "unexplained_clones_upper_bound": 290,
        }]}}
        text = prominence.render_traffic(data)
        self.assertIn("300 clones", text)
        self.assertIn("100.0 clones per page view", text)
        self.assertIn("upper bound only", text)
        self.assertIn("| 2026-11-01 | 200 | 30 | 5 |", text)


if __name__ == "__main__":
    unittest.main()
