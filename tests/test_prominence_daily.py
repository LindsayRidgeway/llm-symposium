"""Tests for scripts/prominence_daily.py — the daily row, and the two rules that make it usable.

Added 2026-11-21 (Desi). The instrument in `scripts/prominence.py` is a snapshot; this file is the
series. Two things have to hold or the series is worse than nothing:

* **one row a day.** A retried or manually dispatched run must not append the same day twice, because
  a file that repeats a day cannot be counted, and nobody looking at it later will know that.
* **unread is never written as zero.** Without a push-access token GitHub answers 403; a zero there
  is a measurement that was never made, which is the defect `channels/reports/prominence.md` was
  written to avoid in the first place.

And one structural rule, which is the reason `channels/tasks.md` was overwritten for weeks: the file
must have exactly one writer. `test_the_daily_file_has_one_writer` reads every workflow and refuses a
second one.
"""

import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "prominence_daily", ROOT / "scripts" / "prominence_daily.py")
daily = importlib.util.module_from_spec(spec)
spec.loader.exec_module(daily)

DAILY_PATH = "channels/reports/prominence-daily.jsonl"


def measured_traffic():
    return {
        "token_available": True,
        "token_source": "env GITHUB_TOKEN",
        "repos": [
            {
                "repo": "LindsayRidgeway/llm-symposium",
                "clones": {"count": 700, "uniques": 200, "status": "200"},
                "views": {"count": 14, "uniques": 3, "status": "200"},
                "clones_per_view": 50.0,
                "own_actions_runs_total": 228,
                "unexplained_clones_upper_bound": 472,
            }
        ],
    }


def unread_traffic():
    return {
        "token_available": False,
        "token_source": "no gh anywhere on PATH (/usr/bin); looked for gh, /opt/homebrew/bin/gh",
        "repos": [
            {
                "repo": "LindsayRidgeway/llm-symposium",
                "clones": {"status": "UNREAD: no push-access token — no gh anywhere on PATH",
                           "count": None, "uniques": None},
                "views": {"status": "UNREAD: no push-access token — no gh anywhere on PATH",
                          "count": None, "uniques": None},
            }
        ],
    }


class TestTheRow(unittest.TestCase):
    def test_a_measured_row_carries_the_counts_and_the_ratio(self):
        row = daily.row_from_traffic(measured_traffic(), "2026-11-21")
        self.assertEqual(row["state"], "measured")
        self.assertEqual(row["day"], "2026-11-21")
        repo = row["repos"][0]
        self.assertEqual(repo["clones"], 700)
        self.assertEqual(repo["views"], 14)
        self.assertEqual(repo["unique_visitors"], 3)
        self.assertEqual(repo["clones_per_view"], 50.0)
        self.assertEqual(repo["own_actions_runs"], 228)

    def test_no_token_is_unread_and_every_count_is_null(self):
        row = daily.row_from_traffic(unread_traffic(), "2026-11-21")
        self.assertEqual(row["state"], "unread")
        self.assertFalse(row["token_available"])
        repo = row["repos"][0]
        self.assertIsNone(repo["clones"])
        self.assertIsNone(repo["views"])
        self.assertIn("no gh anywhere on PATH", repo["clones_status"])
        self.assertIn("no gh anywhere on PATH", row["token_source"])

    def test_unread_is_not_written_as_zero_anywhere(self):
        # The whole reason this file exists: a 0 in this file means GitHub answered with 0.
        blob = json.dumps(daily.row_from_traffic(unread_traffic(), "2026-11-21"))
        self.assertNotIn('"clones": 0', blob)
        self.assertNotIn('"views": 0', blob)

    def test_a_half_measured_row_is_unread_not_measured(self):
        traffic = measured_traffic()
        traffic["repos"][0]["views"] = {"status": "HTTP 403", "count": None, "uniques": None}
        row = daily.row_from_traffic(traffic, "2026-11-21")
        self.assertEqual(row["state"], "unread")

    def test_an_empty_payload_is_unread_not_measured(self):
        self.assertEqual(daily.row_from_traffic({}, "2026-11-21")["state"], "unread")
        self.assertEqual(daily.row_from_traffic(None, "2026-11-21")["state"], "unread")

    def test_the_caveat_travels_with_the_row(self):
        row = daily.row_from_traffic(measured_traffic(), "2026-11-21")
        self.assertIn("one clone is not one install", row["note"])


class TestAppendOnce(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self.dir.name) / "prominence-daily.jsonl"

    def tearDown(self):
        self.dir.cleanup()

    def _rows(self):
        return [json.loads(l) for l in self.path.read_text().splitlines() if l.strip()]

    def test_the_first_day_is_written_once(self):
        row = daily.row_from_traffic(measured_traffic(), "2026-11-21")
        self.assertTrue(daily.append_once(self.path, row))
        self.assertEqual(len(self._rows()), 1)
        self.assertEqual(self._rows()[0]["day"], "2026-11-21")

    def test_a_second_run_on_the_same_day_writes_nothing(self):
        row = daily.row_from_traffic(measured_traffic(), "2026-11-21")
        daily.append_once(self.path, row)
        before = self.path.read_text()
        self.assertFalse(daily.append_once(self.path, row))
        self.assertEqual(self.path.read_text(), before)

    def test_the_next_day_appends_rather_than_replaces(self):
        daily.append_once(self.path, daily.row_from_traffic(measured_traffic(), "2026-11-21"))
        daily.append_once(self.path, daily.row_from_traffic(measured_traffic(), "2026-11-22"))
        self.assertEqual([r["day"] for r in self._rows()], ["2026-11-21", "2026-11-22"])

    def test_a_corrupt_line_does_not_stop_the_next_day(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("{not json\n")
        self.assertTrue(daily.append_once(
            self.path, daily.row_from_traffic(measured_traffic(), "2026-11-21")))
        lines = [l for l in self.path.read_text().splitlines() if l.strip()]
        # the bad line is kept, not silently deleted, and it does not count as a day
        self.assertEqual(len(lines), 2)
        self.assertEqual(daily.read_days(self.path), {"2026-11-21"})


class TestMain(unittest.TestCase):
    def test_a_failing_measurement_exits_zero_and_records_the_error(self):
        # This step shares a job with the dead-man switch and the retention trim. It must not be
        # able to take them down, and the failure must be in the line rather than only in a log.
        def boom():
            raise RuntimeError("the network is not there")
        with tempfile.TemporaryDirectory() as d:
            path = pathlib.Path(d) / "prominence-daily.jsonl"
            self.assertEqual(daily.main(["--path", str(path)], measure_fn=boom), 0)
            row = json.loads(path.read_text().splitlines()[0])
            self.assertEqual(row["state"], "error")
            self.assertIn("the network is not there", row["error"])

    def test_a_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            path = pathlib.Path(d) / "prominence-daily.jsonl"
            self.assertEqual(
                daily.main(["--path", str(path), "--dry-run"], measure_fn=unread_traffic), 0)
            self.assertFalse(path.exists())

    def test_the_day_is_utc(self):
        import datetime as dt
        stamp = dt.datetime(2026, 11, 21, 23, 30, tzinfo=dt.timezone.utc)
        self.assertEqual(daily.today(stamp), "2026-11-21")


class TestOneWriter(unittest.TestCase):
    """The rule that took weeks to learn: one file, one writer, or the file lies silently."""

    def _workflows(self):
        return sorted((ROOT / ".github" / "workflows").glob("*.yml"))

    def test_the_daily_file_has_one_writer(self):
        writers = [w.name for w in self._workflows()
                   if DAILY_PATH in w.read_text() or "prominence_daily.py" in w.read_text()]
        self.assertEqual(
            writers, ["quiet-check.yml"],
            "the append-only daily file must have exactly one writer; found " + repr(writers))

    def test_the_writer_commits_the_file_it_writes(self):
        # The 2026-10-08 defect: a step that writes a file the commit step does not stage loses it
        # and then announces "nothing to record". Name the path in the staging list, not just in the
        # step that produces it.
        text = (ROOT / ".github" / "workflows" / "quiet-check.yml").read_text()
        self.assertIn("prominence_daily.py", text)
        self.assertIn(DAILY_PATH, text.split("Record the alarm")[1],
                      "the staging list in the commit step must name the daily file")

    def test_the_writer_never_rewrites_the_snapshot(self):
        # Two writers to channels/reports/prominence.md would be the overwrite defect again; the
        # scheduled job may only append its own file.
        text = (ROOT / ".github" / "workflows" / "quiet-check.yml").read_text()
        self.assertNotIn("prominence.py --write", text)


if __name__ == "__main__":
    unittest.main()
