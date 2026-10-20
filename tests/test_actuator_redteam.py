#!/usr/bin/env python3
"""Red-team tests for the Symposium Actuator — RT-5, authorised-but-wrong patches.

Agenda item 15. RT-5 states the gap in one line: *no mechanism anywhere checks
the content of a change; gates authenticate the asker and nothing else.* This
file is the part of that gap the actuator owns, tested offline.

The actuator's self-modification guard protected exactly one path until
2026-10-20 — `actuator/apply.py` — while the thing that decides whether a patch
*passes* was a plain file in the tree the patch can edit:

  RT-5a  A patch that rewrites `tests/test_projection.py` to `assert True` and
         simultaneously breaks the invariant that suite exists to check is
         APPLIED, because the tampered suite is what runs. The guard guarded the
         engine, not the verdict.
  RT-5b  A patch that adds `.github/workflows/*.yml` is APPLIED, committed and
         pushed to main by `.github/workflows/actuator.yml` — and a push made
         with the push token *does* trigger workflows, so the added job then runs
         repo code with `SYMPOSIUM_PUSH_TOKEN` in its environment. That is a path
         from "may submit a patch" to "may run arbitrary code with the credential
         that writes main", which is precisely what the deadbolt is supposed to
         deny.

Both are now closed by two independent layers, and each layer is tested here
separately so that a regression in one is visible even if the other still holds:

  Layer 1  `PROTECTED_PATHS` / `PROTECTED_PREFIXES` in `actuator/apply.py`.
  Layer 2  `verify()` runs the suite from its **committed** (HEAD) copy, so a
           working-tree edit to the suite cannot grade the patch that edited it.

The tests never touch the live repository, never use a real credential, and
write nothing outside a throwaway temp directory (`agenda/15` rule 1).

Run:  python3 tests/test_actuator_redteam.py
Stdlib only; requires `git` on PATH.
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
APPLY_PY = REPO_ROOT / "actuator" / "apply.py"

MAIN_V1 = "VALUE = 1\n"
MAIN_V2 = "VALUE = 2\n"
SUITE_LINES = [
    "import os, sys",
    "sys.path.insert(0, os.getcwd())",
    "from main import VALUE",
    "assert VALUE == 2, VALUE",
]
SUITE = "\n".join(SUITE_LINES) + "\n"
PROBE = 'print("probe ok")\n'


def _git(repo: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)


def make_repo() -> Path:
    """A throwaway git repo shaped like the real one, with one base commit."""
    repo = Path(tempfile.mkdtemp(prefix="actuator-redteam-"))
    (repo / "main.py").write_text(MAIN_V1, encoding="utf-8")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_projection.py").write_text(SUITE, encoding="utf-8")
    (repo / "probes").mkdir()
    (repo / "probes" / "ticktick_recurrence_probe.py").write_text(PROBE, encoding="utf-8")
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".github" / "workflows" / "actuator.yml").write_text("name: Actuator\n", encoding="utf-8")
    for d in ("actuator/requests", "actuator/applied", "actuator/rejected"):
        (repo / d).mkdir(parents=True)
    shutil.copy(APPLY_PY, repo / "actuator" / "apply.py")
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@local")
    _git(repo, "config", "user.name", "Actuator Red Team")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")
    return repo


def run_actuator(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "actuator/apply.py"],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=300,
    )


def satisfy_suite(repo: Path) -> None:
    """Make the verify suite pass on the current tree, so that a rejection can be
    attributed to the guard rather than to an already-red suite.

    Without this, a guard test can pass for the wrong reason: the patch is
    refused because the *baseline* was failing, not because it was protected.
    """
    (repo / "main.py").write_text("VALUE = 2\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "satisfy suite")


def drop_request(repo: Path, name: str, body: str) -> None:
    (repo / "actuator" / "requests" / name).write_text(body, encoding="utf-8")


def patch_main(old: str, new: str) -> str:
    return (
        "diff --git a/main.py b/main.py\n"
        "--- a/main.py\n"
        "+++ b/main.py\n"
        "@@ -1 +1 @@\n"
        f"-{old}\n"
        f"+{new}\n"
    )


PATCH_REWRITE_SUITE = (
    "diff --git a/tests/test_projection.py b/tests/test_projection.py\n"
    "--- a/tests/test_projection.py\n"
    "+++ b/tests/test_projection.py\n"
    "@@ -4 +4 @@\n"
    "-assert VALUE == 2, VALUE\n"
    "+assert True\n"
)

PATCH_DELETE_SUITE = (
    "diff --git a/tests/test_projection.py b/tests/test_projection.py\n"
    "deleted file mode 100644\n"
    "--- a/tests/test_projection.py\n"
    "+++ /dev/null\n"
    "@@ -1,4 +0,0 @@\n"
    + "".join(f"-{line}\n" for line in SUITE_LINES)
)

PATCH_ADD_WORKFLOW = (
    "diff --git a/.github/workflows/rt5b.yml b/.github/workflows/rt5b.yml\n"
    "new file mode 100644\n"
    "--- /dev/null\n"
    "+++ b/.github/workflows/rt5b.yml\n"
    "@@ -0,0 +1,4 @@\n"
    "+name: rt5b\n"
    "+on: push\n"
    "+jobs:\n"
    "+  x: {runs-on: ubuntu-latest, steps: [{run: 'echo $SYMPOSIUM_PUSH_TOKEN'}]}\n"
)

PATCH_EDIT_EXISTING_WORKFLOW = (
    "diff --git a/.github/workflows/actuator.yml b/.github/workflows/actuator.yml\n"
    "--- a/.github/workflows/actuator.yml\n"
    "+++ b/.github/workflows/actuator.yml\n"
    "@@ -1 +1,2 @@\n"
    " name: Actuator\n"
    "+# tampered\n"
)


class RedTeamTest(unittest.TestCase):
    """RT-5a / RT-5b: the verdict, the CI surface, and the two layers closing them."""

    # --- Layer 1: the protected-path guard -----------------------------------

    def test_patch_cannot_rewrite_the_verify_suite(self):
        """RT-5a: a patch that neuters the suite *and* breaks the invariant is rejected."""
        repo = make_repo()
        satisfy_suite(repo)
        drop_request(repo, "rt5a.patch", PATCH_REWRITE_SUITE + patch_main("VALUE = 2", "VALUE = 3"))
        r = run_actuator(repo)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("self-modification", r.stdout)
        self.assertIn("tests/test_projection.py", r.stdout)
        self.assertEqual((repo / "main.py").read_text(encoding="utf-8"), MAIN_V2)
        self.assertTrue((repo / "actuator" / "rejected" / "rt5a.patch").exists())

    def test_patch_cannot_delete_the_verify_suite(self):
        """The guard reads both header paths, so deleting the suite is not a way round it."""
        repo = make_repo()
        satisfy_suite(repo)
        drop_request(repo, "rt5a-delete.patch", PATCH_DELETE_SUITE)
        r = run_actuator(repo)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("self-modification", r.stdout)
        self.assertTrue((repo / "tests" / "test_projection.py").exists())

    def test_patch_cannot_add_a_workflow(self):
        """RT-5b: a new workflow file is a new job with the push token in scope."""
        repo = make_repo()
        satisfy_suite(repo)
        drop_request(repo, "rt5b-new.patch", PATCH_ADD_WORKFLOW)
        r = run_actuator(repo)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("self-modification", r.stdout)
        self.assertIn(".github/workflows/", r.stdout)
        self.assertFalse((repo / ".github" / "workflows" / "rt5b.yml").exists())

    def test_patch_cannot_edit_an_existing_workflow(self):
        repo = make_repo()
        satisfy_suite(repo)
        drop_request(repo, "rt5b-edit.patch", PATCH_EDIT_EXISTING_WORKFLOW)
        r = run_actuator(repo)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("self-modification", r.stdout)
        self.assertEqual(
            (repo / ".github" / "workflows" / "actuator.yml").read_text(encoding="utf-8"),
            "name: Actuator\n",
        )

    # --- Layer 2: the verdict is read from HEAD, not from the patch ----------

    def test_verify_uses_the_committed_suite_not_the_working_copy(self):
        """A suite edited *outside* a patch still cannot grade that patch.

        This is the layer that holds if the guard is ever widened, refactored or
        bypassed: the working-tree copy is replaced with `assert True`, the patch
        touches only `main.py`, and verification must still fail because the HEAD
        copy of the suite is what runs.
        """
        repo = make_repo()
        satisfy_suite(repo)
        (repo / "tests" / "test_projection.py").write_text("assert True\n", encoding="utf-8")
        drop_request(repo, "rt5a-layer2.patch", patch_main("VALUE = 2", "VALUE = 3"))
        r = run_actuator(repo)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("REJECTED", r.stdout)
        self.assertIn("verification failed", r.stdout)
        self.assertEqual((repo / "main.py").read_text(encoding="utf-8"), MAIN_V2)
        self.assertTrue((repo / "actuator" / "rejected" / "rt5a-layer2.patch").exists())

    # --- Positive controls: the guard must not have closed the road ----------

    def test_legitimate_patch_still_applies(self):
        """The ordinary path must still work through the HEAD-copy verifier."""
        repo = make_repo()
        drop_request(repo, "legit.patch", patch_main("VALUE = 1", "VALUE = 2"))
        r = run_actuator(repo)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("APPLIED", r.stdout)
        self.assertEqual((repo / "main.py").read_text(encoding="utf-8"), "VALUE = 2\n")
        self.assertTrue((repo / "actuator" / "applied" / "legit.patch").exists())

    def test_legitimate_patch_to_a_non_protected_test_still_applies(self):
        """Protection is a list, not a blanket ban on tests/."""
        repo = make_repo()
        (repo / "tests" / "test_other.py").write_text("X = 0\n", encoding="utf-8")
        (repo / "main.py").write_text("VALUE = 2\n", encoding="utf-8")  # suite satisfied
        _git(repo, "add", "-A")
        _git(repo, "commit", "-qm", "other test")
        body = (
            "diff --git a/tests/test_other.py b/tests/test_other.py\n"
            "--- a/tests/test_other.py\n"
            "+++ b/tests/test_other.py\n"
            "@@ -1 +1 @@\n"
            "-X = 0\n"
            "+X = 1\n"
        )
        drop_request(repo, "other-test.patch", body)
        r = run_actuator(repo)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("APPLIED", r.stdout)
        self.assertEqual((repo / "tests" / "test_other.py").read_text(encoding="utf-8"), "X = 1\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
