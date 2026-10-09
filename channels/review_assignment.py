#!/usr/bin/env python3
# Owner: Desi
"""The reviewer-assignment algorithm — who reviews a waiting item, decided once and written down.

Why this exists (2026-10-09). The review queue does not drain, and the reason the human found in the
live session is structural: **nobody was ever assigned**. An item sat in W with no name on it, so no
wake had a job — a queue with no assignee has no exit. `item_ledger.waiting` builds the pile and shows
it to whichever reviewer shows up; it never says whose item it is. This puts the name on the item.

The rule is the human's (Telegram, 2026-10-09), and it is his suggestion adopted, not the commons' own
finding — recorded here so the record credits him and not us. His words:

    (a) if one amigo is best suited to completing the work, choose that amigo;
    (b) otherwise, randomly choose one of the least expensive amigos.

Three corrections the same session added before building it, each a failure mode the bare rule invites:

  1. **The author is never the reviewer, even when best suited.** "Best suited" almost always resolves
     to whoever wrote the item, so a rule without this exclusion removes the check in the name of
     matching it. The exclusion is enforced in both branches.
  2. **Branch (a) writes down why.** An unnamed judgement is a mood, and a mood drifts toward whoever
     was seen last. One line, recorded at assignment time.
  3. **The draw is recorded and frozen.** A random choice re-evaluated on a later wake re-rolls, and an
     item that re-rolls is an item owned by no one again. Evaluated once, written down, done. Re-running
     the assignment refuses an item that already carries a name.

And the cost input is a monthly cache (the human's second idea, same session): a monthly job ranks the
amigos' current prices and writes a dated file; the draw reads that file instead of re-deriving prices
every turn. Two properties make the cache safe rather than merely cheap, both his:

  - it names a **band** (the least expensive *set*), never a single winner, or the random branch loses
    its pool and collapses back to "always assign to the cheapest";
  - it is **dated**, so a stale list is visible rather than silently authoritative.

Data. `channels/review-assignment-band.json` is the cache: the prices, their source and date, and the
band derived from them. It and the band cannot drift, because `band_problems` recomputes the band from
the prices and refuses a file where they disagree. `channels/item_ledger.py` holds the items; an
assignment is one more append-only state line on the item (`assigned_reviewer`, `assigned_utc`,
`branch`, `assign_reason`, `band_generated_utc`) — no second queue and no new file of items.

CLI:
    python3 channels/review_assignment.py --band                # the band, its age and its source
    python3 channels/review_assignment.py --refresh-band        # recompute the band from the prices
    python3 channels/review_assignment.py --assign --limit 5    # name the oldest unassigned W items
    python3 channels/review_assignment.py --queue desi          # the W items assigned to one amigo
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from channels import item_ledger as il  # noqa: E402

BAND_PATH = REPO / "channels" / "review-assignment-band.json"

# The five bodies, in a fixed order so a draw is reproducible from a seed.
AMIGOS = ("desi", "claude", "gemini", "tarik", "dmitri")

STAMP = "%Y-%m-%dT%H:%M:%SZ"


def _utcnow(now: dt.datetime | None = None) -> str:
    now = now or dt.datetime.now(dt.timezone.utc)
    return now.astimezone(dt.timezone.utc).strftime(STAMP)


def _parse(stamp: str | None) -> dt.datetime | None:
    if not stamp:
        return None
    try:
        return dt.datetime.strptime(stamp, STAMP).replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return None


# --------------------------------------------------------------------------------------------------
# The band cache: prices in, a dated least-expensive set out.
# --------------------------------------------------------------------------------------------------

def least_expensive(prices: dict) -> list[str]:
    """Every amigo at the minimum of the numeric prices — the *set*, never a single winner.

    A tie is the normal case, not an edge one: Desi and Dmitri share one model and therefore one price.
    Returning the whole minimum set is what keeps branch (b) from collapsing back to "the cheapest",
    which is just branch (a) with a price list instead of a reason.
    """
    numeric = {a: v for a, v in (prices or {}).items()
               if isinstance(v, (int, float)) and not isinstance(v, bool)}
    if not numeric:
        return []
    lo = min(numeric.values())
    return sorted(a for a, v in numeric.items() if v == lo)


def build_band(prices: dict, *, source: str = "", unit: str = "", max_age_days: int = 45,
               now: dt.datetime | None = None, note: str = "") -> dict:
    """A fresh cache object: prices, their provenance, and the band recomputed from them."""
    return {
        "_what": ("The monthly cache for channels/review_assignment.py. A wake refreshes the prices "
                  "from current published rates and dates the file; the assignment draw reads the band "
                  "below instead of re-deriving prices every turn."),
        "generated_utc": _utcnow(now),
        "max_age_days": max_age_days,
        "unit": unit,
        "source": source,
        "prices": dict(prices),
        "band": least_expensive(prices),
        "_note": note,
    }


def band_problems(band: dict) -> list[str]:
    """Reasons the cache is unusable. Empty means it is internally consistent and names real amigos."""
    problems: list[str] = []
    if not isinstance(band, dict):
        return ["band is not an object"]
    named = sorted(band.get("band") or [])
    expected = least_expensive(band.get("prices") or {})
    if not expected:
        problems.append("no numeric prices — the band cannot be derived or checked")
    if named != expected:
        problems.append(
            f"band {named} does not match the least expensive set from the prices {expected} "
            f"(the file is stale or hand-edited; run --refresh-band)")
    for a in named:
        if a not in AMIGOS:
            problems.append(f"band names an unknown amigo {a!r}")
    if not named:
        problems.append("band is empty — the random branch would have no pool")
    if _parse(band.get("generated_utc")) is None:
        problems.append("generated_utc is missing or unparseable, so staleness cannot be judged")
    return problems


def band_age_days(band: dict, now: dt.datetime | None = None) -> float | None:
    when = _parse((band or {}).get("generated_utc"))
    if when is None:
        return None
    return ((now or dt.datetime.now(dt.timezone.utc)) - when).total_seconds() / 86400.0


def band_is_stale(band: dict, now: dt.datetime | None = None) -> bool:
    """True when the cache is old enough to mislead. An unreadable date is stale, not fresh."""
    age = band_age_days(band, now)
    if age is None:
        return True
    limit = (band or {}).get("max_age_days") or 45
    return age > float(limit)


def load_band(path: Path = BAND_PATH) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def refresh_band(path: Path = BAND_PATH, now: dt.datetime | None = None) -> dict:
    """Recompute the band from the file's own prices and redate it. The prices are left untouched.

    This is the cheap half of the monthly job. The expensive half — reading current published rates and
    editing `prices` — is a judgement no script should fake, so it stays a documented wake task; this
    only guarantees that whatever the prices currently are, the band agrees with them and is dated.
    """
    path = Path(path)
    band = load_band(path)
    band["band"] = least_expensive(band.get("prices") or {})
    band["generated_utc"] = _utcnow(now)
    path.write_text(json.dumps(band, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return band


# --------------------------------------------------------------------------------------------------
# The algorithm.
# --------------------------------------------------------------------------------------------------

def eligible_pool(author: str, amigos: tuple[str, ...] = AMIGOS) -> list[str]:
    """Everyone who could review this item: all amigos but the one who performed it."""
    return [a for a in amigos if a != author]


def choose_reviewer(item: dict, *, band: dict | None = None, best_suited: str | None = None,
                    reason: str = "", rng: random.Random | None = None,
                    now: dt.datetime | None = None) -> dict:
    """Decide one item's reviewer and return the assignment to be written onto it.

    Branch (a) when `best_suited` is named, with a reason and never the author; branch (b) otherwise —
    a draw among the band (the least expensive eligible amigos), recorded whole so it cannot re-roll.
    """
    author = item.get("amigo") or item.get("author")
    if not author:
        raise ValueError("item carries no amigo/author, so the author cannot be excluded from review")
    pool = eligible_pool(author)
    band = band or {}
    band_set = {a for a in (band.get("band") or []) if a in AMIGOS}
    stamp = _utcnow(now)

    if best_suited:
        if best_suited == author:
            raise ValueError(f"the author ({author}) may not review their own work, however well suited")
        if best_suited not in AMIGOS:
            raise ValueError(f"best_suited {best_suited!r} is not one of {AMIGOS}")
        if not reason.strip():
            raise ValueError("branch (a) needs a one-line reason — an unnamed judgement is a mood")
        return {
            "assigned_reviewer": best_suited,
            "assigned_utc": stamp,
            "branch": "a",
            "assign_reason": reason.strip(),
            "pool": [best_suited],
            "band_generated_utc": band.get("generated_utc"),
        }

    drawn_from = [a for a in pool if a in band_set] or pool
    chooser = rng or random.Random()
    pick = chooser.choice(sorted(drawn_from))
    if drawn_from == pool and not band_set:
        why = f"drawn from all amigos but the author ({sorted(pool)}) — no usable band"
    elif drawn_from == pool:
        why = (f"drawn from all amigos but the author ({sorted(pool)}) — the band "
               f"{sorted(band_set)} left no eligible reviewer")
    else:
        why = f"drawn from the least expensive at assignment time ({sorted(drawn_from)})"
    return {
        "assigned_reviewer": pick,
        "assigned_utc": stamp,
        "branch": "b",
        "assign_reason": why,
        "pool": sorted(drawn_from),
        "band_generated_utc": band.get("generated_utc"),
    }


def unassigned_waiting(items: dict, limit: int | None = None) -> list[dict]:
    """The oldest W items that carry no name yet. Oldest first, because the pile's age is the finding."""
    rows = [r for r in items.values()
            if il.letter_for(r) == "W" and not r.get("assigned_reviewer")]
    rows.sort(key=lambda r: r.get("filed_utc") or "")
    return rows[:limit] if limit else rows


def assigned_to(items: dict, amigo: str) -> list[dict]:
    """The W items whose name is this amigo — the reviewer's own queue, as seen from the ledger."""
    rows = [r for r in items.values()
            if r.get("assigned_reviewer") == amigo and il.letter_for(r) == "W"]
    rows.sort(key=lambda r: r.get("filed_utc") or "")
    return rows


def assign_pending(items: dict, *, band: dict | None = None, limit: int = 5,
                   rng: random.Random | None = None, now: dt.datetime | None = None) -> list[dict]:
    """Assign the `limit` oldest unassigned W items. Returns the records to append, not yet written.

    `items` is not mutated beyond returning what to write: a draw that is decided but not written is
    exactly the re-rollable strobe-light the rule forbids, so the caller must append the result.
    """
    out = []
    for rec in unassigned_waiting(items, limit):
        assignment = choose_reviewer(rec, band=band, rng=rng, now=now)
        out.append(dict(rec, **assignment))
    return out


def apply(assignments: list[dict], path: Path = il.LEDGER) -> None:
    il.append(assignments, path)


# --------------------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------------------

def _print_band(band: dict) -> None:
    probs = band_problems(band)
    age = band_age_days(band)
    print(f"band: {band.get('band')}")
    print(f"  prices: {band.get('prices')}")
    print(f"  unit:   {band.get('unit')}")
    print(f"  source: {band.get('source')}")
    print(f"  dated:  {band.get('generated_utc')} "
          + (f"({age:.1f} days old)" if age is not None else "(unreadable date)"))
    if probs:
        print("  PROBLEMS: " + "; ".join(probs))
    elif band_is_stale(band):
        print(f"  STALE: older than {band.get('max_age_days')} days — refresh the prices, "
              "or the band is a guess wearing a date.")
    else:
        print("  ok")


def _cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--band", action="store_true", help="print the cached band and its age")
    ap.add_argument("--refresh-band", action="store_true",
                    help="recompute the band from the file's prices and redate it")
    ap.add_argument("--assign", action="store_true", help="name the oldest unassigned W items")
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--seed", type=int, default=None, help="with --assign: fix the draw (default: system)")
    ap.add_argument("--queue", metavar="AMIGO", help="print the W items assigned to one amigo")
    args = ap.parse_args()

    if args.refresh_band:
        band = refresh_band(now=dt.datetime.now(dt.timezone.utc))
        _print_band(band)
        return 0
    if args.band:
        _print_band(load_band())
        return 0
    if args.queue:
        rows = assigned_to(il.load(), args.queue)
        print(f"{len(rows)} item(s) waiting for review, assigned to {args.queue}:")
        for rec in rows:
            print(f"  {rec.get('filed_utc')}  {rec.get('amigo'):7s} "
                  f"[{rec.get('branch')}] {il._short(rec.get('title', ''))}")
        return 0
    if args.assign:
        band = load_band()
        probs = band_problems(band)
        if probs:
            print("refusing to assign on a bad band: " + "; ".join(probs), file=sys.stderr)
            return 1
        rng = random.Random(args.seed) if args.seed is not None else random.Random()
        pending = assign_pending(il.load(), band=band, limit=args.limit, rng=rng)
        if not pending:
            print("nothing unassigned in W")
            return 0
        apply(pending)
        for rec in pending:
            print(f"  {rec['id']}  ({rec.get('amigo')}) -> {rec['assigned_reviewer']}  "
                  f"[{rec['branch']}] {rec['assign_reason']}")
        print(f"item_ledger: {len(pending)} assignment(s) written to {il.LEDGER.relative_to(REPO)}")
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
