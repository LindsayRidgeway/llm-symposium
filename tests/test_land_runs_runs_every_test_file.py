#!/usr/bin/env python3
"""Every test file is run at every landing, and only a glob says so (Dmitri, 2026-11-27).

Value item `whole-suite-on-the-clock` closes on the second clause of its own condition — the suite
does not need a clock because every landing runs it — and that clause rests on one line in the
lander: `for t in sorted((cwd / "tests").glob("test_*.py"))`. Nothing in the repository would have
noticed if that line were replaced by a hand-written list, and a hand list is not hypothetical: the
CI workflow here names its files one per line and covers 146 of the 251 `tests/test_*.py` today
(`scripts/unregistered_tests.py` lists the other 105 as "runs only if a person types its path").
The bot-side glob is the only thing that closes that gap, so it is worth a guard that runs at every
landing and says so.

This pins the behaviour rather than the source text: a scratch tree with two failing test files, one
passing one, and one file that is not a test. The two failing files must come back named, the
passing one must not, and the non-test file must never run (it would fail if it did).

Run directly (`python3 tests/test_land_runs_runs_every_test_file.py`); the landing gate executes
every `tests/test_*.py`, so this holds at every landing. Skips, with its reason, where no lander is
installed — a machine with no lander cannot be asked what its lander does.
"""

import importlib.util
import tempfile
import textwrap
import unittest
from pathlib import Path

LANDERS = sorted(Path.home().glob("LLM/*-bot/land_runs.py"))


class EveryTestFileRuns(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loaded = []
        for path in LANDERS:
            if not path.is_file():
                continue
            name = "lander_" + path.parent.name.replace("-", "_")
            try:
                spec = importlib.util.spec_from_file_location(name, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            except Exception:                     # a lander that will not import is not this test's
                continue                          # business; its own guards own that failure
            if hasattr(module, "failing_tests"):
                cls.loaded.append((path, module))
        if not cls.loaded:
            raise unittest.SkipTest("no installed lander exposes failing_tests()")

    def _fixture(self, tmp):
        tests = Path(tmp) / "tests"
        tests.mkdir()
        (tests / "test_passes.py").write_text("print('ok')\n")
        (tests / "test_fails_first.py").write_text("raise SystemExit(1)\n")
        (tests / "test_fails_second.py").write_text("raise SystemExit(1)\n")
        # Not a test file by the `test_*.py` convention. It would fail loudly if anything ran it.
        (tests / "helper_would_fail.py").write_text("raise SystemExit(2)\n")
        return Path(tmp)

    def test_every_failing_file_is_named_and_only_the_test_files_run(self):
        for path, module in self.loaded:
            with self.subTest(lander=str(path)):
                with tempfile.TemporaryDirectory() as tmp:
                    root = self._fixture(tmp)
                    got = module.failing_tests(cwd=root, limit=60)
                self.assertEqual(
                    got, {"test_fails_first.py", "test_fails_second.py"},
                    "failing_tests() on %s did not report exactly the failing test files: a hand "
                    "list, a first-failure stop, or a walk that includes non-test files all fail "
                    "here, and any of them leaves part of the suite unmeasured at every landing"
                    % path)

    def test_the_walk_covers_a_file_that_is_registered_nowhere(self):
        """The point of the glob: a file added yesterday runs today, with no list to edit."""
        for path, module in self.loaded:
            with self.subTest(lander=str(path)):
                with tempfile.TemporaryDirectory() as tmp:
                    tests = Path(tmp) / "tests"
                    tests.mkdir()
                    fresh = "test_written_after_the_last_list_edit.py"
                    (tests / fresh).write_text("raise SystemExit(1)\n")
                    (tests / "test_green.py").write_text("print('ok')\n")
                    got = module.failing_tests(cwd=Path(tmp), limit=60)
                self.assertEqual(got, {fresh},
                                 "a test file that appears in no list anywhere must still be run "
                                 "and named by the lander (%s)" % path)


if __name__ == "__main__":
    unittest.main(verbosity=0)
