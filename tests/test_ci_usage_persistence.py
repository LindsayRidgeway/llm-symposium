#!/usr/bin/env python3
# Owner: Desi
"""Does a usage row survive the runner? Proved offline, with the workflows' own commands.

Why this exists (2026-10-20). The to-do item was "persist the CI usage rows": add a commit-and-
push step for `channels/usage/ci-usage.jsonl`, because `--summary` still prints *no CI usage
recorded yet*. Measured before writing anything: **all three workflows that record a row already
stage, commit and push the ledger** (`autonomous-goose-tarik.yml` `git add channels/usage/`,
`channel-poll.yml` `git add channels/ …`, `symposium.yml` `git add .`). The ledger is empty for a
different reason — nothing that spends is on a clock — and the item was about to become the
fourth rebuild of work that already exists.

So the useful thing to build is not another commit step. It is a proof that the existing ones
work, executable without a GitHub runner, plus a check (`scripts/ci_spend_audit.py`, `keeps`
column) that fails the day an edit drops one.

What this cannot prove: that GitHub Actions itself runs the step. That needs a dispatched run and
is named as the remaining gap in the report, not claimed here. What it does prove: given a row in
the working tree and the exact `git add` pathspec the workflow file contains, the file is staged,
commits, and pushes into a clone of the same shape as `origin/main`.

Run: python3 tests/test_ci_usage_persistence.py    (exit 0 pass, 1 fail)
"""

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from channels import usage            # noqa: E402
from scripts import ci_spend_audit as audit  # noqa: E402

LEDGER = audit.LEDGER_PATH
RECORDERS = ("autonomous-goose-tarik.yml", "channel-poll.yml", "symposium.yml")


def git(cwd, *args, check=True):
    result = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)
    if check and result.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result


def add_pathspecs(workflow_text: str) -> list:
    """The `git add` arguments in a workflow that would take the ledger with them.

    Read from the file, not hard-coded, so the test applies the command the workflow actually
    runs. A pathspec that only looks like a parent (`channels/usage-notes/`) is excluded by
    `_covers_ledger` and is the subject of its own test in `test_ci_spend_audit.py`.
    """
    found = []
    for raw in workflow_text.splitlines():
        line = audit._strip_comment(raw).strip()
        match = re.search(r"\bgit\s+add\b(.*)", line)
        if not match:
            continue
        rest = re.split(r"&&|\|\||[;|]", match.group(1))[0]
        for arg in rest.split():
            arg = arg.strip("'\"")
            if arg != "--" and audit._covers_ledger(arg) and arg not in found:
                found.append(arg)
    return found


class ARepoLikeTheRunners(unittest.TestCase):
    """A throwaway clone with one real row written by the ledger's own API."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "repo"
        self.root.mkdir()
        git(self.root, "-c", "init.defaultBranch=main", "init", "-q")
        git(self.root, "config", "user.name", "LLM Symposium Bot")
        git(self.root, "config", "user.email", "bot@llm-symposium.local")
        (self.root / "channels" / "usage").mkdir(parents=True)
        self.ledger = self.root / LEDGER
        # The same call the workflows make, with an explicit path so it cannot touch the real
        # ledger (channels/usage.py refuses implicit writes from a test process; naming the
        # path is how a test says "I mean this file").
        usage.record_api_call("openai", "gpt-6-astra",
                              {"usage": {"prompt_tokens": 1200, "completion_tokens": 340}},
                              source="symposium-runner", path=self.ledger)

    def tearDown(self):
        self._tmp.cleanup()

    def staged_names(self):
        return git(self.root, "diff", "--staged", "--name-only").stdout.split()


class TheRowItself(ARepoLikeTheRunners):
    def test_the_call_wrote_a_real_row(self):
        rows = usage.load_rows(self.ledger)
        self.assertEqual(len(rows), 1, "record_api_call must append exactly one row")
        row = rows[0]
        self.assertEqual(row["source"], "symposium-runner")
        self.assertEqual(row["provider"], "openai")
        self.assertEqual(row["input"], 1200)
        self.assertEqual(row["output"], 340)

    def test_the_summary_reads_it_back(self):
        text = usage.summarize(usage.load_rows(self.ledger))
        self.assertIn("gpt-6-astra", text)
        self.assertNotIn("no CI usage recorded yet", text)


class EveryRecorderStagesTheLedger(ARepoLikeTheRunners):
    """The defect this guards: a workflow that writes the row and stages something else.

    `test-and-report.yml` stages `tests/last-verification.txt`; `quiet-check.yml` stages its own
    alert directories. Neither records usage, and both are correct. But a copy-paste of either
    staging line into a recorder would leave the ledger behind and the audit silent — until now.
    """

    def test_each_recorder_stages_this_file(self):
        for name in RECORDERS:
            with self.subTest(workflow=name):
                pathspecs = add_pathspecs(audit._read(audit.WORKFLOWS / name))
                self.assertTrue(pathspecs, f"{name} records usage and stages nothing")
                staged = set()
                for pathspec in pathspecs:
                    # `-A` is a flag, not a pathspec: it is handed to git as it is written.
                    git(self.root, "add", pathspec)
                    staged |= set(self.staged_names())
                self.assertIn(LEDGER, staged,
                              f"{name} stages {pathspecs} and the ledger is not among them")

    def test_a_pathspec_that_misses_the_ledger_is_visible(self):
        """The negative control: without it, the test above would pass on any `git add`."""
        decoy = self.root / "tests" / "last-verification.txt"
        decoy.parent.mkdir(parents=True, exist_ok=True)
        decoy.write_text("a real file, staged by a real workflow that records no usage\n")
        git(self.root, "add", "tests/last-verification.txt")
        staged = self.staged_names()
        self.assertIn("tests/last-verification.txt", staged)
        self.assertNotIn(LEDGER, staged)


class TheRowSurvives(ARepoLikeTheRunners):
    """Staging → commit → push, into a bare origin, then read it back from the remote."""

    def _bare_origin(self):
        origin = Path(self._tmp.name) / "origin.git"
        subprocess.run(["git", "init", "--bare", "-q", "-b", "main", str(origin)],
                       capture_output=True)
        git(self.root, "remote", "add", "origin", str(origin))
        return origin

    def test_commit_and_push_puts_the_row_in_origin(self):
        origin = self._bare_origin()
        (self.root / "README.md").write_text("seed\n")
        git(self.root, "add", "--", "README.md")
        git(self.root, "commit", "-q", "-m", "seed")
        git(self.root, "push", "-q", "origin", "HEAD:refs/heads/main")

        pathspecs = add_pathspecs(audit._read(audit.WORKFLOWS / "symposium.yml"))
        for pathspec in pathspecs:
            git(self.root, "add", pathspec)
        self.assertIn(LEDGER, self.staged_names())
        self.assertIn(LEDGER, git(self.root, "diff", "--cached", "--name-only").stdout.split())
        git(self.root, "commit", "-q", "-m", "record(usage): one row")
        git(self.root, "push", "-q", "origin", "HEAD:refs/heads/main")

        shown = git(origin, "show", f"main:{LEDGER}").stdout.strip()
        rows = [json.loads(line) for line in shown.splitlines() if line.strip()]
        self.assertEqual(len(rows), 1, "the row that reached origin is not the row that was written")
        self.assertEqual(rows[0]["input"], 1200)

    def test_an_uncommitted_row_does_not_reach_origin(self):
        """The failure the `keeps` column exists to catch: written, never committed, gone."""
        origin = self._bare_origin()
        (self.root / "README.md").write_text("seed\n")
        git(self.root, "add", "--", "README.md")
        git(self.root, "commit", "-q", "-m", "seed")
        git(self.root, "push", "-q", "origin", "HEAD:refs/heads/main")
        listed = git(origin, "ls-tree", "-r", "--name-only", "main").stdout
        self.assertNotIn(LEDGER, listed.split())
        self.assertTrue(self.ledger.exists(), "the row was written locally and thrown away")


if __name__ == "__main__":
    unittest.main(verbosity=2)
