#!/usr/bin/env python3
# Owner: Desi
"""The revisit trigger for Status 5 — the items a model looked at and postponed.

Why this exists (2026-10-19): the census at 2026-10-19T03:09Z counts 120 items in Status 5 and
*not one has ever left it*. A state that no mechanism can move out of is not a queue, it is a
graveyard with a label on it — the same defect the ledger already repaired once, when one word,
"accomplished", carried both "the lander closed it" and "a model read it".

The measurement that matters, taken the same morning over all 120 rows:

  * 105 name a *delivery* reason — "absent from main", "unlanded", "not on main", "delivery state";
  * 0 have landed since: not one postponed run id appears in any landing commit on main;
  * 11 have all of their named paths present in the tree now, 14 have none;
  * every one of the 120 was postponed within the last seven days.

So the pile is not full of work waiting on a person. It is mostly reviews that correctly found the
payload missing, parked in a state whose exit nobody runs. This script is the thing that runs it:
it re-asks each item's blocker a question a machine can answer, and names the items whose answer
has changed.

    python3 scripts/blocked_revisit.py                 # the report
    python3 scripts/blocked_revisit.py --stale-days 14 # age the "nobody re-looked" line
    python3 scripts/blocked_revisit.py --json          # the same facts, for another tool

Four verdicts, in this order, and the first that applies wins:

  landed        the run id now appears in a landing commit on main — the blocker has gone
  arrived       a path it names was *written after the postponement* and is not furniture — the
                payload may have reached main under a different run id (added 2026-10-20)
  stale         postponed longer than --stale-days ago with no later row for the same id
  present       every repo path the item names exists now — weak evidence: a *modified* file exists
                whether or not the change landed, so this says "look", not "done"
  absent        none of the named paths exists — the blocker stands exactly as recorded
  unverifiable  the item names no repo path, so no machine here can check its reason

Only the first three are "needs a look". A script that reports everything as needing a look is the
same as one that reports nothing.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "channels" / "items.jsonl"
STATUS5 = "postponed"

# More commits than this touching one path make it furniture: it changes for other reasons than
# this item's payload. 15 is above every payload file named by a postponed item and below every
# path the 2026-10-20 measurement showed doing the flagging (24-45 commits).
FURNITURE_OVER = 15


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def postponed(rows: list[dict]) -> list[dict]:
    """One row per postponed id: the *latest* postponed row, since the ledger can hold duplicates."""
    latest: dict[str, dict] = {}
    for row in rows:
        if row.get("state") != STATUS5:
            continue
        i = row["id"]
        if i not in latest or row.get("state_utc", "") >= latest[i].get("state_utc", ""):
            latest[i] = row
    return [latest[i] for i in sorted(latest)]


def later_rows(rows: list[dict], item: dict) -> list[dict]:
    """Rows for the same id dated after the postponement — a re-look leaves one of these."""
    return [r for r in rows
            if r["id"] == item["id"] and r.get("state_utc", "") > item.get("state_utc", "")]


def landed_ids(repo: Path, log_text: str | None = None) -> str:
    """The whole git log as text; a landing commit names the run id it carries."""
    if log_text is not None:
        return log_text
    try:
        return subprocess.run(["git", "-C", str(repo), "log", "--all", "--format=%s%n%b"],
                              capture_output=True, text=True, check=False).stdout
    except OSError:
        return ""


def repo_paths(item: dict) -> list[str]:
    return [p for p in item.get("paths", []) if p and not p.startswith(("http://", "https://"))]


# A repository path written in an item's own words ("…is absent from main"). The `paths` field is
# not the payload: it lists what the *reviewed run* touched, so a review filed because a report
# never landed reads `present` on shared files that were never in question.
MENTIONED = re.compile(
    r"\b((?:channels|scripts|tests|docs|research|governance|agenda|to-do-lists|\.github)"
    r"/[A-Za-z0-9_./-]*[A-Za-z0-9_-]\.[A-Za-z0-9]+)")


def reason_paths(item: dict) -> list[str]:
    """Repository paths named in the item's reason/title, in first-seen order, deduplicated.

    Evidence, not a verdict: which of these exist is reported beside the verdict so a reader can
    see whether the thing the reason called missing has since arrived. Making it decide the
    verdict would break the rule the tests pin — order of evidence, declared paths first.
    """
    text = " ".join(str(item.get(k) or "") for k in ("reason", "title", "short_title"))
    out: list[str] = []
    for match in MENTIONED.finditer(text):
        path = match.group(1)
        if path not in out:
            out.append(path)
    return out


def git(repo: Path, *args: str) -> str:
    try:
        return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                              check=False).stdout
    except OSError:
        return ""


def touch_counts(repo: Path) -> dict[str, int]:
    """path -> number of commits that changed it, from one pass of `git log --name-only`.

    This is what separates a payload from the furniture. Measured 2026-10-20: 102 of the 126
    postponed items name at least one path written *after* the postponement, so "a named path
    changed since" flags almost the whole pile — because five shared files do most of the
    changing (`channels/reject-queue.md` in 45 items, `.github/workflows/test-and-report.yml` in
    34, `to-do-lists/desi.md` in 26, `scripts/README.md` in 24, `channels/items.jsonl` in 15).
    A path every wake touches says nothing about one item's payload; a path that changes twice a
    year and changed this week says a great deal.
    """
    counts: dict[str, int] = {}
    for line in git(repo, "log", "--format=", "--name-only").splitlines():
        path = line.strip()
        if path:
            counts[path] = counts.get(path, 0) + 1
    return counts


def arrived(item: dict, repo: Path, touches: dict[str, int],
            furniture_over: int = FURNITURE_OVER) -> list[tuple[str, str]]:
    """(path, timestamp) for named paths written to main after the postponement, furniture excluded.

    Evidence, not a verdict, and deliberately conservative: a path that does not exist, a path
    changed more than `furniture_over` times, and a path whose last write predates the
    postponement all say nothing about whether this item's payload landed.
    """
    out: list[tuple[str, str]] = []
    named = list(dict.fromkeys(list(item.get("paths") or []) + reason_paths(item)))
    postponed_utc = str(item.get("state_utc") or "")
    for path in named:
        if path.startswith(("http://", "https://")) or not (repo / path).exists():
            continue
        if touches.get(path, 0) > furniture_over:
            continue
        stamp = git(repo, "log", "-1", "--format=%cI", "--", path).strip()
        if stamp and postponed_utc and stamp > postponed_utc:
            out.append((path, stamp[:19]))
    return out
             now: dt.datetime, touches: dict | None = None) -> tuple[str, str]:
    """(verdict, one line of why). The first verdict that applies wins; order is the rule."""
    if item["id"] in log_text:
        return "landed", "its run id now appears in a landing commit on main"
    try:
        when = dt.datetime.strptime(item["state_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    except (KeyError, ValueError):
        when = now
    age = (now - when).days
    if age > stale_days and not later_rows(rows, item):
        return "stale", f"postponed {age} days ago and no later row names it again"
    evidence = arrived(item, repo, touches or {})
    if evidence:
        path, stamp = evidence[0]
        more = f" (and {len(evidence) - 1} more)" if len(evidence) > 1 else ""
        return "arrived", f"{path} was last written {stamp}{more} — after the postponement, so the payload may be home"
    paths = repo_paths(item)
    if not paths:
        return "unverifiable", "names no repository path, so its reason cannot be checked here"
    present = [p for p in paths if (repo / p).exists()]
    if present and len(present) == len(paths):
        return "present", f"all {len(paths)} named path(s) exist now (a modified file proves nothing — look)"
    if not present:
        return "absent", f"none of its {len(paths)} named path(s) exists — the blocker stands"
    return "absent", f"{len(present)} of {len(paths)} named path(s) exist; the payload is not there"


ORDER = ["landed", "arrived", "stale", "present", "absent", "unverifiable"]
NEEDS_A_LOOK = {"landed", "arrived", "stale", "present"}


def build(rows: list[dict], log_text: str, repo: Path, stale_days: int,
          now: dt.datetime | None = None, touches: dict[str, int] | None = None) -> list[dict]:
    now = now or dt.datetime.now(dt.timezone.utc)
    if touches is None:
        touches = touch_counts(repo)
    out = []
    for item in postponed(rows):
        verdict, why = classify(item, rows, log_text, repo, stale_days, now, touches)
        named = reason_paths(item)
        out.append({"id": item["id"], "verdict": verdict, "why": why,
                    "postponed_utc": item.get("state_utc", ""),
                    "amigo": item.get("amigo", "?"), "reviewer": item.get("reviewer", "?"),
                    "title": (item.get("short_title") or item.get("title") or "")[:70],
                    "reason_named": named,
                    "reason_present": [p for p in named if (repo / p).exists()],
                    "reason_absent": [p for p in named if not (repo / p).exists()]})
    return sorted(out, key=lambda r: (ORDER.index(r["verdict"]), r["postponed_utc"]))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--stale-days", type=int, default=14)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all", action="store_true", help="list every item, not only those needing a look")
    a = ap.parse_args()

    rows = load(Path(a.ledger))
    repo = Path(a.repo)
    facts = build(rows, landed_ids(repo), repo, a.stale_days)

    if a.json:
        print(json.dumps({"items": facts, "counts": counts(facts)}, indent=1))
        return 0

    print(f"Status 5 (postponed): {len(facts)} item(s)")
    for verdict in ORDER:
        print(f"  {verdict:<13}{counts(facts)[verdict]:4d}")
    look = [f for f in facts if f["verdict"] in NEEDS_A_LOOK]
    print(f"\nneeds a look now: {len(look)}")
    for f in (facts if a.all else look):
        print(f"  [{f['verdict']}] {f['id']}  postponed {f['postponed_utc'][:10]} by {f['reviewer']}"
              f"  {f['title']}\n      {f['why']}")
        if f["reason_named"]:
            line = (f"      its own words name {len(f['reason_named'])} more path(s): "
                    f"{len(f['reason_present'])} present, {len(f['reason_absent'])} absent")
            if f["reason_present"]:
                line += f" — present: {', '.join(f['reason_present'][:3])}"
            print(line)
    return 0


def counts(facts: list[dict]) -> dict[str, int]:
    out = {v: 0 for v in ORDER}
    for f in facts:
        out[f["verdict"]] = out.get(f["verdict"], 0) + 1
    return out


if __name__ == "__main__":
    sys.exit(main())
