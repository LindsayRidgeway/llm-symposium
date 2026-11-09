#!/usr/bin/env python3
"""A mirrored verdict must leave the "fold these in first" warning once it is in the ledger.

The defect this pins is a comparison, not a loop, and it is why the same three ids were printed
under every wake for six days. `item_ledger.unreplayed_verdicts()` asks whether the ledger row is
behind the mirror file, and it used to ask by comparing two `state_utc` strings as text. The two
sides are written in different formats by design: the ledger row carries ISO-8601
(`2026-11-08T06:53:01Z`, written by `review()`), a hand-written mirror carries the compact stamp
(`20261108T065301Z`), because that is what `scripts/ledger_verdict_mirror.py` names its files by.

Text order between those two is not time order. `-` (0x2d) sorts below `1` (0x31), so
`2026-11-08T…` < `20261108T…` for *every* pair, whatever the instant. The mirror is therefore
older than the row it was replayed from, forever, and the warning can never drain.

Measured at HEAD on 2026-11-09 before the repair: three ids
(codex-20261108T045905Z-87d4be45, 20261028T053300Z-55114152, 20261028T073326Z-85e03a27), each with
a ledger row at `2026-11-08T06:53:0xZ` and a mirror at `20261108T06530xZ` — identical instants
written two ways. All three are reproduced as fixtures below.

Run: python3 tests/test_unreplayed_verdicts.py
"""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "channels"))

_spec = importlib.util.spec_from_file_location("item_ledger", REPO / "channels" / "item_ledger.py")
il = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(il)


def row(item_id: str, state, state_utc, reviewer, filed="2026-11-08T06:00:00Z") -> dict:
    return {"id": item_id, "amigo": "desi", "filed_utc": filed, "state": state,
            "state_utc": state_utc, "reviewer": reviewer, "reason": "a reason",
            "title": "a test item", "source": "derived"}


class UnreplayedVerdictsTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.ledger = self.tmp / "items.jsonl"
        self.verdicts = self.tmp / "ledger-verdicts"
        self.verdicts.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def write_ledger(self, *rows):
        self.ledger.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows),
                               encoding="utf-8")

    def mirror(self, item_id, state, state_utc, reviewer="dmitri", name=None):
        path = self.verdicts / (name or f"{state_utc.replace('-', '').replace(':', '')}-{item_id}.json")
        path.write_text(json.dumps({"id": item_id, "state": state, "state_utc": state_utc,
                                    "reviewer": reviewer, "reason": "a reason", "run": "",
                                    "mirrored_utc": "2026-11-09T00:00:00Z"}, sort_keys=True),
                        encoding="utf-8")
        return path

    def pending(self):
        return il.unreplayed_verdicts(self.ledger, self.verdicts)

    # --- the measured bug -------------------------------------------------------------------

    def test_compact_mirror_of_the_same_instant_is_replayed(self):
        """The three live ids, reproduced: same instant, two formats, nothing left to fold in."""
        self.write_ledger(
            row("codex-20261108T045905Z-87d4be45", "accomplished", "2026-11-08T06:53:01Z", "dmitri"),
            row("20261028T053300Z-55114152", "accomplished", "2026-11-08T06:53:58Z", "dmitri"),
            row("20261028T073326Z-85e03a27", "accomplished", "2026-11-08T06:53:58Z", "dmitri"),
        )
        self.mirror("codex-20261108T045905Z-87d4be45", "accomplished", "20261108T065301Z")
        self.mirror("20261028T053300Z-55114152", "accomplished", "20261108T065358Z")
        self.mirror("20261028T073326Z-85e03a27", "accomplished", "20261108T065358Z")
        self.assertEqual(self.pending(), [])

    def test_a_compact_mirror_older_than_the_row_is_not_reported(self):
        """A superseded mirror has nothing to fold in — `replay` never walks a verdict backwards.

        This is the case the old text comparison got right by accident for ISO/ISO and wrong for
        every mixed pair, which is why the direction is asserted here rather than left implicit.
        """
        self.write_ledger(row("item-1", "accomplished", "2026-11-08T09:00:00Z", "dmitri"))
        self.mirror("item-1", "postponed", "20261108T065301Z")
        self.assertEqual(self.pending(), [])

    def test_a_compact_mirror_newer_than_the_row_is_reported(self):
        self.write_ledger(row("item-1", "accomplished", "2026-11-08T06:53:01Z", "dmitri"))
        self.mirror("item-1", "accomplished", "20261108T120000Z")
        self.assertEqual(self.pending(), ["item-1"])

    def test_the_two_formats_compare_equal_in_both_directions(self):
        """Not an accident of which side is ISO: the comparison is on parsed instants."""
        self.write_ledger(row("item-1", "accomplished", "20261108T065301Z", "dmitri"))
        self.mirror("item-1", "accomplished", "2026-11-08T06:53:01Z", name="iso-item-1.json")
        self.assertEqual(self.pending(), [])

    # --- the reasons the check exists -------------------------------------------------------

    def test_a_row_with_no_verdict_is_unreplayed(self):
        self.write_ledger(row("item-1", None, None, None))
        self.mirror("item-1", "accomplished", "20261108T065301Z")
        self.assertEqual(self.pending(), ["item-1"])

    def test_a_machine_stamp_is_not_a_verdict(self):
        for machine in ("auto:land", "auto:path"):
            with self.subTest(reviewer=machine):
                self.write_ledger(row("item-1", "accomplished", "2026-11-08T06:53:01Z", machine))
                self.mirror("item-1", "accomplished", "20261108T065301Z")
                self.assertEqual(self.pending(), ["item-1"])

    def test_an_undatable_mirror_is_reported_rather_than_silently_accepted(self):
        self.write_ledger(row("item-1", "accomplished", "2026-11-08T06:53:01Z", "dmitri"))
        self.mirror("item-1", "accomplished", "yesterday-ish")
        self.assertEqual(self.pending(), ["item-1"])

    def test_an_unreadable_mirror_file_is_skipped_not_fatal(self):
        self.write_ledger(row("item-1", "accomplished", "2026-11-08T06:53:01Z", "dmitri"))
        (self.verdicts / "broken.json").write_text("{not json", encoding="utf-8")
        self.mirror("item-1", "accomplished", "20261108T065301Z")
        self.assertEqual(self.pending(), [])

    def test_no_verdict_directory_reads_as_nothing_pending(self):
        self.write_ledger(row("item-1", None, None, None))
        self.assertEqual(il.unreplayed_verdicts(self.ledger, self.tmp / "absent"), [])

    # --- the helper the comparison now trusts -----------------------------------------------

    def test_verdict_moment_accepts_both_shapes_and_normalises_to_utc(self):
        iso = il.verdict_moment({"state": "accomplished", "state_utc": "2026-11-08T06:53:01Z"})
        compact = il.verdict_moment({"state": "accomplished", "state_utc": "20261108T065301Z"})
        self.assertEqual(iso, compact)
        self.assertTrue(iso.endswith("+00:00"))

    def test_verdict_moment_is_empty_for_an_unstamped_decision(self):
        self.assertEqual(il.verdict_moment({"state": None, "state_utc": None}), "")
        self.assertEqual(il.verdict_moment({"state": "accomplished", "state_utc": ""}), "")


if __name__ == "__main__":
    unittest.main()
