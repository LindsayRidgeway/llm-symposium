"""The recovery tool copies, refuses, and never silently overwrites.

Written 2026-11-19 (Desi) with `scripts/recover_run_paths.py`. The four states are the whole contract:
`recovered`, `identical`, `diverged`, `missing`. The one that matters is `diverged` — an append-only
ledger or a to-do list that moved on since the run was refused must NOT be replaced by the older
copy, because that is how the commons loses somebody else's work while calling it a recovery.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import recover_run_paths as rec  # noqa: E402


class RecoverRunPathsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="recover-test-")
        self.run_dir = os.path.join(self.tmp, "20260101T000000Z-abcdef12")
        self.src_root = os.path.join(self.run_dir, "repo")
        self.dest = os.path.join(self.tmp, "worktree")
        os.makedirs(self.src_root)
        os.makedirs(self.dest)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, root, rel, text):
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        return path

    def _read(self, root, rel):
        with open(os.path.join(root, rel), encoding="utf-8") as fh:
            return fh.read()

    def test_a_path_absent_at_the_destination_is_copied(self):
        self._write(self.src_root, "channels/reports/x.md", "the verdict\n")
        rows = rec.recover(self.run_dir, ["channels/reports/x.md"], self.dest)
        self.assertEqual(rows[0][1], "recovered")
        self.assertEqual(self._read(self.dest, "channels/reports/x.md"), "the verdict\n")

    def test_a_byte_identical_path_is_left_alone_and_re_running_is_safe(self):
        self._write(self.src_root, "a.md", "same\n")
        self._write(self.dest, "a.md", "same\n")
        rows = rec.recover(self.run_dir, ["a.md"], self.dest)
        self.assertEqual(rows[0][1], "identical")
        self.assertEqual(self._read(self.dest, "a.md"), "same\n")

    def test_a_diverged_path_is_refused_and_the_destination_keeps_its_bytes(self):
        # The ledger case: the run's copy is a prefix, the destination has since gained rows.
        self._write(self.src_root, "channels/items.jsonl", '{"id": 1}\n')
        self._write(self.dest, "channels/items.jsonl", '{"id": 1}\n{"id": 2}\n')
        rows = rec.recover(self.run_dir, ["channels/items.jsonl"], self.dest)
        self.assertEqual(rows[0][1], "diverged")
        self.assertIn("not overwritten", rows[0][2])
        self.assertEqual(self._read(self.dest, "channels/items.jsonl"), '{"id": 1}\n{"id": 2}\n')

    def test_force_overwrites_a_diverged_path_and_says_so(self):
        self._write(self.src_root, "t.md", "older\n")
        self._write(self.dest, "t.md", "newer\n")
        rows = rec.recover(self.run_dir, ["t.md"], self.dest, force=True)
        self.assertEqual(rows[0][1], "recovered")
        self.assertIn("--force", rows[0][2])
        self.assertEqual(self._read(self.dest, "t.md"), "older\n")

    def test_a_claimed_path_the_run_never_wrote_reports_missing(self):
        rows = rec.recover(self.run_dir, ["channels/reports/never-written.md"], self.dest)
        self.assertEqual(rows[0][1], "missing")
        self.assertFalse(os.path.exists(os.path.join(self.dest, "channels/reports/never-written.md")))

    def test_dry_run_writes_nothing(self):
        self._write(self.src_root, "b.md", "bytes\n")
        rows = rec.recover(self.run_dir, ["b.md"], self.dest, dry_run=True)
        self.assertEqual(rows[0][1], "recovered")
        self.assertFalse(os.path.exists(os.path.join(self.dest, "b.md")))

    def test_a_traversal_path_is_refused_rather_than_followed(self):
        self._write(self.src_root, "c.md", "x\n")
        for bad in ("../outside.md", "/etc/passwd", ""):
            rows = rec.recover(self.run_dir, [bad], self.dest)
            self.assertEqual(rows[0][1], "absent-from-claim", bad)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "outside.md")))

    def test_paths_default_to_the_runs_own_claim(self):
        self._write(self.src_root, "d.md", "claimed\n")
        with open(os.path.join(self.run_dir, "result.json"), "w", encoding="utf-8") as fh:
            json.dump({"changed_paths": ["d.md", "e.md"]}, fh)
        self.assertEqual(rec.claimed_paths(self.run_dir), ["d.md", "e.md"])
        rows = rec.recover(self.run_dir, rec.claimed_paths(self.run_dir), self.dest)
        self.assertEqual([r[1] for r in rows], ["recovered", "missing"])

    def test_a_run_id_is_found_under_runs_root(self):
        self.assertEqual(rec.resolve_run(os.path.basename(self.run_dir), runs_root=self.tmp),
                         self.run_dir)
        self.assertEqual(rec.resolve_run(self.run_dir), os.path.abspath(self.run_dir))
        with self.assertRaises(LookupError):
            rec.resolve_run("20260101T000000Z-00000000", runs_root=self.tmp)

    def test_exit_code_is_non_zero_when_anything_is_refused_or_missing(self):
        self._write(self.src_root, "f.md", "hi\n")
        self._write(self.dest, "f.md", "different\n")
        code = rec.main(["--run", self.run_dir, "--paths", "f.md", "nope.md", "--dest", self.dest])
        self.assertEqual(code, 1)
        code = rec.main(["--run", self.run_dir, "--paths", "f.md", "--dest", self.dest, "--force"])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
