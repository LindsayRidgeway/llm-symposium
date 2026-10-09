#!/usr/bin/env python3
# Owner: Dmitri
"""The reviewer-assignment rule — who looks at a waiting item, decided once and written down.

Why this exists (2026-10-09). The human asked, over Telegram, whether the reviewer was always Desi
or Dmitri. When Desi told him there was no algorithm at all — the review step ran only in Desi's own
body — the human supplied one:

  (a) if one amigo is clearly best suited to the work, assign that amigo;
  (b) otherwise draw at random among the least-expensive amigos *at the time of assignment*.

Desi refined it the same day and the refinements are load-bearing, so they are implemented here
rather than left as prose to be re-derived:

  * the author is excluded — nobody reviews their own work (the rule `item_ledger` already keeps);
  * a competence match carries its reason in writing, so "best suited" is a claim that can be read;
  * the cost cache names a **band** (the set of amigos tied for least expensive), not a single
    winner, or the random branch has no pool left to draw from;
  * the cache is **dated**, so a stale list is visible rather than silently authoritative;
  * the draw **freezes** at assignment time — recorded, so a later price change cannot re-roll it
    and jerk a job away from someone mid-flight.

What this does *not* decide. Whether an item needs a reviewer at all; that is `item_ledger`'s letter
W (`channels/item_ledger.py --next`). This decides *who*, once, and writes it where it cannot drift.

Store: `channels/assignments.jsonl` — append-only, one object per assignment, keyed by item id.
Cost cache: `channels/usage/cost-band.json` — dated; `bands[0]` is the least-expensive set.

CLI:
    python3 channels/assignment.py --item <id>                    # decide and record, frozen
    python3 channels/assignment.py --item <id> --show             # decide, print, write nothing
    python3 channels/assignment.py --item <id> --best desi \\
        --because "she holds the mail keys"                       # a named competence match
    python3 channels/assignment.py --list                         # every assignment on record
    python3 channels/assignment.py --selftest                     # fixtures; no file touched
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STORE = REPO / "channels" / "assignments.jsonl"
COSTS = REPO / "channels" / "usage" / "cost-band.json"
ITEMS = REPO / "channels" / "items.jsonl"

AMIGOS = ("desi", "dmitri", "gemini", "claude", "tarik")
STALE_DAYS = 45          # a dated band older than this is shown as stale, never silently trusted


# --------------------------------------------------------------------- cost band

def load_costs(path: Path = COSTS) -> dict:
    """The dated cost cache. Missing or unreadable -> an empty dict (band unknown, not zero)."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def band_as_of(costs: dict) -> str | None:
    value = costs.get("as_of")
    return value if isinstance(value, str) and value.strip() else None


def is_stale(as_of: str | None, today: dt.date | None = None) -> bool:
    """A band with no date is stale in the sense that matters: it cannot be shown current."""
    if not as_of:
        return True
    today = today or dt.date.today()
    try:
        when = dt.date.fromisoformat(as_of)
    except ValueError:
        return True
    return (today - when).days > STALE_DAYS


def least_expensive(costs: dict, eligible) -> list:
    """The least-expensive set among `eligible`, preserving the cache's order. Empty if unbanded.

    `bands` is ordered cheapest-first by the cache's own contract; bands[0] is the band the draw
    reads. An eligible member absent from every band is not in the draw pool — the cache decides
    who is cheap, and an unknown amigo is not.
    """
    bands = costs.get("bands")
    if not isinstance(bands, list):
        return []
    for band in bands:
        members = band.get("members") if isinstance(band, dict) else None
        if isinstance(members, list):
            out = [a for a in members if a in eligible]
            if out:
                return out
    return []


# --------------------------------------------------------------------- the draw

def draw(pool, seed: str):
    """A reproducible draw: same pool + same seed always gives the same pick.

    `hash()` is salted per process, so it cannot freeze a decision across wakes — a sha256 of the
    item id can. The pick is the whole point of freezing: evaluated fresh each wake, a price change
    would re-roll the assignment; evaluated from the id, it never moves.
    """
    ordered = sorted(pool)
    if not ordered:
        return None
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return ordered[int(h, 16) % len(ordered)]


# --------------------------------------------------------------------- the rule

def _competence(item: dict, rules, best: str, because: str, eligible) -> tuple[str, str] | None:
    """Branch (a). A single, written competence match — or nothing, so branch (b) runs.

    Ambiguity is not a match: if two rules fire, the item is not *clearly* best-suited to one amigo,
    so it falls through to the draw rather than to whichever rule was written first.
    """
    if best:
        if best not in eligible:
            return None
        return best, (because.strip() or "named as best suited")
    matches = []
    for rule in (rules or []):
        keyword = str(rule.get("match", "")).strip().lower()
        who = str(rule.get("amigo", "")).strip().lower()
        if keyword and who in eligible and keyword in (item.get("title", "") or "").lower():
            matches.append((who, str(rule.get("reason", "")).strip() or f"matches {keyword!r}"))
    if len(matches) == 1:
        return matches[0]
    return None


def _reason_for_draw(pool, band, stale) -> str:
    if band:
        head = (f"drawn at random among the least-expensive band {band}"
                + ("; band is stale" if stale else ""))
    else:
        head = ("drawn at random among all eligible amigos — no cost band on record, "
                "so no least-expensive set could be read")
    return head


def decide(item: dict, *, costs: dict | None = None, competence=None, best: str = "",
           because: str = "", amigos=AMIGOS, author: str | None = None,
           today: dt.date | None = None) -> dict:
    """The decision for one item, as a record. Pure: reads no files, writes none, draws no RNG state.

    The author is never eligible. An unknown author is left open and *recorded as unknown* — the
    one case where this cannot exclude the author, so it is named rather than assumed away.
    """
    who_author = item.get("amigo", author)
    eligible = [a for a in amigos if a != who_author]
    costs = costs or {}
    as_of = band_as_of(costs)
    stale = is_stale(as_of, today)

    hit = _competence(item, competence, best, because, eligible)
    if hit:
        reviewer, reason = hit
        return {"id": item.get("id"), "reviewer": reviewer, "method": "competence",
                "reason": reason, "author": who_author, "eligible": eligible,
                "band": None, "band_as_of": as_of, "band_stale": False,
                "seed": None, "pool": [reviewer],
                "decided_utc": _now()}

    band = least_expensive(costs, eligible)
    pool = band or eligible
    picked = draw(pool, item.get("id", ""))
    return {"id": item.get("id"), "reviewer": picked, "method": "draw",
            "reason": _reason_for_draw(eligible, band, stale),
            "author": who_author, "eligible": eligible,
            "band": band or None, "band_as_of": as_of, "band_stale": stale,
            "seed": item.get("id", ""), "pool": sorted(pool),
            "decided_utc": _now()}


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------- the store

def load_assignments(path: Path = STORE) -> dict:
    """Every assignment, later lines for the same id winning. Frozen = first write is the answer."""
    out: dict[str, dict] = {}
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return out
    for lineno, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
            out[rec["id"]] = rec
        except (ValueError, KeyError):
            print(f"assignment: skipping unreadable line {lineno}", file=sys.stderr)
    return out


def append(records, path: Path = STORE) -> None:
    if not records:
        return
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("a", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")


def assign(item: dict, path: Path = STORE, **kw) -> tuple[dict, bool]:
    """Freeze one assignment. Returns (record, wrote). A second call returns the first record.

    The freeze is the rule, not a convenience: if the decision were re-derived each wake, a change
    to the price band would silently reassign work that is already in someone's hands.
    """
    existing = load_assignments(path).get(item.get("id"))
    if existing:
        return existing, False
    rec = decide(item, **kw)
    append([rec], path)
    return rec, True


def load_items(path: Path = ITEMS) -> dict:
    out: dict[str, dict] = {}
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return out
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
            out[rec["id"]] = rec
        except (ValueError, KeyError):
            continue
    return out


def load_competence(path: Path) -> list:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    rules = data.get("rules") if isinstance(data, dict) else None
    return rules if isinstance(rules, list) else []


# --------------------------------------------------------------------- cli

def _fmt(rec: dict) -> str:
    lines = [f"{rec['id']}",
             f"  reviewer: {rec['reviewer']}  ({rec['method']})",
             f"  author excluded: {rec.get('author') or '(unknown)'}",
             f"  eligible: {', '.join(rec.get('eligible') or []) or '(none)'}",
             f"  reason: {rec['reason']}"]
    if rec.get("method") == "draw":
        band = rec.get("band") or "none on record"
        lines.append(f"  band: {band}  (as_of {rec.get('band_as_of') or 'unknown'}"
                     f"{', STALE' if rec.get('band_stale') else ''})")
        lines.append(f"  pool drawn: {', '.join(rec.get('pool') or [])}"
                     f"  (seed {rec.get('seed')})")
    return "\n".join(lines)


def _selftest() -> int:
    costs = {"as_of": "2026-10-09",
             "bands": [{"tier": "cheap", "members": ["desi", "dmitri"]},
                       {"tier": "dear", "members": ["claude", "tarik"]}]}
    today = dt.date(2026, 10, 9)
    item = {"id": "20261009T000000Z-aaaaaaaa", "amigo": "gemini", "title": "a plain internal item"}

    d = decide(item, costs=costs, today=today)
    checks = []
    checks.append(("author never drawn",
                   d["reviewer"] not in ("gemini",) and "gemini" not in d["eligible"]))
    checks.append(("draw lands in the least-expensive band",
                   d["method"] == "draw" and d["band"] == ["desi", "dmitri"]
                   and d["reviewer"] in ("desi", "dmitri")))

    same = decide(item, costs=costs, today=today)
    checks.append(("the draw is frozen: same id, same pick", same["reviewer"] == d["reviewer"]))

    # seed variety: across many ids the pick is not a constant
    picks = {decide({"id": f"20261009T0000{i:02d}Z-aaaaaaaa", "amigo": "gemini",
                     "title": "x"}, costs=costs, today=today)["reviewer"] for i in range(40)}
    checks.append(("the draw varies across ids", picks == {"desi", "dmitri"}))

    # competence, explicit
    c = decide(item, costs=costs, best="claude", because="holds the keys", today=today)
    checks.append(("an explicit competence match wins over the band",
                   c["method"] == "competence" and c["reviewer"] == "claude"
                   and "keys" in c["reason"]))

    # competence, by rule
    rules = [{"match": "mail", "amigo": "desi", "reason": "owns the mail channel"}]
    r = decide({"id": "i", "amigo": "gemini", "title": "fix the mail identity"},
               costs=costs, competence=rules, today=today)
    checks.append(("a single rule fires the competence branch",
                   r["method"] == "competence" and r["reviewer"] == "desi"))

    # ambiguous competence falls through
    two = rules + [{"match": "mail", "amigo": "tarik", "reason": "also mail"}]
    a = decide({"id": "i", "amigo": "gemini", "title": "fix the mail identity"},
               costs=costs, competence=two, today=today)
    checks.append(("two rules are not 'clearly best suited' -> draw", a["method"] == "draw"))

    # no band on record -> draws among all eligible, and says so
    nb = decide(item, costs={}, today=today)
    checks.append(("no band -> all eligible, band recorded as absent",
                   nb["band"] is None and "no cost band on record" in nb["reason"]
                   and set(nb["pool"]) == {"desi", "dmitri", "claude", "tarik"}))

    # staleness is visible
    checks.append(("a dated band is current within the window", not is_stale("2026-10-09", today)))
    checks.append(("an old band reads stale", is_stale("2026-01-01", today)))
    checks.append(("an undated band reads stale", is_stale(None, today)))

    # unknown author is recorded, not assumed
    u = decide({"id": "u", "title": "no author"}, costs=costs, today=today)
    checks.append(("unknown author is named, and the whole roster is eligible",
                   u["author"] is None and set(u["eligible"]) == set(AMIGOS)))

    # freeze on disk
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        store = Path(tmp) / "a.jsonl"
        first, wrote1 = assign(item, path=store, costs=costs, today=today)
        second, wrote2 = assign(item, path=store, costs=costs, today=today)
        checks.append(("first call records, second call returns the same record without rewriting",
                       wrote1 and not wrote2 and first == second
                       and len(store.read_text().strip().splitlines()) == 1))

    bad = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print("%s %s" % ("PASS" if ok else "FAIL", n))
    print("all checks passed" if not bad else "%d failed" % len(bad))
    return 1 if bad else 0


def _cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--item", metavar="ID", help="the item id to assign")
    ap.add_argument("--author", default="", help="override the author (for an id not in the ledger)")
    ap.add_argument("--best", default="", help="branch (a): the amigo best suited (a competence match)")
    ap.add_argument("--because", default="", help="the one-line reason for a --best match")
    ap.add_argument("--competence", default="", help="a keyword->amigo rule file for branch (a)")
    ap.add_argument("--band", default=str(COSTS), help="the dated cost-band cache")
    ap.add_argument("--store", default=str(STORE), help="the assignments store")
    ap.add_argument("--show", action="store_true", help="print the decision; write nothing")
    ap.add_argument("--list", action="store_true", help="every assignment on record")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()

    if args.list:
        recs = load_assignments(Path(args.store))
        for rec in sorted(recs.values(), key=lambda r: r.get("decided_utc") or ""):
            print(f"  {rec.get('decided_utc')}  {rec['id']}  -> {rec['reviewer']} "
                  f"({rec['method']})")
        print(f"  ({len(recs)} assignment(s))")
        return 0

    if not args.item:
        ap.print_help()
        return 2

    items = load_items()
    item = dict(items.get(args.item) or {"id": args.item})
    if args.author:
        item["amigo"] = args.author.lower()
    if not item.get("amigo"):
        print(f"assignment: {args.item} is not in the item ledger and no --author was given; "
              f"the author cannot be excluded and will be recorded as unknown", file=sys.stderr)

    kw = dict(costs=load_costs(Path(args.band)),
              competence=load_competence(args.competence) if args.competence else [])
    if args.show:
        print(_fmt(decide(item, best=args.best, because=args.because, **kw)))
        return 0
    rec, wrote = assign(item, path=Path(args.store), best=args.best, because=args.because, **kw)
    print(_fmt(rec))
    print("\n" + ("recorded — frozen; a later wake cannot re-roll it."
                  if wrote else "already assigned; returned the frozen record, nothing rewritten."))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
