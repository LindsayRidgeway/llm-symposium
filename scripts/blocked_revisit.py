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

Recounted 2026-11-07, after the "landed" test was repaired: **235** items sit in Status 5. This
paragraph said 292 until later the same day: the reader behind the census kept the latest *postponed*
row per id, so 58 items whose later verdict was `accomplished` or `rejected` never left the queue —
the same defect the script exists to find, in the script. The census now agrees with
`channels/item_ledger.load()` (235 postponed of 1,137 items) and is pinned by a test on the real
ledger; the account is `channels/reports/2026-11-07-desi-three-numbers-for-one-pile.md`. Of the 235,
**37** have a landing commit whose subject names them. The same pile read as **61** landed under the old
test, and the **14** between those numbers are what the old test was actually measuring — every one
of them is an id that appears in a *body* or a *path list* rather than a lander's subject:

  * a verdict file named for the item (`channels/ledger-verdicts/...-20261107T004723Z-4189b82b.json`)
    listed among the paths another run's lander carried — the item was *reviewed*, not landed;
  * `review(wake): Tarik reads 20261022T091715Z-3ab0f188` — a review subject naming the item;
  * a report body quoting the id;
  * `Publish the exact recovered original RT4 guard/test pair on an unmerged review branch. Original
    run 20260930T165900Z-24cb3cd6` — a commit that says in its own subject that the branch is
    unmerged, counted as a landing.

The cost of being strict is a false negative: a landing written with some future subject shape would
be missed. Measured over 582 `land(wake)` commits, the shape has only ever had two forms, and both
are in `LANDER_SUBJECT`; the miss-and-recount is one line when a third appears.

Four verdicts, in this order, and the first that applies wins:

  landed        a landing commit on main *names* the run id in its subject — the blocker is gone;
                re-look. A commit that merely mentions the id in its body does not count (fixed
                2026-11-07: the first version was a substring search over the whole log, so a
                recovery commit that quoted an id in a restored filename marked that run landed)
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
LEDGER_PATH = "channels/items.jsonl"  # never evidence — see `repo_paths`
STATUS5 = "postponed"

# The two shapes the landing machine writes, and the only two in this repository's history:
#   land(wake): work from run <id>
#   land(wake): Codex work from run codex-<id>
# 582 of 582 land(wake) commits on 2026-11-07 carry the id this way. Matched against the *subject*,
# anchored at both ends, so a body that quotes a lander cannot make anything look landed.
LANDER_SUBJECT = re.compile(r"^land\(wake\): (?:Codex )?work from run (?P<id>\S+)$")


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def postponed(rows: list[dict]) -> list[dict]:
    """One row per id that is *still* postponed: the newest verdict decides, not the newest parking.

    This used to keep, for each id, the latest row whose state was `postponed` — right for "what
    did this item last say while it was parked", wrong for the only question this file is asked:
    *is it parked now*. A postponement superseded by a later `accomplished` or `rejected` row
    therefore never left the queue, and the script whose whole purpose is to prove that Status 5 is
    not a graveyard could not see an exit.

    Measured 2026-11-07 (channels/reports/2026-11-07-desi-three-numbers-for-one-pile.md): of the
    293 ids this function returned, **58 had a later verdict that was not a postponement** — 56 of
    them a model's decision (48 from the 2026-11-03 expiry review, 7 Tarik's, 1 Gemini's) and 2
    `rejected` — and 46 of the 58 were printed as `present`, which is in `NEEDS_A_LOOK`. The
    ledger's own reader (`item_ledger.load()`, with the 2026-10-25 inherit rule and the 2026-10-27
    newer-wins rule) called the pile 235, not 293. `tests/test_blocked_revisit.py` now compares the
    two readers on the real ledger, so this cannot drift apart again quietly.

    A row with no `state` is a filing snapshot, not a verdict, and does not vote — the rule the
    2026-11-06 null-stamp crash fix put here.
    """
    newest: dict[str, dict] = {}
    for row in rows:
        if not row.get("state"):
            continue
        i = row["id"]
        if i not in newest or (row.get("state_utc") or "") >= (newest[i].get("state_utc") or ""):
            newest[i] = row
    return [newest[i] for i in sorted(newest) if newest[i].get("state") == STATUS5]


def later_rows(rows: list[dict], item: dict) -> list[dict]:
    """Rows for the same id dated after the postponement — a re-look leaves one of these."""
    return [r for r in rows
            if r["id"] == item["id"]
            and (r.get("state_utc") or "") > (item.get("state_utc") or "")]


def landing_log(repo: Path, log_text: str | None = None) -> str:
    """Subjects of the landing commits on main, one per line.

    Subjects only, and main only. The verdict this feeds is "the run's work reached main", and
    neither of the two things this used to accept is that: an id quoted in a *body* (measured
    2026-11-07 — `git log --all --grep=b2420fec` had exactly one hit, 26dd4d7e, the lander for a
    *different* run, because a restored filename in its body contained b2420fec; under the old
    substring test that run read as landed without having landed), and a lander sitting on a draft
    branch rather than main.
    """
    if log_text is not None:
        return log_text
    refs = ["main", "origin/main", "HEAD"]
    ref = "HEAD"
    for candidate in refs:
        ok = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", candidate],
                            capture_output=True, text=True, check=False)
        if ok.returncode == 0 and ok.stdout.strip():
            ref = candidate
            break
    try:
        return subprocess.run(["git", "-C", str(repo), "log", ref, "--format=%s"],
                              capture_output=True, text=True, check=False).stdout
    except OSError:
        return ""


def landed_run_ids(log_text: str) -> set[str]:
    """Every run id a landing commit says it carried, with the `codex-` prefix normalised away.

    The prefix is a naming convention, not part of the id: the ledger stores some runs as
    `codex-2026...` and some committers write the bare form, so comparing one form to one form
    would miss real landings. Normalising both sides is the only place this can go wrong once.
    """
    ids: set[str] = set()
    for line in log_text.splitlines():
        match = LANDER_SUBJECT.match(line.strip())
        if match:
            ids.add(match.group("id").removeprefix("codex-"))
    return ids


def repo_paths(item: dict) -> list[str]:
    """Paths that can be evidence about *this* item. The ledger is never one of them.

    Every wake appends to `channels/items.jsonl`, so its presence says nothing about any particular
    item — the same reason `item_ledger.postpone_expired()` skips those rows. Before 2026-11-07 this
    script counted them as `present`, which put 13 rows in `NEEDS_A_LOOK` on the strength of a file
    that had been rewritten a dozen times since the postponement was written.
    """
    return [p for p in item.get("paths", [])
            if p and not p.startswith(("http://", "https://")) and p != LEDGER_PATH]


def classify(item: dict, rows: list[dict], landed: set[str], repo: Path, stale_days: int,
             now: dt.datetime) -> tuple[str, str]:
    """(verdict, one line of why). The first verdict that applies wins; order is the rule."""
    if item["id"].removeprefix("codex-") in landed:
        return "landed", "a landing commit on main names this run id — the blocker is gone"
    try:
        when = dt.datetime.strptime(item["state_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    except (KeyError, ValueError):
        when = now
    age = (now - when).days
    if age > stale_days and not later_rows(rows, item):
        return "stale", f"postponed {age} days ago and no later row names it again"
    paths = repo_paths(item)
    if not paths:
        if any(p == LEDGER_PATH for p in (item.get("paths") or [])):
            return ("unverifiable",
                    "its only named path is the ledger itself, which every wake appends to")
        return "unverifiable", "names no repository path, so its reason cannot be checked here"
    present = [p for p in paths if (repo / p).exists()]
    if present and len(present) == len(paths):
        return "present", f"all {len(paths)} named path(s) exist now (a modified file proves nothing — look)"
    if not present:
        return "absent", f"none of its {len(paths)} named path(s) exists — the blocker stands"
    return "absent", f"{len(present)} of {len(paths)} named path(s) exist; the payload is not there"


ORDER = ["landed", "stale", "present", "absent", "unverifiable"]
NEEDS_A_LOOK = {"landed", "stale", "present"}


def build(rows: list[dict], log_text: str, repo: Path, stale_days: int,
          now: dt.datetime | None = None) -> list[dict]:
    now = now or dt.datetime.now(dt.timezone.utc)
    landed = landed_run_ids(log_text)
    out = []
    for item in postponed(rows):
        verdict, why = classify(item, rows, landed, repo, stale_days, now)
        out.append({"id": item["id"], "verdict": verdict, "why": why,
                    "postponed_utc": item.get("state_utc", ""),
                    "amigo": item.get("amigo", "?"), "reviewer": item.get("reviewer", "?"),
                    "title": (item.get("short_title") or item.get("title") or "")[:70]})
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
    facts = build(rows, landing_log(repo), repo, a.stale_days)

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
    return 0


def counts(facts: list[dict]) -> dict[str, int]:
    out = {v: 0 for v in ORDER}
    for f in facts:
        out[f["verdict"]] = out.get(f["verdict"], 0) + 1
    return out


if __name__ == "__main__":
    sys.exit(main())
