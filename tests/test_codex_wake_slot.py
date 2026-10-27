#!/usr/bin/env python3
"""Offline clock-slot regressions; no claim creation or scheduler calls."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.codex_wake_slot import resolve_slot


class WakeSlotTests(unittest.TestCase):
    def test_observed_early_dispatch_uses_upcoming_clock_slot(self):
        row = resolve_slot("2026-10-18T11:55:15Z")
        self.assertEqual(row["claim_path"], "channels/tarik-codex-wakes/claims/2026-10-18-0800.json")
        self.assertEqual(row["scheduled_slot_local"], "2026-10-18T08:00:00-04:00")
        self.assertEqual(row["seconds_from_slot"], -285)
        self.assertEqual(row["basis"], "inferred_early_window")

    def test_exact_slot_and_late_dispatch_keep_same_occurrence(self):
        for timestamp in ("2026-10-18T08:00:00Z", "2026-10-18T08:04:08Z"):
            self.assertTrue(resolve_slot(timestamp)["claim_path"].endswith("2026-10-18-0400.json"))

    def test_aware_local_offset_is_normalized_to_utc(self):
        self.assertEqual(resolve_slot("2026-10-18T07:55:15-04:00"),
                         resolve_slot("2026-10-18T11:55:15Z"))

    def test_early_window_boundary_does_not_expand(self):
        self.assertTrue(resolve_slot("2026-10-18T11:50:00Z")["claim_path"].endswith("-0800.json"))
        self.assertTrue(resolve_slot("2026-10-18T11:49:59Z")["claim_path"].endswith("-0400.json"))

    def test_midnight_uses_new_york_calendar_date(self):
        row = resolve_slot("2026-10-19T03:55:00Z")
        self.assertTrue(row["claim_path"].endswith("2026-10-19-0000.json"))
        self.assertEqual(row["scheduled_utc"], "2026-10-19T04:00:00Z")

    def test_explicit_occurrence_overrides_inference_for_a_manual_replay(self):
        row = resolve_slot("2026-10-18T11:55:15Z", "2026-10-18T08:00:00Z")
        self.assertTrue(row["claim_path"].endswith("-0400.json"))
        self.assertFalse(row["inferred"])

    def test_invalid_explicit_slot_and_naive_time_are_rejected(self):
        for start, scheduled in [
            ("2026-10-18T08:00:00", None),
            ("2026-10-18T08:00:00Z", "2026-10-18T09:00:00Z"),
            ("2026-10-18T08:00:00Z", "2026-10-18T08:00:01Z"),
        ]:
            with self.subTest(start=start, scheduled=scheduled), self.assertRaises(ValueError):
                resolve_slot(start, scheduled)

    def test_spring_transition_uses_local_four_not_four_utc_hours(self):
        row = resolve_slot("2026-03-08T07:55:00Z")
        self.assertEqual(row["scheduled_slot_local"], "2026-03-08T04:00:00-04:00")
        self.assertEqual(row["scheduled_utc"], "2026-03-08T08:00:00Z")

    def test_fall_transition_uses_local_four_after_five_elapsed_hours(self):
        row = resolve_slot("2026-11-01T08:55:00Z")
        self.assertEqual(row["scheduled_slot_local"], "2026-11-01T04:00:00-05:00")
        self.assertEqual(row["scheduled_utc"], "2026-11-01T09:00:00Z")

    def test_both_repeated_fall_hours_still_belong_to_midnight(self):
        for timestamp in ("2026-11-01T05:30:00Z", "2026-11-01T06:30:00Z"):
            self.assertTrue(resolve_slot(timestamp)["claim_path"].endswith("2026-11-01-0000.json"))

    def test_existing_claim_files_do_not_change_selection_or_get_modified(self):
        with tempfile.TemporaryDirectory() as directory:
            claim = Path(directory) / "2026-10-18-0800.json"
            claim.write_text('{"run_id":"other-owner"}')
            before = claim.read_bytes()
            row = resolve_slot("2026-10-18T11:55:15Z")
            self.assertTrue(row["claim_path"].endswith(claim.name))
            self.assertEqual(claim.read_bytes(), before)
            self.assertEqual(len(list(Path(directory).iterdir())), 1)

    def test_cli_matches_api_and_has_no_side_effects(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/codex_wake_slot.py"),
                 "--started-utc", "2026-10-18T11:55:15Z"],
                cwd=directory, text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), resolve_slot("2026-10-18T11:55:15Z"))
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
