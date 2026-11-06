#!/usr/bin/env python3
"""Reconcile the landing refusals — which refused runs are still refused.

Why this exists (2026-10-19, Dmitri). `land_runs.py` writes `landing_failed.txt` into a run's own
directory when the repository's tests show the run's diff introduced new failures, and that file is
never touched again. It is a **verdict**, not a state: it stays in the run directory after the same
work has landed under a later run's commit. Read a fortnight later it says "this work was refused"
about work that is on `main` and green.

Measured this wake, on the run that this wake was assigned to review (desi `20261019T110921Z-df991cc4`):

* its `landing_failed.txt` reads `this run's diff introduced new failures: test_drive_bridge_status.py`;
* all eight paths it claims are on `main`, added whole by desi run `20261019T130933Z-8421299d`
  (commit `6b85041d`), whose own report says the flaky test was traced and fixed;
* the test now passes 15/15 consecutive runs, and the race that made it flaky is documented in the
  test file itself (`mount_unreadable`).

So the refusal was true on the day and is false now, and nothing in the repository distinguishes the
two. That is the same shape as the 2026-09-23 defect ("unlanded is not missing"): a durable marker
that a later reader takes for a verdict about today, which is how ten wakes came to recompute the
same work. This script does the reconciliation a machine can do: for every refusal on the disk, check
whether the run's own claimed paths reached this checkout's `main`.

Classification, per refused run:

    reconciled  every path the run's LAND line claims is on main — the refusal was made good later
    partial     some are on main and some are not — real missing work, and the refusal is half true
    open        none of the claimed paths is on main — the refusal still stands
    no-claim    no LAND line with paths (cut off, or a report that never said) — nothing to check

The `no-claim` rows matter more than they look: a run cut off at its action cap often refused with
nothing named, and that is a delivery nobody can chase from the run record alone.

Read-only. It never edits a run directory. It does not re-run a test unless `--recheck` is asked for
(added 2026-10-23), and that flag exists because the path check answers only half the question: a
refusal names a test as its cause, and whether *that* still reproduces is a second measurement.

Measured 2026-10-23, all 89 refusals on disk: no-claim 37, partial 21, open 13, reconciled 18. Two
in five were refused with nothing named and one in five was made good later, so the record as it
stands is not a list of unfinished work — it is a list of moments. The five test files that refuse
most often (`test_evidence_table_registration`, `test_cited_path_gate`, `test_gen_feed_freshness`,
`test_gallery_unwired_works`, `test_declutter_audit`) all pass on the tree of that measurement.

`--unfiled` (added 2026-11-06) answers the question the crash repair raised and did not answer: a
failed landing nobody can be handed is still a failed landing. It prints every surveyed run whose id
appears nowhere in `channels/items.jsonl` — the set difference between this survey and the ledger,
in one field comparison. Measured on the six bots the day it was written: 597 failed landings, 13
never named in the ledger, 10 of those naming work that is not on main. `--actionable-only` keeps
just those 10. Nothing schedules it yet; it is a report, and the honest wiring is a caller, which
this file still does not have.

`--recheck` labels each refusal `green-now` if every test it blames passes in this checkout today,
`red-now` if one still fails, `gone` if the blamed file no longer exists, `untested` if the reason
names none. `green-now` does NOT prove the run was innocent — it says the cause does not reproduce
here, which is exactly what the path-based `reconciled` says about the paths. Both are statements
about today, and neither is a verdict about the day of the refusal.

Wired 2026-11-05 (Dmitri), thirteen days late. Between 2026-10-23 and today this docstring was the
only place `--recheck` existed: `main()` never declared the flag, `survey()` was called without it,
`render()` had no column for it and no test mentioned it, so `recheck()` and `named_tests()` were
dead code that twelve green tests could not notice. That is the retention.py shape a second time —
an instrument documented as working with no call site, which is why the lesson is now a test
(`tests/test_landing_refusals.py::RecheckTest`) and not another paragraph. Everything below is
unchanged: the flag runs the tests a refusal blames, so it is opt-in, and nothing here edits a run
directory.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# A LAND line, as the wake instruction asks for it: `LAND: a, b, c`. Reports also carry
# `LAND: (none yet)`, `LAND: (pending)` and `LAND: (nothing yet)` — those are claims of nothing.
LAND_RE = re.compile(r"^\s*LAND:\s*(.+)$", re.MULTILINE)
PLACEHOLDER = re.compile(r"^\(.*\)$")


def claimed_paths(report_text: str) -> list[str]:
    """The paths a run's report claims, from its last LAND line.

    Last, not first: a report is rewritten as the run proceeds (the instruction says so), so an
    earlier line can legitimately name less than the run finished with.
    """
    matches = LAND_RE.findall(report_text or "")
    if not matches:
        return []
    out: list[str] = []
    for raw in matches[-1].split(","):
        item = raw.strip().strip("`").strip().rstrip(".")
        if not item or PLACEHOLDER.match(item):
            continue
        out.append(item)
    return out


def read(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except OSError:
        return ""


# Added 2026-11-06 (Dmitri). `landing_failed.txt` is written by the test gate and by nothing else,
# so a run that failed *before* the gate was reached left no file here at all and this survey could
# not see it. Measured on the six bots' run directories: 20 runs carry
# `land: landing_error: name 'a' is not defined` in `result.json` and no `landing_failed.txt`; the
# lander crashed, wrote no file, filed no item, and left the run reading `awaiting_review`. Their
# work is in `changes.patch` and no queue contains them — the same gap that hid a gwen run from
# every reading queue on 2026-11-05, found by hand instead of by this script. `result.json`'s `land`
# field is the only place a crashed or conflicted landing is recorded.
#
# The values below were read off 1,303 run directories on 2026-11-06, not guessed: these three mean
# the work reached main (or a handoff that carried it), and every other value means it did not.
LAND_SUCCEEDED = ("landed", "already_landed", "handoff_result_published")


def land_value(run_dir: Path) -> str:
    """`result.json`'s `land` field, or "" when there is none to read."""
    raw = read(run_dir / "result.json")
    if not raw:
        return ""
    try:
        data = json.loads(raw)
    except ValueError:
        return ""
    land = data.get("land") if isinstance(data, dict) else ""
    return land if isinstance(land, str) else ""


def land_failed(run_dir: Path) -> bool:
    """Did this run's landing fail, whether or not the gate got far enough to say so?"""
    land = land_value(run_dir)
    return bool(land) and land.split(":")[0].strip() not in LAND_SUCCEEDED


def classify(run_dir: Path, repo: Path) -> dict:
    """One refusal, checked against the repository's own files."""
    gate_reason = read(run_dir / "landing_failed.txt").strip().splitlines()
    land = land_value(run_dir)
    reason = gate_reason
    paths = claimed_paths(read(run_dir / "report.txt"))
    present = [p for p in paths if (repo / p).exists()]
    if not paths:
        state = "no-claim"
    elif len(present) == len(paths):
        state = "reconciled"
    elif present:
        state = "partial"
    else:
        state = "open"
    if not reason and land:
        # No gate verdict, but `result.json` says the landing failed. Its text is the whole record:
        # `landing_error: name 'a' is not defined` is a crash, and a crash is why no file exists.
        reason = [land]
    return {
        "run": run_dir.name,
        "bot": run_dir.parent.parent.parent.name,
        "state": state,
        # `gate` means the test gate refused the run and wrote its verdict down. Anything else is
        # the land field's own word for what happened, and those runs are the ones no queue held.
        "source": "gate" if gate_reason else (land.split(":")[0].strip() or ""),
        "land": land,
        "reason": reason[0] if reason else "",
        "claimed": len(paths),
        "on_main": len(present),
        "missing": [p for p in paths if p not in present],
    }


TEST_RE = re.compile(r"\btest_[A-Za-z0-9_]+\.py\b")
RECHECK_TIMEOUT = 180


def named_tests(reason: str) -> list[str]:
    """The test files a refusal blames, by name, in the order it names them.

    The refusal text is always `this run's diff introduced new failures: a.py, b.py`, so the names
    are the only part of the verdict that says *what to run*. Reading them out is the whole trick.
    """
    out: list[str] = []
    for name in TEST_RE.findall(reason or ""):
        if name not in out:
            out.append(name)
    return out


def _default_runner(test_path: Path, repo: Path) -> tuple[int, str]:
    proc = subprocess.run([sys.executable, str(test_path)], cwd=str(repo),
                          capture_output=True, text=True, timeout=RECHECK_TIMEOUT)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def _why(output: str) -> str:
    """The last line of a test run that says something — the count, or the failure."""
    for line in reversed((output or "").strip().splitlines()):
        line = line.strip()
        if line and not line.startswith(("Ran ", "OK", "---")):
            return line[:90]
    tail = (output or "").strip().splitlines()
    return (tail[-1].strip()[:90] if tail else "")


def recheck(row: dict, repo: Path, runner=_default_runner,
            cache: dict | None = None) -> dict:
    """Does the test this refusal blames still fail here? One measurement per named test.

    `cache` is per-invocation: `test_evidence_table_registration.py` is blamed by eleven separate
    refusals and must not be re-run eleven times. The runner is injectable so the tests below can
    assert the labelling without running a real suite.
    """
    cache = {} if cache is None else cache
    names = named_tests(row.get("reason", ""))
    out = dict(row)
    out["tests"] = names
    if not names:
        out["recheck"] = "untested"
        out["recheck_detail"] = []
        return out
    detail = []
    for name in names:
        if name not in cache:
            path = repo / "tests" / name
            if not path.exists():
                cache[name] = ("gone", "not in this checkout")
            else:
                try:
                    code, text = runner(path, repo)
                    cache[name] = ("green-now" if code == 0 else "red-now", _why(text))
                except Exception as exc:                      # timeout, unreadable, anything
                    cache[name] = ("error", f"{type(exc).__name__}: {exc}"[:90])
        state, why = cache[name]
        detail.append((name, state, why))
    states = [d[1] for d in detail]
    if "red-now" in states:
        verdict = "red-now"
    elif "green-now" in states:
        verdict = "green-now"
    elif "error" in states:
        verdict = "error"
    else:
        verdict = "gone"
    out["recheck"] = verdict
    out["recheck_detail"] = detail
    return out


def find_runs(roots: list[Path]) -> list[Path]:
    """Every run directory under the given roots whose landing failed.

    It used to look for `landing_failed.txt` and nothing else, which answered "which runs did the
    gate refuse" and was silent about every run that failed on the way to the gate — 20 crashes, 155
    conflicts and 222 dirty-tree refusals at the last count. A run counts now if it carries the
    gate's file *or* if `result.json` says its landing did not succeed.
    """
    found: list[Path] = []
    for root in roots:
        pattern = os.path.join(str(root), "*", "tick-state", "runs", "*")
        for hit in glob.glob(pattern):
            run_dir = Path(hit)
            if (run_dir / "landing_failed.txt").exists() or land_failed(run_dir):
                found.append(run_dir)
    return sorted(set(found), key=lambda p: p.name)


def survey(roots: list[Path], repo: Path, recheck_tests: bool = False,
           recheck_runner=_default_runner, source: str = "") -> dict:
    """Survey every failed landing. `source` narrows it: "gate" is the test gate's refusals only.

    The split matters because the two kinds fail differently. A gate refusal is a *decision* with a
    reason written beside the patch, so the patch and the reason sit together. A crash or a conflict
    has neither: `result.json` carries one line, and the work survives only inside `changes.patch`.
    """
    rows = [classify(r, repo) for r in find_runs(roots)]
    if source:
        rows = [row for row in rows if row.get("source") == source]
    if recheck_tests:
        cache: dict = {}
        rows = [recheck(row, repo, runner=recheck_runner, cache=cache) for row in rows]
    counts: dict[str, int] = {}
    sources: dict[str, int] = {}
    for row in rows:
        counts[row["state"]] = counts.get(row["state"], 0) + 1
        sources[row.get("source", "")] = sources.get(row.get("source", ""), 0) + 1
    facts = {
        "repo": str(repo),
        "refusals": len(rows),
        "counts": counts,
        "sources": sources,
        "rows": rows,
    }
    if recheck_tests:
        rechecked: dict[str, int] = {}
        for row in rows:
            key = row.get("recheck", "untested")
            rechecked[key] = rechecked.get(key, 0) + 1
        facts["recheck_counts"] = rechecked
    return facts


def unfiled(rows: list[dict], ledger_text: str, actionable_only: bool = False) -> list[dict]:
    """The failed landings that `channels/items.jsonl` has never named.

    Why this exists (2026-11-06, Dmitri). Recognising a crashed or conflicted landing was only half
    the repair: the point of seeing it is that somebody can be handed it. `item_ledger.py --collect`
    builds its rows from the runs it notices, so a run it never noticed is a run no queue can hold —
    and nothing anywhere compared the two sets. So this does the comparison, as a set operation on
    one field: a row is *filed* if its run id appears anywhere in the ledger's text (the id is used
    as `id`, as `source_run`, and inside reason strings, so a field-by-field scan would miss rows
    that are filed under another name).

    `actionable_only` keeps the rows that name work and do not have it: `open` and `partial` with at
    least one claimed path. That is the slice a human or a wake can act on; `reconciled` rows need
    nothing and `no-claim` rows have nothing to chase from the run record alone.
    """
    out = [row for row in rows if row.get("run") and row["run"] not in (ledger_text or "")]
    if actionable_only:
        out = [row for row in out if row.get("state") in ("open", "partial") and row.get("claimed")]
    return out


def render(facts: dict) -> str:
    counts = facts["counts"]
    rechecking = "recheck_counts" in facts
    lines = [
        f"{facts['refusals']} failed landing(s) on disk; checked against {facts['repo']}",
        "  by state: " + (", ".join(f"{k} {v}" for k, v in sorted(counts.items())) if counts else "none"),
    ]
    sources = facts.get("sources") or {}
    if sources:
        lines.append("  by source: " + ", ".join(f"{k or '?'} {v}" for k, v in sorted(sources.items())))
    if rechecking:
        rc = facts["recheck_counts"]
        lines.append("  recheck: " + (", ".join(f"{k} {v}" for k, v in sorted(rc.items())) or "none"))
    lines.append("")
    order = {"open": 0, "partial": 1, "no-claim": 2, "reconciled": 3}
    for row in sorted(facts["rows"], key=lambda r: (order.get(r["state"], 9), r["run"])):
        detail = ""
        if row["state"] == "partial":
            detail = "  missing: " + ", ".join(row["missing"][:4])
            if len(row["missing"]) > 4:
                detail += f" (+{len(row['missing']) - 4} more)"
        line = (
            f"  [{row['state']:<10}] {row['bot']:<7} {row['run']}  "
            f"{row['on_main']}/{row['claimed']} on main{detail}"
        )
        source = row.get("source", "")
        if source and source != "gate":
            # The gate's refusals are the majority and their shape is known; the rest are the ones
            # this survey could not see before 2026-11-06, so they are named on the line.
            line += f"  via {source}"
        if rechecking:
            verdict = row.get("recheck", "untested")
            line += f"  recheck: {verdict}"
            # Only the tests that still bite say anything; `green-now` details are noise on a line
            # meant to be scanned for what is left to do — except that a mixed row (one test green,
            # one gone) is labelled `green-now`, so the state word is printed and not just the
            # runner's last line. Measured live 2026-11-05: `recheck: green-now  test_status_census.py:
            # not in this checkout` read as a contradiction until the state was named.
            biting = []
            for name, state, why in row.get("recheck_detail", []):
                if state == "green-now":
                    continue
                biting.append(f"{name} ({state})" + (f": {why}" if state in ("red-now", "error") else ""))
            if biting:
                line += "  " + "; ".join(biting)[:120]
        lines.append(line)
        if row["state"] in ("open", "partial", "no-claim") and row["reason"]:
            lines.append(f"               reason: {row['reason'][:110]}")
    if "unfiled" in facts:
        named = facts["unfiled"]
        lines += ["", f"never named in {facts.get('ledger', 'the ledger')}: {len(named)} of "
                      f"{facts['refusals']}"]
        for row in sorted(named, key=lambda r: r["run"]):
            lines.append(
                f"  [{row['state']:<10}] {row['bot']:<10} {row['run']}  "
                f"{row['on_main']}/{row['claimed']} on main  via {row.get('source') or '?'}"
            )
            if row.get("missing"):
                lines.append("               missing: " + ", ".join(row["missing"][:3]))
        if not named:
            lines.append("  none — every failed landing on disk is in the ledger")
    lines += [
        "",
        "reconciled = the refusal was made good later; do not redo that work.",
        "open/partial = real missing work; the run's reason above is the starting point.",
        "no-claim = a refusal with nothing named; only the run's own transcript can say what it was.",
    ]
    if rechecking:
        lines.append(
            "recheck = whether the test the refusal blamed still fails here today (green-now, "
            "red-now, gone, untested); it is a statement about today, not a verdict on the day."
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs-root", action="append", default=None,
                    help="directory holding <bot>/tick-state/runs (repeatable); "
                         "defaults to ~/LLM")
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parent.parent),
                    help="the checkout whose files are the test of 'reached main'")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--recheck", action="store_true",
                    help="re-run the test files each refusal blames and label it "
                         "green-now / red-now / gone / untested (slow: one run per named test, "
                         "cached across refusals)")
    ap.add_argument("--source", default="",
                    help="only rows whose source matches: `gate` is the test gate's refusals; "
                         "any other value is the land field's own word (landing_error, conflict, "
                         "push_failed, refused_dirty_tree, commit_failed, lock_timeout)")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when any refusal is still open or partial")
    ap.add_argument("--unfiled", action="store_true",
                    help="also list failed landings that channels/items.jsonl has never named — "
                         "the ones no queue can hold")
    ap.add_argument("--actionable-only", action="store_true",
                    help="with --unfiled: only rows with work named and not on main "
                         "(open/partial with a claim)")
    ap.add_argument("--ledger", default="",
                    help="the ledger to compare against (default: <repo>/channels/items.jsonl)")
    args = ap.parse_args(argv)

    roots = [Path(os.path.expanduser(r)) for r in (args.runs_root or ["~/LLM"])]
    repo = Path(args.repo).resolve()
    facts = survey(roots, repo, recheck_tests=args.recheck, source=args.source)
    if args.unfiled:
        ledger = Path(args.ledger) if args.ledger else repo / "channels" / "items.jsonl"
        facts["ledger"] = str(ledger)
        facts["unfiled"] = unfiled(facts["rows"], read(ledger),
                                   actionable_only=args.actionable_only)
    if args.json:
        print(json.dumps(facts, indent=2))
    else:
        print(render(facts))
    if args.strict and (facts["counts"].get("open") or facts["counts"].get("partial")):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
