#!/usr/bin/env python3
"""The landing-conflict report must name, per file, what a discarded patch actually costs.

Written 2026-10-14 (Dmitri) with `scripts/landing_conflict_report.py`. The tool exists because
the lander's single word `"land": "conflict"` hides two things at once: *which* file's hunk
stopped applying, and *how much of the run was lost with it*. `git apply` is atomic, so a run
that changed four paths and touched one another wake also touched delivers nothing — even
though some of its files pass the lander's own check on their own.

So the thing worth pinning is the arithmetic: one conflicting file must not be reported as if
every file conflicted, and the files that *would* land must be named, because those are the
ones salvageable by hand. Offline: every case is built in a throwaway git repository under a
temp directory, and the real checkout is only read by one CLI smoke test.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import landing_conflict_report as lcr  # noqa: E402


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)


class Repo:
    """A throwaway work tree with one commit, so a patch has something to apply to."""

    def __init__(self, tmp: Path, name="work"):
        self.path = tmp / name
        self.path.mkdir(parents=True, exist_ok=True)
        git(self.path, "init", "-q")
        git(self.path, "config", "user.email", "t@example.invalid")
        git(self.path, "config", "user.name", "T")

    def write(self, rel, text):
        p = self.path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def commit(self, message="c"):
        git(self.path, "add", "-A")
        git(self.path, "commit", "-q", "-m", message)

    def run_dir(self, name, patch_text):
        d = self.path.parent / "runs" / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "changes.patch").write_text(patch_text, encoding="utf-8")
        return d


def patch_for(cwd, *paths):
    """The diff of the given paths against HEAD, in the lander's own format."""
    return git(cwd, "diff", "HEAD", "--", *paths).stdout


class SplitPatchTest(unittest.TestCase):
    def test_names_every_file_in_order(self):
        p = ("diff --git a/one.txt b/one.txt\n"
             "--- a/one.txt\n+++ b/one.txt\n@@ -1 +1 @@\n-a\n+b\n"
             "diff --git a/two.txt b/two.txt\n"
             "--- a/two.txt\n+++ b/two.txt\n@@ -1 +1 @@\n-c\n+d\n")
        self.assertEqual([path for path, _ in lcr.split_patch(p)], ["one.txt", "two.txt"])

    def test_a_new_file_is_named_by_its_new_name(self):
        p = ("diff --git a/new.md b/new.md\nnew file mode 100644\n"
             "--- /dev/null\n+++ b/new.md\n@@ -0,0 +1 @@\n+hello\n")
        chunks = lcr.split_patch(p)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0][0], "new.md")

    def test_a_path_with_no_dash_headers_falls_back_to_the_diff_line(self):
        p = "diff --git a/odd.txt b/odd.txt\nindex 1..2 100644\n"
        self.assertEqual(lcr.split_patch(p)[0][0], "odd.txt")


class AssessTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="lcr-"))
        self.repo = Repo(self.tmp)
        self.repo.write("keeps.txt", "one\ntwo\nthree\n")
        self.repo.write("moves.txt", "alpha\nbeta\n")
        self.repo.commit()

    def test_a_patch_that_applies_whole_is_not_a_loss(self):
        self.repo.write("keeps.txt", "one\ntwo\nthree\nfour\n")
        d = self.repo.run_dir("run-a", patch_for(self.repo.path, "keeps.txt"))
        self.repo.commit("reset")
        r = lcr.assess(self.repo.path, d / "changes.patch")
        self.assertEqual(r["whole"], "applicable")
        self.assertEqual(r["lost_with_the_rest"], [])
        self.assertEqual(r["files"], [{"path": "keeps.txt", "verdict": "applicable"}])

    def test_one_stale_hunk_makes_the_whole_patch_discarded_and_names_what_dies_with_it(self):
        # The run changed two paths: one new file, and one file that another wake has since moved.
        self.repo.write("moves.txt", "alpha\nbeta\nNEW\n")
        self.repo.write("report.md", "a new report\n")
        stale = patch_for(self.repo.path, "moves.txt", "report.md")
        self.repo.commit("the run's work is in the tree for a moment")
        # Another wake lands on moves.txt while this run is parked: the hunk's context is gone.
        self.repo.write("moves.txt", "alpha\nbeta\nNEW\nSOMEBODY ELSE\n")
        self.repo.commit("another wake")
        d = self.repo.run_dir("run-b", stale)
        r = lcr.assess(self.repo.path, d / "changes.patch")
        self.assertEqual(r["whole"], "discarded")
        verdicts = {f["path"]: f["verdict"] for f in r["files"]}
        self.assertEqual(verdicts["moves.txt"], "conflict")
        self.assertEqual(verdicts["report.md"], "already_landed")
        self.assertIn("report.md", r["lost_with_the_rest"])
        self.assertNotIn("moves.txt", r["lost_with_the_rest"])

    def test_work_already_in_the_tree_reads_backwards(self):
        self.repo.write("keeps.txt", "one\ntwo\nthree\nfour\n")
        landing = patch_for(self.repo.path, "keeps.txt")
        self.repo.commit("landed")
        d = self.repo.run_dir("run-c", landing)
        r = lcr.assess(self.repo.path, d / "changes.patch")
        self.assertEqual(r["whole"], "already_landed")
        self.assertEqual(r["files"][0]["verdict"], "already_landed")

    def test_no_patch_on_disk_is_not_a_crash(self):
        d = self.tmp / "runs" / "run-d"
        d.mkdir(parents=True)
        (d / "changes.patch").write_text("", encoding="utf-8")
        r = lcr.assess(self.repo.path, d / "changes.patch")
        self.assertEqual(r["whole"], "empty")
        self.assertEqual(r["files"], [])

    def test_a_new_file_the_run_wrote_but_never_landed_is_applicable(self):
        self.repo.write("only-new.md", "text\n")
        self.repo.commit("for the patch to see it")
        d = self.repo.run_dir("run-e", patch_for(self.repo.path, "only-new.md"))
        git(self.repo.path, "rm", "-q", "--cached", "only-new.md")
        (self.repo.path / "only-new.md").unlink()
        self.repo.commit("the run was parked before this file landed")
        r = lcr.assess(self.repo.path, d / "changes.patch")
        self.assertEqual(r["files"][0]["verdict"], "applicable")


class CliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="lcr-cli-"))
        self.repo = Repo(self.tmp)
        self.repo.write("a.txt", "x\n")
        self.repo.commit()

    def test_json_is_machine_readable_and_exit_says_whether_anything_is_lost(self):
        self.repo.write("a.txt", "x\ny\n")
        d = self.repo.run_dir("run-cli", patch_for(self.repo.path, "a.txt"))
        self.repo.commit("landed it")
        out = subprocess.run([sys.executable, str(ROOT / "scripts" / "landing_conflict_report.py"),
                              "--repo", str(self.repo.path), "--json", str(d)],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        rows = json.loads(out.stdout)
        self.assertEqual(rows[0]["whole"], "already_landed")
        self.assertEqual(rows[0]["run"], "run-cli")

    def test_a_discarded_patch_exits_nonzero_and_says_so(self):
        self.repo.write("a.txt", "x\nrun-line\n")
        d = self.repo.run_dir("run-cli2", patch_for(self.repo.path, "a.txt"))
        self.repo.commit("parked")
        self.repo.write("a.txt", "x\nrun-line\nsomebody-else\n")
        self.repo.commit("moved on")
        out = subprocess.run([sys.executable, str(ROOT / "scripts" / "landing_conflict_report.py"),
                              "--repo", str(self.repo.path), str(d)],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 1)
        self.assertIn("DISCARDED", out.stdout)
        self.assertIn("1 file(s)", out.stdout)

    def test_it_reads_real_parked_runs_without_writing_anything(self):
        """The real corpus: the tool must survive the run directories as they are on disk."""
        runs = Path.home() / "LLM" / "dmitri-bot" / "tick-state" / "runs"
        if not runs.is_dir():
            self.skipTest("no local run corpus on this machine")
        before = git(ROOT, "status", "--porcelain").stdout
        out = subprocess.run([sys.executable, str(ROOT / "scripts" / "landing_conflict_report.py"),
                              "--runs-root", str(runs), "--json"],
                             capture_output=True, text=True)
        self.assertIn(out.returncode, (0, 1), out.stderr)
        rows = json.loads(out.stdout)
        self.assertTrue(rows)
        for r in rows:
            self.assertIn(r["whole"], ("applicable", "already_landed", "discarded", "empty"))
        self.assertEqual(git(ROOT, "status", "--porcelain").stdout, before,
                         "the report must not write into the checkout it measures")


if __name__ == "__main__":
    unittest.main(verbosity=2)
