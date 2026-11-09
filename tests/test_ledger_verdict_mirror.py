#!/usr/bin/env python3
"""A verdict must survive the run that wrote it (scripts/ledger_verdict_mirror.py).

The defect this pins is the loop, not a bug: `item_ledger.py --review` records a verdict by
appending one line to `channels/items.jsonl`, a 3,000-line file main also appends to live.
Delivery applies a patch, the patch carries that file's tail as context, the context is stale
within minutes, the hunk fails, and `git apply` being atomic, the whole run is discarded —
verdict included. The item returns to `waiting` and the next wake reviews it again.

Measured on two consecutive wakes of 2026-10-26 (runs 20261026T094058Z-eb5c4d6e and
20261026T114111Z-bdc12b38): the same item, codex-20261026T082005Z-93ddaeaa, reviewed twice in
one day, the first verdict lost. Same mechanism as the 2026-10-23 lost delivery.

The mirror writes each verdict as its own one-line file under `channels/ledger-verdicts/`, which
is a clean add and always applies, and `replay` folds it back into the ledger idempotently and
never backwards. These cases are all temp-directory work — nothing here touches the live ledger.

Run: python3 tests/test_ledger_verdict_mirror.py
"""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "channels"))

_spec = importlib.util.spec_from_file_location(
    "ledger_verdict_mirror", REPO / "scripts" / "ledger_verdict_mirror.py")
lvm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lvm)
import item_ledger  # noqa: E402  (already imported by lvm; bound here to call review())

ROW = {"id": "codex-test-1", "amigo": "tarik", "state": None, "state_utc": None,
       "reviewer": None, "reason": None, "title": "a test item", "source": "codex"}


class LedgerVerdictMirrorTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.verdicts = self.tmp / "ledger-verdicts"
        self.ledger = self.tmp / "items.jsonl"
        self.ledger.write_text(json.dumps(ROW, sort_keys=True) + "\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def lines(self):
        return self.ledger.read_text().strip().splitlines()

    def test_mirror_writes_one_named_file(self):
        path = lvm.mirror("codex-test-1", "accomplished", "dmitri", "did the work: ran 1",
                          "run-1", self.verdicts, "2026-10-26T11:41:50Z")
        rec = json.loads(path.read_text())
        self.assertEqual(rec["id"], "codex-test-1")
        self.assertEqual(rec["state"], "accomplished")
        self.assertEqual(rec["reviewer"], "dmitri")
        self.assertEqual(rec["run"], "run-1")
        self.assertEqual(path.name, "20261026T114150Z-codex-test-1.json")

    def test_mirror_refuses_a_verdict_with_no_record(self):
        bad = [
            {"state": "maybe"},
            {"state": "accomplished", "reviewer": " "},
            {"state": "accomplished", "reviewer": "dmitri", "reason": "   "},
        ]
        for case in bad:
            kwargs = {"item_id": "codex-test-1", "state": "accomplished", "reviewer": "dmitri",
                      "reason": "did the work: ran 1", "verdicts": self.tmp / "v2"}
            kwargs.update(case)
            with self.assertRaises(SystemExit, msg=f"mirror accepted {case}"):
                lvm.mirror(**kwargs)

    def test_replay_folds_the_verdict_in_and_is_idempotent(self):
        lvm.mirror("codex-test-1", "postponed", "dmitri", "blocked on a merger", "",
                   self.verdicts, "2026-10-26T11:41:50Z")
        first = lvm.replay(self.ledger, self.verdicts)
        self.assertEqual(first["applied"], ["codex-test-1"])
        self.assertEqual(first["skipped"], [])
        self.assertEqual(len(self.lines()), 2)
        live = json.loads(self.lines()[-1])
        self.assertEqual(live["state"], "postponed")
        self.assertEqual(live["reviewer"], "dmitri")
        # the replay must not throw away the rest of the item's row
        self.assertEqual(live["title"], "a test item")

        second = lvm.replay(self.ledger, self.verdicts)
        self.assertEqual(second["applied"], [])
        self.assertEqual(second["skipped"], ["codex-test-1"])
        self.assertEqual(len(self.lines()), 2, "replaying twice must not append twice")

    def test_replay_never_walks_a_verdict_backwards(self):
        lvm.mirror("codex-test-1", "accomplished", "dmitri", "did the work: ran 2", "",
                   self.verdicts, "2026-10-26T12:00:00Z")
        lvm.replay(self.ledger, self.verdicts)
        lvm.mirror("codex-test-1", "postponed", "tarik", "older verdict", "",
                   self.verdicts, "2026-10-26T09:00:00Z")
        result = lvm.replay(self.ledger, self.verdicts)
        self.assertEqual(result["applied"], [])
        self.assertIn("codex-test-1", result["skipped"])
        live = json.loads(self.lines()[-1])
        self.assertEqual(live["state"], "accomplished")
        self.assertEqual(live["reviewer"], "dmitri")

    def test_replay_names_an_unknown_item_instead_of_inventing_it(self):
        lvm.mirror("codex-not-in-the-ledger", "rejected", "dmitri", "never do this", "",
                   self.verdicts, "2026-10-26T11:41:50Z")
        result = lvm.replay(self.ledger, self.verdicts)
        self.assertEqual(result["unknown"], ["codex-not-in-the-ledger"])
        self.assertEqual(result["applied"], [])
        self.assertEqual(len(self.lines()), 1)

    def test_dry_run_changes_nothing(self):
        lvm.mirror("codex-test-1", "accomplished", "dmitri", "did the work: ran 3", "",
                   self.verdicts, "2026-10-26T11:41:50Z")
        result = lvm.replay(self.ledger, self.verdicts, dry_run=True)
        self.assertEqual(result["applied"], ["codex-test-1"])
        self.assertEqual(len(self.lines()), 1)

    def test_mirror_normalises_the_compact_stamp_a_hand_written_verdict_carries(self):
        """The filename is compact by design; `state_utc` must not be.

        Measured 2026-11-08: three verdicts written by hand the previous wake carried
        `20261108T065358Z`, the shape of every run id here. `item_ledger.verdict_stamp` refuses
        it, so `replay` could never fold them in and the three items stayed in the reading queue
        as though unread.
        """
        path = lvm.mirror("codex-test-1", "accomplished", "dmitri", "did the work: ran 4", "",
                          self.verdicts, "20261026T114150Z")
        rec = json.loads(path.read_text())
        self.assertEqual(rec["state_utc"], "2026-10-26T11:41:50Z")
        self.assertEqual(path.name, "20261026T114150Z-codex-test-1.json",
                         "the filename keeps the compact spelling")
        self.assertEqual(lvm.replay(self.ledger, self.verdicts)["applied"], ["codex-test-1"])
        self.assertEqual(json.loads(self.lines()[-1])["state_utc"], "2026-10-26T11:41:50Z")

    def test_a_compact_stamp_already_on_disk_is_read_rather_than_fatal(self):
        """A mirror file written before this repair must still fold in, not abort the batch."""
        self.verdicts.mkdir(parents=True, exist_ok=True)
        (self.verdicts / "20261026T114150Z-codex-test-1.json").write_text(json.dumps({
            "id": "codex-test-1", "state": "accomplished", "state_utc": "20261026T114150Z",
            "reviewer": "dmitri", "reason": "did the work: ran 5", "run": "",
        }) + "\n", encoding="utf-8")
        result = lvm.replay(self.ledger, self.verdicts)
        self.assertEqual(result["applied"], ["codex-test-1"])
        self.assertEqual(result["unreadable"], [])
        self.assertEqual(json.loads(self.lines()[-1])["state_utc"], "2026-10-26T11:41:50Z")

    def test_one_unreadable_mirror_does_not_hold_the_batch_hostage(self):
        """A bad file is named; it does not stop the good verdicts beside it from folding in."""
        lvm.mirror("codex-test-1", "accomplished", "dmitri", "did the work: ran 6", "",
                   self.verdicts, "2026-10-26T11:41:50Z")
        (self.verdicts / "broken.json").write_text("{not json", encoding="utf-8")
        (self.verdicts / "stampless.json").write_text(json.dumps({
            "id": "codex-test-1", "state": "rejected", "state_utc": "sometime",
            "reviewer": "tarik", "reason": "no"}) + "\n", encoding="utf-8")
        result = lvm.replay(self.ledger, self.verdicts)
        self.assertEqual(result["applied"], ["codex-test-1"])
        self.assertEqual(len(result["unreadable"]), 2, result["unreadable"])
        self.assertTrue(any("broken.json" in p for p in result["unreadable"]))
        self.assertTrue(any("stampless.json" in p for p in result["unreadable"]))

    def test_a_verdict_time_with_no_clock_is_refused(self):
        with self.assertRaises(SystemExit):
            lvm.mirror("codex-test-1", "accomplished", "dmitri", "did the work", "",
                       self.verdicts, "2026-10-26T11:41:50")


    def test_invalid_compact_dates_do_not_block_a_valid_neighbor(self):
        bad = ["20261100T085200Z", "20261301T085200Z", "20260229T085200Z",
               "20261131T085200Z", "20261108T245200Z", "20261108T086000Z",
               "20261108T085260Z", "00001108T085200Z"]
        self.verdicts.mkdir()
        for i, stamp in enumerate(bad):
            (self.verdicts / f"bad-{i}.json").write_text(json.dumps({
                "id": ROW["id"], "state": "rejected", "state_utc": stamp,
                "reviewer": "dmitri", "reason": "invalid calendar fixture"}) + "\n")
        lvm.mirror(ROW["id"], "accomplished", "dmitri", "valid neighbor", "",
                   self.verdicts, "2026-11-09T08:52:00Z")
        before = self.ledger.read_bytes()
        dry = lvm.replay(self.ledger, self.verdicts, dry_run=True)
        self.assertEqual(self.ledger.read_bytes(), before)
        self.assertEqual(dry["applied"], [ROW["id"]])
        self.assertEqual(len(dry["unreadable"]), len(bad))
        result = lvm.replay(self.ledger, self.verdicts)
        self.assertEqual(result["applied"], [ROW["id"]])
        self.assertEqual(len(result["unreadable"]), len(bad))
        for i in range(len(bad)):
            self.assertTrue(any(f"bad-{i}.json:" in e for e in result["unreadable"]))
        self.assertTrue(self.ledger.read_bytes().startswith(before))
        self.assertEqual(len(self.lines()), 2)
        self.assertEqual(json.loads(self.lines()[-1])["state"], "accomplished")
        again = lvm.replay(self.ledger, self.verdicts)
        self.assertEqual(again["applied"], [])
        self.assertEqual(again["skipped"], [ROW["id"]])
        self.assertEqual(len(self.lines()), 2)

    def test_mirror_refuses_invalid_compact_dates_before_writing(self):
        for stamp in ["20261100T085200Z", "20260229T085200Z", "20261108T245200Z"]:
            with self.subTest(stamp=stamp), self.assertRaises(SystemExit):
                lvm.mirror(ROW["id"], "rejected", "dmitri", "bad time", "",
                           self.verdicts, stamp)
            self.assertFalse(self.verdicts.exists())

    def test_valid_leap_day_and_offset_normalize_to_utc(self):
        for stamp in ["20240229T123456Z", "2024-02-29T12:34:56Z",
                      "2024-02-29T13:34:56+01:00"]:
            with self.subTest(stamp=stamp):
                self.assertEqual(lvm._aware(stamp), "2024-02-29T12:34:56Z")

    def test_normalization_preserves_four_digit_early_year(self):
        self.assertEqual(lvm._aware("00010101T000000Z"), "0001-01-01T00:00:00Z")
        path = lvm.mirror(ROW["id"], "postponed", "dmitri", "early fixture", "",
                          self.verdicts, "00010101T000000Z")
        self.assertEqual(json.loads(path.read_text())["state_utc"], "0001-01-01T00:00:00Z")
        self.assertEqual(lvm.replay(self.ledger, self.verdicts)["applied"], [ROW["id"]])

    def test_nontext_stamp_is_reported_per_file(self):
        self.verdicts.mkdir()
        for i, stamp in enumerate([20261108, ["20261108T085200Z"], {"time": "bad"}]):
            (self.verdicts / f"nontime-{i}.json").write_text(json.dumps({
                "id": ROW["id"], "state": "rejected", "state_utc": stamp,
                "reviewer": "dmitri", "reason": "nontext time"}) + "\n")
        lvm.mirror(ROW["id"], "postponed", "dmitri", "valid fixture", "",
                   self.verdicts, "2026-11-09T08:52:00Z")
        result = lvm.replay(self.ledger, self.verdicts)
        self.assertEqual(result["applied"], [ROW["id"]])
        self.assertEqual(len(result["unreadable"]), 3)

    def test_out_of_range_utc_conversion_is_reported_per_file(self):
        self.verdicts.mkdir()
        (self.verdicts / "outside-utc.json").write_text(json.dumps({
            "id": ROW["id"], "state": "rejected", "state_utc": "0001-01-01T00:00:00+01:00",
            "reviewer": "dmitri", "reason": "UTC would be year zero"}) + "\n")
        lvm.mirror(ROW["id"], "postponed", "dmitri", "valid fixture", "",
                   self.verdicts, "2026-11-09T08:52:00Z")
        result = lvm.replay(self.ledger, self.verdicts)
        self.assertEqual(result["applied"], [ROW["id"]])
        self.assertEqual(len(result["unreadable"]), 1)
        self.assertIn("outside-utc.json", result["unreadable"][0])

    def test_item_ledger_review_leaves_one_mirror_file(self):
        """The documented path must mirror too, not just the second command somebody remembers.

        Until 2026-11-09 `item_ledger.review()` wrote only to items.jsonl, so every `--review`
        verdict for sixteen days was one stale-context hunk away from being discarded with its run.
        """
        item_ledger.review(self.ledger, "codex-test-1", "accomplished", "did the work: channels/items.jsonl",
                           "dmitri")
        files = sorted(self.verdicts.glob("*.json"))
        self.assertEqual(len(files), 1, f"expected exactly one mirror, got {[f.name for f in files]}")
        mirrored = json.loads(files[0].read_text())
        ledger_row = json.loads(self.lines()[-1])
        self.assertEqual(mirrored["state_utc"], ledger_row["state_utc"])
        self.assertEqual(mirrored["state"], "accomplished")
        self.assertEqual(mirrored["reviewer"], "dmitri")
        self.assertEqual(files[0].name,
                         mirrored["state_utc"].replace("-", "").replace(":", "")
                         + "-codex-test-1.json")
        # A mirror that replay would not fold in is a mirror that bought nothing.
        self.assertEqual(lvm.replay(self.ledger, self.verdicts)["applied"], [])

    def test_review_survives_a_mirror_that_cannot_be_written(self):
        """A mirror failure must never cost the ledger row: the row is the record."""
        self.verdicts.write_text("not a directory")  # mkdir will fail with OSError
        item_ledger.review(self.ledger, "codex-test-1", "postponed", "waiting on a reviewer",
                           "dmitri")
        row = json.loads(self.lines()[-1])
        self.assertEqual(row["state"], "postponed")
        self.assertEqual(row["reason"], "waiting on a reviewer")


if __name__ == "__main__":
    unittest.main(verbosity=2)
