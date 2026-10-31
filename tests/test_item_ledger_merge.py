#!/usr/bin/env python3
"""The merge in `load()`, pinned against a frozen copy of the reader it replaced.

Why this file exists (2026-10-31, desi). `load()` used to take the last line of
`channels/items.jsonl` *whole*: an item's title, paths, assignment and `cost_usd` were only ever
as complete as whichever row was appended last. That is the one reason `assign()` cannot write a
diff — a row mentioning only `assigned_to` would erase everything else for every queue in the six
bots — and it is why 50 items carried a `cost_usd` in `load()` that no single raw row held.

The measurement came first (`channels/reports/2026-10-31-desi-what-a-merge-would-do-to-the-ledger.md`):
against the real ledger, **3,876 rows for 879 items**, a verdict-aware merge changes the decision
on **0 items**, while a naive field-union changes it on exactly the 9 `held`/`backdated` items —
a stale copy appended late walking the reason backwards. So the risky half of the merge is not the
field accumulation; it is the temptation to accumulate the verdict too.

What is asserted here, in order of how much it would hurt to be wrong:

1. on the real ledger, the merged reader makes the same decision as the frozen pre-merge reader,
   for every item — the property that licenses the change at all;
2. the `held` and `disagree_state` ids are each resolved to the copy `verdict_stamp()` says is
   newest, and the census is not empty (a test that passes because there is nothing to test is
   the failure mode this house keeps finding);
3. a diff-shaped row adds to its item instead of replacing it;
4. a zero is a value and a blank is not — the falsy-zero defect, in a reader;
5. the two older exceptions survive the rewrite: silence is not a reversal (10-25), and a
   backdated row cannot un-decide a newer verdict (10-27).
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import channels.item_ledger as il  # noqa: E402

LEDGER = REPO / "channels" / "items.jsonl"


def legacy_load(path: Path = LEDGER) -> dict:
    """`load()` as it stood before 2026-10-31 — the last line wins whole, with the two exceptions.

    Frozen here on purpose, not imported: the point of the test is to compare the current reader
    against the previous one, and a reference that changes with the subject proves nothing. This
    is the exact loop the merge replaced, kept verbatim.
    """
    items: dict = {}
    if not path.exists():
        return items
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
            prev = items.get(rec["id"])
            if prev is not None and prev.get("state") and not rec.get("state"):
                for key in il.VERDICT_KEYS:
                    if not rec.get(key):
                        rec[key] = prev.get(key)
            elif prev is not None and il.verdict_stamp(prev) and il.verdict_stamp(rec) \
                    and il.verdict_stamp(rec) < il.verdict_stamp(prev):
                for key in il.VERDICT_KEYS:
                    rec[key] = prev.get(key)
                rec["verdict_kept_from"] = prev.get("state_utc")
            items[rec["id"]] = rec
        except (ValueError, KeyError):
            continue
    return items


def write_ledger(rows) -> Path:
    fd = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
    with fd:
        for row in rows:
            fd.write(json.dumps(row) + "\n")
    return Path(fd.name)


FULL = {
    "id": "x1",
    "amigo": "desi",
    "title": "a whole record",
    "paths": ["channels/item_ledger.py"],
    "filed_utc": "2026-10-01T00:00:00Z",
    "state": "accomplished",
    "state_utc": "2026-10-02T00:00:00Z",
    "reason": "did the thing",
    "reviewer": "gemini",
    "cost_usd": 0.42,
}


class RealLedgerTest(unittest.TestCase):
    """The property that licenses the change, measured on the ledger itself."""

    def setUp(self):
        self.now = il.load(LEDGER)
        self.was = legacy_load(LEDGER)

    def test_the_ledger_is_worth_measuring_on(self):
        # A comparison over three items would pass for the wrong reason.
        self.assertGreaterEqual(len(self.now), 800, "the ledger shrank — is the path right?")
        self.assertEqual(set(self.now), set(self.was))

    def test_every_item_decides_the_same_as_the_pre_merge_reader(self):
        changed = []
        for item_id, rec in self.now.items():
            before = self.was[item_id]
            if any(rec.get(k) != before.get(k) for k in il.DECISION_FIELDS):
                changed.append((item_id, {k: (before.get(k), rec.get(k))
                                          for k in il.DECISION_FIELDS
                                          if rec.get(k) != before.get(k)}))
        self.assertEqual(changed, [], f"{len(changed)} item(s) changed decision under the merge")

    def test_the_merge_only_ever_adds_fields(self):
        # The other half of the promise: the merged record is a superset of the last line, so a
        # queue reading it cannot lose a field the old reader handed it.
        lost = []
        for item_id, rec in self.now.items():
            before = self.was[item_id]
            for key, value in before.items():
                if il.carries(value) and rec.get(key) != value:
                    lost.append((item_id, key, value, rec.get(key)))
        self.assertEqual(lost, [], f"{len(lost)} field(s) lost under the merge")

    def test_the_held_items_keep_the_newer_reason(self):
        census = il.duplicates(LEDGER)
        self.assertTrue(census["held"], "no held item today — this test would prove nothing")
        for item_id in census["held"]:
            stated = [r for r in self._copies(item_id) if il.verdict_stamp(r)]
            newest = max(stated, key=il.verdict_stamp)
            rec = self.now[item_id]
            self.assertEqual(rec["reason"], newest["reason"], item_id)
            self.assertEqual(rec["state_utc"], newest["state_utc"], item_id)

    def test_the_disagreeing_ids_resolve_by_stamp(self):
        census = il.duplicates(LEDGER)
        self.assertTrue(census["disagree_state"], "no disagreement today — nothing is tested")
        for item_id in census["disagree_state"]:
            stated = [r for r in self._copies(item_id) if il.verdict_stamp(r)]
            newest = max(stated, key=il.verdict_stamp)
            self.assertEqual(self.now[item_id]["state"], newest["state"], item_id)

    def _copies(self, item_id):
        rows = []
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("id") == item_id:
                rows.append(rec)
        return rows


class MergeRowTest(unittest.TestCase):
    """`merge_row()` itself, on four-row ledgers where the answer is not in doubt."""

    def test_a_diff_shaped_row_adds_instead_of_replacing(self):
        path = write_ledger([
            FULL,
            {"id": "x1", "assigned_to": "dmitri", "assign_kind": "draw",
             "assign_reason": "b", "assigned_utc": "2026-10-03T00:00:00Z", "assigned_by": "desi"},
        ])
        rec = il.load(path)[ "x1"]
        # Nothing the full record said may be lost...
        for key in ("amigo", "title", "state", "state_utc", "reason", "reviewer"):
            self.assertEqual(rec[key], FULL[key], key)
        self.assertEqual(rec["paths"], FULL["paths"])
        # ...and the diff-shaped row is added in full.
        self.assertEqual(rec["assigned_to"], "dmitri")
        self.assertEqual(rec["assign_reason"], "b")

    def test_a_zero_is_a_value_not_silence(self):
        path = write_ledger([FULL, {"id": "x1", "cost_usd": 0.0}])
        self.assertEqual(il.load(path)["x1"]["cost_usd"], 0.0)
        # And a blank is silence: an empty path list must not erase a real one.
        path = write_ledger([FULL, {"id": "x1", "paths": []}])
        self.assertEqual(il.load(path)["x1"]["paths"], FULL["paths"])

    def test_silence_is_still_not_a_reversal(self):
        path = write_ledger([FULL, {"id": "x1", "assigned_to": "gemini"}])
        rec = il.load(path)["x1"]
        self.assertEqual((rec["state"], rec["reason"], rec["reviewer"]),
                         (FULL["state"], FULL["reason"], FULL["reviewer"]))

    def test_a_backdated_diff_row_cannot_un_decide(self):
        newer = dict(FULL, state_utc="2026-10-09T00:00:00Z", reason="the newer reason",
                     reviewer="tarik")
        stale = {"id": "x1", "state": "postponed", "state_utc": "2026-10-05T00:00:00Z",
                 "reason": "the older reason", "reviewer": "claude",
                 "paths": ["other/path.py"]}
        rec = il.load(write_ledger([FULL, newer, stale]))["x1"]
        self.assertEqual(rec["reason"], "the newer reason")
        self.assertEqual(rec["state_utc"], "2026-10-09T00:00:00Z")
        self.assertEqual(rec["verdict_kept_from"], "2026-10-09T00:00:00Z")
        # The late copy still gets to say what it says about the item's shape.
        self.assertEqual(rec["paths"], ["other/path.py"])

    def test_a_stated_verdict_wins_whole(self):
        revised = {"id": "x1", "state": "postponed", "state_utc": "2026-10-10T00:00:00Z",
                   "reason": "waiting on the lander", "reviewer": "claude"}
        rec = il.load(write_ledger([FULL, revised]))["x1"]
        self.assertEqual((rec["state"], rec["reason"], rec["reviewer"]),
                         ("postponed", "waiting on the lander", "claude"))
        self.assertEqual(rec["title"], FULL["title"])

    def test_an_unassigned_snapshot_clears_the_assignment(self):
        """The group rule the wide branch depends on, learned the hard way this wake.

        `tests/test_item_ledger_wide_branch.py` appends a second, *unassigned* copy of an item and
        then requires the draw to re-derive the same name. Field-by-field accumulation broke it:
        `assigned_to` survived from the earlier copy, the item read as assigned, and the draw
        returned nothing — a frozen draw that cannot be re-derived. So assignment keys are a group
        taken from the last copy whole (`is_assignment_key()`), and this pins that.
        """
        assigned = dict(FULL, assigned_to="tarik", assign_kind="draw", assign_reason="b")
        rec = il.load(write_ledger([assigned, {"id": "x1", "title": "a later snapshot"}]))["x1"]
        self.assertNotIn("assigned_to", rec)
        self.assertNotEqual(rec.get("assign_kind"), "draw")
        # ...while the fields that are merely facts about the item still accumulate.
        self.assertEqual(rec["title"], "a later snapshot")
        self.assertEqual(rec["reason"], FULL["reason"])
        self.assertEqual(rec["paths"], FULL["paths"])


if __name__ == "__main__":
    unittest.main()
