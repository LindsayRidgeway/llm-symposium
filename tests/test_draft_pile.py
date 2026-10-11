#!/usr/bin/env python3
"""The draft-pile reader must classify each branch's change against the base, not guess.

Written 2026-10-11 (Dmitri) for `scripts/draft_pile.py`, the closer the review gate never
had. The tool exists because a `drafts/tick-*` branch keeps content that never reached
`main`, and every later wake that reads "these paths never reached main" has to guess
whether the content is new. `draft_pile.py` answers that from git instead of by hand —
which means its classification *is* the answer, and a wrong classification is worse than
no tool: it would delete a branch that held real work, or rescue one that was already on
`main` and re-land a duplicate (the loop the tool was written to end).

So every state the tool can emit is pinned here on a throwaway repository built branch by
branch, plus the verdict function and both renderers, plus one CLI smoke test against the
real checkout (which asserts the tool runs, not what it finds).

Offline. No third-party dependencies. `draft_pile.git()` shells out to `git` in the
process working directory, so the git-backed cases `chdir` into the throwaway repo.

Run: python3 tests/test_draft_pile.py
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import draft_pile as dp  # noqa: E402


def run(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)


def commit_all(repo: Path, message: str) -> str:
    run(repo, "add", "-A")
    run(repo, "commit", "-q", "-m", message)
    return run(repo, "rev-parse", "HEAD").stdout.strip()


def build_fixture(repo: Path):
    """A base branch and one branch per classification state.

    Seed (C0) holds: edited.txt, edited2.txt, moved.txt, del_target.txt. Branches fork
    from C0; `main` then advances so that some branch edits are already on the base
    (LANDED/ADDED_LANDED), some collide (MOVED_ON/ADD_CONFLICT), and some the base never
    took (NEW/EDIT_UNLANDED).

    Returns the C0 commit id.
    """
    run(repo, "init", "-q")
    run(repo, "config", "user.email", "t@example.invalid")
    run(repo, "config", "user.name", "Test")
    run(repo, "symbolic-ref", "HEAD", "refs/heads/main")  # portable across git versions
    (repo / "edited.txt").write_text("v1\n")
    (repo / "edited2.txt").write_text("v1\n")
    (repo / "moved.txt").write_text("v1\n")
    (repo / "del_target.txt").write_text("x\n")
    c0 = commit_all(repo, "seed")

    def branch(name):
        run(repo, "checkout", "-q", "-b", name, c0)

    # A branch adds a path the base never has.
    branch("b/new")
    (repo / "newfile.txt").write_text("brand new\n")
    commit_all(repo, "add new")

    # A branch edits a path the base still holds at its pre-edit version.
    branch("b/edit")
    (repo / "edited2.txt").write_text("v2-branch\n")
    commit_all(repo, "edit")

    # A branch deletes a path.
    branch("b/delete")
    run(repo, "rm", "-q", "del_target.txt")
    commit_all(repo, "delete")

    # A branch edits a path the base later moves on independently.
    branch("b/moved")
    (repo / "moved.txt").write_text("branch-v2\n")
    commit_all(repo, "moved")

    # A branch adds a path the base later adds identically (already landed).
    branch("b/addedlanded")
    (repo / "added_landed.txt").write_text("same\n")
    commit_all(repo, "added landed")

    # A branch adds a path the base later adds differently (conflict).
    branch("b/conflict")
    (repo / "conflict.txt").write_text("branch\n")
    commit_all(repo, "conflict")

    # A branch edits a path to exactly what the base later edits it to (landed).
    branch("b/landed")
    (repo / "edited.txt").write_text("v2\n")
    commit_all(repo, "landed")

    # Back on main: the base advances, creating every "base has its own version" case.
    run(repo, "checkout", "-q", "main")
    (repo / "conflict.txt").write_text("main\n")
    (repo / "added_landed.txt").write_text("same\n")
    (repo / "moved.txt").write_text("main-v2\n")
    (repo / "edited.txt").write_text("v2\n")
    commit_all(repo, "advance base")

    # A branch identical to the base tip, and an orphan with no merge-base at all.
    run(repo, "branch", "b/noop", "main")
    run(repo, "checkout", "-q", "--orphan", "b/orphan")
    (repo / "unrelated.txt").write_text("orphan\n")
    commit_all(repo, "orphan root")
    run(repo, "checkout", "-q", "main")
    return c0


class DraftPileGitTest(unittest.TestCase):
    """Classification, built from real git history, one state per branch."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tmp = Path(cls._tmp.name)
        cls.repo = cls.tmp / "repo"
        cls.repo.mkdir()
        cls._cwd = os.getcwd()
        build_fixture(cls.repo)
        os.chdir(cls.repo)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls._cwd)
        cls._tmp.cleanup()

    def setUp(self):
        self.reports, self.skipped = dp.build_pile("b/*", "main", "")
        self.by_branch = {r["branch"]: r for r in self.reports}

    def state(self, branch, path):
        return self.by_branch[branch]["paths"].get(path)

    def test_new_when_base_lacks_the_path(self):
        self.assertEqual(self.state("b/new", "newfile.txt"), "NEW")

    def test_edit_unlanded_when_base_never_took_the_edit(self):
        self.assertEqual(self.state("b/edit", "edited2.txt"), "EDIT_UNLANDED")

    def test_deleted_when_the_branch_removes_a_path(self):
        self.assertEqual(self.state("b/delete", "del_target.txt"), "DELETED")

    def test_moved_on_when_base_holds_its_own_version(self):
        self.assertEqual(self.state("b/moved", "moved.txt"), "MOVED_ON")

    def test_added_landed_when_base_already_has_identical_content(self):
        self.assertEqual(self.state("b/addedlanded", "added_landed.txt"), "ADDED_LANDED")

    def test_add_conflict_when_base_has_unrelated_content(self):
        self.assertEqual(self.state("b/conflict", "conflict.txt"), "ADD_CONFLICT")

    def test_landed_when_branch_edit_is_already_on_base(self):
        self.assertEqual(self.state("b/landed", "edited.txt"), "LANDED")

    def test_orphan_branch_is_uncomparable_not_classified(self):
        self.assertIn("b/orphan", self.skipped)
        self.assertNotIn("b/orphan", self.by_branch)

    def test_ignored_globs_are_not_counted_as_changes(self):
        reports, _ = dp.build_pile("b/new", "main", "new*")
        ignore_report = reports[0]
        self.assertEqual(ignore_report["paths"], {})
        self.assertEqual(ignore_report["ignored"], {"newfile.txt": "NEW"})

    def test_verdict_per_branch(self):
        self.assertEqual(dp._verdict(self.by_branch["b/new"]["paths"]), "HOLDS_WORK")
        self.assertEqual(dp._verdict(self.by_branch["b/edit"]["paths"]), "HOLDS_WORK")
        self.assertEqual(dp._verdict(self.by_branch["b/moved"]["paths"]), "REVIEW")
        self.assertEqual(dp._verdict(self.by_branch["b/conflict"]["paths"]), "REVIEW")
        self.assertEqual(dp._verdict(self.by_branch["b/landed"]["paths"]), "SAFE_TO_DELETE")
        self.assertEqual(dp._verdict(self.by_branch["b/delete"]["paths"]), "SAFE_TO_DELETE")
        self.assertEqual(dp._verdict(self.by_branch["b/noop"]["paths"]), "SAFE_TO_DELETE")


class DraftPileVerdictTest(unittest.TestCase):
    """The verdict must never call a branch deletable while it holds new content."""

    def test_unlanded_state_always_reads_as_work(self):
        for state in dp.UNLANDED_STATES:
            self.assertEqual(dp._verdict({"p": state}), "HOLDS_WORK", state)

    def test_landed_states_read_as_safe_to_delete(self):
        for state in dp.LANDED_STATES:
            self.assertEqual(dp._verdict({"p": state}), "SAFE_TO_DELETE", state)

    def test_ambiguous_state_is_review_not_delete(self):
        for state in ("MOVED_ON", "ADD_CONFLICT"):
            self.assertEqual(dp._verdict({"p": state}), "REVIEW", state)

    def test_empty_change_set_is_safe_to_delete(self):
        self.assertEqual(dp._verdict({}), "SAFE_TO_DELETE")


class DraftPileRenderTest(unittest.TestCase):
    """Both renderers must carry the unlanded paths and a delete command, not a count only."""

    def setUp(self):
        # The real ref layout: fetched drafts live at origin/drafts/tick-*. The renderers
        # strip the leading remote segment, so the delete command must name the branch
        # relative to origin (`--delete drafts/tick-b`), not a fragment of it.
        self.reports = [
            {"branch": "origin/drafts/tick-a", "merge_base": "0" * 40,
             "paths": {"docs/x.html": "NEW"}, "ignored": {}},
            {"branch": "origin/drafts/tick-b", "merge_base": "1" * 40,
             "paths": {"a.py": "LANDED"}, "ignored": {"to-do-lists/x.md": "NEW"}},
        ]
        self.skipped = ["origin/drafts/tick-orphan"]

    def test_text_render_names_the_unlanded_path(self):
        out = dp.render_text(self.reports, self.skipped)
        self.assertIn("docs/x.html", out)
        self.assertIn("origin/drafts/tick-orphan", out)
        self.assertIn("git push origin --delete drafts/tick-b", out)

    def test_markdown_render_names_the_unlanded_path(self):
        out = dp.render_markdown(self.reports, self.skipped, "main", "*/drafts/tick-*")
        self.assertIn("| `docs/x.html` | drafts/tick-a |", out)
        self.assertIn("git push origin --delete drafts/tick-b", out)
        self.assertIn("DO NOT EDIT", out)

    def test_text_render_counts_match_the_reports(self):
        out = dp.render_text(self.reports, self.skipped)
        self.assertIn("branches: 2 compared, 1 uncomparable", out)
        self.assertIn("HOLDS_WORK (base demonstrably lacks the content): 1", out)


class DraftPileCliTest(unittest.TestCase):
    """The CLI wiring: pattern, --json and --md, and a run against the real checkout."""

    def test_cli_writes_json_and_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            repo = tmp / "repo"
            repo.mkdir()
            build_fixture(repo)
            cwd = os.getcwd()
            os.chdir(repo)
            try:
                jout = tmp / "pile.json"
                mout = tmp / "pile.md"
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    rc = dp.main(["--pattern", "b/*", "--json", str(jout), "--md", str(mout)])
            finally:
                os.chdir(cwd)
            self.assertEqual(rc, 0)
            payload = json.loads(jout.read_text())
            self.assertEqual(payload["base"], "main")
            verdicts = {b["branch"]: b["verdict"] for b in payload["branches"]}
            self.assertEqual(verdicts["b/new"], "HOLDS_WORK")
            self.assertEqual(verdicts["b/landed"], "SAFE_TO_DELETE")
            self.assertIn("b/orphan", payload["uncomparable"])
            self.assertIn("Content the base branch does not have", mout.read_text())

    def test_cli_runs_in_the_real_checkout(self):
        """A smoke test only: the tool runs and exits 0, whatever this checkout holds."""
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "draft_pile.py")],
            cwd=str(ROOT), capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("branches:", proc.stdout)


if __name__ == "__main__":
    unittest.main()
