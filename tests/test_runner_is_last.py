#!/usr/bin/env python3
"""Nothing named `test_*` may sit below the runner — the census that would have caught five dead tests.

WHY THIS EXISTS (measured 2026-11-07, Desi)
-------------------------------------------
The house runs tests by typing the file (`pytest` is not installed here; the CI workflow does
`python3 tests/test_mail.py`). A module runs top to bottom, so a runner placed above a class runs
before that class exists. Three files had one:

* `tests/test_landing_refusals.py` — the whole `UnfiledTest` class, holding the `--unfiled` census,
  five tests. A direct run printed `Ran 30 tests`; the class holding the newest work was never run.
* `tests/test_drive_bridge_status.py` — `TestReceiptsAreClaimsNotConversions`, unreachable since it
  landed. Direct run 19, actual 20.
* `tests/test_mail.py` — worse, because its runner collects `globals()` by name at the moment it is
  called: four credential-redaction tests (password-reset links, invitation tokens) were defined
  below it, so they ran in no invocation at all — not directly, and not under `-m unittest`, which
  finds no `TestCase` in that file either. 24/24 became 28/28 the moment the runner moved down.

The defect is invisible by construction: a green run reports the tests it ran, not the ones it
skipped. The repository already names this shape — `scripts/unregistered_tests.py` calls it partial
collection and detects it inside throwaway fixtures; this test makes the same measurement about
`tests/` itself.

WHAT IT CHECKS, AND WHAT IT DOES NOT
------------------------------------
It parses `tests/test_*.py` with `ast` and, for any module-level `if __name__ == "__main__":` block
that is not the last statement carrying code, flags every module-level class or `test_*` function
defined below it. Text inside string literals is invisible to `ast`, which matters: the fixture
strings in `tests/test_unregistered_tests.py` contain deliberately misplaced runners and must not be
read as real ones. It does not judge a runner's contents, and does not look inside functions.
"""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent


def guard_line(tree: ast.Module) -> int | None:
    """The line of a module-level `if __name__ == "__main__":` block, if there is one."""
    for statement in tree.body:
        if not isinstance(statement, ast.If):
            continue
        condition = statement.test
        if not (isinstance(condition, ast.Compare)
                and isinstance(condition.left, ast.Name) and condition.left.id == "__name__"
                and len(condition.comparators) == 1
                and isinstance(condition.comparators[0], ast.Constant)
                and condition.comparators[0].value == "__main__"):
            continue
        return statement.lineno
    return None


def stranded(path: Path) -> list[str]:
    """Names of module-level tests defined below the runner in `path`."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError) as exc:
        return [f"<unparsable: {exc}>"]
    line = guard_line(tree)
    if line is None:
        return []
    out = []
    for node in tree.body:
        if node.lineno <= line:
            continue
        if isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body
                       if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                       and n.name.startswith("test")]
            if methods:
                out.append(f"{node.name} ({len(methods)} test method(s))")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            out.append(f"{node.name}()")
    return out


class RunnerIsLastTest(unittest.TestCase):
    def test_no_test_is_defined_below_its_files_runner(self):
        offenders = {}
        for path in sorted(TESTS.glob("test_*.py")):
            found = stranded(path)
            if found:
                offenders[path.name] = found
        self.assertEqual(
            offenders, {},
            "these tests are defined below their file's `if __name__ == \"__main__\"` block, so a "
            "direct run — which is how this repository runs its tests — never reaches them: "
            f"{offenders}",
        )

    def test_the_check_finds_a_stranded_class(self):
        # The test must be able to fail, or it is a green light wired to nothing.
        sample = TESTS / "_runner_position_sample.py"
        sample.write_text(
            "import unittest\n"
            "class Early(unittest.TestCase):\n    def test_a(self): pass\n"
            "if __name__ == \"__main__\":\n    unittest.main()\n"
            "class Late(unittest.TestCase):\n    def test_b(self): pass\n",
            encoding="utf-8",
        )
        self.addCleanup(sample.unlink)
        self.assertEqual(stranded(sample), ["Late (1 test method(s))"])

    def test_a_correctly_placed_runner_is_silent(self):
        sample = TESTS / "_runner_position_sample_ok.py"
        sample.write_text(
            "import unittest\n"
            "class Only(unittest.TestCase):\n    def test_a(self): pass\n"
            "if __name__ == \"__main__\":\n    unittest.main()\n",
            encoding="utf-8",
        )
        self.addCleanup(sample.unlink)
        self.assertEqual(stranded(sample), [])

    def test_a_runner_inside_a_string_is_not_a_runner(self):
        # tests/test_unregistered_tests.py keeps deliberately broken samples in string constants.
        self.assertEqual(guard_line(ast.parse('EARLY = """\nif __name__ == "__main__":\n'
                                              '    unittest.main()\nclass Late: pass\n"""\n')), None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
