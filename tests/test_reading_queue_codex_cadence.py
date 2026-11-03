"""The reading queue must consume public review-only Codex wake evidence."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "channels"))
import item_ledger as il

class PublicQueueCadence(unittest.TestCase):
    ID = "codex-20261102T050205Z-86bfded6"
    START = "2026-11-02T05:02:05Z"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "scripts").mkdir()
        shutil.copy(REPO / "scripts" / "wake_cadence.py",
                    self.root / "scripts" / "wake_cadence.py")
        self.ledger = self.root / "channels" / "items.jsonl"
        self.ledger.parent.mkdir()
        self.ledger.write_text("")
        self.runs = self.root / "empty-runs"
        self.runs.mkdir()
        self.records = self.ledger.parent / "tarik-codex-wakes"
        self.records.mkdir()
        self.now = il.dt.datetime(2026, 11, 2, 6, 2, 5, tzinfo=il.dt.timezone.utc)

    def record(self, root=None, **changes):
        rec = {"run_id": self.ID, "amigo": "tarik", "platform": "codex",
               "started_utc": self.START, "status": "completed_substantive_review_only"}
        rec.update(changes)
        ((root or self.records) / (self.ID + ".json")).write_text(json.dumps(rec))

    def measured(self, **kw):
        with mock.patch.object(il, "REPO", self.root):
            return il.measured_cadence(now=self.now, runs_root=self.runs,
                                       ledger=self.ledger, **kw)

    def test_review_only_record_reaches_rate_display_without_a_ledger_item(self):
        self.record()
        got = self.measured()
        self.assertEqual(got["tarik"]["hours_since"], 1.0)
        self.assertEqual(got["tarik"]["wakes_in_window"], 1)
        self.assertIn("last 1h ago", il.rate_beside(got, "tarik"))
        self.assertEqual(self.ledger.read_text(), "")

    def test_default_root_follows_explicit_ledger_not_host_checkout(self):
        self.record()
        elsewhere = self.root / "other-checkout"
        elsewhere.mkdir()
        with mock.patch.object(il, "REPO", elsewhere):
            (elsewhere / "scripts").mkdir()
            shutil.copy(REPO / "scripts" / "wake_cadence.py",
                        elsewhere / "scripts" / "wake_cadence.py")
            got = il.measured_cadence(now=self.now, runs_root=self.runs, ledger=self.ledger)
        self.assertEqual(got["tarik"]["wakes_in_window"], 1)

    def test_explicit_public_root_overrides_the_default(self):
        alternate = self.root / "other-records"
        alternate.mkdir()
        self.record(root=alternate)
        self.assertIsNone(self.measured()["tarik"]["hours_since"])
        self.assertEqual(self.measured(codex_root=alternate)["tarik"]["hours_since"], 1.0)

    def test_same_ledger_id_and_public_record_count_once(self):
        self.record()
        self.ledger.write_text(json.dumps({"id": self.ID, "amigo": "tarik"}) + "\n")
        self.assertEqual(self.measured()["tarik"]["wakes_in_window"], 1)

    def test_invalid_record_is_not_silently_promoted_to_a_wake(self):
        self.record(platform="goose")
        got = self.measured()
        self.assertIsNone(got["tarik"]["hours_since"])
        self.assertIn("assumed", il.rate_beside(got, "tarik"))

    def test_measurement_never_rewrites_rows_or_frozen_weights(self):
        self.record()
        self.ledger.write_text(json.dumps({"id": "old", "amigo": "desi",
            "state": "accomplished", "reviewer": "auto:land",
            "reading_assigned_to": "tarik", "reading_assign_kind": "draw"}) + "\n")
        before = self.ledger.read_bytes()
        weights = dict(il.WAKES_PER_DAY)
        self.measured()
        self.assertEqual(self.ledger.read_bytes(), before)
        self.assertEqual(il.WAKES_PER_DAY, weights)

    def test_unavailable_instrument_keeps_the_assumed_fallback(self):
        (self.root / "scripts" / "wake_cadence.py").unlink()
        self.assertIsNone(self.measured())
        self.assertEqual(il.rate_beside(None, "tarik"), "assumed")

if __name__ == "__main__":
    unittest.main()
