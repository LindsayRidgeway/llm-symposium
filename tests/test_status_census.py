#!/usr/bin/env python3
"""The 24-hour status audit — four shapes, and the one that used to pass while hiding an arrival.

Written 2026-10-19 by Desi. Origin: the first real window (A = 2026-10-17T23:29Z, B =
2026-10-19T01:09Z) FAILED, and the report is `channels/reports/2026-10-19-desi-status-audit-b.md`.
The ledger grew by 32 items; the trail could place 18; ten were named as unaccounted; four more
were *masked* — not counted at A, then carried to exactly the right answer at B by an in-window
close on an item A never had, so the raw comparison said nothing at all.

That is why these tests exist rather than a one-line fix. The window failed for a real reason —
the ledger had no write clock, so a row appended after A for an older run could not be placed —
and a validator that can be satisfied by an arrival it never counted is worse than no validator.

The four shapes every future window must land in one of:

1. clean: an item filed inside the window is a transition, applied, and the window PASSES;
2. backdated, stamped: a row written inside the window for an older run carries `recorded_utc`,
   so the ledger's write clock places it as an arrival and the window PASSES;
3. backdated, unstamped: the same row with no write stamp is UNPLACEABLE — FAIL, named;
4. masked: an item absent from A is closed inside the window and the plain comparison agrees;
   it must be reported as a MASKED ARRIVAL, not silence;
5. lost update: a status change with no logged row at all must FAIL.

Run: python3 tests/test_status_census.py        (exit 0 pass, 1 fail)
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import status_census as sc  # noqa: E402

fails = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}  {detail}")
        fails.append(name)


def row(item, filed, state=None, state_utc=None, recorded=None, reviewer="auto:land", amigo="desi"):
    r = {"id": item, "amigo": amigo, "scope": "internal", "title": "t",
         "filed_utc": filed, "source": "derived"}
    if state:
        r["state"] = state
        r["state_utc"] = state_utc or filed
        r["reviewer"] = reviewer
    if recorded:
        r["recorded_utc"] = recorded
    return r


def window(rows, a, b):
    """The same three steps main() takes, without writing census files."""
    evs = sc.events(rows)
    ca, cb = sc.census(rows, a), sc.census(rows, b)
    trail = sorted(sc.transitions(evs, a, b) + sc.arrivals(rows, evs, a, b, ca),
                   key=lambda t: t["ts"])
    return evs, ca, cb, trail, sc.validate(evs, a, b, ca, cb, trail), sc.classify(ca, cb, trail)


A, B = "2026-10-19T00:00:00Z", "2026-10-20T00:00:00Z"

print("1. clean window — filed and closed inside (A, B]")
rows = [row("20261019T010000Z-aaaaaaaa", "2026-10-19T01:00:00Z")]
evs, ca, cb, trail, bad, split = window(rows, A, B)
check("A is empty", ca == {}, ca)
check("B counts it at Status 2", cb.get("20261019T010000Z-aaaaaaaa") == "2", cb)
check("it is a placed arrival", split["placed"] == ["20261019T010000Z-aaaaaaaa"], split)
check("no unplaceable, no masked", not bad and not split["masked"], (bad, split))

print("2. backdated row WITH a write stamp — the repair")
rows = [row("20261018T130000Z-bbbbbbbb", "2026-10-18T13:00:00Z",
            recorded="2026-10-19T05:00:00Z")]
evs, ca, cb, trail, bad, split = window(rows, A, B)
check("A does not have it", "20261018T130000Z-bbbbbbbb" not in ca, ca)
check("the trail places it at the write time",
      [t["ts"] for t in trail if t["id"] == "20261018T130000Z-bbbbbbbb"] == ["2026-10-19T05:00:00Z"],
      trail)
check("validation passes", not bad, bad)
check("classified as placed", split["placed"] == ["20261018T130000Z-bbbbbbbb"], split)

print("3. backdated row with NO write stamp — unplaceable, and named")
rows = [row("20261018T130000Z-cccccccc", "2026-10-18T13:00:00Z")]
evs, ca, cb, trail, bad, split = window(rows, A, B)
check("A does not have it", "20261018T130000Z-cccccccc" not in ca, ca)
check("validation fails", len(bad) == 1 and bad[0]["predicted"] == sc.ABSENT, bad)
check("classified unplaceable", split["unplaceable"] == ["20261018T130000Z-cccccccc"], split)
check("nothing claims it is masked or placed",
      not split["masked"] and not split["placed"], split)

print("4. masked arrival — the case that used to print PASS")
# Item filed before A (so absent from census A only because the row arrived late), then closed
# inside the window: predicted 1, counted 1 — the plain comparison agrees and says nothing.
rows = [
    row("20261018T170000Z-dddddddd", "2026-10-18T17:00:00Z", amigo="tarik"),
    {"id": "20261018T170000Z-dddddddd", "amigo": "desi", "scope": "internal", "title": "t",
     "filed_utc": "2026-10-18T17:00:00Z", "state": "accomplished",
     "state_utc": "2026-10-19T13:00:00Z", "reviewer": "desi", "source": "derived",
     "assigned_to": "desi", "assigned_utc": "2026-10-19T12:00:00Z", "assigned_by": "draw"},
]
evs, ca, cb, trail, bad, split = window(rows, A, B)
check("A does not have it", "20261018T170000Z-dddddddd" not in ca, ca)
check("B counts it closed", cb.get("20261018T170000Z-dddddddd") == "1", cb)
check("the raw comparison would have said nothing", not bad, bad)
check("it is reported as a MASKED ARRIVAL",
      split["masked"] == ["20261018T170000Z-dddddddd"], split)

print("5. lost update — a status change with no logged row")
rows = [row("20261019T010000Z-eeeeeeee", "2026-10-19T01:00:00Z")]
evs = sc.events(rows)
ca = sc.census(rows, A)
cb = dict(sc.census(rows, B))
cb["20261019T010000Z-eeeeeeee"] = "1"          # pretend a close happened that nobody logged
bad = sc.validate(evs, A, B, ca, cb, sc.transitions(evs, A, B))
check("validation fails on the unlogged change", len(bad) == 1, bad)

print("6. the writer stamps what the reader needs")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "channels"))
import item_ledger as il  # noqa: E402
with tempfile.TemporaryDirectory() as tmp:
    p = Path(tmp) / "items.jsonl"
    il.append([{"id": "20261018T130000Z-ffffffff", "amigo": "desi", "scope": "internal",
                "title": "t", "filed_utc": "2026-10-18T13:00:00Z"}], p)
    written = json.loads(p.read_text(encoding="utf-8").strip())
    check("append writes recorded_utc", written.get("recorded_utc", "").endswith("Z"),
          written.get("recorded_utc"))
    check("event time is untouched", written["filed_utc"] == "2026-10-18T13:00:00Z", written)
    il.append([{"id": "x", "recorded_utc": "2026-10-19T00:00:00Z"}], p)
    second = json.loads(p.read_text(encoding="utf-8").splitlines()[1])
    check("an explicit stamp is not overwritten",
          second["recorded_utc"] == "2026-10-19T00:00:00Z", second)

print()
if fails:
    print(f"FAILED {len(fails)}: {', '.join(fails)}")
    sys.exit(1)
print("all status-census checks pass")
