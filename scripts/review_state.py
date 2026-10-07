#!/usr/bin/env python3
# Owner: Desi
"""The review-state reader — a sharper reading of the same ledger, not a sixth queue.

Settled with the human in the Telegram thread of 2026-10-07. The four-letter scheme
(N/A/P/R, `channels/item_ledger.py`) put two opposite things under one word. `P` counted both an
item someone looked at and said "not now" — a decision, with a reason written down — and an item
nobody had looked at — an absence. Same collapse inside `N`: everything performed shared one letter
whether or not anyone had judged it reviewable. The human's fix, and his exact wording:

    P = postponed by decision      (only if a reason is already written on disk)
    W = waiting for review         (no reason on disk, however long it has sat)
    N = performed, no review needed (only if the artifact already says why not)
    V = performed, needed review    (the default — no statement, no exemption)

The rule that makes it work without new data, in his words: "a postponement counts as P only if the
reason is already written in the artifact. No reason on disk → W. Same for N: it's N only if the
artifact already says why no review was needed; if it doesn't say, it reads as V." So this reader
maintains nothing. It reads `channels/items.jsonl` and the reasons a reviewer had to write anyway.
No new ledger, no new field to remember — the failure mode is honest: an unexplained stall reads as
waiting, which is what it is.

The diagnostic he asked for is the day's change, not the level. V counts everything that ever needed
review; W counts what is still waiting; so V−W is the cumulative drainage. A frozen V−W over several
days means the drain stopped. Pairing it with ΔW separates the two failures that look identical in a
level: Δ(V−W)=0 while ΔW>0 is unambiguously broken (backlog grows, nothing drains); both positive is
a capacity problem, not a process one. Dwell was considered and deliberately not built for now (he
judged it dead weight in the regime the data is actually in).

One honest limit, stated first because it changes what Δ(V−W) means: an `accomplished` item is set by
the lander's test gate (`land(wake)` on main), and the ledger itself says that is verifiable but "not
the same as reviewed." So Δ(V−W) measures items that *reached main* in the window, which is the
landing pipeline, not a human reading each one. When the landing pipeline stalls, Δ(V−W) is 0 while
ΔW climbs — and this reader will say so, which is the point.

CLI:
    python3 scripts/review_state.py                 # lifetime + the last 24h + the deltas
    python3 scripts/review_state.py --hours 24
    python3 scripts/review_state.py --json          # machine-readable, for a later hint in the report
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from channels.item_ledger import AMIGOS, load  # noqa: E402

STAMP = "%Y-%m-%dT%H:%M:%SZ"
# The states a review can end in. A `postponed` state only counts as P (a decision) when it also
# carries a reason; the ledger's `review()` refuses a reason-less postponement, but an older or
# hand-written row could still arrive without one, so the rule is enforced here too, not assumed.
REVIEW_STATES = ("accomplished", "rejected", "postponed")

# An item is N only if its own record says why it needed no review. The phrases are deliberately
# narrow: the whole reason N is trustworthy is that an exemption is explicit, so any stray "clear"
# or "minor" must NOT create one — a false N is exactly how N becomes the new dumping ground the
# human warned about.
NO_REVIEW_RE = re.compile(
    r"no review (?:was )?(?:needed|required|necessary)|"
    r"review (?:was )?not (?:needed|required)|"
    r"needs? no review|exempt(?:ed)? from review|"
    r"no review needed",
    re.I,
)

LETTERS = ("N", "V", "A", "P", "W", "R")


def _when(rec: dict, key: str) -> dt.datetime | None:
    v = rec.get(key)
    if not v:
        return None
    try:
        return dt.datetime.strptime(v, STAMP).replace(tzinfo=dt.timezone.utc)
    except (ValueError, TypeError):
        return None


def states_no_review(rec: dict) -> bool:
    """True when the record itself claims the item needed no review."""
    return bool(NO_REVIEW_RE.search(rec.get("reason") or ""))


def resolved_at(rec: dict) -> dt.datetime | None:
    """When the item left the waiting list, or None if it never has.

    `accomplished` (set by the lander), `rejected` and a decided `postponed` are all resolutions;
    an item that is merely present in no state is still waiting.
    """
    if rec.get("state") in REVIEW_STATES:
        return _when(rec, "state_utc") or _when(rec, "filed_utc")
    return None


def classify(rec: dict, at: dt.datetime | None = None) -> str | None:
    """The item's letter, as of `at` (None = now / its latest state). None if not yet performed.

    Order matters and is the agreed rule, not a preference: an item that reached a review outcome is
    A/P/W/R regardless of any later prose; only an item with no outcome can be the exempt N; and a
    postponement without a written reason is W, not P.
    """
    filed = _when(rec, "filed_utc")
    if at is not None and filed is not None and filed > at:
        return None                                   # not yet performed at that time
    state = rec.get("state")
    res = resolved_at(rec)
    if state in REVIEW_STATES and (at is None or (res is not None and res <= at)):
        if state == "accomplished":
            return "A"
        if state == "rejected":
            return "R"
        if state == "postponed" and (rec.get("reason") or "").strip():
            return "P"
        return "W"                                     # postponed with no reason is still waiting
    if states_no_review(rec):
        return "N"                                     # performed, and the record says no review
    return "W"                                         # performed, nobody has looked: waiting


def snapshot(items: dict[str, dict], at: dt.datetime | None = None) -> dict:
    """The six counts as of `at`, plus the partition sums and a per-amigo split.

    `classify` returns one of N/A/P/W/R — never V — because V is not a state an item is *in*: it is
    the complement of the exemption. So V is derived here as A+P+W+R (every performed item that was
    not exempt, which is every item that reached, or is still in, the review pipeline). N sits
    outside that set; total performed = N + V.
    """
    by = {L: collections.Counter() for L in ("N", "A", "P", "W", "R")}
    for rec in items.values():
        letter = classify(rec, at)
        if letter is not None:
            by[letter][rec.get("amigo", "?")] += 1
    out = {L: {"total": sum(c.values()), "by_amigo": dict(c)} for L, c in by.items()}
    amigo = collections.Counter()
    for L in ("A", "P", "W", "R"):
        amigo.update(by[L])
    out["V"] = {"total": sum(amigo.values()), "by_amigo": dict(amigo)}
    out["performed"] = out["N"]["total"] + out["V"]["total"]
    return out


def deltas(items: dict[str, dict], hours: int, now: dt.datetime | None = None) -> dict:
    """The day's movement: Δ(V−W) is drainage, ΔW is backlog growth.

    Both are differences of snapshots, so they need no event log — the ledger's own `filed_utc` and
    `state_utc` timestamps already say when each item arrived and when it left the waiting list.
    """
    now = now or dt.datetime.now(dt.timezone.utc)
    start = now - dt.timedelta(hours=hours)
    then, curr = snapshot(items, start), snapshot(items, None)
    drained_then = then["V"]["total"] - then["W"]["total"]
    drained_now = curr["V"]["total"] - curr["W"]["total"]
    dvw = drained_now - drained_then
    dw = curr["W"]["total"] - then["W"]["total"]
    if dvw == 0 and dw > 0:
        diagnosis = "broken — backlog grew while nothing drained (the drain is stopped)"
    elif dvw > 0 and dw > 0:
        diagnosis = "capacity — draining, but inflow is faster (a throughput problem, not a leak)"
    elif dvw > 0 and dw <= 0:
        diagnosis = "healthy — draining faster than it fills"
    else:
        diagnosis = "quiet — nothing filed and nothing drained in this window"
    return {"hours": hours, "delta_v_minus_w": dvw, "delta_w": dw, "diagnosis": diagnosis,
            "now": curr, "then": then}


def _fmt_signed(n: int) -> str:
    return f"+{n}" if n > 0 else str(n)


def render(hours: int = 24, now: dt.datetime | None = None, items: dict | None = None) -> str:
    now = now or dt.datetime.now(dt.timezone.utc)
    items = load() if items is None else items
    life = snapshot(items, None)
    window = snapshot(items, now - dt.timedelta(hours=hours))
    d = deltas(items, hours, now)

    def line(snap: dict, label: str) -> str:
        return (f"{label:<10} N={snap['N']['total']:<4} V={snap['V']['total']:<4} "
                f"A={snap['A']['total']:<4} P={snap['P']['total']:<4} W={snap['W']['total']:<4} "
                f"R={snap['R']['total']:<4}")

    # The human's equation, kept honest: N+V is every performed item; A+P+W+R is the same set
    # viewed by outcome, which is exactly V. They are one number when nothing is exempt (N=0) and
    # differ by N otherwise — so it is shown, not asserted.
    identity = life["N"]["total"] + life["V"]["total"]
    outcome = life["A"]["total"] + life["P"]["total"] + life["W"]["total"] + life["R"]["total"]
    lines = [
        "**Review state — the six-letter reading** (same ledger, sharper reader; no new data)",
        "P = postponed by decision (a reason is on disk) · W = waiting for review (no reason on disk)",
        "N = performed, no review needed (stated) · V = performed, needed review (the default)",
        "",
        line(life, "Lifetime") + f"  performed={identity}",
        line(window, f"Last {hours}h") + f"  performed={window['performed']}",
        f"          N+V = {identity} performed · A+P+W+R = {outcome}"
        + ("  ✓ equal" if identity == outcome else f"  (the {life['N']['total']} exempt item(s) sit "
           "outside the outcomes, which is the point of N)"),
        "",
        f"**Drainage (last {hours}h)**  Δ(V−W) = {_fmt_signed(d['delta_v_minus_w'])}   "
        f"ΔW = {_fmt_signed(d['delta_w'])}",
        f"  → {d['diagnosis']}",
        f"  V−W now = {life['V']['total'] - life['W']['total']} "
        f"(the cumulative count that ever drained); W = {life['W']['total']} still waiting",
        "  (an A is set by the lander's test gate, so V−W counts items that reached main, not items a",
        "   reader judged — a quiet landing pipeline reads here as a stopped drain, which is honest)",
        "",
        "### By amigo (lifetime) — N=P for one amigo is that amigo's process worth a look",
    ]
    names = sorted(set().union(*[set(life[L]["by_amigo"]) for L in LETTERS]) or set())
    for who in sorted(names, key=lambda w: (-life["V"]["by_amigo"].get(w, 0), w)):
        n, v = life["N"]["by_amigo"].get(who, 0), life["V"]["by_amigo"].get(who, 0)
        p, w = life["P"]["by_amigo"].get(who, 0), life["W"]["by_amigo"].get(who, 0)
        flag = "  ← N=P" if n and n == p else ""
        lines.append(f"  {who:<8} N={n:<4} V={v:<4} P={p:<4} W={w:<4}{flag}")
    n_tot, p_tot = life["N"]["total"], life["P"]["total"]
    if n_tot == p_tot and p_tot > 0:
        lines.append(f"  global N=P ({n_tot}) — the decision criteria exempt exactly as much as they "
                     "defer, which is the broken case")
    elif p_tot == 0:
        lines.append("  global N=P is vacuous right now (P=0: nothing has been decided yet); it only "
                     "means something once a postponement carries a reason")
    return "\n".join(lines)


def as_json(hours: int = 24, now: dt.datetime | None = None) -> dict:
    now = now or dt.datetime.now(dt.timezone.utc)
    items = load()
    return {"lifetime": snapshot(items, None), "window": snapshot(items, now - dt.timedelta(hours=hours)),
            "deltas": deltas(items, hours, now)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--hours", type=int, default=24)
    ap.add_argument("--json", action="store_true", help="machine-readable snapshot + deltas")
    a = ap.parse_args()
    if a.json:
        print(json.dumps(as_json(a.hours), indent=2, sort_keys=True))
        return 0
    print(render(a.hours))
    return 0


if __name__ == "__main__":
    sys.exit(main())
