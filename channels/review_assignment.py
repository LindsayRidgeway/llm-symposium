#!/usr/bin/env python3
# Owner: Desi
"""The assignment algorithm — who reviews an item, and why it was that amigo.

Why this exists (2026-10-09). The human asked, in the 2026-10-09 Telegram chat, how the commons
decides *who* reviews a piece of work. The honest answer was that there was no algorithm: reviews
had piled up in a waiting queue (W) with no reviewer named on any of them. He proposed one, and it
is the rule this module implements:

    (a) if one amigo is best suited to the work, choose that amigo — the author is excluded, and the
        one-line reason is recorded;
    (b) otherwise, choose at random among the *least expensive* amigos.

Two refinements he and Desi settled in the same chat, and both are load-bearing rather than
decoration:

  * Cost only governs the *interchangeable residue*. Anything with a real competence match goes to
    branch (a) first, so cost can never pick a poorly-matched reviewer for work that has a right
    answer. (a) protects (b) from doing harm.
  * The draw is evaluated *once and written down*. If the cost branch were re-rolled on every wake,
    a price change would re-assign an item already in flight. Recording the draw freezes the
    decision at the moment it was made; the price list moves underneath it without moving the
    assignment.

The cost side is cached, not recomputed. His idea (2026-10-09): a **monthly** job ranks the amigos
by price and writes a dated file; every assignment after that reads the file instead of re-deriving
the ranking. Three properties make the cache safe rather than merely cheap, and all three are
pinned in the tests:

  * it names a **band** — the set of least-expensive amigos, all ties included — not a single
    winner, or the random branch loses its pool;
  * it is **dated**, so a stale list is visible in the record instead of silently authoritative;
  * it is read, never recomputed, at assignment time — the draw is what freezes, not the band.

Store. Assignments are append-only JSON Lines, `channels/review-assignments.jsonl`, one object per
line; a later line for the same item id is a state change. Same shape, and for the same reason, as
`channels/items.jsonl`: an append-only file cannot be half-written into a plausible lie, and a
frozen draw is exactly a fact that must not be rewritten in place. The frozen store is the thing
that makes "it cannot re-roll on a later wake" true rather than aspirational.

CLI:
    python3 channels/review_assignment.py --band
    python3 channels/review_assignment.py --assign <item-id> --author <amigo>
    python3 channels/review_assignment.py --assign <item-id> --author <amigo> --best claude \\
        --reason "why claude is best suited"
    python3 channels/review_assignment.py --show <item-id>
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ASSIGNMENTS = REPO / "channels" / "review-assignments.jsonl"
BAND_FILE = REPO / "channels" / "review-cost-band.json"

# The five bodies (ROSTER.md). `author` is the amigo whose wake performed the item; no amigo
# reviews its own work, which is the one exclusion the algorithm never relaxes.
AMIGOS = ("claude", "desi", "gemini", "tarik", "dmitri")

# A band is produced monthly; allow a month plus slack before calling it stale. Staleness is
# recorded and warned about, never silently ignored and never a hard stop — a stale band still
# assigns a reviewer, and a missing reviewer is the worse failure.
BAND_STALE_DAYS = 45


def _today(now=None) -> str:
    return (now or dt.date.today()).isoformat()


# --------------------------------------------------------------------------------------------
# The cost band — the dated monthly cache
# --------------------------------------------------------------------------------------------

def least_expensive_band(prices: dict) -> list:
    """The set of amigos tied at the lowest price. A *band*, never a single winner.

    Returning one name here would collapse the random branch in `choose_reviewer` into a fixed
    assignment, which is exactly the error the human named ("it has to name a band, not a
    winner").
    """
    if not prices:
        raise ValueError("no prices to rank")
    for name, cost in prices.items():
        if cost is None or not isinstance(cost, (int, float)) or cost < 0:
            raise ValueError(f"bad price for {name!r}: {cost!r}")
    low = min(prices.values())
    return sorted(name for name, cost in prices.items() if cost == low)


def build_band(prices: dict, as_of=None, unit="USD per 1M tokens", source="", note="") -> dict:
    """A dated band record. `prices` is kept alongside `band` so the ranking is auditable."""
    return {
        "as_of": as_of or _today(),
        "unit": unit,
        "prices": {k: prices[k] for k in sorted(prices)},
        "band": least_expensive_band(prices),
        "source": source,
        "note": note,
    }


def write_band(prices: dict, path=BAND_FILE, **kw) -> dict:
    band = build_band(prices, **kw)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(band, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return band


def read_band(path=BAND_FILE) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def band_age_days(band: dict, today=None) -> int:
    as_of = dt.date.fromisoformat(band["as_of"])
    return ((today or dt.date.today()) - as_of).days


def band_is_stale(band: dict, today=None, max_days: int = BAND_STALE_DAYS) -> bool:
    return band_age_days(band, today) > max_days


# --------------------------------------------------------------------------------------------
# The algorithm
# --------------------------------------------------------------------------------------------

def choose_reviewer(author, band, best=None, best_reason=None, rng=None) -> dict:
    """Decide the reviewer for one item. Does not persist — see `assign`.

    `author`  the amigo whose wake performed the item (never assigned to itself).
    `band`    the least-expensive band, read from the dated cache.
    `best`    the clearly-best-suited amigo, if the caller declares one (branch a).
    `rng`     a `random.Random` for the draw, so a test can seed it.
    """
    if author not in AMIGOS:
        raise ValueError(f"unknown author {author!r} (not one of {AMIGOS})")
    band = list(band)
    for name in band:
        if name not in AMIGOS:
            raise ValueError(f"unknown amigo {name!r} in band (not one of {AMIGOS})")

    # Branch (a): a competence match wins — unless it is the author, who is excluded.
    if best:
        if best not in AMIGOS:
            raise ValueError(f"unknown amigo {best!r} (not one of {AMIGOS})")
        if best != author:
            reason = (best_reason or "").strip()
            if not reason:
                raise ValueError("a competence assignment must record its one-line reason")
            return {"method": "competence", "reviewer": best, "reason": reason,
                    "band": band, "best": best}
        # best-suited *is* the author: fall through to the cost draw rather than break the exclusion.

    # Branch (b): a random draw from the band, with the author removed from the pool.
    pool = sorted(name for name in band if name != author)
    if not pool:
        raise ValueError(
            f"no eligible reviewer: the band {band} contains only the author {author!r}; "
            f"refresh the band or assign by competence"
        )
    pick = (rng or random).choice(pool)
    reason = (f"no competence match; drawn at random from the least-expensive band {band}"
              + (f" (author {author!r} excluded)" if best == author else ""))
    return {"method": "cost-draw", "reviewer": pick, "reason": reason, "band": band,
            "best": None}


# --------------------------------------------------------------------------------------------
# The frozen store
# --------------------------------------------------------------------------------------------

def read_assignments(path=ASSIGNMENTS) -> dict:
    """Latest assignment per item id, from the append-only store."""
    out: dict = {}
    p = Path(path)
    if not p.exists():
        return out
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        item = rec.get("item")
        if item:
            out[item] = rec
    return out


def assignment_for(item, path=ASSIGNMENTS):
    return read_assignments(path).get(item)


def record_assignment(rec, path=ASSIGNMENTS):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def assign(item, author, band_record, best=None, best_reason=None, rng=None,
           path=ASSIGNMENTS, now=None) -> dict:
    """Freeze an assignment for `item`, or return the one already frozen.

    The freeze is the whole point: a second call for the same item returns the recorded reviewer
    unchanged, even if the band (or the caller's `best`) has changed meanwhile. That is what makes
    a later price change unable to jerk a job away from an amigo mid-flight.
    """
    existing = assignment_for(item, path)
    if existing is not None:
        return existing
    decision = choose_reviewer(author, band_record["band"], best=best,
                               best_reason=best_reason, rng=rng)
    rec = dict(decision)
    rec.update({
        "item": item,
        "author": author,
        "band_as_of": band_record.get("as_of"),
        "assigned_utc": (now or dt.datetime.now(dt.timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    })
    return record_assignment(rec, path)


# --------------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------------

def _cmd_band(_args) -> int:
    band = read_band()
    age = band_age_days(band)
    stale = band_is_stale(band)
    print(f"band (as of {band['as_of']}, {age}d old"
          + (", STALE" if stale else "") + f"): {', '.join(band['band'])}")
    print(f"  unit:   {band.get('unit', '')}")
    print(f"  prices: " + ", ".join(f"{k}={v}" for k, v in band["prices"].items()))
    if stale:
        print(f"  ** STALE: older than {BAND_STALE_DAYS} days — the monthly job should refresh it.",
              file=sys.stderr)
    return 0


def _cmd_assign(args) -> int:
    band = read_band()
    if band_is_stale(band):
        print(f"warning: cost band is stale (as of {band['as_of']}); assignment proceeds but "
              f"records that date.", file=sys.stderr)
    rec = assign(args.item, args.author, band, best=args.best, best_reason=args.reason)
    print(f"{rec['item']}: {rec['reviewer']}  [{rec['method']}]  {rec['reason']}")
    return 0


def _cmd_show(args) -> int:
    rec = assignment_for(args.item)
    if rec is None:
        print(f"{args.item}: no assignment recorded")
        return 1
    print(json.dumps(rec, indent=2, sort_keys=True))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Who reviews an item, and why.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--band", action="store_true", help="print the dated cost band")
    g.add_argument("--assign", metavar="ITEM", help="freeze an assignment for ITEM")
    g.add_argument("--show", metavar="ITEM", help="print the assignment recorded for ITEM")
    ap.add_argument("--author", choices=AMIGOS)
    ap.add_argument("--best", choices=AMIGOS, default=None)
    ap.add_argument("--reason", default=None)
    args = ap.parse_args(argv)

    if args.band:
        return _cmd_band(args)
    if args.assign:
        if not args.author:
            ap.error("--assign requires --author")
        args.item = args.assign
        return _cmd_assign(args)
    args.item = args.show
    return _cmd_show(args)


if __name__ == "__main__":
    raise SystemExit(main())
