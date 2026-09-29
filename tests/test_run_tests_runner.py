#!/usr/bin/env python3
"""Tests for scripts/run_tests.py — the one command that runs the whole suite.

The defect these pin (measured 2026-09-29): the commons had **forty** checks in `tests/` and
the CI job that claimed to verify the repository named **thirteen** of them by hand. Nobody
had lied; the list was correct when written and simply stopped growing with the directory,
which is exactly how a hand-kept list fails — silently, and in the direction of looking
complete. These tests pin the properties that make the replacement trustworthy:

  * discovery takes the directory, not a list, so a new test is run the day it is committed;
  * a failing or hanging check is *reported*, not fatal, and the runner still exits non-zero;
  * a check that could not run (no `node`) is printed as skipped, never as a pass;
  * the workflow calls the runner instead of enumerating files, and any test file it still
    names exists on disk.

No network, no repo writes, no model calls. Run: python3 tests/test_run_tests_runner.py
"""
import importlib.util
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = REPO_ROOT / "tests"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "test-and-report.yml"


def _load_runner():
    spec = importlib.util.spec_from_file_location(
        "run_tests", str(REPO_ROOT / "scripts" / "run_tests.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rt = _load_runner()

PASSING = "def test_ok():\n    print('PASS ok')\n\n\nif __name__ == '__main__':\n    raise SystemExit(0)\n"
FAILING = ("import sys\n\ndef test_bad():\n    print('FAIL bad')\n"
           "    raise SystemExit(1)\n\n\nif __name__ == '__main__':\n    test_bad()\n")
HANGING = "import time\n\ntime.sleep(30)\n"
NOT_A_TEST = "print('this file is not named test_* and must be ignored')\n"


def _fixture(tmp: Path, files: dict) -> Path:
    for name, body in files.items():
        (tmp / name).write_text(body, encoding="utf-8")
    return tmp


def test_discovery_takes_the_directory_not_a_list():
    """Every check on disk is found, and nothing else is."""
    found = {p.name for p in rt.discover(TESTS_DIR)}
    on_disk = ({p.name for p in TESTS_DIR.glob("test_*.py")}
               | {p.name for p in TESTS_DIR.glob("validate_*.mjs")})
    assert found == on_disk, "missed: %s / invented: %s" % (on_disk - found, found - on_disk)
    assert len(found) > 30, "the suite shrank to %d checks — is discovery broken?" % len(found)


def test_a_new_test_file_is_found_without_being_named_anywhere():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        _fixture(tmp, {"test_passing.py": PASSING, "not_a_test.py": NOT_A_TEST})
        assert [p.name for p in rt.discover(tmp)] == ["test_passing.py"]


def test_a_failure_is_reported_and_the_rest_still_run():
    with tempfile.TemporaryDirectory() as d:
        tmp = _fixture(Path(d), {"test_a.py": PASSING, "test_b.py": FAILING,
                                 "test_c.py": PASSING})
        got = []
        rc = rt.run_suite(rt.discover(tmp), timeout=30, verbose=False,
                          stream=_Collect(got))
        text = "\n".join(got)
        assert rc == 1, "a failing check must fail the run"
        assert "FAIL b" in text or "test_b.py" in text, text
        assert "3 check(s): 2 passed, 1 failed" in text, text


def test_all_passing_is_a_zero_exit():
    with tempfile.TemporaryDirectory() as d:
        tmp = _fixture(Path(d), {"test_a.py": PASSING, "test_b.py": PASSING})
        got = []
        rc = rt.run_suite(rt.discover(tmp), timeout=30, verbose=False, stream=_Collect(got))
        assert rc == 0, "".join(got)
        assert "2 check(s): 2 passed, 0 failed" in "\n".join(got)


def test_a_hanging_check_times_out_instead_of_hanging_the_gate():
    """A gate that can hang is not a gate. The landing rule is 'no new failures', not 'wait'."""
    with tempfile.TemporaryDirectory() as d:
        tmp = _fixture(Path(d), {"test_slow.py": HANGING})
        got = []
        r = rt.run_one(tmp / "test_slow.py", timeout=2)
        assert r["status"] == "failed", r
        assert "timed out after 2s" in r["out"], r["out"]


def test_a_validator_without_node_is_skipped_not_passed():
    """Absent tooling must show up as a gap in the record, never as a green check."""
    with tempfile.TemporaryDirectory() as d:
        name = Path(d) / "validate_page.mjs"
        name.write_text("// needs node\n", encoding="utf-8")
        real_which = rt.shutil.which
        rt.shutil.which = lambda _: None
        try:
            r = rt.run_one(name, timeout=10)
        finally:
            rt.shutil.which = real_which
        assert r["status"] == "skipped", r
        assert "node" in r["out"], r["out"]


def test_only_filters_and_list_names_every_check():
    assert rt.main(["--list"]) == 0
    listed = subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "run_tests.py"),
                             "--list"], cwd=str(REPO_ROOT), capture_output=True, text=True,
                            timeout=120)
    assert listed.returncode == 0, listed.stderr
    names = [ln.strip() for ln in listed.stdout.splitlines() if ln.strip().endswith((".py", ".mjs"))]
    assert set(names) == {p.name for p in rt.discover(TESTS_DIR)}, \
        "%d listed vs %d on disk" % (len(names), len(rt.discover(TESTS_DIR)))
    filtered = rt.main(["--list", "--only", "mail"])
    assert filtered == 0


def test_the_workflow_calls_the_runner_instead_of_listing_files():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "scripts/run_tests.py" in text, "the verification job must use the runner"
    for line in text.splitlines():
        stripped = line.strip()
        if "tests/test_" in stripped and not stripped.startswith("#"):
            named = stripped.split("tests/", 1)[1].split()[0]
            assert (TESTS_DIR / named).is_file(), "workflow names a missing test: %s" % named


class _Collect:
    """A file-like sink so a test can assert on the runner's own report."""

    def __init__(self, sink):
        self.sink = sink

    def write(self, s):
        self.sink.append(s)

    def flush(self):
        pass


def _run_all():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for t in tests:
        try:
            t()
            print("PASS %s" % t.__name__)
            passed += 1
        except Exception:
            print("FAIL %s" % t.__name__)
            traceback.print_exc()
    print("\n%d/%d tests passed" % (passed, len(tests)))
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    sys.exit(_run_all())
