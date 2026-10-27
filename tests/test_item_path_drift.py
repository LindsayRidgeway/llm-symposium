#!/usr/bin/env python3
"""Tests for scripts/item_path_drift.py — a missing path is two different facts.

The point of the tool is that "absent from main" and "cited under its old name" look identical to a
reviewer with a file-existence check, and they call for opposite actions: one needs a reviewer, the
other needs one line of repair by the item's author. These tests pin the split, the latest-row rule
that makes the counts mean anything, and the deliberate decision not to be a gate by default.

Run: python3 -m unittest tests.test_item_path_drift
"""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts import item_path_drift as ipd


def write_ledger(path: Path, rows: list[dict]) -> Path:
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf8")
    return path


class LoadItemsTests(unittest.TestCase):
    def test_latest_row_wins_for_a_repeated_id(self) -> None:
        """The ledger is append-only; counting raw lines overstates the pile roughly fourfold."""
        with tempfile.TemporaryDirectory() as tmp:
            ledger = write_ledger(Path(tmp) / "items.jsonl", [
                {"id": "a", "state": "waiting"},
                {"id": "a", "state": "accomplished"},
                {"id": "b", "state": "accomplished"},
            ])
            items = ipd.load_items(ledger)
            self.assertEqual(len(items), 2)
            self.assertEqual(items["a"]["state"], "accomplished")

    def test_blank_lines_are_not_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "items.jsonl"
            path.write_text('{"id": "a", "state": "accomplished"}\n\n', encoding="utf8")
            self.assertEqual(list(ipd.load_items(path)), ["a"])


class DriftTests(unittest.TestCase):
    def test_present_paths_produce_no_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs" / "here.md").write_text("x", encoding="utf8")
            items = {"a": {"id": "a", "state": "accomplished", "paths": ["docs/here.md"]}}
            self.assertEqual(ipd.drift(items, root), [])

    def test_moved_file_is_a_citation_repair_not_a_review(self) -> None:
        """The real case: channels/outbound/x.md filed to channels/sent/x.md by drain_outbox()."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "channels" / "sent").mkdir(parents=True)
            (root / "channels" / "sent" / "letter.md").write_text("x", encoding="utf8")
            items = {"a": {"id": "a", "state": "accomplished", "author": "gemini",
                           "title": "a pitch", "paths": ["channels/outbound/letter.md"]}}
            records = ipd.drift(items, root)
            self.assertEqual(len(records), 1)
            self.assertFalse(records[0]["needs_review"])
            missing = records[0]["missing"][0]
            self.assertEqual(missing["verdict"], "moved")
            self.assertEqual(missing["found_at"], str(Path("channels/sent/letter.md")))

    def test_genuinely_absent_file_needs_a_reviewer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            items = {"a": {"id": "a", "state": "accomplished",
                           "paths": ["docs/never-written.md"]}}
            records = ipd.drift(items, root)
            self.assertTrue(records[0]["needs_review"])
            self.assertEqual(records[0]["missing"][0]["verdict"], "absent")

    def test_one_absent_path_makes_the_item_a_review_even_if_another_moved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "new").mkdir()
            (root / "new" / "kept.svg").write_text("x", encoding="utf8")
            items = {"a": {"id": "a", "state": "accomplished",
                           "paths": ["old/kept.svg", "old/lost.svg"]}}
            records = ipd.drift(items, root)
            self.assertTrue(records[0]["needs_review"])
            verdicts = {m["path"]: m["verdict"] for m in records[0]["missing"]}
            self.assertEqual(verdicts, {"old/kept.svg": "moved", "old/lost.svg": "absent"})

    def test_waiting_items_are_not_counted(self) -> None:
        """Only closed work carries a citation anyone is judging."""
        with tempfile.TemporaryDirectory() as tmp:
            items = {"a": {"id": "a", "state": "waiting", "paths": ["gone.md"]}}
            self.assertEqual(ipd.drift(items, Path(tmp)), [])

    def test_git_directory_is_not_searched_for_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git" / "objects").mkdir(parents=True)
            (root / ".git" / "objects" / "letter.md").write_text("x", encoding="utf8")
            items = {"a": {"id": "a", "state": "accomplished", "paths": ["outbox/letter.md"]}}
            records = ipd.drift(items, root)
            self.assertEqual(records[0]["missing"][0]["verdict"], "absent")


class CliTests(unittest.TestCase):
    def _run(self, root: Path, *extra: str) -> tuple[int, str]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = ipd.main(["--repo", str(root), "--ledger", str(root / "items.jsonl"), *extra])
        return code, buf.getvalue()

    def test_json_output_carries_the_split(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sent").mkdir()
            (root / "sent" / "moved.md").write_text("x", encoding="utf8")
            write_ledger(root / "items.jsonl", [
                {"id": "a", "state": "accomplished", "paths": ["outbox/moved.md"]},
                {"id": "b", "state": "accomplished", "paths": ["nowhere/lost.md"]},
            ])
            code, out = self._run(root, "--json")
            self.assertEqual(code, 0)
            data = json.loads(out)
            self.assertEqual(data["counts"]["moved"], 1)
            self.assertEqual(data["counts"]["absent"], 1)
            self.assertEqual(data["counts"]["items_needing_review"], 1)

    def test_it_is_not_a_gate_unless_asked(self) -> None:
        """A stale citation must not block a landing — that would reward editing strings over work."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_ledger(root / "items.jsonl", [
                {"id": "a", "state": "accomplished", "paths": ["nowhere/lost.md"]},
            ])
            self.assertEqual(self._run(root)[0], 0)
            self.assertEqual(self._run(root, "--fail-on-absent")[0], 1)

    def test_clean_tree_exits_zero_even_with_fail_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "here.md").write_text("x", encoding="utf8")
            write_ledger(root / "items.jsonl", [
                {"id": "a", "state": "accomplished", "paths": ["here.md"]},
            ])
            self.assertEqual(self._run(root, "--fail-on-absent")[0], 0)


if __name__ == "__main__":
    unittest.main()
