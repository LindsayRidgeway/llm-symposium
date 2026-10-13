#!/usr/bin/env python3
"""The review gate's closer must decide correctly, offline, on a repository it can see.

Written 2026-10-09 (Dmitri) with `scripts/draft_gate_closer.py`. The gate's defect (2026-09-23) is
that a wake cannot tell a genuinely stranded artifact from one already on `main`, so wakes redo
landed work — the vulvodynia screen was written and recovered four times. The closer's whole value is
the decision it makes; a closer that mistakes a duplicate for unlanded work re-opens the loop it was
built to close, and one that mistakes unlanded work for a duplicate *deletes* it. So every class is
pinned here against a throwaway git repository built for the purpose.

The cases, each one a real failure mode:
  * byte-identical content under a DIFFERENT path on the base is REDUNDANT, not stranded (the
    mass-merge trap);
  * a file whose bytes are on no path is STRANDED (the lost-work case);
  * routine to-do-list churn does not make a branch look like it delivered anything;
  * a deletion is not unlanded work;
  * `--apply-delete` removes only the redundant branch and never a stranded one;
  * `--check` is a usable gate.

Offline. Uses the system `git` on a temp repo; writes nothing to this repository.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "draft_gate_closer.py"

spec = importlib.util.spec_from_file_location("draft_gate_closer", SCRIPT)
closer = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = closer  # dataclass needs its module in sys.modules on py3.9
spec.loader.exec_module(closer)


def git(repo, *args):
    proc = subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.email=test@example.invalid",
            "-c",
            "user.name=test",
            "-c",
            "commit.gpgsign=false",
            *args,
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {proc.stderr}")
    return proc.stdout


def write(repo: Path, rel: str, text: str):
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


class DraftGateCloserTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="draft-gate-"))
        self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)
        repo = self.dir / "repo"
        repo.mkdir()
        git(repo, "init", "-q")
        git(repo, "symbolic-ref", "HEAD", "refs/heads/main")
        # Base: one document whose bytes will be re-committed verbatim on a redundant branch.
        write(repo, "docs/existing.md", "shared body\n")
        write(repo, "to-do-lists/amigo.md", "queue v1\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "base")
        self.repo = repo

        # REDUNDANT: its one real file is byte-identical to an existing base file; the rest is churn.
        git(repo, "checkout", "-q", "-b", "drafts/tick-redundant")
        write(repo, "docs/dup.md", "shared body\n")
        write(repo, "to-do-lists/amigo.md", "queue v2\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "dup")

        # STRANDED: one genuinely new file, plus a redundant one — it must still read as STRANDED.
        git(repo, "checkout", "-q", "main")
        git(repo, "checkout", "-q", "-b", "drafts/tick-stranded")
        write(repo, "research/new-thing.md", "brand new evidence\n")
        write(repo, "docs/dup2.md", "shared body\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "new")

        # EMPTY: identical to base.
        git(repo, "checkout", "-q", "main")
        git(repo, "checkout", "-q", "-b", "drafts/tick-empty")
        git(repo, "commit", "-q", "--allow-empty", "-m", "nothing")

        # DELETION: removes a base file; a deletion is not unlanded work.
        git(repo, "checkout", "-q", "main")
        git(repo, "checkout", "-q", "-b", "drafts/tick-deletion")
        os.remove(repo / "docs" / "existing.md")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "remove")
        git(repo, "checkout", "-q", "main")

    def plan(self, *extra):
        return closer.build_plan(str(self.repo), "main", "drafts/tick-*", closer.DEFAULT_IGNORE)

    def by_ref(self, plan):
        return {b["ref"]: b for b in plan["branches"]}

    def test_classification_of_each_failure_mode(self):
        plan = self.plan()
        b = self.by_ref(plan)
        self.assertEqual(plan["refs_found"], 4)
        self.assertEqual(b["drafts/tick-redundant"]["classification"], closer.REDUNDANT)
        self.assertEqual(b["drafts/tick-stranded"]["classification"], closer.STRANDED)
        self.assertEqual(b["drafts/tick-empty"]["classification"], closer.EMPTY)
        self.assertEqual(b["drafts/tick-deletion"]["classification"], closer.EMPTY)

    def test_duplicate_content_under_new_path_is_not_stranded(self):
        b = self.by_ref(self.plan())["drafts/tick-redundant"]
        self.assertIn("docs/dup.md", b["redundant"])
        self.assertEqual(b["stranded"], [])
        # the to-do churn is recorded as ignored, not as delivered work
        self.assertIn("to-do-lists/amigo.md", b["ignored"])

    def test_stranded_branch_names_the_unlanded_file(self):
        b = self.by_ref(self.plan())["drafts/tick-stranded"]
        paths = [s["path"] for s in b["stranded"]]
        self.assertEqual(paths, ["research/new-thing.md"])
        self.assertTrue(len(b["stranded"][0]["blob"]) >= 40)

    def test_counts_and_json_shape(self):
        plan = self.plan()
        self.assertEqual(plan["counts"], {closer.REDUNDANT: 1, closer.STRANDED: 1, closer.EMPTY: 2})
        json.dumps(plan)  # must be serialisable
        self.assertEqual(plan["base"], "main")

    def test_apply_delete_removes_only_redundant(self):
        plan = self.plan()
        deleted = closer.apply_deletes(str(self.repo), plan)
        self.assertEqual(deleted, ["drafts/tick-redundant"])
        refs = git(self.repo, "for-each-ref", "--format=%(refname:short)", "refs/heads").split()
        self.assertNotIn("drafts/tick-redundant", refs)
        self.assertIn("drafts/tick-stranded", refs)  # unlanded work is never deleted

    def test_check_exit_code_is_a_gate(self):
        self.assertEqual(closer.main(["--repo", str(self.repo), "--check", "--json"]), 1)
        # A repo with no draft refs is clean, and says so rather than crashing.
        clean = self.dir / "clean"
        clean.mkdir()
        git(clean, "init", "-q")
        git(clean, "symbolic-ref", "HEAD", "refs/heads/main")
        write(clean, "README.md", "nothing here\n")
        git(clean, "add", "-A")
        git(clean, "commit", "-q", "-m", "base")
        self.assertEqual(closer.main(["--repo", str(clean), "--check"]), 0)

    def test_real_repository_smoke(self):
        # The real checkout is a wake tree with no remote, but the tool must run there too and report
        # (not crash on) whatever it finds. Exit is 0 (nothing) or 1 (stranded); JSON must parse.
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--repo", str(ROOT), "--json"],
            capture_output=True,
            text=True,
        )
        self.assertIn(proc.returncode, (0, 1), proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertIn("counts", payload)
        self.assertIn("branches", payload)


if __name__ == "__main__":
    unittest.main(verbosity=2)
