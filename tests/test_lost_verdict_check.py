#!/usr/bin/env python3
"""The lost-verdict check's own cases — a synthetic machine, so the claims are checkable without one.

Why these exist (2026-11-10, Desi). `scripts/lost_verdict_check.py` reports on the real run directories
under ~/LLM, which no test can assert about: the number of lost verdicts is a fact about this machine
on this day, and pinning it would make the test fail every time a wake lands. So these cases build a
throwaway bot tree and a throwaway checkout, each holding exactly one fact, and assert the four states
are told apart. The defect the tool exists to catch — a mirror the run's report names, on no branch
anywhere — is one of them, and it is the case that failed silently for eleven days.

Run: python3 tests/test_lost_verdict_check.py
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lost_verdict_check import (  # noqa: E402
    main,
    mirror_item_id,
    new_files_in_patch,
    recover,
    scan,
    verdict_paths_in,
)

MIRROR = "channels/ledger-verdicts/20261110T011607Z-20261030T194152Z-48920431.json"
MIRROR_TEXT = '{\n  "id": "20261030T194152Z-48920431",\n  "reason": "read"\n}\n'
NEW_FILE_PATCH = (
    "diff --git a/" + MIRROR + " b/" + MIRROR + "\n"
    "new file mode 100644\n"
    "index 00000000..2e19b8b8\n"
    "--- /dev/null\n"
    "+++ b/" + MIRROR + "\n"
    "@@ -0,0 +1,4 @@\n"
    '+{\n'
    '+  "id": "20261030T194152Z-48920431",\n'
    '+  "reason": "read"\n'
    "+}\n"
)


def make_machine(root: Path, report: str, patch: str | None, amigo: str = "gemini",
                 run: str = "20261110T011453Z-1fb8ebdb") -> Path:
    bots = root / "LLM"
    run_dir = bots / f"{amigo}-bot" / "tick-state" / "runs" / run
    run_dir.mkdir(parents=True)
    (run_dir / "report.txt").write_text(report, encoding="utf-8")
    if patch is not None:
        (run_dir / "changes.patch").write_text(patch, encoding="utf-8")
    repo = root / "repo"
    (repo / "channels" / "ledger-verdicts").mkdir(parents=True)
    return bots


class TestPatchParsing(unittest.TestCase):
    def test_new_file_content_is_the_plus_lines_and_the_newline_returns(self):
        got = new_files_in_patch(NEW_FILE_PATCH)
        self.assertEqual(got[MIRROR], MIRROR_TEXT)

    def test_a_modified_file_is_not_returned_as_a_creation(self):
        patch = (
            "diff --git a/channels/items.jsonl b/channels/items.jsonl\n"
            "--- a/channels/items.jsonl\n"
            "+++ b/channels/items.jsonl\n"
            "@@ -1 +1 @@\n"
            "-old\n"
            "+new\n"
        )
        self.assertEqual(new_files_in_patch(patch), {})

    def test_two_new_files_in_one_patch_are_both_read_and_not_confused(self):
        second = MIRROR.replace("48920431", "aaaaaaaa")
        patch = NEW_FILE_PATCH + (
            "diff --git a/" + second + " b/" + second + "\n"
            "new file mode 100644\n"
            "--- /dev/null\n"
            "+++ b/" + second + "\n"
            "@@ -0,0 +1 @@\n"
            '+{"id": "other"}\n'
        )
        got = new_files_in_patch(patch)
        self.assertEqual(len(got), 2)
        self.assertIn("other", got[second])


class TestPathExtraction(unittest.TestCase):
    def test_paths_are_found_in_prose_and_in_a_land_line_and_not_duplicated(self):
        text = ("done. LAND: channels/items.jsonl " + MIRROR + " to-do-lists/x.md\n"
                "and again " + MIRROR + " in the prose, with a comma, after it.\n")
        self.assertEqual(verdict_paths_in(text), [MIRROR])

    def test_a_truncated_path_is_not_reported_as_a_claim(self):
        # Reports are cut off mid-sentence; half a path is not a claim that a file exists.
        self.assertEqual(verdict_paths_in("LAND: channels/ledger-verdicts/20261110T01"), [])

    def test_item_id_is_the_middle_stamp_not_the_run_stamp(self):
        self.assertEqual(mirror_item_id(MIRROR), "20261030T194152Z-48920431")


class TestTheFourStates(unittest.TestCase):
    def test_recoverable_when_the_diff_still_holds_the_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bots = make_machine(root, "LAND: " + MIRROR + "\n", NEW_FILE_PATCH)
            rows = scan(bots, root / "repo")
            self.assertEqual([r["state"] for r in rows], ["RECOVERABLE"])
            written, superseded = recover(rows, root / "repo")
            self.assertEqual(written, [MIRROR])
            self.assertEqual(superseded, [])
            self.assertEqual((root / "repo" / MIRROR).read_text(encoding="utf-8"), MIRROR_TEXT)

    def test_lost_when_the_diff_is_gone_too(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bots = make_machine(root, "LAND: " + MIRROR + "\n", None)
            rows = scan(bots, root / "repo")
            self.assertEqual([r["state"] for r in rows], ["LOST"])
            self.assertEqual(recover(rows, root / "repo")[0], [])

    def test_on_main_when_the_mirror_is_in_the_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bots = make_machine(root, "LAND: " + MIRROR + "\n", None)
            target = root / "repo" / MIRROR
            target.write_text(MIRROR_TEXT, encoding="utf-8")
            self.assertEqual([r["state"] for r in scan(bots, root / "repo")], ["ON MAIN"])

    def test_patched_other_when_the_same_item_landed_under_a_later_stamp(self):
        # The exact case that made the queue pay twice: the id is read, but this path is not there.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bots = make_machine(root, "LAND: " + MIRROR + "\n", NEW_FILE_PATCH)
            landed = root / "repo" / "channels" / "ledger-verdicts" / (
                "20261110T141522Z-20261030T194152Z-48920431.json")
            landed.write_text(MIRROR_TEXT, encoding="utf-8")
            rows = scan(bots, root / "repo")
            self.assertEqual([r["state"] for r in rows], ["PATCHED-OTHER"])
            self.assertIn("20261110T141522Z", rows[0]["on_main_as"])

    def test_two_mirrors_for_one_item_write_one_and_name_the_other(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bots = make_machine(root, "LAND: " + MIRROR + "\n", NEW_FILE_PATCH)
            older = MIRROR.replace("20261110T011607Z", "20261108T011347Z")
            run2 = bots / "gemini-bot" / "tick-state" / "runs" / "20261108T011148Z-a2096655"
            run2.mkdir(parents=True)
            (run2 / "report.txt").write_text("LAND: " + older + "\n", encoding="utf-8")
            (run2 / "changes.patch").write_text(NEW_FILE_PATCH.replace(MIRROR, older),
                                                encoding="utf-8")
            rows = scan(bots, root / "repo")
            self.assertEqual(len(rows), 2)
            written, superseded = recover(rows, root / "repo")
            self.assertEqual(written, [MIRROR])            # the later stamp
            self.assertEqual(superseded, [older])
            self.assertFalse((root / "repo" / older).exists())

    def test_a_run_that_names_no_mirror_is_not_a_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bots = make_machine(root, "LAND: channels/items.jsonl\n", None)
            self.assertEqual(scan(bots, root / "repo"), [])


class TestCommandLine(unittest.TestCase):
    def test_strict_exits_one_only_when_something_is_lost(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bots = make_machine(root, "LAND: " + MIRROR + "\n", NEW_FILE_PATCH)
            repo = root / "repo"
            self.assertEqual(main(["--bots-root", str(bots), "--repo", str(repo), "--strict"]), 0)
            (bots / "gemini-bot" / "tick-state" / "runs" / "20261110T011453Z-1fb8ebdb"
             / "changes.patch").unlink()
            self.assertEqual(main(["--bots-root", str(bots), "--repo", str(repo), "--strict"]), 1)
            self.assertEqual(main(["--bots-root", str(bots), "--repo", str(repo)]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
