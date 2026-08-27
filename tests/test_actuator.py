#!/usr/bin/env python3
"""Tests for the Symposium Actuator (`actuator/apply.py`).

Run:  python3 tests/test_actuator.py
Stdlib only; requires `git` on PATH. Each test builds a throwaway git repo,
copies the real apply.py into it, drops a patch request, runs the actuator,
and asserts the outcome. No network access.
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
SUITE = (
    "import os, sys\n"
    "sys.path.insert(0, os.getcwd())\n"
    "from main import VALUE\n"
    "assert VALUE == 2, VALUE\n"
)
PROBE = 'print("probe ok")\n'


def make_repo() -> Path:
    """Build a throwaway git repo shaped like the real one (minimal)."""
    repo = Path(tempfile.mkdtemp(prefix="actuator-test-"))
    (repo / "main.py").write_text(MAIN_V1, encoding="utf-8")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_projection.py").write_text(SUITE, encoding="utf-8")
    (repo / "probes").mkdir()
    (repo / "probes" / "ticktick_recurrence_probe.py").write_text(PROBE, encoding="utf-8")
    for d in ("actuator/requests", "actuator/applied", "actuator/rejected"):
        (repo / d).mkdir(parents=True)
    shutil.copy(APPLY_PY, repo / "actuator" / "apply.py")
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@local")
    _git(repo, "config", "user.name", "Actuator Test")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "base")
    return repo


def _git(repo: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)


def run_actuator(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "actuator/apply.py"],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=300,
    )


def patch_main(old: str, new: str) -> str:
    return (
        "diff --git a/main.py b/main.py\n"
        "--- a/main.py\n"
        "+++ b/main.py\n"
        "@@ -1 +1 @@\n"
        f"-{old}\n"
        f"+{new}\n"
    )


def drop_request(repo: Path, name: str, body: str) -> None:
    (repo / "actuator" / "requests" / name).write_text(body, encoding="utf-8")


class ActuatorTest(unittest.TestCase):
    def test_valid_patch_applied_and_logged(self):
        repo = make_repo()
        drop_request(repo, "2026-08-27-test-deadbeef.patch", patch_main("VALUE = 1", "VALUE = 2"))
        r = run_actuator(repo)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("APPLIED", r.stdout)
        self.assertEqual((repo / "main.py").read_text(encoding="utf-8"), "VALUE = 2\n")
        self.assertTrue((repo / "actuator" / "applied" / "2026-08-27-test-deadbeef.patch").exists())
        self.assertEqual(list((repo / "actuator" / "requests").glob("*.patch")), [])
        self.assertIn("APPLIED", (repo / "actuator" / "log.md").read_text(encoding="utf-8"))

    def test_failing_patch_rejected_and_reversed(self):
        repo = make_repo()
        drop_request(repo, "2026-08-27-test-beefcafe.patch", patch_main("VALUE = 1", "VALUE = 3"))
        r = run_actuator(repo)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("REJECTED", r.stdout)
        self.assertEqual((repo / "main.py").read_text(encoding="utf-8"), MAIN_V1)  # reversed
        self.assertTrue((repo / "actuator" / "rejected" / "2026-08-27-test-beefcafe.patch").exists())
        self.assertIn("REJECTED", (repo / "actuator" / "log.md").read_text(encoding="utf-8"))

    def test_malformed_patch_rejected(self):
        repo = make_repo()
        drop_request(repo, "bad.patch", "this is not a unified diff\n")
        r = run_actuator(repo)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("REJECTED", r.stdout)
        self.assertTrue((repo / "actuator" / "rejected" / "bad.patch").exists())

    def test_self_modification_rejected(self):
        repo = make_repo()
        body = (
            "diff --git a/actuator/apply.py b/actuator/apply.py\n"
            "--- a/actuator/apply.py\n"
            "+++ b/actuator/apply.py\n"
            "@@ -1 +1 @@\n"
            "-#!/usr/bin/env python3\n"
            "+#!/usr/bin/env python3 # tampered\n"
        )
        drop_request(repo, "evil.patch", body)
        r = run_actuator(repo)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("self-modification", r.stdout)
        self.assertTrue((repo / "actuator" / "rejected" / "evil.patch").exists())

    def test_already_applied_noop(self):
        repo = make_repo()
        body = patch_main("VALUE = 1", "VALUE = 2")
        drop_request(repo, "a.patch", body)
        run_actuator(repo)
        # The same change resubmitted (e.g. the runner re-extracts a review)
        # must be a no-op, not a re-apply or a rejection.
        drop_request(repo, "b.patch", body)
        r = run_actuator(repo)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("already in effect", r.stdout)
        self.assertEqual((repo / "main.py").read_text(encoding="utf-8"), "VALUE = 2\n")
        self.assertTrue((repo / "actuator" / "applied" / "b.patch").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
