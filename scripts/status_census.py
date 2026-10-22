#!/usr/bin/env python3
"""Status census and audit — two counts 24 hours apart, and a log that must explain the difference.

The human's protocol, 2026-10-17, in his words: give the states simple arbitrary names with one
sentence each; count them at time A; count them again at B, twenty-four hours later; produce the
audit trail of every transition in between, saying what it was and which amigo did it (not why —
"that is too subjective"); then **validate the trail**: does applying every logged transition
completely account for the change between the two counts?

The ledger (`channels/items.jsonl`) is append-only and every row carries a timestamp, so a census at
any past minute can be derived rather than remembered. That matters: it means the validation can be
rehearsed on yesterday's window instead of waiting for tomorrow.

    python3 scripts/status_census.py --at 2026-10-17T19:30:00Z     # census now/past, printed
    python3 scripts/status_census.py --census                      # write an immutable snapshot
    python3 scripts/status_census.py --window A B                  # two snapshots + audit + validation
    python3 scripts/status_census.py --window --hours 24           # derive both ends, past 24h

Exit code 1 if the audit trail does not fully account for the difference.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from channels.item_ledger import names_a_person  # noqa: E402
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "channels" / "items.jsonl"
CENSUS_DIR = REPO / "channels" / "census"

# The six statuses. One sentence each, and the old ledger word is named so the two records can be
# read against each other. The split between 1 and 2 is the whole reason this script exists: before
# 2026-10-17 the ledger wrote one word, "accomplished", for both.
STATUS = {
    "1": "done and checked — in the repository, and another model read it and said it holds",
    "2": "done, not checked — in the repository, closed by the landing bot, and no model has read it",
    "3": "waiting, with a name — nobody has looked yet, and a particular amigo is named to look",
    "4": "waiting, with no name — nobody has looked yet and nobody owns it",
    "5": "postponed — a model looked and named what stops it",
    "6": "rejected — a model looked and said it should never be done",
}
# The words those sentences use, defined once, because the human asked and they were not obvious
# (2026-10-17). His seven questions are the reason this block exists.
WORDS = {
    "model": "one of the five amigos — an LLM. 'Architecture' is the company family behind it "
             "(DeepSeek, Anthropic, Google, OpenAI), which is a different thing.",
    "read it": "a model opened the run's report and the files the item names, and judged them. Not a "
               "human, and not the landing bot.",
    "holds": "the work does what it claims: the file is there, it matches the claim, it is not a "
             "duplicate of earlier work, and no file marked DO-NOT-EDIT was hand-edited. It is a "
             "judgement, not a proof — no test decides it.",
    "owns it": "an amigo's name is on the item, so that amigo's wake will see it in its queue. An "
               "item nobody owns is invisible until something names it.",
}

# Measured 2026-10-17, and worth knowing before reading the counts: no item in this ledger has ever
# left Status 5 or Status 6. 117 postponed and 16 rejected, none revisited; one item went from
# Status 2 to Status 1 when a model read work the lander had already closed, and no item has ever
# gone backwards out of 1/2. So "postponed" and "rejected" are terminal in practice even though the
# tooling allows another review — a write-only blockers list is a graveyard with a label on it.
ABSENT = "-"


def _ts(value: str) -> str:
    return (value or "").replace("+00:00", "Z").strip()


def load(path: Path = LEDGER) -> list[dict]:
    rows = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        if line.strip():
            row = json.loads(line)
            row["_seq"] = i
            rows.append(row)
    return rows


def events(rows: list[dict]) -> dict[str, list[dict]]:
    """Every dated event per item: filed, named, closed — with who did it."""
    out: dict[str, list[dict]] = {}
    for r in rows:
        item = out.setdefault(r["id"], [])
        if r.get("filed_utc"):
            item.append({"ts": _ts(r["filed_utc"]), "seq": r["_seq"], "kind": "filed",
                         "actor": r.get("amigo", "?"), "status": "3" if r.get("assigned_to") else "4"})
        if r.get("assigned_utc") and r.get("assigned_to"):
            item.append({"ts": _ts(r["assigned_utc"]), "seq": r["_seq"], "kind": "named",
                         "actor": r.get("assigned_by") or "?", "status": "3",
                         "to": r["assigned_to"]})
        if r.get("state_utc") and r.get("state"):
            # 2026-10-22: "checked" means a body read it. A path comparison (`auto:path`) is the
                  # same kind of fact as the lander's gate (`auto:land`) and used to be counted
                  # here as status 1 — reviewed — which inflated the checked pile, the one the
                  # backlog ratio is measured against.
                  st = {"accomplished": "1" if names_a_person(r.get("reviewer")) else "2",
                  "postponed": "5", "rejected": "6"}[r["state"]]
            item.append({"ts": _ts(r["state_utc"]), "seq": r["_seq"], "kind": "closed",
                         "actor": r.get("reviewer") or "?", "status": st})
    for evs in out.values():
        evs.sort(key=lambda e: (e["ts"], e["seq"]))
        # The ledger can hold the same event twice (a `--collect` and a `--backfill` both appended
        # the same row). Collapsing per (timestamp, kind) keeps the latest information and stops the
        # audit trail inventing a transition out of a duplicate — measured 2026-10-17: four of the
        # first twenty rows were exactly this.
        seen: dict[tuple, dict] = {}
        for e in evs:
            seen[(e["ts"], e["kind"])] = e
        evs[:] = sorted(seen.values(), key=lambda e: (e["ts"], e["seq"]))
    return out


def status_at(evs: list[dict], when: str) -> str:
    s = ABSENT
    for e in evs:
        if e["ts"] <= when:
            s = e["status"]
    return s


def census(rows: list[dict], when: str) -> dict[str, str]:
    return {i: status_at(evs, when) for i, evs in events(rows).items() if status_at(evs, when) != ABSENT}


def counts(c: dict[str, str]) -> dict[str, int]:
    out = {k: 0 for k in list(STATUS) + [ABSENT]}
    for v in c.values():
        out[v] = out.get(v, 0) + 1
    return out


def show(c: dict[str, str], label: str) -> None:
    n = counts(c)
    print(f"{label}: {sum(n.values())} items")
    for k in STATUS:
        print(f"  Status {k}  {n[k]:4d}   {STATUS[k]}")
    if n[ABSENT]:
        print(f"  {ABSENT:>8}  {n[ABSENT]:4d}   (not yet in the ledger)")


def transitions(evs: dict[str, list[dict]], a: str, b: str, rows_at_a: int | None = None) -> list[dict]:
    """Every logged event in (a, b] that moves an item to a different status, with the actor.

    With `rows_at_a`, the window is a window in the *file* — every event whose row was appended after
    that position — which is the only definition that survives a retroactive append.
    """
    out = []
    for item, evs in evs.items():
        before = status_at(evs, a)
        for e in evs:
            inside = (e["seq"] >= rows_at_a) if rows_at_a is not None else (a < e["ts"] <= b)
            if inside:
                if e["status"] != before:
                    out.append({"id": item, "ts": e["ts"], "from": before, "to": e["status"],
                                "actor": e["actor"], "kind": e["kind"]})
                before = e["status"]
    return sorted(out, key=lambda t: t["ts"])


def validate(evs, a, b, census_a, census_b, rows_at_a: int | None = None) -> list[dict]:
    """Apply the logged transitions to census A; any item that disagrees with census B is a hole."""
    predicted = dict(census_a)
    for item in set(census_a) | set(census_b):
        predicted.setdefault(item, ABSENT)
    for t in transitions(evs, a, b, rows_at_a):
        predicted[t["id"]] = t["to"]
    bad = []
    for item in set(predicted) | set(census_b):
        want = census_b.get(item, ABSENT)
        got = predicted.get(item, ABSENT)
        if want != got:
            bad.append({"id": item, "predicted": got, "counted": want})
    return sorted(bad, key=lambda x: x["id"])


def _hours_between(a: str, b: str) -> float:
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    try:
        d = dt.datetime.strptime(b, fmt) - dt.datetime.strptime(a, fmt)
    except ValueError:
        return 0.0
    return d.total_seconds() / 3600.0


def unread_items(rows: list[dict], when: str, limit: int = 12, amigo: str = "",
                 repo: Path = REPO) -> dict:
    """Status 2 — in the repository, closed by the landing bot, and no model has read it.

    This is the pile the founder's target is about, and until 2026-10-21 it had no view: a Status 2
    item carries no name, appears in nobody's `--queue`, and so could only be read by accident.
    "Read before you write" therefore drained the 43 named items and left the 225 alone.

    Two columns are the reason this is a judgement aid and not a list. `closed` is how long the
    work has been sitting there unread, and `files` is how many of the paths the item names are
    still present on main. An item whose files are all there is work to *read*; an item whose files
    are partly missing is a *delivery* problem wearing a reading problem's clothes, and no amount of
    reading will fix it. Separating those two is the whole point — the same confusion cost this
    commons ten wakes in September.

    Oldest landing first, because the oldest unread work is the work most likely to have been
    overtaken by later work that cannot know about it.
    """
    # `events()` reads the row's position in the file (`_seq`), which `load()` sets. A caller that
    # built rows in memory (a test, another tool) has no position, so give it the list index —
    # position in the sequence is the same fact.
    seq_rows = []
    for n, r in enumerate(rows):
        if "_seq" not in r:
            r = dict(r, _seq=n)
        seq_rows.append(r)
    evs = events(seq_rows)
    latest: dict[str, dict] = {}
    for r in seq_rows:
        latest[r["id"]] = r
    items = []
    for item, e in evs.items():
        if status_at(e, when) != "2":
            continue
        row = latest.get(item, {})
        closed = [x for x in e if x["status"] == "2" and x["ts"] <= when]
        closed_at = closed[-1]["ts"] if closed else ""
        paths = [p for p in (row.get("paths") or []) if p]
        present = sum(1 for p in paths if (repo / p).exists())
        items.append({
            "id": item,
            "amigo": row.get("amigo") or "?",
            "scope": row.get("scope") or "",
            "title": row.get("title") or row.get("short_title") or "(no report)",
            "closed_utc": closed_at,
            "age_hours": round(_hours_between(closed_at, when), 1) if closed_at else 0.0,
            "paths": paths,
            "paths_present": present,
            "paths_missing": [p for p in paths if not (repo / p).exists()],
        })
    if amigo:
        items = [i for i in items if i["amigo"] == amigo]
    items.sort(key=lambda i: (i["closed_utc"] or "", i["id"]))
    readable = [i for i in items if i["paths"] and not i["paths_missing"]]
    undelivered = [i for i in items if i["paths_missing"]]
    shown = items if limit <= 0 else items[:limit]
    return {"when": when, "total": len(items), "shown": shown, "limit": limit, "amigo": amigo,
            "readable": len(readable), "undelivered": len(undelivered),
            "oldest": items[0] if items else None}


def show_unread(view: dict) -> None:
    items = view["shown"]
    who = (" for " + view["amigo"]) if view["amigo"] else ""
    print(f"finished and not read{who}: {view['total']} item(s), oldest landing first")
    if not items:
        print("  nothing — every finished item in the ledger has been read.")
        return
    print("")
    print(f"  {'#':>3}  {'id':<28} {'by':<7} {'closed':<12} {'waiting':>9}  {'files':>6}  title")
    for n, i in enumerate(items, 1):
        files = f"{i['paths_present']}/{len(i['paths'])}" if i["paths"] else "-"
        title = " ".join(i["title"].split())[:64]
        print(f"  {n:>3}  {i['id']:<28} {i['amigo']:<7} {i['closed_utc'][:10]:<12} "
              f"{i['age_hours']:>8.0f}h  {files:>6}  {title}")
    if view["limit"] > 0 and view["total"] > len(items):
        print(f"\n  showing {len(items)} of {view['total']}  (--limit 0 for all)")
    print("")
    print(f"  {view['readable']} name only files that are still on main — work to read.")
    print(f"  {view['undelivered']} name at least one file that is not on main — a delivery "
          f"problem, not a reading problem.")
    if view["oldest"]:
        o = view["oldest"]
        print(f"  oldest unread: {o['id']} by {o['amigo']}, closed {o['closed_utc'][:10]}, "
              f"{o['age_hours']:.0f}h ago.")
    print("")
    print("  to drain one, read the run's report and the files it names, then record it:")
    print('    python3 channels/item_ledger.py --review <id> --state accomplished \\')
    print('        --reason "read it: what I opened and what I checked" --reviewer <you>')
    print("  a read that finds the work wrong is still a read: say what is wrong in the reason.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--at", help="census as of this UTC timestamp (default: now)")
    ap.add_argument("--census", action="store_true", help="write an immutable snapshot under channels/census/")
    ap.add_argument("--window", nargs="*", help="A and B: two census snapshots, or --hours")
    ap.add_argument("--hours", type=float, default=24.0)
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--target", action="store_true",
                    help="the founder's target, 2026-10-20: the review backlog must never exceed a "
                         "day's arrivals — counts it, and says PASS or FAIL")
    ap.add_argument("--unread", action="store_true",
                    help="the pile itself: Status 2 items (in the repository, closed by the landing "
                         "bot, read by no model), oldest first, with whether the files they name are "
                         "still on main — the view that did not exist until 2026-10-21")
    ap.add_argument("--limit", type=int, default=12,
                    help="with --unread: how many to show (0 = all); default 12")
    ap.add_argument("--amigo", default="",
                    help="with --unread: only items written by this amigo")
    ap.add_argument("--json", action="store_true", help="with --unread: machine-readable")
    ap.add_argument("--repo", default=str(REPO),
                    help="with --unread: where the named paths are looked for (default: this repo)")
    a = ap.parse_args()

    ledger = Path(a.ledger)
    rows = load(ledger)
    evs = events(rows)
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if a.unread:
        view = unread_items(rows, a.at or now, limit=a.limit, amigo=a.amigo,
                            repo=Path(a.repo))
        if a.json:
            print(json.dumps(view, indent=1, sort_keys=True))
        else:
            show_unread(view)
        return 0

    if a.target:
        now = a.at or now
        since = (dt.datetime.strptime(now, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
                 - dt.timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
        c = census(rows, now)
        unread = sum(1 for v in c.values() if v == "2")
        named = sum(1 for v in c.values() if v == "3")
        arrivals = sum(1 for i, evs in evs.items() if evs and since < evs[0]["ts"] <= now)
        reads = sum(1 for evs in evs.values() for e in evs
                    if since < e["ts"] <= now and e["kind"] == "closed" and e["status"] in ("1", "5", "6"))
        print(f"target: backlog of finished-but-unread must not exceed one day's arrivals")
        print(f"  finished and not read      {unread:5d}")
        print(f"  arrivals in the last 24h   {arrivals:5d}")
        print(f"  reads in the last 24h      {reads:5d}  ({reads / arrivals:.2f} per arrival)" if arrivals else "")
        print(f"  waiting with a name        {named:5d}   <- the queue, which the landing bot keeps short")
        # The pile has its own flows, and they are not the queue's. Measured 2026-10-20: 9 items
        # entered the pile in 24h and 0 left it; over seven days 106 in, 1 out. Reads happen (247
        # in the week) but they land on items still in the queue, i.e. read before or instead of
        # landing. Nothing reads an item *after* the landing bot has closed it, and that is what the
        # pile is made of - so "reads per arrival" can exceed 1 while the pile grows.
        per_item: dict[str, list[dict]] = {}
        for r in rows:
            per_item.setdefault(r["id"], []).append(r)
        into = outof = 0
        for rs in per_item.values():
            closed = sorted([x for x in rs if x.get("state_utc")], key=lambda x: x["state_utc"])
            bot = [x for x in closed if not names_a_person(x.get("reviewer"))]
            model = [x for x in closed if names_a_person(x.get("reviewer"))]
            if bot and bot[0]["state_utc"] > since:
                into += 1
            if bot and model and model[-1]["state_utc"] > since and bot[0]["state_utc"] < model[-1]["state_utc"]:
                outof += 1
        print(f"  pile flow, last 24h        +{into:4d} in   -{outof} out   (items, not rows)")
        # The daily figure is noisy - arrivals have run 16 to 72 a day - so the control interval he
        # asked for is a week: it is the shortest window in which the noise stops deciding the answer.
        week = (dt.datetime.strptime(now, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
                - dt.timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
        arr7 = sum(1 for e in evs.values() if e and week < e[0]["ts"] <= now)
        read7 = sum(1 for e in evs.values() for x in e
                    if week < x["ts"] <= now and x["kind"] == "closed" and x["status"] in ("1", "5", "6"))
        print(f"  last 7 days: {read7} reads / {arr7} arrivals = {read7 / arr7:.2f} per arrival"
              if arr7 else "  last 7 days: no arrivals")
        state = "PASS" if unread <= arrivals else "FAIL"
        print(f"\n  {state}: ", end="")
        if state == "PASS":
            print("the backlog is no larger than a day's work.")
        else:
            pace = (unread - arrivals) / (reads - arrivals) if reads > arrivals else None
            print(f"{unread - arrivals} item(s) over the line; ", end="")
            print(f"drains in about {pace:.0f} day(s) at this pace." if pace else
                  "and reads do not exceed arrivals, so it never drains.")
        return 0 if state == "PASS" else 1

    if a.census:
        when = a.at or now
        c = census(rows, when)
        CENSUS_DIR.mkdir(parents=True, exist_ok=True)
        path = CENSUS_DIR / f"{when.replace(':','').replace('-','')}.json"
        # The row count is the clock. Measured 2026-10-20: ten items sat in Status 2 at B and could
        # not be explained from A, because their rows were appended *after* A carrying timestamps
        # from before it (`--collect` and `--backfill` both write rows about earlier runs). An
        # append-only file's position is the only honest time; its timestamps are about the work,
        # not about the record.
        path.write_text(json.dumps({"at": when, "rows": len(rows), "counts": counts(c), "status": c},
                                   indent=1, sort_keys=True), encoding="utf-8")
        print(f"snapshot written: {path.relative_to(REPO)}")
        show(c, f"census at {when}")
        return 0

    if a.window is not None:
        if len(a.window) == 2:
            sa = json.loads(Path(a.window[0]).read_text(encoding="utf-8"))
            sb = json.loads(Path(a.window[1]).read_text(encoding="utf-8"))
            A, B = sa["at"], sb["at"]
            ca, cb = sa["status"], sb["status"]
            derived = False
            rows_at_a = sa.get("rows")
        else:
            B = a.at or now
            A = (dt.datetime.strptime(B, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
                 - dt.timedelta(hours=a.hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
            ca, cb = census(rows, A), census(rows, B)
            derived = True
            rows_at_a = None
        show(ca, f"A = {A}" + ("  (derived)" if derived else ""))
        print()
        show(cb, f"B = {B}" + ("  (derived)" if derived else ""))
        print()
        na, nb = counts(ca), counts(cb)
        print("change:")
        for k in STATUS:
            d = nb[k] - na[k]
            print(f"  Status {k}  {na[k]:4d} -> {nb[k]:4d}   {d:+d}")
        if derived:
            print("NOTE: both ends derived from today's file — this is a consistency check, not a")
            print("      validation: a retroactive append is already in both ends and cannot show up.")
        elif rows_at_a is None:
            print("NOTE: snapshot A predates the row-count field, so this window is timestamp-based;")
            print("      a row appended later with an older timestamp will look unaccounted.")
        ts = transitions(evs, A, B, rows_at_a)
        print(f"\naudit trail: {len(ts)} transition(s)")
        by_actor: dict[str, int] = {}
        for t in ts:
            by_actor[t["actor"]] = by_actor.get(t["actor"], 0) + 1
        print("  by amigo: " + ", ".join(f"{k} {v}" for k, v in sorted(by_actor.items(), key=lambda x: -x[1])))
        for t in ts:
            print(f"    {t['ts']}  {t['id']}  {t['from']} -> {t['to']}  by {t['actor']} ({t['kind']})")
        bad = validate(evs, A, B, ca, cb, rows_at_a)
        print(f"\nvalidation: {'PASS' if not bad else 'FAIL'} — "
              f"{len(ts)} transitions explain {sum(1 for _ in ts)} status changes")
        for b in bad:
            print(f"  UNACCOUNTED {b['id']}: predicted Status {b['predicted']}, counted Status {b['counted']}")
        return 0 if not bad else 1

    when = a.at or now
    c = census(rows, when)
    show(c, f"census at {when}")
    since = (dt.datetime.strptime(when, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
             - dt.timedelta(hours=a.hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"\ntransitions in the last {a.hours:g}h: {len(transitions(evs, since, when))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
