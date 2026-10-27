#!/usr/bin/env python3
"""Tests for `scripts/repair_ledger_conflicts.py` — the union resolution of a ledger.

Offline. The load-bearing cases are the ones that were wrong in the world on
2026-10-18: a both-added block whose sides do not overlap (both lines must survive),
a block whose sides carry the *same* entry (one copy must survive), and idempotence
(a second pass over a repaired file must change nothing — otherwise the repair
itself becomes a source of churn in an append-only log).
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "repair_ledger_conflicts.py"


def _load():
    spec = importlib.util.spec_from_file_location("repair_ledger_conflicts", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _entry(id_: str, state: str | None = None, **kw) -> str:
    payload = {"id": id_, "amigo": "desi", "state": state}
    payload.update(kw)
    return json.dumps(payload) + "\n"


class RepairTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load()

    def test_both_added_block_keeps_both_sides_in_file_order(self):
        # The 2026-10-18 shape: ours = two desi entries, theirs = two codex entries.
        text = (
            _entry("a")
            + "<<<<<<< HEAD\n"
            + _entry("desi-1")
            + _entry("desi-2")
            + "=======\n"
            + _entry("codex-1")
            + _entry("codex-2")
            + ">>>>>>> 4a921369\n"
            + _entry("z")
        )
        repaired, stats = self.mod.repair_text(text)
        ids = [json.loads(line)["id"] for line in repaired.splitlines()]
        self.assertEqual(ids, ["a", "desi-1", "desi-2", "codex-1", "codex-2", "z"])
        self.assertEqual(stats["blocks"], 1)
        self.assertEqual(stats["ours"], 2)
        self.assertEqual(stats["theirs"], 2)
        self.assertEqual(stats["duplicates_dropped"], 0)
        self.assertNotIn("<<<<<<<", repaired)
        self.assertNotIn("=======", repaired)
        self.assertNotIn(">>>>>>>", repaired)

    def test_same_entry_on_both_sides_is_kept_once(self):
        text = (
            "<<<<<<< HEAD\n"
            + _entry("same", reviewer="dmitri")
            + "=======\n"
            + _entry("same", reviewer="dmitri")
            + ">>>>>>> x\n"
        )
        repaired, stats = self.mod.repair_text(text)
        self.assertEqual(len(repaired.splitlines()), 1)
        self.assertEqual(stats["duplicates_dropped"], 1)

    def test_same_entry_with_different_key_order_is_still_the_same_entry(self):
        a = '{"id": "same", "state": "postponed"}\n'
        b = '{"state": "postponed", "id": "same"}\n'
        text = "<<<<<<< HEAD\n" + a + "=======\n" + b + ">>>>>>> x\n"
        repaired, stats = self.mod.repair_text(text)
        self.assertEqual(len(repaired.splitlines()), 1)
        self.assertEqual(stats["duplicates_dropped"], 1)

    def test_two_blocks_are_both_resolved(self):
        text = (
            "<<<<<<< HEAD\n"
            + _entry("a1")
            + "=======\n"
            + _entry("b1")
            + ">>>>>>> x\n"
            + _entry("mid")
            + "<<<<<<< HEAD\n"
            + _entry("a2")
            + "=======\n"
            + _entry("b2")
            + ">>>>>>> x\n"
        )
        repaired, stats = self.mod.repair_text(text)
        ids = [json.loads(line)["id"] for line in repaired.splitlines()]
        self.assertEqual(ids, ["a1", "b1", "mid", "a2", "b2"])
        self.assertEqual(stats["blocks"], 2)

    def test_idempotent(self):
        text = (
            "<<<<<<< HEAD\n" + _entry("a") + "=======\n" + _entry("b") + ">>>>>>> x\n"
        )
        once, _ = self.mod.repair_text(text)
        twice, stats = self.mod.repair_text(once)
        self.assertEqual(once, twice)
        self.assertEqual(stats["blocks"], 0)

    def test_clean_file_is_untouched(self):
        text = _entry("a") + _entry("b")
        repaired, stats = self.mod.repair_text(text)
        self.assertEqual(repaired, text)
        self.assertEqual(stats["blocks"], 0)

    def test_non_json_payload_is_carried_through_and_named(self):
        text = (
            "<<<<<<< HEAD\n"
            + _entry("a")
            + "garbage line\n"
            + "=======\n"
            + _entry("b")
            + ">>>>>>> x\n"
        )
        repaired, stats = self.mod.repair_text(text)
        self.assertIn("garbage line", repaired)
        self.assertEqual(len(stats["non_json"]), 1)

    def test_diff3_base_row_is_refused_rather_than_guessed(self):
        text = (
            "<<<<<<< HEAD\n" + _entry("a") + "||||||| base\n" + _entry("o")
            + "=======\n" + _entry("b") + ">>>>>>> x\n"
        )
        with self.assertRaises(ValueError):
            self.mod.repair_text(text)

    def test_unterminated_block_is_refused(self):
        with self.assertRaises(ValueError):
            self.mod.repair_text("<<<<<<< HEAD\n" + _entry("a"))

    def test_marker_inside_json_string_is_not_a_block(self):
        # A ledger entry may legitimately *quote* a marker; only column-0 rows count.
        text = _entry("a", note="<<<<<<< HEAD was here")
        repaired, stats = self.mod.repair_text(text)
        self.assertEqual(stats["blocks"], 0)
        self.assertEqual(repaired, text)


class CommandLineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = _load()
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "items.jsonl"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write(self, text: str) -> None:
        self.path.write_text(text, encoding="utf-8")

    def test_check_returns_1_when_markers_present_and_write_clears_them(self):
        self._write("<<<<<<< HEAD\n" + _entry("a") + "=======\n" + _entry("b") + ">>>>>>> x\n")
        self.assertEqual(self.mod.main(["prog", str(self.path), "--check"]), 1)
        self.assertEqual(self.mod.main(["prog", str(self.path), "--write"]), 0)
        self.assertEqual(self.mod.main(["prog", str(self.path), "--check"]), 0)
        self.assertNotIn("<<<<<<<", self.path.read_text(encoding="utf-8"))

    def test_dry_run_does_not_touch_the_file(self):
        text = "<<<<<<< HEAD\n" + _entry("a") + "=======\n" + _entry("b") + ">>>>>>> x\n"
        self._write(text)
        self.assertEqual(self.mod.main(["prog", str(self.path)]), 0)
        self.assertEqual(self.path.read_text(encoding="utf-8"), text)

    def test_the_real_ledger_is_clean(self):
        """The integration case: if this fails, a conflict is on disk in the ledger."""
        ledger = ROOT / "channels" / "items.jsonl"
        if not ledger.exists():
            self.skipTest("no ledger in this checkout")
        repaired, stats = self.mod.repair_text(ledger.read_text(encoding="utf-8"))
        self.assertEqual(stats["blocks"], 0, "channels/items.jsonl still carries conflict markers")


class RealTreeTest(unittest.TestCase):
    """The guard Dmitri wrote must agree with this tool: no markers anywhere in the tree."""

    def test_check_conflict_markers_script_is_green(self):
        script = ROOT / "scripts" / "check_conflict_markers.py"
        if not script.exists():
            self.skipTest("guard absent")
        proc = subprocess.run(
            [sys.executable, str(script)], capture_output=True, text=True, cwd=ROOT
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
