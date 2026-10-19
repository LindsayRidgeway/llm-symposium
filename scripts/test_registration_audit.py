#!/usr/bin/env python3
# Owner: Desi
"""Which test files on disk does no workflow ever execute?

Why this exists (2026-10-19). The repository has been bitten by the same defect at least five
times, and each time it was found by hand: `tests/test_maternal_pain_search.py` pinned a map and
was registered nowhere (found 2026-10-08); four evidence-table tests were absent from the suite
(2026-09-30); `test_auto_reply.py` guarded a predicate that drew eight junk replies because the
file ran nowhere (2026-10-09); `test_telegram.py` was pytest-shaped with no runner (2026-10-12);
and on the morning this was written, `tests/test_item_ledger_wide_branch.py` — the file that pins
the wide branch of the reviewer draw, written the same day — was sitting on `main` executed by
nothing. Measured at 07:10Z 2026-10-19: 116 test files on disk, 94 executed by the main
verification workflow, 2 more by the Tarik cloud workflow, **21 executed by no file in
`.github/workflows/` at all.**

An unregistered test is worse than a missing one. It reads as a guarantee — the artefact it pins
usually cites it by name — while proving nothing, and every wake that trusts it spends its budget
on a claim nobody checked.

What counts as registration: the test's path appears as a command in a workflow file, on a line
that is not a YAML comment. Comments matter here more than usual, because this repository
retired half its schedules by commenting out the cron and leaving a paragraph explaining why —
a scan that counts commented lines would call a retired suite *covered*.

Two ways a test may be on disk and still not run, and only one of them is an error:

  registered   executed by some workflow. The normal case.
  exempt       listed in `EXEMPT` below, with a reason. A test that needs the network, the live
               rover, or a credential the CI runner does not have cannot run in the offline
               suite; the file stays, and the audit records why it never runs.
  missing      neither. **Exit 1.** Either register it or say in `EXEMPT` why it cannot run.

The `EXEMPT` list is checked in both directions: an exempt path that is now registered, or that
no longer exists, is also a failure. An allowlist nobody prunes is how "exempt" quietly becomes
"forgotten".

CLI:
  python3 scripts/test_registration_audit.py            # table, exit 1 if a test runs nowhere
  python3 scripts/test_registration_audit.py --json     # the same, machine-readable
  python3 scripts/test_registration_audit.py --list     # every test and where it is executed
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS = "tests"
WORKFLOWS = Path(".github") / "workflows"

# A test named on a command line. Deliberately anchored to the tests/ prefix so a comment that
# merely mentions a filename in prose is not mistaken for an execution.
CALL_RE = re.compile(r"tests/(test_[A-Za-z0-9_]+\.py)")

# Tests that exist on disk and deliberately do not run in CI. Each entry needs a reason, and the
# reason is the record: "it fails" is not one, "it needs a live host the runner does not have" is.
EXEMPT: dict[str, str] = {
    "tests/test_rover_wake.py": (
        "reaches the live rover host; it fails with every outbound route blocked, so it cannot "
        "run in the offline verification suite — it is a manual check, run by hand on the Mac"
    ),
}


def _live_lines(text: str) -> list[str]:
    """The workflow's lines with YAML comments removed.

    A line whose first non-space character is `#` is a comment. Nothing else is touched: an
    inline `# ...` after a command is left alone, because the command on that line still ran.
    """
    return [ln for ln in text.splitlines() if not ln.lstrip().startswith("#")]


def scan_workflows(root: Path = ROOT) -> dict[str, list[str]]:
    """test file name -> workflow files whose live lines execute it. Sorted and deduplicated."""
    found: dict[str, set[str]] = {}
    wf_dir = root / WORKFLOWS
    if not wf_dir.is_dir():
        return {}
    for wf in sorted(wf_dir.glob("*.y*ml")):
        for line in _live_lines(wf.read_text(encoding="utf-8", errors="replace")):
            for name in CALL_RE.findall(line):
                found.setdefault(name, set()).add(wf.name)
    return {name: sorted(set(names)) for name, names in found.items()}


def on_disk(root: Path = ROOT) -> list[str]:
    d = root / TESTS
    if not d.is_dir():
        return []
    return sorted(p.name for p in d.glob("test_*.py") if p.is_file())


def audit(root: Path = ROOT, exempt: dict[str, str] | None = None) -> dict:
    """The three buckets, plus the two ways the allowlist itself can be wrong."""
    exempt = EXEMPT if exempt is None else exempt
    registered = scan_workflows(root)
    names = on_disk(root)
    missing = [n for n in names if n not in registered and f"{TESTS}/{n}" not in exempt]
    exempt_used = {p: exempt[p] for p in sorted(exempt) if (root / p).is_file()}
    stale = {
        "now_registered": sorted(p for p in exempt if f"{TESTS}/{Path(p).name}" in registered),
        "gone": sorted(p for p in exempt if not (root / p).is_file()),
    }
    reasons_missing = sorted(p for p, why in exempt.items() if not (why or "").strip())
    ok = not missing and not stale["now_registered"] and not stale["gone"] and not reasons_missing
    return {
        "on_disk": len(names),
        "registered": len([n for n in names if n in registered]),
        "unregistered": [f"{TESTS}/{n}" for n in missing],
        "exempt": exempt_used,
        "allowlist_problems": stale,
        "exempt_without_reason": reasons_missing,
        "workflows": {n: registered[n] for n in sorted(registered) if n in set(names)},
        "ok": ok,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--list", action="store_true", help="name every test and its workflows")
    a = ap.parse_args()

    res = audit()
    if a.json:
        print(json.dumps(res, indent=1, sort_keys=True))
        return 0 if res["ok"] else 1
    if a.list:
        for name, wfs in res["workflows"].items():
            print(f"  {name:48s} {', '.join(wfs)}")
        for path in res["exempt"]:
            print(f"  {Path(path).name:48s} EXEMPT")
        return 0 if res["ok"] else 1

    print(f"test registration: {res['on_disk']} test file(s) on disk, "
          f"{res['registered']} executed by a workflow, {len(res['exempt'])} exempt")
    if res["unregistered"]:
        print(f"\nUNREGISTERED — {len(res['unregistered'])} test(s) no workflow executes:")
        for path in res["unregistered"]:
            print(f"  {path}")
        print("Register each in .github/workflows/test-and-report.yml (or another workflow that "
              "can run it), or add it to this script's EXEMPT with a reason.")
    for path, why in res["exempt"].items():
        print(f"  exempt: {path} — {why}")
    bad = res["allowlist_problems"]
    for path in bad["now_registered"]:
        print(f"STALE EXEMPTION: {path} is registered now — remove it from EXEMPT")
    for path in bad["gone"]:
        print(f"STALE EXEMPTION: {path} does not exist — remove it from EXEMPT")
    for path in res["exempt_without_reason"]:
        print(f"NO REASON: {path} is exempt with an empty reason")
    if res["ok"]:
        print("\nevery test on disk runs somewhere, or says why it cannot")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
