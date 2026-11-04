#!/usr/bin/env python3
"""Which test files exist that no runner ever executes — the gate for the defect that has now
recurred three times.

Why this exists (2026-10-30, Desi). Every research artefact in this repository says it is pinned by a
test, and every pin is false if that test is never run. The same defect — a test file written, landed,
and registered nowhere — was found and repaired on 2026-10-13 (24 files), again on 2026-10-18, and
again on 2026-10-30, when `tests/test_item_evidence_lint.py` (on main since `209ebc25`, 2026-10-19,
83 cases) and `tests/test_status_census_unread.py` (22 cases) turned out never to have executed in CI.
Each time it was found by a reader noticing, never by a gate. This is the gate.

It is a REPORT first, and deliberately not a hard failure. A gate that turns landing red on day one
blocks every amigo, and the only thing worse than an unregistered test is a red main. So the default
exit status is 0 and the finding is printed under a heading a human reads. `--strict` exits 1 and is
what CI can be pointed at once the list is empty.

The five states, because they are not the same fact:

* MISSING    a test file with its own `__main__` runner, named nowhere in any workflow. This is the
             defect: it can only ever run if a person types its path.
* NO-OP      a test file with no runner that *is* named in a workflow. The registration is a lie in
             the opposite direction: `python3 tests/x.py` on a file with no `__main__` prints
             `Ran 0 tests … OK`, which reads as a pass. Reported separately because the repair is
             different — either give it a runner or take the line out.
* PARTIAL    a directly invoked unittest script calls unittest.main before later TestCase classes.
             The runner collects before those definitions exist, even though the command can pass.
             Module-form discovery imports a guarded script and does not have this ordering problem.
* EXEMPT     pytest-style (no runner of either kind), not registered. Deliberately left out of CI since
             2026-10-13, because pytest is not installed in this project and a registration would
             report green while checking nothing. Listed so the exemption is visible and counted
             rather than assumed.
* DANGLING   a workflow line naming a test file that does not exist. The registry then fails on the
             absence rather than passing on it, but it means a test was renamed or deleted and the
             line stayed.

A file counts as self-running if it contains a `__main__` block, calls `unittest.main()`, or is not
pytest-style — not if its name looks right. A file
counts as registered if some workflow under `.github/workflows/` invokes it as `tests/<name>.py` or as
`-m unittest tests.<name>` anywhere in the file, comments included — the workflow documents itself in
comments, and a path named in a comment is not an invocation, so comment lines are skipped. That
last distinction is the one that hid the 10-30 pair: `test_item_evidence_lint` was *discussed* in the
workflow's comments and never run by it.

Usage:
    python3 scripts/unregistered_tests.py             # report, exit 0
    python3 scripts/unregistered_tests.py --strict    # exit 1 if anything is MISSING, NO-OP, PARTIAL or DANGLING
    python3 scripts/unregistered_tests.py --json
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TESTS = REPO / "tests"
WORKFLOWS = REPO / ".github" / "workflows"

# `python3 tests/test_foo.py` and `python3 -m unittest tests.test_foo` (also `-m unittest tests/test_foo`).
CALL = re.compile(r"python3\s+(?:-m\s+unittest\s+)?tests[./]([A-Za-z0-9_]+?)(?:\.py)?(?:\s|$)", re.MULTILINE)
DIRECT_CALL = re.compile(r"python3\s+tests[./]([A-Za-z0-9_]+?)(?:\.py)?(?:\s|$)", re.MULTILINE)
# A file is "pytest-style" if it only *defines* tests for a collector to find. pytest is not
# installed in this project, so such a file runs only if something calls it — that is the exemption.
PYTEST_STYLE = re.compile(r"^(?:def test_|class \w+\s*\(\s*(?:unittest\.)?TestCase)", re.MULTILINE)


def has_runner(path: Path) -> bool:
    """True if the file does something when executed. See PYTEST_STYLE above for the two no-entry shapes."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    if "__main__" in text or "unittest.main()" in text:
        return True
    # No entry point: it still runs if it is a bare script (its checks are module-level statements),
    # and it does nothing if it only defines tests. Six registered files are the first shape and two
    # exempt files are the second; telling them apart by style is what stops this script from
    # reporting a working test as a no-op, which its own first draft did.
    return not PYTEST_STYLE.search(text)


def early_unittest_runner(path: Path) -> dict | None:
    """Find the common guarded unittest.main-before-TestCase defect without importing tests.

    This bounded static check recognizes literal __name__ guards, unittest.main calls and
    direct TestCase bases. It does not certify dynamic runners, aliases or full collection.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError):
        return None
    for statement in tree.body:
        if not isinstance(statement, ast.If):
            continue
        condition = statement.test
        if not (isinstance(condition, ast.Compare)
                and isinstance(condition.left, ast.Name) and condition.left.id == "__name__"
                and len(condition.ops) == 1 and isinstance(condition.ops[0], ast.Eq)
                and len(condition.comparators) == 1
                and isinstance(condition.comparators[0], ast.Constant)
                and condition.comparators[0].value == "__main__"):
            continue
        for action in statement.body:
            if not (isinstance(action, ast.Expr) and isinstance(action.value, ast.Call)):
                continue
            call = action.value.func
            if not (isinstance(call, ast.Attribute) and call.attr == "main"
                    and isinstance(call.value, ast.Name) and call.value.id == "unittest"):
                continue
            late = [node.name for node in tree.body if isinstance(node, ast.ClassDef)
                    and node.lineno > action.lineno and any(
                        (isinstance(base, ast.Attribute) and base.attr == "TestCase")
                        or (isinstance(base, ast.Name) and base.id == "TestCase")
                        for base in node.bases)]
            if late:
                return {"runner_line": action.lineno, "later_test_classes": late}
    return None


def registered_names(workflows: Path = WORKFLOWS, *, direct_only: bool = False) -> dict[str, list[str]]:
    """Map test module name -> the workflow files that invoke it, skipping comment-only mentions."""
    found: dict[str, list[str]] = {}
    if not workflows.is_dir():
        return found
    for wf in sorted(workflows.glob("*.yml")) + sorted(workflows.glob("*.yaml")):
        try:
            text = wf.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue  # a path named in a comment is not an invocation
            for name in (DIRECT_CALL if direct_only else CALL).findall(line):
                found.setdefault(name, [])
                if wf.name not in found[name]:
                    found[name].append(wf.name)
    return found


def classify(tests: Path = TESTS, workflows: Path = WORKFLOWS) -> dict[str, list[dict]]:
    """Classify registration, partial collection and missing-file findings without executing tests."""
    reg = registered_names(workflows)
    direct = registered_names(workflows, direct_only=True)
    present = {p.stem: p for p in sorted(tests.glob("test_*.py"))}
    out: dict[str, list[dict]] = {"missing": [], "no_op": [], "exempt": [], "dangling": [], "partial": []}

    for stem, path in present.items():
        runner = has_runner(path)
        named_in = reg.get(stem, [])
        try:
            shown = str(path.relative_to(REPO))
        except ValueError:  # a fixture directory outside the repository (the tests do this)
            shown = str(path)
        rec = {"test": path.name, "path": shown, "workflows": named_in}
        if runner and not named_in:
            out["missing"].append(rec)
        elif runner and named_in:
            early = early_unittest_runner(path) if direct.get(stem) else None
            if early:
                out["partial"].append(dict(rec, **early))
            continue  # the good state, not printed
        elif not runner and named_in:
            out["no_op"].append(rec)
        else:
            out["exempt"].append(rec)

    for stem, named_in in sorted(reg.items()):
        if stem not in present:
            out["dangling"].append({"test": f"{stem}.py", "workflows": named_in})
    return out


def render(result: dict[str, list[dict]]) -> str:
    total = sum(len(result.get(k, [])) for k in ("missing", "no_op", "exempt", "dangling", "partial"))
    lines: list[str] = []
    lines.append("Test registration and collection — the census of tests/ against every workflow")
    lines.append("")

    def block(key: str, title: str, why: str, rows: list[dict]) -> None:
        lines.append(f"{title} ({len(rows)})")
        if not rows:
            lines.append("  none")
        else:
            lines.append(f"  {why}")
            for r in rows:
                wf = ", ".join(r.get("workflows") or []) or "—"
                lines.append(f"  {r['test']:<52} {wf}")
                if r.get("later_test_classes"):
                    lines.append("    after runner at line " + str(r["runner_line"]) + ": "
                                 + ", ".join(r["later_test_classes"]))
        lines.append("")

    block("missing", "MISSING — has a runner, named in no workflow",
          "the defect: this file runs only if a person types its path", result["missing"])
    block("no_op", "NO-OP — named in a workflow, has no runner",
          "`python3` on it prints 'Ran 0 tests ... OK', which reads as a pass", result["no_op"])
    block("partial", "PARTIAL — direct unittest runner precedes later test classes",
          "move the runner below all test classes or use module discovery", result.get("partial", []))
    block("dangling", "DANGLING — a workflow names a file that does not exist",
          "a test was renamed or deleted and the line stayed", result["dangling"])
    block("exempt", "EXEMPT — pytest-style, not registered",
          "deliberate since 2026-10-13: pytest is not installed, so registering would check nothing",
          result["exempt"])

    lines.append(f"{total} file(s) accounted for. Exit 0 by default; --strict fails on everything above "
                 "the EXEMPT line.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if anything is MISSING, NO-OP, PARTIAL or DANGLING (the states a gate can repair)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--tests", type=Path, default=TESTS, help=argparse.SUPPRESS)
    ap.add_argument("--workflows", type=Path, default=WORKFLOWS, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    result = classify(args.tests, args.workflows)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render(result))

    bad = len(result["missing"]) + len(result["no_op"]) + len(result["dangling"]) + len(result.get("partial", []))
    return 1 if (args.strict and bad) else 0


if __name__ == "__main__":
    sys.exit(main())
