#!/usr/bin/env python3
"""Tests for scripts/wake_reconnaissance_census.py.

The point of these tests is the number the census quotes: if `>` inside a printed
string counts as a write, or a streamed tool call is counted three times, the median
is wrong. So each test pins one of those.

Run: python3 tests/test_wake_reconnaissance_census.py
"""

import gzip
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import wake_reconnaissance_census as census  # noqa: E402


def _line(name, arguments, call_id):
    return json.dumps(
        {
            "type": "message",
            "message": {
                "id": call_id,
                "role": "assistant",
                "content": [
                    {"type": "toolRequest", "id": call_id,
                     "toolCall": {"status": "success",
                                  "value": {"name": name, "arguments": arguments}}}
                ],
            },
        }
    )


def _write_run(root: Path, run_id: str, lines, workspace_exists=True, packed=False,
               cut_off=True):
    run_dir = root / run_id
    run_dir.mkdir(parents=True)
    if workspace_exists:
        (run_dir / "repo").mkdir()
    (run_dir / "report.txt").write_text("a report\n", encoding="utf-8")
    payload = "\n".join(lines) + "\n"
    if packed:
        with gzip.open(run_dir / "worker.jsonl.gz", "wt", encoding="utf-8") as handle:
            handle.write(payload)
    else:
        (run_dir / "worker.jsonl").write_text(payload, encoding="utf-8")
    (run_dir / "result.json").write_text(
        json.dumps(
            {
                "workspace": str(run_dir / "repo"),
                "cut_off": cut_off,
                "status": "awaiting_review",
                "changed_paths": ["a.txt"],
            }
        ),
        encoding="utf-8",
    )
    return run_dir


class ShellDetectionTests(unittest.TestCase):
    def test_redirection_to_a_file_is_a_write(self):
        targets = census.shell_write_targets(
            "printf 'hello' > report.txt", Path("/run")
        )
        self.assertEqual([str(t) for t in targets], ["/run/report.txt"])

    def test_dev_null_is_not_a_write(self):
        self.assertEqual(
            census.shell_write_targets("python3 x.py 2>/dev/null", Path("/run")), []
        )
        self.assertEqual(
            census.shell_write_targets("ls 2>&1 | head", Path("/run")), []
        )

    def test_arrow_inside_quotes_is_not_a_write(self):
        self.assertEqual(
            census.shell_write_targets("echo 'a > b' && grep -n 'x>y' f.py", Path("/run")),
            [],
        )

    def test_leading_cd_is_used_to_resolve(self):
        command = "cd /checkout/repo && cat > notes.md <<'EOF'\nbody\nEOF"
        cwd = census.command_cwd(command, Path("/elsewhere"))
        self.assertEqual(str(cwd), "/checkout/repo")
        targets = census.shell_write_targets(command, cwd)
        self.assertEqual([str(t) for t in targets], ["/checkout/repo/notes.md"])

    def test_a_command_without_a_cd_runs_in_the_workspace(self):
        self.assertEqual(
            census.command_cwd("ls -la", Path("/workspace")), Path("/workspace")
        )

    def test_tee_and_cp_and_git_apply_count(self):
        for command in (
            "echo x | tee out.txt",
            "cp scripts/a.py tests/b.py",
            "git apply /tmp/x.patch",
        ):
            self.assertTrue(
                census.shell_write_targets(command, Path("/run")), command
            )


class ClassificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.run_dir = self.tmp / "20260101T000000Z-aaaa"
        self.run_dir.mkdir()
        self.workspace = self.run_dir / "repo"
        self.workspace.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_inside_checkout_is_repo(self):
        self.assertEqual(
            census.classify([self.workspace / "channels" / "x.md"], self.workspace), "repo"
        )

    def test_beside_checkout_is_state(self):
        self.assertEqual(
            census.classify([self.run_dir / "report.txt"], self.workspace), "state"
        )

    def test_tmp_is_elsewhere(self):
        self.assertEqual(census.classify([Path("/tmp/scratch/x.py")], self.workspace), "elsewhere")

    def test_repo_wins_when_a_command_writes_both(self):
        self.assertEqual(
            census.classify(
                [self.run_dir / "report.txt", self.workspace / "a.md"], self.workspace
            ),
            "repo",
        )


class CensusTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "runs"
        self.root.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_counts_actions_before_the_first_write_into_the_checkout(self):
        run_id = "20260101T000000Z-aaaa"
        run_dir = self.root / run_id
        repo = run_dir / "repo"
        lines = [
            json.dumps({"type": "session", "note": "banner"}),
            _line("shell", {"command": f"cd {run_dir} && printf 'x' > report.txt"}, "c1"),
            _line("shell", {"command": f"cd {repo} && cat a.md"}, "c2"),
            _line("shell", {"command": f"cd {repo} && git log --oneline -3"}, "c3"),
            _line("shell", {"command": f"cd {repo} && cat > notes.md"}, "c4"),
            _line("shell", {"command": f"cd {repo} && git status"}, "c5"),
        ]
        _write_run(self.root, run_id, lines)

        row = census.census_run(run_dir)
        self.assertEqual(row["actions"], 5)
        self.assertEqual(row["first_any_write"], 1)      # its own report
        self.assertEqual(row["first_repo_write"], 4)     # the first artefact
        self.assertEqual(row["recon_before_repo"], 3)
        self.assertTrue(row["cut_off"])
        self.assertEqual(row["changed_paths"], 1)

    def test_a_run_that_never_writes_into_the_checkout(self):
        run_id = "20260101T010000Z-bbbb"
        run_dir = self.root / run_id
        lines = [
            _line("shell", {"command": f"cd {run_dir} && printf 'x' > report.txt"}, "c1"),
            _line("shell", {"command": "grep -rn needle /somewhere"}, "c2"),
        ]
        _write_run(self.root, run_id, lines)
        row = census.census_run(run_dir)
        self.assertIsNone(row["first_repo_write"])
        self.assertIsNone(row["recon_before_repo"])

    def test_gzipped_transcript_is_read(self):
        run_id = "20260101T020000Z-cccc"
        run_dir = self.root / run_id
        lines = [
            _line("shell", {"command": f"cd {run_dir}/repo && cat > a.md"}, "c1"),
        ]
        _write_run(self.root, run_id, lines, packed=True)
        row = census.census_run(run_dir)
        self.assertEqual(row["first_repo_write"], 1)

    def test_streamed_duplicates_of_one_call_are_counted_once(self):
        run_id = "20260101T030000Z-dddd"
        run_dir = self.root / run_id
        full = f"cd {run_dir}/repo && cat > a.md"
        lines = [
            _line("shell", {"command": full}, "c1"),
            _line("shell", {"command": full}, "c1"),  # the stream repeated it
            _line("shell", {"command": full}, "c1"),
        ]
        _write_run(self.root, run_id, lines)
        self.assertEqual(census.census_run(run_dir)["actions"], 1)

    def test_the_write_tool_counts_with_an_absolute_path(self):
        run_id = "20260101T040000Z-eeee"
        run_dir = self.root / run_id
        lines = [
            _line("shell", {"command": "ls -la"}, "c1"),
            _line("write", {"path": str(run_dir / "repo" / "docs" / "a.md")}, "c2"),
        ]
        _write_run(self.root, run_id, lines)
        row = census.census_run(run_dir)
        self.assertEqual(row["first_repo_write"], 2)
        self.assertEqual(row["recon_before_repo"], 1)

    def test_summary_reports_the_median_and_the_cut_off_count(self):
        run_id = "20260101T050000Z-ffff"
        run_dir = self.root / run_id
        lines = [
            _line("shell", {"command": "ls"}, "c1"),
            _line("shell", {"command": "ls"}, "c2"),
            _line("shell", {"command": f"cd {run_dir}/repo && cat > a.md"}, "c3"),
        ]
        _write_run(self.root, run_id, lines)
        rows = census.census_runs(self.root)
        self.assertEqual(len(rows), 1)
        summary = census.summarize(rows)
        self.assertEqual(summary["runs_read"], 1)
        self.assertEqual(summary["runs_cut_off"], 1)
        self.assertEqual(summary["median_recon_before_repo"], 2)
        self.assertEqual(summary["runs_20_plus_actions_before_repo_write"], 0)
        self.assertIn("median", census.render(summary))

    def test_since_filter(self):
        for run_id in ("20260101T060000Z-aaaa", "20260202T060000Z-bbbb"):
            _write_run(
                self.root,
                run_id,
                [_line("shell", {"command": "ls"}, "c1")],
            )
        self.assertEqual(len(census.census_runs(self.root, since="20260202")), 1)

    def test_a_run_without_a_transcript_is_skipped(self):
        (self.root / "20260101T070000Z-none").mkdir()
        self.assertEqual(census.census_runs(self.root), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
