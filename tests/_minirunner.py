"""Run pytest-style test functions with no pytest installed (Desi, 2026-11-26).

Three files in `tests/` were written pytest-style — bare `def test_...` functions, some taking a
`tmp_path` fixture — and the census excused them as "pytest-style, not registered" on the ground
that registering would check nothing, because pytest is not installed on the wake machines. The
excuse was true and the conclusion was wrong: a file with no runner is not a file whose tests are
skipped with a visible reason, it is a file whose assertions **never execute anywhere**. The landing
gate executes each `tests/test_*.py` as a script, and a script with no `__main__` exits 0 — so three
guards (retention enforcement, ledger mirror folding, window land collision) reported "pass" on
every landing while reading nothing, and the same shape had already let
`tests/test_no_zeroed_tracked_files.py` sit dead for a week while the leftover it was written to
catch stayed tracked.

This is the smallest thing that ends the excuse: no pytest, no plugins, no magic. It runs the
module's own `test_*` functions, gives any function that asks for `tmp_path` a fresh temporary
directory, and exits non-zero if anything raised. It does not implement fixtures, parametrization or
markers — a file that needs those should be rewritten, not shimmed.

    if __name__ == "__main__":
        from _minirunner import run
        run(globals())
"""
from __future__ import annotations

import inspect
import sys
import tempfile
import traceback
from pathlib import Path


def run(namespace: dict, argv=None) -> int:
    """Execute every `test_*` callable in `namespace`. Returns a process exit code."""
    wanted = list(argv or [])
    failed = 0
    ran = 0
    for name in sorted(namespace):
        if not name.startswith("test_"):
            continue
        fn = namespace[name]
        if not callable(fn):
            continue
        if wanted and not any(w in name for w in wanted):
            continue
        try:
            params = list(inspect.signature(fn).parameters)
        except (TypeError, ValueError):
            params = []
        with tempfile.TemporaryDirectory() as td:
            kwargs = {}
            for p in params:
                if p == "tmp_path":
                    kwargs[p] = Path(td)
                else:
                    raise SystemExit(
                        "%s asks for fixture %r, which this runner does not provide: rewrite the "
                        "test or extend the runner, but do not let it exit 0 without running."
                        % (name, p))
            ran += 1
            try:
                fn(**kwargs)
                print("ok   " + name)
            except Exception:                       # noqa: BLE001 — a failing test is the point
                failed += 1
                print("FAIL " + name)
                traceback.print_exc()
    print("%d test(s), %d failed" % (ran, failed))
    if not ran:
        print("NOTHING RAN — a runner that collects nothing must not report success")
        return 2
    return 1 if failed else 0


if __name__ == "__main__":
    # `python3 tests/_minirunner.py file.py [name-substring]` — run one pytest-style file by hand.
    import importlib.util

    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    target = Path(sys.argv[1]).resolve()
    spec = importlib.util.spec_from_file_location(target.stem, target)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(target.parent))
    spec.loader.exec_module(mod)
    raise SystemExit(run(vars(mod), sys.argv[2:]))
