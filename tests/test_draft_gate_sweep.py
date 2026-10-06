#!/usr/bin/env python3
"""The review gate's closer must actually classify a branch, and must never close a live one.

Written 2026-10-06 (Dmitri) with `scripts/draft_gate_sweep.py`. The tool exists because the gate
has never had a closer: 99 of 101 `drafts/tick-*` branches were open on 2026-10-05, and wakes kept
recomputing work that sat on one of them. The failure this test guards is the expensive one — a
branch holding real, unlanded work being called EMPTY or LANDED and deleted. A false "already
landed" is the same loss the four re-written vulvodynia screens already cost, but silent.

So the cases are chosen to separate the two verdicts that look alike and are not:

  * a branch whose file equals main's blob  -> LANDED  (closable)
  * a branch whose file differs from main's -> UNSETTLED (must be kept)
  * a branch that changed only its to-do list -> EMPTY  (closable)
  * a branch already merged into main        -> EMPTY  (closable)

Stdlib only; requires `git` on PATH. Each test builds a throwaway repo under a temp dir. Offline.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import draft_gate_sweep as gate  # noqa: E402

SCRIPT = ROOT / "scripts" / "draft_gate_sweep.py"


def _git(repo: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)


def _write(repo: Path, rel: str, text: str):
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def build_repo(tmp: Path) -> Path:
    """A throwaway repo shaped like the real one: `main` plus four draft branches."""
    _git(tmp, "init", "-q", "-b", "main")
    _git(tmp, "config", "user.email", "test@local")
    _git(tmp, "config", "user.name", "Gate Test")
    _write(tmp, "works/base.md", "base\n")
    _write(tmp, "to-do-lists/dmitri.md", "# todo\n")
    _git(tmp, "add", ".")
    _git(tmp, "commit", "-qm", "base")

    # 1. UNSETTLED — adds a file main does not have, and touches its to-do list (ignored).
    _git(tmp, "checkout", "-q", "-b", "drafts/tick-20260916T000000Z-aaaa111")
    _write(tmp, "works/story.md", "unlanded story\n")
    _write(tmp, "to-do-lists/dmitri.md", "# todo\n- did a thing\n")
    _git(tmp, "add", ".")
    _git(tmp, "commit", "-qm", "story")

    # 2. LANDED — its file is byte-identical to the copy that is already on main.
    _git(tmp, "checkout", "-q", "main")
    _git(tmp, "checkout", "-q", "-b", "drafts/tick-20260917T000000Z-bbbb222")
    _write(tmp, "works/landed.md", "same on both\n")
    _git(tmp, "add", ".")
    _git(tmp, "commit", "-qm", "landed file")
    _git(tmp, "checkout", "-q", "main")
    _write(tmp, "works/landed.md", "same on both\n")
    _git(tmp, "add", ".")
    _git(tmp, "commit", "-qm", "land same content to main")

    # 3. EMPTY — changed nothing but its to-do list.
    _git(tmp, "checkout", "-q", "-b", "drafts/tick-20260918T000000Z-cccc333")
    _write(tmp, "to-do-lists/dmitri.md", "# todo\n- only bookkeeping\n")
    _git(tmp, "add", ".")
    _git(tmp, "commit", "-qm", "todo only")

    # 4. EMPTY — already merged into main, so it carries no change relative to it.
    _git(tmp, "checkout", "-q", "main")
    _git(tmp, "checkout", "-q", "-b", "drafts/tick-20260919T000000Z-dddd444")
    _write(tmp, "works/merged.md", "merged\n")
    _git(tmp, "add", ".")
    _git(tmp, "commit", "-qm", "merged work")
    _git(tmp, "checkout", "-q", "main")
    _git(tmp, "merge", "-q", "--no-ff", "-m", "merge draft", "drafts/tick-20260919T000000Z-dddd444")

    _git(tmp, "checkout", "-q", "main")
    return tmp


class DraftGateSweep(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.repo = build_repo(Path(cls._tmp.name))

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def ref(self, stamp: str) -> str:
        p = _git(self.repo, "for-each-ref", "--format=%(refname)",
                 f"refs/heads/drafts/tick-{stamp}*")
        refs = [r for r in p.stdout.splitlines() if r.strip()]
        self.assertEqual(len(refs), 1, f"expected one branch for {stamp}: {refs}")
        return refs[0]

    def test_branch_date_is_read_from_the_name(self):
        self.assertEqual(gate.branch_date("drafts/tick-20260916T000000Z-aaaa111"), "2026-09-16")
        self.assertIsNone(gate.branch_date("drafts/no-date-here"))

    def test_noise_is_the_wakes_own_bookkeeping(self):
        self.assertTrue(gate.is_noise("to-do-lists/dmitri.md"))
        self.assertFalse(gate.is_noise("works/story.md"))
        # A path that merely shares a prefix string is not bookkeeping.
        self.assertFalse(gate.is_noise("to-do-lists-archive/x.md"))

    def test_unsettled_branch_keeps_its_unlanded_file(self):
        r = gate.classify_branch(self.repo, "main", self.ref("20260916"))
        self.assertEqual(r["status"], "UNSETTLED")
        self.assertIn("works/story.md", r["unlanded"])
        self.assertEqual(r["landed"], [])
        # The to-do change is noise, and noise alone never makes a branch unsettled.
        self.assertIn("to-do-lists/dmitri.md", r["noise"])

    def test_landed_branch_is_recognised_by_blob_equality(self):
        r = gate.classify_branch(self.repo, "main", self.ref("20260917"))
        self.assertEqual(r["status"], "LANDED")
        self.assertIn("works/landed.md", r["landed"])
        self.assertEqual(r["unlanded"], [])

    def test_todo_only_branch_is_empty(self):
        r = gate.classify_branch(self.repo, "main", self.ref("20260918"))
        self.assertEqual(r["status"], "EMPTY")

    def test_merged_branch_is_empty(self):
        r = gate.classify_branch(self.repo, "main", self.ref("20260919"))
        self.assertEqual(r["status"], "EMPTY")

    def test_only_empty_and_landed_are_closable(self):
        refs = gate.list_draft_branches(self.repo, gate.LOCAL_REF_GLOB)
        self.assertEqual(len(refs), 4)
        records = [gate.classify_branch(self.repo, "main", r) for r in refs]
        closable = gate.closable(records)
        statuses = sorted(r["status"] for r in closable)
        self.assertEqual(statuses, ["EMPTY", "EMPTY", "LANDED"])
        # The branch holding unlanded work is never in the set.
        self.assertNotIn("works/story.md",
                         [p for r in closable for p in r["unlanded"]])

    def test_cli_json_reports_the_counts(self):
        p = subprocess.run(
            [sys.executable, str(SCRIPT), "--repo", str(self.repo),
             "--no-fetch", "--main", "main", "--json"],
            capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        data = json.loads(p.stdout)
        self.assertEqual(data["counts"], {"EMPTY": 2, "LANDED": 1, "UNSETTLED": 1})
        unsettled = [b for b in data["branches"] if b["status"] == "UNSETTLED"]
        self.assertEqual(len(unsettled), 1)
        self.assertIn("works/story.md", unsettled[0]["unlanded"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
