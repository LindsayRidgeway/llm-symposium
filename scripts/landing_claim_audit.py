#!/usr/bin/env python3
"""Which machine-closed ledger rows certify a landing that never carried their work.

Owner: Desi.  Written 2026-11-10.

**The two rules this measures.** The ledger closes work without a reader in two ways,
and both are statements about the repository that are read as statements about the work:

1. `auto:land` — "landed on main (lander's test gate passed)". It keys on the run id
   appearing in *any* `land(wake): work from run <id>` commit, so a run that landed its
   report and lost the path carrying its work is certified exactly like a run that
   landed everything. Measured case, filed 2026-11-09: run `20261108T225315Z-8533d17c`
   changed a test file, its report says the repair is in, the row is `accomplished` /
   `auto:land`, and `git log --all -- tests/test_workflow_commands_exist.py` shows no
   commit from that run at all — only the 2026-10-28 one.
2. `auto:path` — "every path this item names is present on main". A path that existed
   *before* the run is present whatever became of the run's change, so a lost
   modification and a clean landing are indistinguishable to that check. Its known
   inverse case is the deletion patch (2026-11-09: 2 of 2 rows closed on the presence
   of the files they meant to remove).

**What this does.** One pass over the log, no network, no writes: for every row the
machines closed, ask which of the paths the row *names* were actually touched by a
commit naming that run. Paths are compared to what the commit changed, not to what
exists on disk. A row whose named paths none of its run's commits touched is **hollow**
— the certification names nothing the run did. A row where only some were touched is
**partial** — the landing was real but smaller than the row claims.

`channels/items.jsonl` is subtracted from every row, because every landing touches it
and its presence says nothing (the same reason `item_ledger.reconcile_paths` refuses to
close a row whose only artefact is the ledger).

**What it is not.** It does not repair a row and it writes nothing: the ledger is
append-only and a state word is a reviewer's call. It prints the rows, the paths each
run's commits actually carried, and exits 1 when anything is hollow so a test can run
it as an alarm.

Usage:  python3 scripts/landing_claim_audit.py [--json] [--limit N] [--show-all]
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
LEDGER = REPO / "channels" / "items.jsonl"
LEDGER_PATH = "channels/items.jsonl"
MACHINE_REVIEWERS = ("auto:land", "auto:path", "auto")
MARK = "@@commit@@"


def commits_by_run(repo: pathlib.Path) -> dict[str, set[str]]:
    """Run id -> the paths the commits naming it actually changed. One git call."""
    out = subprocess.run(
        ["git", "-C", str(repo), "log", "--all", "--name-only",
         f"--pretty=format:{MARK}%s"],
        capture_output=True, text=True, timeout=300, check=True,
    ).stdout
    found: dict[str, set[str]] = collections.defaultdict(set)
    current: list[str] = []
    for line in out.splitlines():
        if line.startswith(MARK):
            current = [tok for tok in line[len(MARK):].split() if tok[:1].isdigit()]
            # A subject may name one run id; the lander's does exactly one.
            continue
        if not line.strip():
            continue
        for run_id in current:
            found[run_id].add(line.strip())
    return found


def latest_rows(path: pathlib.Path, machine_only: bool = False) -> dict[str, dict]:
    """The row in force for each id — or, with machine_only, the last *machine* row.

    `machine_only` exists because a reader's verdict replaces the machine's claim in the
    ledger: run `20261108T225315Z-8533d17c` is the measured case, and its false
    `auto:land` row was hidden the moment its reading was verdicted. Auditing only the
    rows in force therefore measures the survivors of the defect, not its incidence.
    """
    rows: dict[str, dict] = {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if not (isinstance(rec, dict) and rec.get("id")):
                continue
            if machine_only:
                if not (rec.get("state") == "accomplished"
                        and rec.get("reviewer") in MACHINE_REVIEWERS):
                    continue
            rows[rec["id"]] = rec  # last write wins: the ledger is append-only
    return rows


def audit(rows: dict[str, dict], commits: dict[str, set[str]]) -> list[dict]:
    findings = []
    for run_id, rec in rows.items():
        if rec.get("state") != "accomplished":
            continue
        if rec.get("reviewer") not in MACHINE_REVIEWERS:
            continue
        named = [p for p in (rec.get("paths") or [])
                 if isinstance(p, str) and p != LEDGER_PATH]
        if not named:
            continue
        carried = set(commits.get(run_id, ()))
        touched = [p for p in named if p in carried]
        if not touched:
            findings.append({"id": run_id, "amigo": rec.get("amigo"),
                             "reviewer": rec.get("reviewer"), "kind": "hollow",
                             "named": named, "touched": [], "title": rec.get("title", "")[:90]})
        elif len(touched) < len(named):
            findings.append({"id": run_id, "amigo": rec.get("amigo"),
                             "reviewer": rec.get("reviewer"), "kind": "partial",
                             "named": named, "touched": touched,
                             "title": rec.get("title", "")[:90]})
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledger", type=pathlib.Path, default=LEDGER)
    ap.add_argument("--repo", type=pathlib.Path, default=REPO)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--limit", type=int, default=15)
    ap.add_argument("--show-all", action="store_true")
    ap.add_argument("--machine-rows", action="store_true",
                    help="audit the last machine row per id even where a reader has since verdicted it")
    args = ap.parse_args()

    rows = latest_rows(args.ledger, machine_only=args.machine_rows)
    commits = commits_by_run(args.repo)
    findings = audit(rows, commits)
    hollow = [f for f in findings if f["kind"] == "hollow"]
    partial = [f for f in findings if f["kind"] == "partial"]
    checked = sum(1 for r in rows.values()
                  if r.get("state") == "accomplished"
                  and r.get("reviewer") in MACHINE_REVIEWERS)

    if args.json:
        print(json.dumps({"checked": checked, "hollow": hollow, "partial": partial},
                         indent=1, sort_keys=True))
    else:
        print(f"{checked} machine-closed rows; {len(hollow)} hollow, {len(partial)} partial")
        for label, group in (("HOLLOW", hollow), ("PARTIAL", partial)):
            for f in (group if args.show_all else group[:args.limit]):
                print(f"\n{label}  {f['id']}  ({f['amigo']}, {f['reviewer']})")
                print(f"  names {len(f['named'])}, carried by the run's commits: {len(f['touched'])}")
                for p in f["named"]:
                    print(f"    {'+' if p in f['touched'] else '-'} {p}")
                if f["title"]:
                    print(f"  \"{f['title']}\"")
            if not args.show_all and len(group) > args.limit:
                print(f"\n  ... {len(group) - args.limit} more {label.lower()} row(s); --show-all")
    return 1 if hollow else 0


if __name__ == "__main__":
    sys.exit(main())
