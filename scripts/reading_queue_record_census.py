#!/usr/bin/env python3
# Owner: dmitri
"""Can the never-read pile actually be read? A census of what a reader would find on this machine.

Why this exists, and why it is not a duplicate. Three tools already touch this ground and none of
them answers this question:

  - `channels/item_ledger.py --reading-queue <amigo>` names the items (the pile: work the landing
    gate closed and no model ever opened). It says *who* owes a reading, not whether the reading
    can be done.
  - `scripts/unlanded_worklist.py` asks, per run, which claimed paths are absent from the local
    main, read out of the run records.
  - `scripts/wake_review_queue.py` and its test pin the queue's routing, not its contents.

The question this answers is the one a wake actually hits at the moment it decides whether to
read: *if I open this item now, is there anything on this machine to judge it by?* Measured
2026-10-26 over dmitri's 110 never-read items, because four consecutive wakes were cut off while
judging that pile and at least six of their verdicts said "postponed: the record is absent from
main".

That reason is half true and it was being read as if it were wholly true. A run that is cut off, or
whose patch is refused by the lander, leaves nothing on `main` — but it usually leaves both its own
`report.txt` and the files it wrote in `~/LLM/<amigo>-bot/tick-state/runs/<id>/`. `main` is the
shared copy, not the only copy. So "absent from main" describes where a document is, never whether
the work in it can be examined. The wake instruction already says this about unlanded paths
("UNLANDED IS NOT MISSING"); nobody had measured how far it holds for the reading queue.

The measurement, 2026-10-26, for `--amigo dmitri` over the 110 items named to him:

  - every named path present in this checkout: **108 / 110** — the artefacts are here, so the thing
    itself can be read and its numbers re-derived;
  - a written record on disk (the author's `report.txt`, substantive or not): **102 / 110**;
  - neither an artefact nor a record: **0 / 110**;
  - record on disk missing: **8**, and all eight are Tarik's `codex-` runs, which keep their state
    somewhere other than `tick-state/runs/<id>/` — the one shape of item this tool cannot vouch for.

So the pile is readable today and was readable during every wake that postponed it. What it lacks
is a reader, which is a different problem and is the one the capacity table in `item_ledger.py`
already addresses.

What this tool does NOT do, stated so nobody trusts it further. A present path may be a stale copy
(a later revision stranded on a branch); "absent" means absent from *this checkout*, so if the
checkout is behind `origin/main` the answer is wrong in the same direction. It prints the main
commit it looked at for that reason, exactly as `scripts/unlanded_worklist.py` does.

Usage:
  python3 scripts/reading_queue_record_census.py --amigo dmitri
  python3 scripts/reading_queue_record_census.py              # all five names, one table
  python3 scripts/reading_queue_record_census.py --amigo dmitri --json
  python3 scripts/reading_queue_record_census.py --selftest   # fixtures, touches nothing
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from channels import item_ledger as il  # noqa: E402

# A record below this size is one line of intent, not an account of what happened: the runs that
# were cut off at their action cap leave exactly that, a single "Started:" sentence. Counting those
# as records would overstate what a reader finds, so they are counted separately.
SUBSTANTIVE = 200


def main_commit(repo: Path = REPO) -> str:
    """The commit this checkout is at, or 'unknown'. Printed because a census of a stale tree lies."""
    try:
        out = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    return out.stdout.strip() or "unknown" if out.returncode == 0 else "unknown"


def run_dir(root: Path, run_id: str) -> Path | None:
    """The author's own run directory for this item, wherever on disk it lives. Never guessed."""
    hits = sorted(root.glob(f"*-bot/tick-state/runs/{run_id}"))
    return hits[0] if hits else None


def record_of(directory: Path | None) -> tuple[str, int]:
    """('substantive'|'thin'|'absent', size) for the author's own written account."""
    if directory is None:
        return "absent", 0
    report = directory / "report.txt"
    size = report.stat().st_size if report.is_file() else 0
    if size >= SUBSTANTIVE:
        return "substantive", size
    result = directory / "result.json"
    if result.is_file() and result.stat().st_size >= SUBSTANTIVE:
        return "substantive", result.stat().st_size
    return ("thin", size) if size else ("absent", 0)


def census(repo: Path, root: Path, who: str = "", ledger: Path | None = None) -> dict:
    """One row per never-read item named to `who` (or to anyone), judged from this machine only."""
    items = il.reading_queue(path=ledger or il.LEDGER, who=who)
    rows = []
    for rec in items:
        rid = rec.get("id") or ""
        paths = [p for p in (rec.get("paths") or []) if isinstance(p, str)]
        present = [p for p in paths if (repo / p).exists()]
        kind, size = record_of(run_dir(root, rid) if rid else None)
        rows.append({
            "id": rid,
            "amigo": rec.get("amigo") or "",
            "filed_utc": rec.get("filed_utc") or "",
            "title": (rec.get("short_title") or "")[:60],
            "paths": len(paths),
            "paths_present": len(present),
            "artefact": bool(paths) and len(present) == len(paths),
            "record": kind,
            "record_bytes": size,
        })
    return {"main": main_commit(repo), "who": who or "all", "rows": rows}


def summary(data: dict) -> dict:
    rows = data["rows"]
    return {
        "items": len(rows),
        "artefact_here": sum(1 for r in rows if r["artefact"]),
        "record_substantive": sum(1 for r in rows if r["record"] == "substantive"),
        "record_thin": sum(1 for r in rows if r["record"] == "thin"),
        "record_absent": sum(1 for r in rows if r["record"] == "absent"),
        "nothing_to_judge": sum(1 for r in rows if not r["artefact"] and r["record"] == "absent"),
    }


def report(data: dict, out=sys.stdout) -> None:
    s = summary(data)
    print(f"reading queue — {data['who']}, judged at main {data['main']}", file=out)
    print(f"  {s['items']:4d} item(s) nobody has read, named to {data['who']}", file=out)
    print(f"  {s['artefact_here']:4d} name only paths that are present here  -> the work itself can "
          f"be read and its numbers re-derived", file=out)
    print(f"  {s['record_substantive']:4d} leave the author's own account on disk (>= {SUBSTANTIVE}B)",
          file=out)
    print(f"  {s['record_thin']:4d} leave one line of intent (cut off before they wrote it up)",
          file=out)
    print(f"  {s['record_absent']:4d} leave no record at all", file=out)
    print(f"  {s['nothing_to_judge']:4d} have neither an artefact nor a record -> nothing to judge "
          f"from this machine", file=out)
    idle = [r for r in data["rows"] if not r["artefact"] and r["record"] == "absent"]
    if idle:
        print("\n  the unjudgeable set, named so a wake stops hunting for it:", file=out)
        for r in idle:
            print(f"    {r['id']}  {r['amigo']:7s} {r['filed_utc'][:10]}  {r['title']}", file=out)
    print("\n  Note: a record on disk is not a licence to trust it. It says what the run believed it "
          "did;\n  the artefact is what a reader must check it against.", file=out)


def selftest() -> int:
    """Fixtures only: a fake repo and a fake runs root, so nothing real is read or written."""
    failures = []

    def check(name, got, want):
        if got != want:
            failures.append(f"{name}: got {got!r}, want {want!r}")

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        repo, root = tmp / "repo", tmp / "LLM"
        (repo / "docs").mkdir(parents=True)
        (repo / "docs" / "here.md").write_text("x" * 10, encoding="utf-8")
        ledger = repo / "channels" / "items.jsonl"
        ledger.parent.mkdir(parents=True)
        rows = [
            # artefact present + substantive record
            {"id": "r1", "amigo": "desi", "state": "accomplished", "reviewer": "auto:land",
             "paths": ["docs/here.md"], "filed_utc": "2026-10-01T00:00:00Z",
             "reading_assigned_to": "desi"},
            # artefact absent + substantive record -> a delivery state, still readable
            {"id": "r2", "amigo": "desi", "state": "accomplished", "reviewer": "auto:path",
             "paths": ["docs/gone.md"], "filed_utc": "2026-10-02T00:00:00Z",
             "reading_assigned_to": "desi"},
            # artefact present + one-line record
            {"id": "r3", "amigo": "desi", "state": "accomplished", "reviewer": "auto",
             "paths": ["docs/here.md"], "filed_utc": "2026-10-03T00:00:00Z",
             "reading_assigned_to": "desi"},
            # neither -> the unjudgeable set
            {"id": "r4", "amigo": "tarik", "state": "accomplished", "reviewer": "auto",
             "paths": ["docs/gone.md"], "filed_utc": "2026-10-04T00:00:00Z",
             "reading_assigned_to": "dmitri"},
            # read by a model: not in the pile at all
            {"id": "r5", "amigo": "desi", "state": "accomplished", "reviewer": "desi",
             "paths": ["docs/here.md"], "filed_utc": "2026-10-05T00:00:00Z"},
        ]
        ledger.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        for rid, size, name in (("r1", 400, "report.txt"), ("r2", 400, "report.txt"),
                                ("r3", 20, "report.txt")):
            d = root / "desi-bot" / "tick-state" / "runs" / rid
            d.mkdir(parents=True)
            (d / name).write_text("y" * size, encoding="utf-8")
        (root / "tarik-bot" / "tick-state" / "runs" / "r4").mkdir(parents=True)

        data = census(repo, root, ledger=ledger)
        check("items", len(data["rows"]), 4)
        check("artefact_here", summary(data)["artefact_here"], 2)
        check("record_substantive", summary(data)["record_substantive"], 2)
        check("record_thin", summary(data)["record_thin"], 1)
        check("nothing_to_judge", summary(data)["nothing_to_judge"], 1)

        data = census(repo, root, who="desi", ledger=ledger)
        check("filtered to one name", len(data["rows"]), 3)
        out = sys.stdout
        try:
            import io
            sys.stdout = io.StringIO()
            report(data)
            printed = sys.stdout.getvalue()
        finally:
            sys.stdout = out
        check("report names the pile", "3 item(s)" in printed, True)

    for f in failures:
        print(f"SELFTEST FAIL {f}")
    print(f"selftest: {len(failures)} failure(s)" if failures else "selftest: ok")
    return 1 if failures else 0


def cli(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--amigo", choices=list(il.AMIGOS), default="", help="one name; default all")
    ap.add_argument("--root", default=str(Path.home() / "LLM"), help="where <bot>-bot lives")
    ap.add_argument("--repo", default=str(REPO), help="the checkout to test paths against")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    data = census(Path(args.repo), Path(args.root), args.amigo)
    if args.json:
        print(json.dumps({"main": data["main"], "who": data["who"],
                          "summary": summary(data), "rows": data["rows"]}, indent=1))
    else:
        report(data)
    return 0


if __name__ == "__main__":
    sys.exit(cli())
