#!/usr/bin/env python3
# Owner: Desi (landing gate subsystem). Filed 2026-10-19.
"""What the failure gate blamed, and whether the blame survives a second look.

Why this exists (2026-10-19, Desi). By this date every wake in four bodies was being refused at
the landing gate, and the only durable trace of a refusal is one line in a run directory:

    this run's diff introduced new failures: test_cited_path_gate.py, test_ci_spend_audit.py

`scripts/landing_refusals.py` (Dmitri, same day) answers a different question — whether the run's
*claimed paths* reached `main` — and classifies the delivery: reconciled / partial / open /
no-claim. This file answers the question that line leaves open: **was the blame true?** Three
things can make a named test a false accusation, and the gate cannot tell them apart, because it
measures only two instants of one shared checkout (`failing_tests()` before the patch, after it):

  * a test that fails intermittently — pass before, fail after, and the diff had nothing to do
    with it (`test_drive_bridge_status.py`: a documented race in `mount_unreadable`);
  * a tree-wide audit tripped by the run's *content* rather than its code — a report that cites
    an artefact nobody landed fails `test_cited_path_gate.py`, and the run never read that rule;
  * a run cut off before it could run the suite, leaving its own change to a pinned contract
    (a verdict string) to be found by the gate instead of by the preflight.

So the census walks every refusal on the disk and classifies the *blame*, from the run's own patch
rather than from memory:

    own_new_test        the run created this test and it failed — true blame, and the gate's
                        undo threw the file away, so main has never seen it
    edited_by_run       the named test is a file the run's own patch modifies
    untouched_in_tree   the named test exists on main and the run did not touch it: an audit, a
                        contract pin, or a flake — only a re-run can say which
    phantom             not in the tree and not in the run's patch: a name no tree held

With `--repro`, each refusal's patch is applied to a throwaway worktree at today's `HEAD` and the
named tests are re-run there. That separates "confirmed" (the refusal reproduces from the patch
alone) from "not-reproducible" (the blame was a flake or the shared checkout's own state). A patch
that no longer applies is reported as `base_moved` — not a verdict about the run.

Read-only on every run directory. It never edits a patch, a report, or `landing_failed.txt`.
Writes nothing outside a temporary worktree it removes.

Usage:
  python3 scripts/refusal_causes.py                       # the census, no re-runs
  python3 scripts/refusal_causes.py --repro --limit 12    # re-run the newest 12 refusals
  python3 scripts/refusal_causes.py --repro --repro-timeout 120
  python3 scripts/refusal_causes.py --json

Exit status: 0 = census produced; 2 = usage or setup error.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RUNS = str(Path.home() / "LLM" / "*" / "tick-state" / "runs")
REFUSAL_LINE = re.compile(r"this run's diff introduced new failures:\s*(.+)", re.S)
TIMEOUT_NOTE = re.compile(r"\s*\(timeout\)\s*$")
TEST_NAME = re.compile(r"^tests/test_[A-Za-z0-9_]+\.py$")

BLAME_LABELS = ("own_new_test", "edited_by_run", "untouched_in_tree", "phantom")


def read(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except OSError:
        return ""


def blamed_tests(text: str) -> list[tuple[str, bool]]:
    """Names the refusal blames, and whether it recorded a timeout for each.

    The gate writes one comma-separated line (`", ".join(sorted(after - before))`); a timeout is
    marked by the string `" (timeout)"` appended to the stem, not to the file name.
    """
    match = REFUSAL_LINE.search(text or "")
    if not match:
        return []
    out: list[tuple[str, bool]] = []
    for raw in match.group(1).splitlines()[0].split(","):
        item = raw.strip()
        if not item:
            continue
        timed_out = bool(TIMEOUT_NOTE.search(item))
        item = TIMEOUT_NOTE.sub("", item)
        if not item.endswith(".py"):
            item += ".py"
        out.append((item, timed_out))
    return out


def patch_paths(patch_text: str) -> tuple[set[str], set[str]]:
    """(every path the patch touches, the paths it creates) — from `diff --git` headers."""
    touched: set[str] = set()
    created: set[str] = set()
    current = None
    for line in (patch_text or "").splitlines():
        if line.startswith("diff --git "):
            parts = line.split()
            if len(parts) >= 4 and parts[3].startswith("b/"):
                current = parts[3][2:]
                touched.add(current)
            else:
                current = None
        elif line.startswith("new file mode") and current:
            created.add(current)
    return touched, created


def blame_class(name: str, repo: Path, touched: set[str], created: set[str]) -> str:
    path = "tests/" + name
    present = (Path(repo) / path).is_file()
    if not present:
        return "own_new_test" if path in created else "phantom"
    return "edited_by_run" if path in touched else "untouched_in_tree"


def run_dirs(pattern: str) -> list[Path]:
    found = [Path(p) for p in glob.glob(os.path.join(pattern, "*", "landing_failed.txt"))]
    return sorted(found, key=lambda p: p.parent.name)


def census(rows_pattern: str, repo: Path = REPO_ROOT, limit: int = 0) -> list[dict]:
    """One row per refusal on disk, blame classified from the run's own patch."""
    out: list[dict] = []
    for failed in run_dirs(rows_pattern):
        run_dir = failed.parent
        blamed = blamed_tests(read(failed))
        patch = run_dir / "changes.patch"
        touched, created = patch_paths(read(patch))
        items = [
            {
                "test": name,
                "timeout": timed_out,
                "blame": blame_class(name, repo, touched, created),
            }
            for name, timed_out in blamed
        ]
        out.append(
            {
                "amigo": run_dir.parent.parent.parent.name.replace("-bot", ""),
                "run": run_dir.name,
                "run_dir": str(run_dir),
                "has_patch": patch.is_file(),
                "patch_paths": sorted(touched),
                "blamed": items,
            }
        )
    out.sort(key=lambda row: row["run"], reverse=True)
    return out[:limit] if limit else out


def _child_env() -> dict:
    env = dict(os.environ)
    # The suite must not write into the real spend ledger while being probed.
    env["CI_USAGE_PATH"] = os.path.join(tempfile.gettempdir(), "refusal-census-usage.jsonl")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return env


def _tail(output: str, limit: int = 400) -> str:
    """The most informative end of a failure: the assertion or the error, else the last lines."""
    lines = [ln.rstrip() for ln in (output or "").splitlines() if ln.strip()]
    picked = [ln for ln in lines if ln.startswith(("AssertionError", "FAIL:", "Error"))]
    chosen = picked[-1] if picked else (lines[-1] if lines else "")
    return chosen[:limit]


def _run_named(tree: Path, names: list[str], timeout: int, env: dict) -> dict:
    """Run each named test file inside `tree`; state is passes / fails / timeout / missing."""
    out = {}
    for name in names:
        path = tree / "tests" / name
        if not path.is_file():
            out[name] = {"state": "missing", "tail": ""}
            continue
        try:
            proc = subprocess.run(
                [sys.executable, str(path)], cwd=str(tree), capture_output=True, text=True,
                timeout=timeout, env=env,
            )
            state = "fails" if proc.returncode != 0 else "passes"
            tail = "" if proc.returncode == 0 else _tail((proc.stdout or "") + (proc.stderr or ""))
        except subprocess.TimeoutExpired:
            state, tail = "timeout", ""
        out[name] = {"state": state, "tail": tail}
    return out


def _verdict(states: set[str]) -> str:
    failing = states & {"fails", "timeout"}
    if failing and "passes" not in states and "missing" not in states:
        return "confirmed"
    return "partial" if failing else "not-reproducible"


def repro(run_dir: Path, repo: Path = REPO_ROOT, timeout: int = 120) -> dict:
    """Apply this run's patch to a throwaway worktree and re-run only the tests it was blamed for.

    Two things can stop the patch applying, and they mean opposite things:

      * every path the patch *creates* already exists at `HEAD` — the work landed under a later
        run, so the refusal is moot (`already_applied`); the tests are still run, on the tree that
        now holds that work, and a passing suite is the evidence that nothing was lost;
      * the patch's base has moved in some other file (`scripts/README.md`, a to-do list, an
        append-only ledger): the census cannot say anything about the run from here
        (`base_moved`), and the tests are run on `HEAD` anyway so the row still shows whether that
        name is red on `main` today.

    The worktree is always removed: a second checkout left behind is the next wake's foreign dirt.
    """
    run_dir = Path(run_dir)
    blamed = [name for name, _ in blamed_tests(read(run_dir / "landing_failed.txt"))]
    result = {"verdict": "unchecked", "tree": "none", "detail": "", "tests": {}}
    patch = run_dir / "changes.patch"
    if not blamed or not patch.is_file():
        result["verdict"] = "no_claim" if not blamed else "no_patch"
        return result
    touched, created = patch_paths(read(patch))
    tmp = tempfile.mkdtemp(prefix="refusal-repro-")
    tree = Path(tmp) / "tree"
    try:
        add = subprocess.run(
            ["git", "-C", str(repo), "worktree", "add", "--detach", str(tree), "HEAD"],
            capture_output=True, text=True,
        )
        if add.returncode != 0:
            result.update(verdict="setup_error", detail=(add.stderr or "").strip()[:300])
            return result
        env = _child_env()
        applied = subprocess.run(
            ["git", "-C", str(tree), "apply", str(patch)], capture_output=True, text=True
        )
        applied_3 = False
        if applied.returncode != 0:
            three = subprocess.run(
                ["git", "-C", str(tree), "apply", "-3", str(patch)], capture_output=True, text=True
            )
            applied_3 = three.returncode == 0
            if applied_3:
                applied = three
        if applied.returncode == 0 or applied_3:
            result["tree"] = "patched" + ("-3way" if applied_3 else "")
            result["tests"] = _run_named(tree, blamed, timeout, env)
            result["verdict"] = _verdict({e["state"] for e in result["tests"].values()})
            return result
        # The patch cannot be applied. Only one of the two reasons is a fact about the work.
        absent = [p for p in created if not (tree / p).is_file()]
        result["tree"] = "head"
        result["detail"] = (applied.stderr or "").strip().splitlines()[-1][:300]
        result["tests"] = _run_named(tree, blamed, timeout, env)
        if not absent:
            result["verdict"] = "already_applied"
            result["tree"] = "head-with-work"
        else:
            result["verdict"] = "base_moved"
        if any(e["state"] in ("fails", "timeout") for e in result["tests"].values()):
            result["verdict"] += "+red_on_main"
        return result
    finally:
        subprocess.run(
            ["git", "-C", str(repo), "worktree", "remove", "--force", str(tree)],
            capture_output=True, text=True,
        )
        shutil.rmtree(tmp, ignore_errors=True)


def summarise(rows: list[dict]) -> dict:
    """Counts the report leads with: blame labels, named tests, and (if run) verdicts."""
    by_blame: dict[str, int] = {label: 0 for label in BLAME_LABELS}
    by_test: dict[str, int] = {}
    by_verdict: dict[str, int] = {}
    refusals_with_own_test = 0
    for row in rows:
        labels = set()
        for item in row["blamed"]:
            by_blame[item["blame"]] = by_blame.get(item["blame"], 0) + 1
            by_test[item["test"]] = by_test.get(item["test"], 0) + 1
            labels.add(item["blame"])
        if "own_new_test" in labels:
            refusals_with_own_test += 1
        verdict = (row.get("repro") or {}).get("verdict")
        if verdict:
            by_verdict[verdict] = by_verdict.get(verdict, 0) + 1
    return {
        "refusals": len(rows),
        "blame": by_blame,
        "distinct_tests": len(by_test),
        "top_tests": sorted(by_test.items(), key=lambda kv: (-kv[1], kv[0]))[:12],
        "refusals_with_own_new_test": refusals_with_own_test,
        "verdicts": by_verdict,
    }


def render(rows: list[dict], summary: dict) -> str:
    lines = [
        "# Landing refusals — what the gate blamed",
        "",
        "%d refusal(s) on disk; %d distinct test file(s) named."
        % (summary["refusals"], summary["distinct_tests"]),
        "",
        "| blame | count |",
        "|---|---|",
    ]
    for label in BLAME_LABELS:
        lines.append("| %s | %d |" % (label, summary["blame"].get(label, 0)))
    lines += ["", "| test | refusals naming it |", "|---|---|"]
    for name, count in summary["top_tests"]:
        lines.append("| %s | %d |" % (name, count))
    if summary["verdicts"]:
        lines += ["", "| re-run verdict | refusals |", "|---|---|"]
        for verdict, count in sorted(summary["verdicts"].items()):
            lines.append("| %s | %d |" % (verdict, count))
    lines += ["", "## Every refusal", "", "| amigo | run | blamed | blame | verdict |", "|---|---|---|---|---|"]
    for row in rows:
        blamed = ", ".join(
            item["test"] + (" (timeout)" if item["timeout"] else "") for item in row["blamed"]
        ) or "(nothing named)"
        labels = ", ".join(sorted({item["blame"] for item in row["blamed"]})) or "-"
        verdict = (row.get("repro") or {}).get("verdict", "-")
        lines.append("| %s | %s | %s | %s | %s |" % (row["amigo"], row["run"], blamed, labels, verdict))
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", default=DEFAULT_RUNS, help="glob of run directories")
    parser.add_argument("--limit", type=int, default=0, help="newest N refusals only (0 = all)")
    parser.add_argument("--repro", action="store_true", help="re-run the blamed tests in a worktree")
    parser.add_argument("--repro-timeout", type=int, default=120, help="seconds per test file")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    if not glob.glob(os.path.join(args.runs, "*", "landing_failed.txt")):
        print("no refusals found under %s" % args.runs, file=sys.stderr)
        return 2
    rows = census(args.runs, REPO_ROOT, limit=args.limit)
    if args.repro:
        for row in rows:
            started = time.time()
            row["repro"] = repro(Path(row["run_dir"]), REPO_ROOT, timeout=args.repro_timeout)
            row["repro"]["seconds"] = round(time.time() - started, 1)
    summary = summarise(rows)
    if args.json:
        print(json.dumps({"summary": summary, "rows": rows}, indent=2))
    else:
        print(render(rows, summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
