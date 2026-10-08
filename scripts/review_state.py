#!/usr/bin/env python3
# Owner: Desi
"""The review state — P/W/N/V read off the item ledger, with the day's Δ(V−W) and ΔW.

Why (2026-10-07, the human in Telegram). The daily report counts N/A/P/R, and he asked to split two
of those letters, because each was hiding two different things:

    N (old) = every item a wake performed
            -> N = performed and no review needed
            -> V = performed and review needed
    P (old) = every item neither accomplished nor rejected
            -> P = postponed by decision, the reason written down
            -> W = waiting for review, nobody has looked

    A = accomplished (the lander's test gate passed)          R = rejected

The identity that closes it, in his words: N + V = A + P + W + R. Both sides are the same set of
performed items counted two ways — by whether they needed review (N+V) and by how they ended
(A+P+W+R) — so W is not a fourth outcome; it is the part of V that has not drained yet.

The rule that needs no new data, from the same exchange: a postponement counts as P **only if its
reason is already on disk**; no reason means W, however long it has sat. And N counts **only if the
item already states why no review was needed**; if it does not say, it reads as V. So nothing new is
kept: the classifier reads what a reviewer had to write anyway, and its failure mode is honest — an
unexplained stall reads as waiting, which is what it is.

The one number to watch. V − W is the count of items that needed review and are no longer waiting.
Its daily change, Δ(V−W), is the drain rate; ΔW is the inflow. Δ(V−W)=0 for several days is a
stopped drain; Δ(V−W)=0 *while* ΔW>0 is an unambiguous break in the process; both positive is a
capacity problem, not a broken one.

What reads as N. There is no "no review was needed" field anywhere, and this script does not add
one. An item declares itself review-free by *saying so* in the record's own `reason` text — the same
`reason` a reviewer already writes for P, read for the other question. Until an item says it, it
reads as V, which is the human's stated rule. (Measured 2026-10-08: no item says it, so N=0 and
V=performed across the whole corpus — a fact, not a fault.)

Usage:
    python3 scripts/review_state.py                  # P/W/N/V now, with the last 24h deltas
    python3 scripts/review_state.py --hours 48
    python3 scripts/review_state.py --json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from channels.item_ledger import load  # noqa: E402

LEDGER = REPO / "channels" / "items.jsonl"
STAMP = "%Y-%m-%dT%H:%M:%SZ"

# An item says it needed no review by saying so, in the reason already on disk. No new field.
NO_REVIEW_RE = re.compile(r"\bno review (?:was )?needed\b|\breview (?:was )?not needed\b", re.I)


def _parse(stamp: str | None) -> dt.datetime | None:
    if not stamp:
        return None
    try:
        return dt.datetime.strptime(stamp, STAMP).replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return None


def classify(rec: dict) -> str:
    """The item's outcome — A, R, P or W. A partition: every item is exactly one of these.

    P needs a reason on disk; a blank reason is W, no matter the state field, which is the human's
    rule ("a postponement counts as P only if its reason is written").
    """
    state = (rec.get("state") or "").strip().lower()
    if state == "accomplished":
        return "A"
    if state == "rejected":
        return "R"
    if state == "postponed" and (rec.get("reason") or "").strip():
        return "P"
    return "W"


def tally(items: dict[str, dict], as_of: dt.datetime | None = None) -> dict:
    """The counts at `as_of` (or now, if None). Reconstructed from the record's own timestamps.

    `as_of` answers "what did this look like yesterday": an item whose terminal state change is
    younger than the cutoff is counted as it was before that change, i.e. as still waiting. This is
    why no snapshot file is needed — the ledger already carries the times.
    """
    out = {"performed": 0, "N": 0, "V": 0, "A": 0, "P": 0, "W": 0, "R": 0, "by_amigo": {}}
    for rec in items.values():
        filed = _parse(rec.get("filed_utc"))
        if as_of is not None and filed is not None and filed > as_of:
            continue
        state = rec.get("state")
        if as_of is not None:
            state_utc = _parse(rec.get("state_utc"))
            if state and state_utc is not None and state_utc > as_of:
                state = None                     # this outcome had not happened yet at `as_of`
        eff = dict(rec, state=state)
        out["performed"] += 1
        if NO_REVIEW_RE.search(rec.get("reason") or ""):
            out["N"] += 1
        else:
            out["V"] += 1
        out[classify(eff)] += 1
        who = rec.get("amigo", "?")
        slot = out["by_amigo"].setdefault(who, {"N": 0, "V": 0, "A": 0, "P": 0, "W": 0, "R": 0})
        slot["N" if NO_REVIEW_RE.search(rec.get("reason") or "") else "V"] += 1
        slot[classify(eff)] += 1
    return out


def drained(t: dict) -> int:
    """V − W: items that needed review and are no longer waiting. Not the same as 'reviewed' —
    most of them are `accomplished`, set by the lander's test gate, which is not a person's
    judgement — but it is the drainage the human asked to watch, and the caveat is one line."""
    return t["V"] - t["W"]


def diagnostic(d_drained: int, dw: int) -> str:
    if d_drained < 0:
        return "NEGATIVE Δ(V−W): items went back into waiting — a correction, or a defect"
    if d_drained == 0 and dw > 0:
        return "BROKEN: nothing drained while the backlog grew (Δ(V−W)=0, ΔW>0)"
    if d_drained > 0 and dw > 0:
        return "draining, but inflow faster — a capacity problem, not a broken process"
    if d_drained > 0 and dw <= 0:
        return "draining"
    return "quiet: no drain and no inflow"


def _flagged_pairs(t: dict) -> list[str]:
    """N = P, globally or per amigo, is the human's signal that the decision criteria are off.
    Guarded against the trivial N=P=0 — an empty equality says nothing."""
    out = []
    if t["N"] and t["N"] == t["P"]:
        out.append("N = P globally — the decision criteria are worth inspecting")
    for who, s in sorted(t["by_amigo"].items()):
        if s["N"] and s["N"] == s["P"]:
            out.append(f"N = P for {who} — that amigo's process is worth a look")
    return out


def render(now: dict, then: dict, window_hours: int, as_of: dt.datetime) -> str:
    d_drained = drained(now) - drained(then)
    dw = now["W"] - then["W"]
    out = [f"Review state — {as_of.strftime('%Y-%m-%d %H:%M %Z')} "
           f"(deltas over the last {window_hours}h)", ""]
    out.append(f"  performed  {now['performed']:>4}")
    out.append(f"    N {now['N']:>4}  performed, no review needed")
    out.append(f"    V {now['V']:>4}  performed, review needed")
    out.append("  outcome")
    out.append(f"    A {now['A']:>4}  accomplished (lander's test gate passed)")
    out.append(f"    P {now['P']:>4}  postponed, reason written down")
    out.append(f"    W {now['W']:>4}  waiting for review")
    out.append(f"    R {now['R']:>4}  rejected")
    out.append("")
    out.append(f"  V−W = {drained(now):>4}  no longer waiting        Δ(V−W) = {d_drained:+d}")
    out.append(f"  W   = {now['W']:>4}  still waiting             ΔW     = {dw:+d}")
    out.append(f"  check: N+V = {now['N'] + now['V']}   A+P+W+R = "
               f"{now['A'] + now['P'] + now['W'] + now['R']}   performed = {now['performed']}")
    out.append("")
    out.append(f"  diagnostic: {diagnostic(d_drained, dw)}")
    for line in _flagged_pairs(now):
        out.append(f"  flag: {line}")
    if now["by_amigo"]:
        out.append("")
        out.append("  by amigo (N/V  A/P/W/R)")
        for who in ("desi", "claude", "gemini", "tarik", "dmitri"):
            s = now["by_amigo"].get(who)
            if not s:
                continue
            out.append(f"    {who:<8} {s['N']:>3}/{s['V']:<3}  "
                       f"{s['A']:>2}/{s['P']:>2}/{s['W']:>2}/{s['R']:>2}")
    return "\n".join(out)


def _cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--hours", type=int, default=24, help="delta window (default 24)")
    ap.add_argument("--ledger", type=Path, default=LEDGER)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--now", default=None, help="ISO-8601 UTC instant to treat as now (testing)")
    args = ap.parse_args()

    items = load(args.ledger)
    as_of = _parse(args.now) if args.now else dt.datetime.now(dt.timezone.utc)
    now = tally(items)
    then = tally(items, as_of - dt.timedelta(hours=args.hours))

    if args.json:
        print(json.dumps({"as_of": as_of.strftime(STAMP), "window_hours": args.hours,
                          "now": now, "then": then,
                          "delta_drained": drained(now) - drained(then),
                          "delta_W": now["W"] - then["W"]}, indent=2, sort_keys=True))
        return 0
    print(render(now, then, args.hours, as_of))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
