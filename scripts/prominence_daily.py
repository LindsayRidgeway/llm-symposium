#!/usr/bin/env python3
"""One dated row a day: the prominence number written down instead of re-derived.

Why this file exists
--------------------
`channels/reports/prominence.md` is a *snapshot*. It is rewritten whole every time someone runs
`scripts/prominence.py --write`, so it never holds a series: run it twice and you have the same
fourteen-day table twice, not fifteen days.

The value-queue item `prominence-meter` closed every part of itself except the last: it asked for a
**daily** number, and nothing scheduled ran the instrument. The 2026-11-20 11:19Z wake left that
open with the reason on the record — "adding a second scheduled writer to `channels/` is exactly the
overwrite defect argued in `channels/tasks.md`".

That reading was half right, and the half it got wrong is the whole job. The defect was never "a
second writer"; it was **two writers to one file**. `channel-poll.yml` rewrote `channels/tasks.md`
wholesale about twelve times a day while four other processes wrote the same file, then retried the
rejected push by rebasing. A file with exactly one writer cannot race, and an append-only file cannot
be overwritten by a process that only ever adds lines.

So: `channels/reports/prominence-daily.jsonl`, one JSON line per UTC day, appended. The only
caller is the `daily-prominence` step of `.github/workflows/quiet-check.yml` — the one scheduled job
that is left holding `contents: write`, the same job that took the retention trim off the reject
queue on 2026-10-28. `tests/test_prominence_daily.py::test_the_daily_file_has_one_writer` fails if a
second workflow ever names the path.

Three behaviours that are deliberate
------------------------------------
* **Idempotent per day.** A re-run — a manual dispatch, a retry after a push race — appends nothing.
  Otherwise one day appears four times in the file and the series lies about its own length.
* **Unread is not zero.** Without a push-access token the traffic API answers 403. The row is then
  written with `"state": "unread"`, the token source, and `null` for every count. A zero would be a
  measurement; this is an absence, and the difference is the reason the instrument exists.
* **Exit 0, always.** This step shares a job with the dead-man switch, the retention trim and the
  route alert. A prominence failure must never take those down. The failure is printed, and recorded
  in the line itself as `"state": "error"`.

What a clone is worth is not decided here; read `channels/reports/prominence.md` before quoting one.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DAILY = ROOT / "channels" / "reports" / "prominence-daily.jsonl"

if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

try:  # the measurement already exists; this file must not re-implement it
    import prominence  # noqa: E402
except Exception as exc:  # noqa: BLE001 - a missing instrument is an answer, not a crash at import
    prominence = None  # type: ignore[assignment]
    _IMPORT_ERROR = f"{type(exc).__name__}: {exc}"
else:
    _IMPORT_ERROR = ""

NOTE = ("one clone is not one install: our own Actions runs are subtracted above, local wakes are not "
        "countable from outside, and a clone with no page view beside it is a crawler. "
        "See channels/reports/prominence.md.")

FIELDS = ("clones", "unique_cloners", "views", "unique_visitors", "clones_per_view",
          "own_actions_runs", "unexplained_clones_upper_bound")


def today(now: dt.datetime | None = None) -> str:
    """The UTC date this row is filed under. UTC, because the clock that writes it is UTC."""
    now = now or dt.datetime.now(dt.timezone.utc)
    return now.strftime("%Y-%m-%d")


def row_from_traffic(traffic: object, day: str, measured_utc: str | None = None) -> dict:
    """Pure: turn `prominence.measure_traffic()`'s output into the one line that gets appended.

    The state is computed from the data, never asserted by the caller: a row is `measured` only when
    every repo's clone count *and* view count are integers. Anything else is `unread`, and the status
    strings travel with it so a reader can see which URL said what.
    """
    data = traffic if isinstance(traffic, dict) else {}
    repos: list[dict] = []
    for raw in data.get("repos") or []:
        if not isinstance(raw, dict):
            continue
        clones = raw.get("clones") if isinstance(raw.get("clones"), dict) else {}
        views = raw.get("views") if isinstance(raw.get("views"), dict) else {}
        repos.append({
            "repo": raw.get("repo"),
            "clones": clones.get("count"),
            "unique_cloners": clones.get("uniques"),
            "views": views.get("count"),
            "unique_visitors": views.get("uniques"),
            "clones_per_view": raw.get("clones_per_view"),
            "own_actions_runs": raw.get("own_actions_runs_total"),
            "unexplained_clones_upper_bound": raw.get("unexplained_clones_upper_bound"),
            "clones_status": clones.get("status"),
            "views_status": views.get("status"),
        })
    measured = bool(repos) and all(
        isinstance(r["clones"], int) and isinstance(r["views"], int) for r in repos)
    return {
        "day": day,
        "measured_utc": measured_utc,
        "state": "measured" if measured else "unread",
        "token_available": bool(data.get("token_available")),
        "token_source": data.get("token_source"),
        "repos": repos,
        "note": NOTE,
    }


def read_days(path: pathlib.Path) -> set[str]:
    """Every day already in the file. Unparseable lines are skipped, not fatal: one bad line must
    not stop the series, and it must not be silently treated as a day either."""
    path = pathlib.Path(path)
    if not path.exists():
        return set()
    days: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict) and isinstance(row.get("day"), str):
            days.add(row["day"])
    return days


def append_once(path: pathlib.Path, row: dict) -> bool:
    """Append the row unless its day is already present. True means a line was written."""
    path = pathlib.Path(path)
    if row.get("day") in read_days(path):
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")
    return True


def summarise(row: dict) -> str:
    """One plain line for the job log, so a human reading a failed run sees the number."""
    if row.get("state") == "error":
        return f"{row.get('day')}: ERROR {row.get('error')}"
    if row.get("state") == "unread":
        return f"{row.get('day')}: unread ({row.get('token_source')})"
    parts = []
    for r in row.get("repos") or []:
        parts.append(f"{r.get('repo')}: {r.get('clones')} clones / {r.get('views')} views")
    return f"{row.get('day')}: " + "; ".join(parts)


def main(argv: list[str] | None = None, measure_fn=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--path", default=str(DAILY), help="the append-only file (default: %(default)s)")
    ap.add_argument("--dry-run", action="store_true", help="print the row, write nothing")
    ap.add_argument("--json", action="store_true", help="print the measurement as JSON")
    args = ap.parse_args(argv)

    day = today()
    path = pathlib.Path(args.path)
    if measure_fn is None:
        if prominence is None:
            row: dict = {"day": day, "state": "error", "repos": [],
                         "error": f"scripts/prominence.py could not be imported — {_IMPORT_ERROR}"}
        else:
            measure_fn = prominence.measure_traffic
            row = {}
    else:
        row = {}

    if not row:
        try:
            traffic = measure_fn()
            row = row_from_traffic(traffic, day,
                                   measured_utc=(traffic or {}).get("measured_utc")
                                   if isinstance(traffic, dict) else None)
            if isinstance(traffic, dict) and not row["measured_utc"]:
                row["measured_utc"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception as exc:  # noqa: BLE001 - this must not take the job down
            row = {"day": day, "state": "error", "repos": [],
                   "error": f"{type(exc).__name__}: {exc}", "note": NOTE}

    print(summarise(row))
    if args.json:
        print(json.dumps(row, indent=2, sort_keys=True))
    if args.dry_run:
        print(json.dumps(row, indent=2, sort_keys=True))
        return 0
    written = append_once(path, row)
    try:
        shown = path.relative_to(ROOT)
    except ValueError:
        shown = path
    print(f"{'appended' if written else 'already recorded'} -> {shown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
