#!/usr/bin/env python3
"""Every line of `channels/items.jsonl` must be a JSON object — the ledger fails *quietly* otherwise.

Written 2026-10-24 (Dmitri), after the defect was measured on `main`.

**What was there.** A merge conflict on `channels/items.jsonl` had been resolved by committing both
sides *and the three marker lines*: `<<<<<<< HEAD` at line 2558, `=======` at 2580,
`>>>>>>> 34ad5731…` at 2592. `commit` on 2026-10-24 sat on `main` with those three lines in a file
that four architectures append to.

**Why it survived.** `channels/item_ledger.py` does not fail on a line it cannot read. It prints
`item_ledger: skipping unreadable line N` and carries on, so every ledger run under-reported by
whatever the block held and no test went red. The conflict-marker guard
(`tests/test_conflict_markers.py`, written 2026-10-11) does catch the three markers — it was red on
this block — but it is a guard against *one* cause of an unreadable line, not against the class. A
truncated append, a half-written flush or a hand edit leaves the same symptom with no marker in it,
and nothing was watching for that.

**What this test pins.** The class: a non-empty line in the ledger that is not a JSON object. The
load-bearing case reads the real file, so any future block turns the suite red and the lander
refuses it. The second case runs the same helper on a string, so the check cannot pass by the file
happening to be clean today.

Offline and fast — no network, no live ledger writes.
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "channels" / "items.jsonl"


def unreadable_lines(text):
    """[(line number, first 80 characters)] for every non-empty line that is not a JSON object.

    Line numbers are 1-based and count every line, blank ones included, so a message can be matched
    against `item_ledger.py`'s own `skipping unreadable line N` output without arithmetic.
    """
    bad = []
    for number, line in enumerate(text.split("\n"), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except Exception as exc:  # noqa: BLE001 — any failure is the same failure here
            bad.append((number, f"{line[:80]!r} ({type(exc).__name__})"))
            continue
        if not isinstance(row, dict):
            bad.append((number, f"{line[:80]!r} (not an object)"))
        elif not row.get("id"):
            bad.append((number, f"{line[:80]!r} (no id)"))
    return bad


class LedgerParsesTest(unittest.TestCase):
    def test_the_real_ledger_parses(self):
        """The load-bearing case: if this fails, an item in the ledger is invisible to every report.

        Repair it with `python3 scripts/repair_ledger_conflicts.py --write` when the cause is a
        merge block, and do not excuse it: the ledger's own answer to an unreadable line is to skip
        it silently, which is how this block sat on `main` unremarked.
        """
        text = LEDGER.read_text(encoding="utf-8")
        bad = unreadable_lines(text)
        detail = "\n".join(f"  line {n}: {what}" for n, what in bad[:10])
        self.assertEqual(bad, [], f"{len(bad)} unreadable line(s) in channels/items.jsonl:\n{detail}")

    def test_the_check_catches_a_marker_block(self):
        """The class, not the snapshot: the 2026-10-24 block in miniature."""
        text = (
            '{"id": "a", "state": "accomplished"}\n'
            '{"id": "b", "state": "accomplished"}\n'
            "<<<<<<< HEAD\n"
            '{"id": "c", "state": "postponed"}\n'
            "=======\n"
            '{"id": "d", "state": "postponed"}\n'
            ">>>>>>> 34ad5731\n"
        )
        numbers = [n for n, _ in unreadable_lines(text)]
        self.assertEqual(numbers, [3, 5, 7], "the three marker lines must be named by line number")

    def test_the_check_catches_a_truncated_append(self):
        """No marker needed: a half-written row is the same failure, and nothing else catches it."""
        text = '{"id": "a", "state": "accomplished"}\n{"id": "b", "sta'
        numbers = [n for n, _ in unreadable_lines(text)]
        self.assertEqual(numbers, [2])

    def test_blank_lines_are_not_errors(self):
        """The file ends with a blank line; an empty line is not a corrupt record."""
        self.assertEqual(unreadable_lines('{"id": "a"}\n\n'), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
