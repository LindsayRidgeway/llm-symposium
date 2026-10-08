#!/usr/bin/env python3
# Owner: Desi
"""The review-state reporter — the six letters N/V/A/P/W/R, read from artifacts already on disk.

Why this exists (2026-10-07). The human asked (Telegram 12:48): do high "not yet reviewed" counts
mean the review process is broken? The commons had one word, *postponed*, doing two opposite jobs —
a decision to wait (someone looked and said not now, and why) and an absence (nobody has looked) —
so the number could not answer him. He split it, in this order, over the morning's exchange:

    P = postponed by decision        (someone looked, said not now, and wrote why)
    W = waiting for review           (nobody has looked)
    N = performed, no review needed
    V = performed, needed review

with A (reviewed and accomplished) and R (rejected) carried over from the old scheme, and the
diagnostic: track Δ(V−W) per day; zero for several days means the drain has stopped; zero *while*
ΔW climbs is unambiguous breakage; both positive is a capacity problem, not a process failure.

His condition, which is the whole design (13:55): *existing artifacts only — no new ledger, no new
fields anyone has to fill in.* So this reader does not ask anyone to tag anything. It classifies
what a reviewer had to write anyway, and the failure mode is honest: an item with no reason on disk
reads as waiting, which is what it is.

The two partitions (each item is in exactly one of each):

  needed-review?   N   the record already states the check that stood in place of review
                   V   everything else — review was needed (or the record does not say otherwise)

  outcome          A   accomplished (the item reached main)
                   P   postponed and the reason is written on disk
                   W   no decision recorded — waiting, nobody has looked
                   R   rejected

He wrote the identity `N + V = A + P + W + R`. Both sides are the whole set counted two ways, so the
identity holds by construction and the information is entirely in the splits — which is why V and W
are the pair worth watching and why `V` is compared against `W` directly (V ≥ W is a fact, not a
finding; the *delta* carries it).

The one judgment call, stated because a reviewer may overrule it: an item whose record shows the
automatic lander (`reviewer == "auto:land"`, `reason == "landed on main (lander's test gate
passed)"`) is read as **N** — performed, and the lander's test gate is the stated check that stood
in place of a human review. Read the other way (the gate is not a review, so those items still need
one) they are **V**, and N collapses toward zero. The reader prints the auto-land count so the
choice is visible rather than buried.

CLI:
    python3 scripts/review_state.py                # read the ledger as it stands now
    python3 scripts/review_state.py --asof 2026-10-06
    python3 scripts/review_state.py --days 3       # a small history of the daily deltas
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "channels" / "items.jsonl"
TS = "%Y-%m-%dT%H:%M:%SZ"
AMIGO_ORDER = ("desi", "claude", "gemini", "tarik", "dmitri")
AUTO_REVIEWER = "auto:land"


def _parse(ts: str | None) -> dt.datetime | None:
    if not ts:
        return None
    try:
        return dt.datetime.strptime(ts, TS).replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return None


def load_lines(path: Path = LEDGER) -> list[dict]:
    """Every line of the append-only ledger, in file order. A corrupt line is skipped loudly."""
    recs: list[dict] = []
    if not path.exists():
        return recs
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            recs.append(json.loads(line))
        except ValueError:
            print(f"review_state: skipping unreadable line {lineno}", file=sys.stderr)
    return recs


def timeline(path: Path = LEDGER) -> dict[str, list[tuple[str, dict]]]:
    """Per item id, the ordered (timestamp, record) events that describe it.

    Each item starts unreviewed at its `filed_utc`; a terminal review adds an event at its
    `state_utc`. Duplicate lines (the ledger has some) collapse to one event, keyed by timestamp.
    This is the whole trick that lets a *delta* be read from an append-only file: the file already
    holds the history, so the state at any past instant is recoverable without a snapshot table.
    """
    by_id: dict[str, dict[str, dict]] = {}
    for rec in load_lines(path):
        item_id = rec.get("id")
        if not item_id:
            continue
        events = by_id.setdefault(item_id, {})
        filed = rec.get("filed_utc")
        if filed:
            # The unreviewed opening state (state is null on the first line for every item).
            events.setdefault(filed, dict(rec, state=None, state_utc=None, reason=None,
                                          reviewer=None))
        if rec.get("state") and rec.get("state_utc"):
            events[rec["state_utc"]] = rec
    out: dict[str, list[tuple[str, dict]]] = {}
    for item_id, events in by_id.items():
        out[item_id] = sorted(events.items(), key=lambda kv: kv[0])
    return out


def state_as_of(path: Path = LEDGER, when: dt.datetime | None = None) -> list[dict]:
    """The record describing each item's latest known state at or before `when`."""
    if when is None:
        when = dt.datetime.now(dt.timezone.utc)
    rows: list[dict] = []
    for events in timeline(path).values():
        latest = None
        for ts, rec in events:
            moment = _parse(ts)
            if moment is None or moment <= when:
                latest = rec
            else:
                break
        if latest is not None:
            rows.append(latest)
    return rows


def needed_review(rec: dict) -> str:
    """`N` when the record already states the check that stood in place of review, else `V`."""
    if rec.get("reviewer") == AUTO_REVIEWER and (rec.get("reason") or "").strip():
        return "N"
    return "V"


def outcome(rec: dict) -> str:
    """`A`, `P`, `W` or `R`, read from the terminal state and whether a reason is written."""
    state = rec.get("state")
    if state == "accomplished":
        return "A"
    if state == "rejected":
        return "R"
    if state == "postponed":
        # P is a decision *with a reason on disk*. Postponed without a reason is W (13:55 rule:
        # no reason → waiting, no matter how long it has sat).
        return "P" if (rec.get("reason") or "").strip() else "W"
    return "W"  # no terminal state: nobody has looked


def classify(rec: dict) -> dict:
    return {"need": needed_review(rec), "outcome": outcome(rec)}


def counts(rows: list[dict]) -> dict:
    """The six tallies, plus the by-amigo split the human reads it two ways with."""
    n = v = a = p = w = r = 0
    by_amigo = {who: {"N": 0, "V": 0, "A": 0, "P": 0, "W": 0, "R": 0} for who in AMIGO_ORDER}
    auto_land = 0
    for rec in rows:
        c = classify(rec)
        need, out = c["need"], c["outcome"]
        if need == "N":
            n += 1
        else:
            v += 1
        if out == "A":
            a += 1
        elif out == "P":
            p += 1
        elif out == "W":
            w += 1
        else:
            r += 1
        who = rec.get("amigo", "?")
        slot = by_amigo.setdefault(who, {"N": 0, "V": 0, "A": 0, "P": 0, "W": 0, "R": 0})
        slot[need] += 1
        slot[out] += 1
        if need == "N":
            auto_land += 1
    return {"N": n, "V": v, "A": a, "P": p, "W": w, "R": r,
            "total": len(rows), "by_amigo": by_amigo, "auto_land": auto_land}


def verdict(dv_minus_w: int, dw: int) -> str:
    """The diagnostic in one clause, straight from the 13:46 agreement."""
    if dv_minus_w == 0 and dw > 0:
        return "broken — inflow with no drainage"
    if dv_minus_w == 0:
        return "stalled — no drainage, no new inflow"
    if dv_minus_w > 0 and dw > 0:
        return "capacity — draining, but inflow is faster"
    if dv_minus_w > 0:
        return "draining"
    return "shrinking backlog"


def deltas(path: Path = LEDGER, days: int = 1) -> list[dict]:
    """Day-over-day snapshots of V, W and the diagnostic V−W, newest last.

    `days` snapshots ending now and stepping back 24h each. Each row is the reading at that instant
    plus its change from the instant 24h earlier.
    """
    now = dt.datetime.now(dt.timezone.utc)
    stamps = [now - dt.timedelta(days=k) for k in range(days, -1, -1)]
    rows = []
    prev = None
    for when in stamps:
        c = counts(state_as_of(path, when))
        row = {"at": when.strftime(TS), "V": c["V"], "W": c["W"], "V-W": c["V"] - c["W"]}
        if prev is not None:
            row["dV-W"] = row["V-W"] - (prev["V"] - prev["W"])
            row["dW"] = row["W"] - prev["W"]
            row["verdict"] = verdict(row["dV-W"], row["dW"]) if row["dW"] or row["dV-W"] \
                else "quiet — nothing filed or drained"
        rows.append(row)
        prev = row
    return rows


def render(c: dict, rows: list[dict] | None = None) -> str:
    out = []
    out.append(f"items: {c['total']}   N+V={c['N'] + c['V']}  A+P+W+R="
               f"{c['A'] + c['P'] + c['W'] + c['R']}  (must both equal {c['total']})")
    out.append(f"need review:  N={c['N']} (no review needed: {c['auto_land']} lander-verified)"
               f"   V={c['V']} (review needed)")
    out.append(f"outcome:      A={c['A']} accomplished   P={c['P']} postponed(written reason)"
               f"   W={c['W']} waiting   R={c['R']} rejected")
    out.append(f"diagnostic:   V-W = {c['V'] - c['W']}"
               + ("   (V=W: nothing that ever needed review has drained)"
                  if c["V"] == c["W"] else ""))
    out.append("")
    out.append("by amigo       N    V    A    P    W    R")
    for who in AMIGO_ORDER:
        s = c["by_amigo"].get(who)
        if not s or not any(s.values()):
            continue
        out.append(f"  {who:8s}  {s['N']:4d} {s['V']:4d} {s['A']:4d} {s['P']:4d}"
                   f" {s['W']:4d} {s['R']:4d}")
    if rows:
        out.append("")
        out.append("daily deltas   at (UTC)                    V     W   V-W  d(V-W)   dW   read")
        for i, row in enumerate(rows):
            if i == 0:
                out.append(f"  {row['at']}  {row['V']:5d} {row['W']:5d} {row['V-W']:5d}"
                           f"   {'—':>5} {'—':>4}   baseline")
            else:
                out.append(f"  {row['at']}  {row['V']:5d} {row['W']:5d} {row['V-W']:5d}"
                           f"   {row['dV-W']:+5d} {row['dW']:+4d}   {row['verdict']}")
    return "\n".join(out)


def _cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--asof", help="ISO-8601 UTC instant, e.g. 2026-10-06 or 2026-10-06T12:00:00Z")
    ap.add_argument("--days", type=int, default=1, help="daily-delta history length (default 1)")
    args = ap.parse_args()

    when = None
    if args.asof:
        text = args.asof if "T" in args.asof else args.asof + "T23:59:59Z"
        try:
            when = dt.datetime.strptime(text, TS).replace(tzinfo=dt.timezone.utc)
        except ValueError:
            print(f"review_state: cannot read --asof {args.asof!r}", file=sys.stderr)
            return 2

    c = counts(state_as_of(when=when))
    print(render(c, deltas(days=args.days) if when is None else None))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
