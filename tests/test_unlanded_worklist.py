#!/usr/bin/env python3
"""Tests for `scripts/unlanded_worklist.py`.

Why these exist. The tool answers a question the reject queue said no wake could answer — "did this
run's claimed paths reach main?" — with no git remote. That claim is load-bearing (an item has sat on
the queue since 2026-09-28 partly because of it), so the answer has to be pinned by a test rather
than asserted in a docstring: a verification tool that is itself wrong is worse than none, because it
manufactures a worklist nobody can trust.

Offline. Writes only to a temp directory; touches no bot tree and no repository file.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import unlanded_worklist as uw  # noqa: E402


def make_run(root: Path, amigo: str, run_id: str, changed=None, report=""):
    """A minimal run record: `<root>/<amigo>-bot/tick-state/runs/<run_id>/`."""
    d = root / f"{amigo}-bot" / uw.RUNS_REL / run_id
    d.mkdir(parents=True)
    if changed is not None:
        (d / "result.json").write_text(json.dumps({"run_id": run_id, "changed_paths": changed}),
                                       encoding="utf-8")
    if report:
        (d / "report.txt").write_text(report, encoding="utf-8")
    return d


class ClaimedPaths(unittest.TestCase):
    def test_union_of_result_json_and_land_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            d = make_run(tmp, "desi", "20261008T000000Z-aaaaaaaa",
                         changed=["a.txt", "b.txt"],
                         report="LAND: c.txt, d.txt\n")
            self.assertEqual(uw.claimed_paths(d), ["a.txt", "b.txt", "c.txt", "d.txt"])

    def test_duplicates_dropped_and_placeholders_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            d = make_run(tmp, "desi", "20261008T000000Z-aaaaaaaa",
                         changed=["a.txt", "a.txt"],
                         report="LAND: a.txt, (pending), `b.txt`\n")
            self.assertEqual(uw.claimed_paths(d), ["a.txt", "b.txt"])

    def test_a_report_land_line_is_read_case_insensitively(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            d = make_run(tmp, "desi", "20261008T000000Z-aaaaaaaa",
                         report="land: x/y.md\n")
            self.assertEqual(uw.claimed_paths(d), ["x/y.md"])

    def test_space_separated_paths_and_prose_are_handled(self):
        """The real-file defect: a LAND line that is space-separated, or carries a parenthetical.

        Splitting on commas alone collected a whole sentence as one path and inflated the absence
        count. This pins the tokeniser that fixed it.
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            d = make_run(tmp, "desi", "20261008T000000Z-aaaaaaaa",
                         report="LAND: research/a.md research/b.json to-do-lists/desi.md\n"
                                "LAND: channels/risks.md (R-006 marked Done)\n"
                                "LAND: will follow\n")
            self.assertEqual(uw.claimed_paths(d),
                             ["research/a.md", "research/b.json", "to-do-lists/desi.md",
                              "channels/risks.md"])

    def test_a_bare_word_is_not_mistaken_for_a_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            d = make_run(tmp, "desi", "20261008T000000Z-aaaaaaaa",
                         report="LAND: landed fine and pushed\n")
            self.assertEqual(uw.claimed_paths(d), [])

    def test_result_json_only_and_report_only_both_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            a = make_run(tmp, "desi", "20261008T000000Z-aaaaaaaa", changed=["a.txt"])
            b = make_run(tmp, "desi", "20261008T010000Z-bbbbbbbb", report="LAND: b.txt\n")
            self.assertEqual(uw.claimed_paths(a), ["a.txt"])
            self.assertEqual(uw.claimed_paths(b), ["b.txt"])

    def test_a_malformed_result_json_is_not_fatal(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            d = make_run(tmp, "desi", "20261008T000000Z-aaaaaaaa", report="LAND: a.txt\n")
            (d / "result.json").write_text("{ not json", encoding="utf-8")
            self.assertEqual(uw.claimed_paths(d), ["a.txt"])


class Classify(unittest.TestCase):
    def test_split_against_the_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            (repo / "sub").mkdir(parents=True)
            (repo / "a.txt").write_text("x", encoding="utf-8")
            (repo / "sub" / "b.txt").write_text("x", encoding="utf-8")
            present, absent = uw.classify(["a.txt", "sub/b.txt", "ghost.txt"], repo)
            self.assertEqual(present, ["a.txt", "sub/b.txt"])
            self.assertEqual(absent, ["ghost.txt"])

    def test_a_directory_counts_as_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            (repo / "scripts").mkdir(parents=True)
            present, absent = uw.classify(["scripts"], repo)
            self.assertEqual((present, absent), (["scripts"], []))


class IterRuns(unittest.TestCase):
    def test_only_run_id_directories_are_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_run(root, "desi", "20261008T000000Z-aaaaaaaa", changed=["a.txt"])
            (root / "desi-bot" / uw.RUNS_REL / "not-a-run").mkdir()
            got = list(uw.iter_runs(root, "desi"))
            self.assertEqual([d.name for _, d in got], ["20261008T000000Z-aaaaaaaa"])

    def test_a_missing_bot_tree_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(list(uw.iter_runs(Path(tmp), "dmitri")), [])

    def test_runs_are_ordered_by_id_within_a_bot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_run(root, "desi", "20261008T020000Z-aaaaaaaa", changed=["a"])
            make_run(root, "desi", "20261008T010000Z-bbbbbbbb", changed=["b"])
            names = [d.name for _, d in uw.iter_runs(root, "desi")]
            self.assertEqual(names, sorted(names))


class Worklist(unittest.TestCase):
    def test_a_record_less_run_is_not_reported_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            repo = tmp / "repo"
            repo.mkdir()
            make_run(tmp / "root", "desi", "20261008T000000Z-aaaaaaaa",
                     changed=["a.txt"], report="LAND: a.txt\n")
            empty = make_run(tmp / "root", "desi", "20261008T010000Z-bbbbbbbb")
            rows = {r["run"]: r for r in uw.worklist(root=tmp / "root", repo=repo)}
            self.assertEqual(rows["20261008T000000Z-aaaaaaaa"]["absent"], ["a.txt"])
            self.assertEqual(empty.name, "20261008T010000Z-bbbbbbbb")
            self.assertEqual(rows["20261008T010000Z-bbbbbbbb"]["claimed"], [])

    def test_the_row_carries_amigo_and_both_buckets(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            repo = tmp / "repo"
            (repo / "landed").mkdir(parents=True)
            (repo / "landed" / "f.md").write_text("x", encoding="utf-8")
            make_run(tmp / "root", "gemini", "20261008T000000Z-aaaaaaaa",
                     changed=["landed/f.md", "stranded.md"])
            rows = uw.worklist(root=tmp / "root", repo=repo, amigo="gemini")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["amigo"], "gemini")
            self.assertEqual(rows[0]["present"], ["landed/f.md"])
            self.assertEqual(rows[0]["absent"], ["stranded.md"])


class Cli(unittest.TestCase):
    def test_selftest_passes_as_a_subprocess(self):
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "unlanded_worklist.py"),
                               "--selftest"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("all checks passed", proc.stdout)

    def test_json_mode_over_the_real_tree_is_well_formed(self):
        """Runs against the real bot trees (read-only) and checks only that the output parses."""
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "unlanded_worklist.py"),
                               "--json"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        data = json.loads(proc.stdout)
        self.assertIn("verified_against", data)
        self.assertIn("runs", data)
        for row in data["runs"]:
            self.assertEqual(sorted(row), ["absent", "amigo", "claimed", "present", "run"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
