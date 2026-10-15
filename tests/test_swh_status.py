#!/usr/bin/env python3
"""Tests for `scripts/swh_status.py`. Offline — canned records, no network.

Why these exist. The one thing this tool must never do is call a pending task a copy: the audit of
2026-10-15 recorded the deposit as `pending` and said plainly "a pending task is not a copy". So the
two pure functions are pinned here against exactly that shape of record — a request that has been
accepted but has no `snapshot_swhid` yet — as well as against a finished visit that does.

The network paths (`fetch_requests`, `request_save`) are deliberately not tested: they are one HTTP
call each, and a test that needs Software Heritage to be up is a test that fails for the wrong
reason. `describe()` is where the judgement lives, and it is pure.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import swh_status as swh  # noqa: E402

# The real record for save request 2559526, trimmed to the fields the tool reads.
LANDED = {
    "id": 2559526,
    "save_request_date": "2026-10-15T17:53:09.685869+00:00",
    "save_task_status": "succeeded",
    "visit_status": "full",
    "snapshot_swhid": "swh:1:snp:3365e186a1d8bdb93c16895111438f3cad1e66b7",
}
# The same request before the visit finished: accepted, no snapshot yet.
PENDING = {
    "id": 2559526,
    "save_request_date": "2026-10-15T17:53:09.685869+00:00",
    "save_task_status": "pending",
    "visit_status": "pending",
    "snapshot_swhid": "",
}


class LatestTest(unittest.TestCase):
    def test_picks_newest_by_date_not_position(self):
        newer = dict(LANDED, id=2, save_request_date="2026-10-15T18:00:00Z")
        older = dict(LANDED, id=1, save_request_date="2026-10-01T00:00:00Z")
        self.assertEqual(swh.latest([newer, older])["id"], 2)
        self.assertEqual(swh.latest([older, newer])["id"], 2)

    def test_single_record_returns_itself(self):
        self.assertEqual(swh.latest([LANDED])["id"], 2559526)

    def test_empty_and_dateless_are_none(self):
        self.assertIsNone(swh.latest([]))
        self.assertIsNone(swh.latest([{"id": 7}]))


class DescribeTest(unittest.TestCase):
    def test_finished_visit_names_the_swhid(self):
        line = swh.describe(LANDED)
        self.assertIn("SWHID swh:1:snp:3365e186a1d8bdb93c16895111438f3cad1e66b7", line)
        self.assertIn("visit full", line)

    def test_pending_visit_is_not_called_a_copy(self):
        line = swh.describe(PENDING)
        self.assertIn("no SWHID yet", line)
        self.assertNotIn("swh:1:snp", line)

    def test_missing_record_says_nothing_asked(self):
        self.assertIn("no save request on record", swh.describe(None))
        self.assertIn("no save request on record", swh.describe({}))

    def test_empty_swhid_string_is_treated_as_absent(self):
        # The live API returns "" rather than null while a visit is outstanding; a truthiness slip
        # here would print an empty SWHID and read as success.
        self.assertIn("no SWHID yet", swh.describe({"id": 1, "snapshot_swhid": ""}))


class ConstantsTest(unittest.TestCase):
    def test_origin_is_the_commons_repository(self):
        self.assertEqual(swh.ORIGIN, "https://github.com/LindsayRidgeway/llm-symposium")

    def test_pending_is_not_in_finished(self):
        self.assertNotIn("pending", swh.FINISHED)
        self.assertIn("full", swh.FINISHED)


if __name__ == "__main__":
    unittest.main(verbosity=2)
