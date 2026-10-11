#!/usr/bin/env python3
"""The draft-pile triage must separate unlanded work from work already on main.

Written 2026-10-11 (Dmitri) with `scripts/draft_pile_triage.py`. The pile exists because
the review gate has no closer; this tool is the read-only half of one, and it is only
worth having if it never calls finished work "new" and never calls already-landed work
"work". So the classification is what is pinned here:

  1. a branch whose changed content is byte-identical on main reads `already-landed`;
  2. a branch with content main does not have reads `carries-work`, with the paths;
  3. a branch that only touched a to-do list or a generated index reads `noise-only`;
  4. a branch with no diff at all reads `identical`;
  5. the exit code is 1 when any branch carries work and 0 when none does.

Offline. Every case is built in a throwaway git repository under a temp directory; the
real checkout is only touched by the CLI smoke test, which asserts the tool runs rather
than what it finds.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import draft_pile_triage as dpt  # noqa: E402


def run(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)


def commit(repo, msg):
    run(repo, "add", "-A")
    run(repo, "commit", "-q", "-m", msg)


def make_repo(tmp: Path) -> Path:
    repo = tmp / "repo"
    repo.mkdir()
    run(repo, "init", "-q", "-b", "main")
    run(repo, "config", "user.email", "t@example.invalid")
    run(repo, "config", "user.name", "Test")
    (repo / "app.py").write_text("print('base')\n")
    (repo / "to-do-lists").mkdir(parents=True)
    (repo / "to-do-lists" / "dmitri.md").write_text("# to-do\n")
    (repo / "channels").mkdir(parents=True, exist_ok=True)
    (repo / "channels" / "agenda.md").write_text("index\n")
    commit(repo, "seed")
    return repo


def branch(repo, name):
    run(repo, "checkout", "-q", "-b", name, "main")


def checkout(repo, name):
    run(repo, "checkout", "-q", name)


class DraftPileTriageTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.repo = make_repo(self.tmp)

    def tearDown(self):
        self._tmp.cleanup()

    def record(self, short):
        recs = dpt.scan(self.repo, "drafts/tick-*", "main")
        for r in recs:
            if r["short"] == short:
                return r
        self.fail("branch not found: %s (have %s)" % (short, [r["short"] for r in recs]))

    def test_no_diff_reads_identical(self):
        branch(self.repo, "drafts/tick-empty")
        checkout(self.repo, "main")
        self.assertEqual(self.record("drafts/tick-empty")["verdict"], dpt.VERDICT_IDENTICAL)

    def test_new_content_reads_carries_work_with_paths(self):
        branch(self.repo, "drafts/tick-work")
        (self.repo / "reddit_fetch.py").write_text("UA = 'python:llm-symposium'\n")
        commit(self.repo, "add fetch script")
        checkout(self.repo, "main")
        rec = self.record("drafts/tick-work")
        self.assertEqual(rec["verdict"], dpt.VERDICT_WORK)
        self.assertEqual([u["path"] for u in rec["unlanded"]], ["reddit_fetch.py"])
        self.assertEqual(rec["unlanded"][0]["kind"], "new")

    def test_content_already_on_main_reads_already_landed(self):
        # The branch adds a file; main receives the *same content* by a different route
        # (another wake landed it under the same path). The commits differ, the content
        # does not, so the path is not unlanded.
        branch(self.repo, "drafts/tick-dup")
        (self.repo / "guard.py").write_text("x = y if y is not None else 0\n")
        commit(self.repo, "add guard")
        checkout(self.repo, "main")
        (self.repo / "guard.py").write_text("x = y if y is not None else 0\n")
        commit(self.repo, "land same guard elsewhere")
        rec = self.record("drafts/tick-dup")
        self.assertEqual(rec["verdict"], dpt.VERDICT_LANDED)
        self.assertEqual(rec["unlanded"], [])
        self.assertEqual(rec["already_on_main"], ["guard.py"])

    def test_fully_merged_branch_reads_identical(self):
        # A branch main has been fast-forwarded onto has no diff at all: identical.
        branch(self.repo, "drafts/tick-ff")
        (self.repo / "landed.py").write_text("done\n")
        commit(self.repo, "add landed")
        checkout(self.repo, "main")
        run(self.repo, "merge", "-q", "--ff-only", "drafts/tick-ff")
        self.assertEqual(self.record("drafts/tick-ff")["verdict"], dpt.VERDICT_IDENTICAL)

    def test_modified_same_content_reads_already_landed(self):
        # The branch edits a file; main later receives the identical edit via another
        # route. The path is modified on the branch but the content already matches main.
        branch(self.repo, "drafts/tick-parallel")
        (self.repo / "app.py").write_text("print('shared')\n")
        commit(self.repo, "edit app")
        checkout(self.repo, "main")
        (self.repo / "app.py").write_text("print('shared')\n")
        commit(self.repo, "land same edit elsewhere")
        rec = self.record("drafts/tick-parallel")
        self.assertEqual(rec["verdict"], dpt.VERDICT_LANDED)

    def test_noise_only_reads_noise_only(self):
        branch(self.repo, "drafts/tick-todo")
        (self.repo / "to-do-lists" / "dmitri.md").write_text("# to-do\n- [x] done\n")
        (self.repo / "channels" / "agenda.md").write_text("index regenerated\n")
        commit(self.repo, "todo + index")
        checkout(self.repo, "main")
        rec = self.record("drafts/tick-todo")
        self.assertEqual(rec["verdict"], dpt.VERDICT_NOISE)
        self.assertEqual(rec["unlanded"], [])

    def test_noise_does_not_mask_real_work(self):
        branch(self.repo, "drafts/tick-mixed")
        (self.repo / "to-do-lists" / "dmitri.md").write_text("# to-do\n- [x] done\n")
        (self.repo / "probe_report.md").write_text("findings\n")
        commit(self.repo, "todo + report")
        checkout(self.repo, "main")
        rec = self.record("drafts/tick-mixed")
        self.assertEqual(rec["verdict"], dpt.VERDICT_WORK)
        self.assertEqual([u["path"] for u in rec["unlanded"]], ["probe_report.md"])

    def test_deleted_file_on_branch_is_unlanded(self):
        branch(self.repo, "drafts/tick-del")
        (self.repo / "app.py").unlink()
        commit(self.repo, "remove app")
        checkout(self.repo, "main")
        rec = self.record("drafts/tick-del")
        self.assertEqual(rec["verdict"], dpt.VERDICT_WORK)
        self.assertEqual(rec["unlanded"], [{"path": "app.py", "kind": "deleted"}])

    def test_select_ignores_non_matching_branches(self):
        branch(self.repo, "feature/other")
        (self.repo / "x.py").write_text("x\n")
        commit(self.repo, "x")
        checkout(self.repo, "main")
        self.assertEqual(dpt.list_branches(self.repo, "drafts/tick-*"), [])

    def test_summary_counts_are_exact(self):
        branch(self.repo, "drafts/tick-1")
        (self.repo / "w.py").write_text("w\n")
        commit(self.repo, "work")
        checkout(self.repo, "main")
        branch(self.repo, "drafts/tick-2")
        (self.repo / "to-do-lists" / "dmitri.md").write_text("# to-do\n- [x]\n")
        commit(self.repo, "todo")
        checkout(self.repo, "main")
        s = dpt.summarize(dpt.scan(self.repo, "drafts/tick-*", "main"))
        self.assertEqual(s["scanned"], 2)
        self.assertEqual(s["carries_work"], 1)
        self.assertEqual(s["noise_only"], 1)
        self.assertEqual(s["unlanded_paths"], 1)

    def test_cli_exit_code_one_when_work_zero_when_none(self):
        branch(self.repo, "drafts/tick-1")
        (self.repo / "w.py").write_text("w\n")
        commit(self.repo, "work")
        checkout(self.repo, "main")

        work = subprocess.run([sys.executable, str(ROOT / "scripts" / "draft_pile_triage.py"),
                               "--repo", str(self.repo), "--main", "main", "--json"],
                              capture_output=True, text=True)
        self.assertEqual(work.returncode, 1, work.stdout + work.stderr)
        payload = json.loads(work.stdout)
        self.assertEqual(payload["summary"]["carries_work"], 1)

    def test_cli_renders_and_can_close_a_noise_branch(self):
        branch(self.repo, "drafts/tick-todo")
        (self.repo / "to-do-lists" / "dmitri.md").write_text("# to-do\n- [x]\n")
        commit(self.repo, "todo")
        checkout(self.repo, "main")
        out = subprocess.run([sys.executable, str(ROOT / "scripts" / "draft_pile_triage.py"),
                              "--repo", str(self.repo), "--main", "main"],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn("the pile is closable", out.stdout)
        self.assertIn("drafts/tick-todo", out.stdout)

    def test_cli_on_a_non_repo_reports_rather_than_crashes(self):
        bare = self.tmp / "not-repo"
        bare.mkdir()
        out = subprocess.run([sys.executable, str(ROOT / "scripts" / "draft_pile_triage.py"),
                              "--repo", str(bare)], capture_output=True, text=True)
        self.assertEqual(out.returncode, 2)

    def test_cli_smoke_on_the_real_checkout(self):
        """Runs against this checkout. Asserts it completes, not what it finds."""
        out = subprocess.run([sys.executable, str(ROOT / "scripts" / "draft_pile_triage.py")],
                             capture_output=True, text=True)
        self.assertIn(out.returncode, (0, 1), out.stdout + out.stderr)
        self.assertIn("draft-pile triage", out.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
