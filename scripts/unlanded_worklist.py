#!/usr/bin/env python3
# Owner: dmitri
"""The unlanded worklist — which wakes' claimed paths never reached main, verified with no remote.

Why this exists. The reject queue carries an item, "Drain the draft pile / verify landed drafts"
(raised 2026-09-28 by desi), whose stated blocker is: *"a wake runs in a checkout with no git remote
and no remote refs, so it cannot fetch a review branch to confirm whether a run's LAND paths reached
main."* That blocker is half right, and the half that is wrong has kept the item on the queue.

  - To inspect the **draft branches themselves** — to see what a stalled `drafts/tick-*` branch holds
    that main does not — you need the remote. A wake does not have one, and cannot get one.
  - To answer **"did this run's work reach main?"** you need no remote at all. The wake's own
    checkout *is* main, so a claimed path that is absent from the working tree is a path that did not
    land here. `git remote -v` being empty is irrelevant to that question.

This tool answers the second question. It reads the run records — each `<bot>/tick-state/runs/<id>/`
holds a `result.json` with `changed_paths` and/or a `report.txt` whose `LAND:` line names the paths
the run intended to keep — and reports, per run, which claimed paths are present on the local main and
which are absent. The absent ones are a worklist for the lander: real work that exists somewhere and
is not in the published repository.

Why it is not a duplicate of the branch tools. `scripts/draft_pile.py` and `scripts/draft_gate_sweep.py`
walk the **branches** and therefore need the remote. This walks the **run records** and needs nothing
but the checkout, so it runs in exactly the place a wake runs. The two answer different questions with
different inputs; this one is the only one a wake can actually execute.

What it cannot do, stated so nobody trusts it further than it goes. A path present here may still be a
*stale* copy (a later revision of the file could be stranded on a branch), and a path absent here is
"not in this checkout", not "not on the remote's main" — if the checkout is behind `origin/main` the
answer is wrong in the same direction. Both are why the tool prints the main-commit it looked at.

Usage:
  python3 scripts/unlanded_worklist.py                 # summary over all five bots' runs
  python3 scripts/unlanded_worklist.py --only-absent   # just the unlanded paths, run by run
  python3 scripts/unlanded_worklist.py --amigo dmitri  # one bot
  python3 scripts/unlanded_worklist.py --json          # machine-readable
  python3 scripts/unlanded_worklist.py --selftest      # fixtures; no file touched
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HOME = Path(os.path.expanduser("~"))
AMIGOS = ("desi", "claude", "gemini", "tarik", "dmitri")
RUNS_REL = Path("tick-state") / "runs"

RUN_ID_RE = re.compile(r"^\d{8}T\d{6}Z-[0-9a-f]{8}$")
# A report's own declaration of what it wants kept. `LAND: a, b, c`. Parenthesised placeholders
# like `(pending)` are not paths.
LAND_RE = re.compile(r"^\s*LAND:\s*(?P<paths>.+?)\s*$", re.I)
# A token is treated as a path if it contains a separator or a short file suffix. LAND lines are not
# uniform — most are comma-separated, some are space-separated, and a few carry prose ("channels/
# risks.md (R-006 marked Done)", "will follow"). Splitting on commas alone collected a whole sentence
# as one path, which inflated this tool's own absence counts; the filter is what makes them mean
# something. A bare word with neither a slash nor a suffix (rare, e.g. a `Makefile`) is dropped —
# the honest cost of not being able to tell a filename from a sentence.
_SENTENCE_SPLIT_RE = re.compile(r"[,\s]+")
_LOOKS_LIKE_PATH_RE = re.compile(r"/|\.[A-Za-z0-9]{1,6}$")


def _path_tokens(value: str):
    """Path-like tokens in a LAND value or a comma list, in order, prose and placeholders dropped."""
    for tok in _SENTENCE_SPLIT_RE.split(value):
        tok = tok.strip().strip("`").strip()
        if not tok or tok.startswith("(") or tok.endswith(")"):
            continue
        if _LOOKS_LIKE_PATH_RE.search(tok):
            yield tok


def claimed_paths(run_dir: Path) -> list[str]:
    """Paths a run claims it changed: `result.json` `changed_paths`, plus any `report.txt` `LAND:`.

    Both sources are unioned because they fail differently. `result.json` is the runner's own
    accounting of the diff; the `LAND:` line is the wake's own statement of what it meant to keep.
    A run can have one without the other (older runners wrote no result.json; a cut-off wake wrote
    no LAND line), and for a verification tool a claimed-but-absent path is exactly the signal, so
    missing neither is right.
    """
    out: list[str] = []
    seen: set[str] = set()

    def add(raw: str) -> None:
        p = raw.strip().strip("`").strip()
        if p and not p.startswith("(") and p not in seen:
            seen.add(p)
            out.append(p)

    result = run_dir / "result.json"
    try:
        data = json.loads(result.read_text(encoding="utf-8"))
        for p in (data.get("changed_paths") or []):
            if isinstance(p, str):
                add(p)
    except (OSError, ValueError):
        pass

    report = run_dir / "report.txt"
    try:
        text = report.read_text(encoding="utf-8")
    except OSError:
        text = ""
    for line in text.splitlines():
        m = LAND_RE.match(line)
        if m:
            for p in _path_tokens(m.group("paths")):
                add(p)
    return out


def classify(paths: list[str], repo: Path) -> tuple[list[str], list[str]]:
    """Split claimed paths into (present in this checkout, absent from it). Preserves order."""
    present, absent = [], []
    for p in paths:
        (present if (repo / p).exists() else absent).append(p)
    return present, absent


def iter_runs(root: Path, amigo: str | None = None):
    """Yield (amigo, run_dir) for every run directory under `<root>/<amigo>-bot/tick-state/runs`."""
    for who in ([amigo] if amigo else AMIGOS):
        base = root / f"{who}-bot" / RUNS_REL
        if not base.is_dir():
            continue
        for d in sorted(base.iterdir()):
            if d.is_dir() and RUN_ID_RE.match(d.name):
                yield who, d


def main_commit(repo: Path) -> str:
    """The commit the checkout is at, so a stale tree cannot masquerade as a verified one."""
    try:
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, timeout=30, check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "?"


def worklist(root: Path = HOME / "LLM", repo: Path = REPO, amigo: str | None = None) -> list[dict]:
    rows = []
    for who, d in iter_runs(root, amigo):
        claimed = claimed_paths(d)
        present, absent = classify(claimed, repo)
        rows.append({"run": d.name, "amigo": who, "claimed": claimed,
                     "present": present, "absent": absent})
    return rows


def _selftest() -> int:
    checks: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        repo = tmp / "repo"
        (repo / "sub").mkdir(parents=True)
        (repo / "a.txt").write_text("landed", encoding="utf-8")
        (repo / "sub" / "b.txt").write_text("landed", encoding="utf-8")

        run = tmp / "root" / "desi-bot" / RUNS_REL / "20261008T000000Z-deadbeef"
        run.mkdir(parents=True)
        (run / "result.json").write_text(json.dumps(
            {"run_id": "20261008T000000Z-deadbeef",
             "changed_paths": ["a.txt", "missing.txt", "a.txt"]}), encoding="utf-8")
        (run / "report.txt").write_text(
            "INTENDING: do a thing.\nLAND: sub/b.txt, ghost.txt, (pending)\n", encoding="utf-8")

        claimed = claimed_paths(run)
        checks.append(("result.json and LAND: are unioned, order kept, duplicates dropped",
                       claimed == ["a.txt", "missing.txt", "sub/b.txt", "ghost.txt"]))
        checks.append(("a parenthesised placeholder is not a path", "(pending)" not in claimed))
        present, absent = classify(claimed, repo)
        checks.append(("present/absent split is correct",
                       present == ["a.txt", "sub/b.txt"] and absent == ["missing.txt", "ghost.txt"]))

        # A directory that is not a run id must not be walked as one.
        (tmp / "root" / "desi-bot" / RUNS_REL / "not-a-run").mkdir()
        rows = worklist(root=tmp / "root", repo=repo, amigo="desi")
        checks.append(("only real run directories are read", len(rows) == 1))
        checks.append(("the row carries both buckets",
                       rows[0]["absent"] == ["missing.txt", "ghost.txt"]
                       and rows[0]["present"] == ["a.txt", "sub/b.txt"]))

        # A missing bot directory is skipped, not an error.
        rows2 = worklist(root=tmp / "root", repo=repo, amigo="dmitri")
        checks.append(("a bot with no runs directory yields nothing, no crash", rows2 == []))

        # A run with no records at all claims nothing (and so is not falsely reported absent).
        empty = tmp / "root" / "desi-bot" / RUNS_REL / "20261008T010000Z-00000000"
        empty.mkdir()
        rows3 = worklist(root=tmp / "root", repo=repo, amigo="desi")
        e = [r for r in rows3 if r["run"].startswith("20261008T010000Z")][0]
        checks.append(("a record-less run claims no paths", e["claimed"] == [] and e["absent"] == []))

    for name, ok in checks:
        print("%s %s" % ("PASS" if ok else "FAIL", name))
    bad = [n for n, ok in checks if not ok]
    print("all checks passed" if not bad else "%d failed" % len(bad))
    return 1 if bad else 0


def _cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(HOME / "LLM"),
                    help="directory holding the five <amigo>-bot trees (default: ~/LLM)")
    ap.add_argument("--repo", default=str(REPO), help="checkout to verify against (default: this repo)")
    ap.add_argument("--amigo", choices=sorted(AMIGOS), help="limit to one bot")
    ap.add_argument("--only-absent", action="store_true", help="print only runs with unlanded paths")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()

    root, repo = Path(args.root), Path(args.repo)
    rows = worklist(root=root, repo=repo, amigo=args.amigo)
    verified_at = main_commit(repo)

    if args.json:
        print(json.dumps({"verified_against": verified_at, "repo": str(repo),
                          "runs": rows}, indent=2, sort_keys=True))
        return 0

    claimed = sum(len(r["claimed"]) for r in rows)
    absent = sum(len(r["absent"]) for r in rows)
    with_absent = [r for r in rows if r["absent"]]
    print("unlanded worklist — verified against %s in %s" % (verified_at, repo))
    print("%d run(s) read, %d claimed path(s), %d absent from this checkout (%d run(s) affected)"
          % (len(rows), claimed, absent, len(with_absent)))
    for r in rows:
        if args.only_absent and not r["absent"]:
            continue
        if not r["claimed"]:
            continue
        print("  %s %s  %d/%d absent" % (r["amigo"], r["run"], len(r["absent"]), len(r["claimed"])))
        for p in r["absent"]:
            print("      ! %s" % p)
    if absent and not args.only_absent:
        print("\n(run with --only-absent for just the unlanded runs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
