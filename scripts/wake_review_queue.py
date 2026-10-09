#!/usr/bin/env python3
# Owner: Desi
"""The review queue a wake opens with — W, each item named to a reviewer.

Why this exists (2026-10-09). The human's live concern that morning was one number: W is not
draining. The item ledger can already list the oldest items nobody has looked at
(`item_ledger.py --next`), but nothing put that queue *in front of a wake*, and nothing said
*whose* job each item was. A queue with no job addressed to anyone and no place in the wake's
three read sources cannot drain, however motivated the reader is.

So this produces the missing block. It derives W from the ledger the report already keeps — no
new ledger, no new field — gives every item one named reviewer, and prints the block for that
amigo, ready to append to their wake input. The rule for naming a reviewer is the design
decision this file makes, and it is written here so it can be argued with:

    reviewer(id, author) = the amigo at (sha1(id) mod len(roster-others)) in the fixed roster
                           order, where roster-others is every amigo but the author.

Three properties it is chosen for, in order:
  1. Never the author. Nobody signs off on their own work — the same rule `--not-mine` enforces.
  2. Stable. The reviewer is a pure function of the item's id, so an item's reviewer never
     changes between wakes while it waits. A reviewer told to look at item X on Monday must still
     be its reviewer on Friday, or the instruction is noise.
  3. Spread. It is uniform over the other amigos, so a prolific author's pile does not land on a
     single reviewer. A plain ring (reviewer = the next amigo after the author) is simpler but
     sends *every* one of the most prolific author's items to the same neighbour, which is the
     imbalance this trades against stability: this rule spends a little mystery to avoid loading
     one amigo with the whole of another's output.

An item whose author is not on the roster has no assignable reviewer and is returned as a
**hole** — not silently dropped, not handed to a default, because an item nobody can be named for
is exactly the kind of thing that sits in W forever while looking accounted for.

CLI:
    python3 scripts/wake_review_queue.py --amigo desi        # the block for one amigo
    python3 scripts/wake_review_queue.py --all               # every reviewer, one section each
    python3 scripts/wake_review_queue.py --amigo desi --limit 3
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from channels import item_ledger as il  # noqa: E402

MAX_SHOWN = 5  # keep the block short enough not to crowd the wake's three read sources


def reviewer_for(item_id: str, author: str, roster: tuple[str, ...] = il.AMIGOS) -> str | None:
    """The one amigo named to review this item, or None if the author is not on the roster.

    An author the roster does not know is a hole, not a default: there is nobody to name as
    reviewer, and handing it to an arbitrary amigo would hide the fact that nobody owns it.
    """
    if author not in roster:
        return None
    others = [m for m in roster if m != author]
    if not others:
        return None
    digest = hashlib.sha1(item_id.encode("utf-8")).hexdigest()
    return others[int(digest, 16) % len(others)]


def waiting_items(items: dict[str, dict]) -> list[dict]:
    """Every item still waiting for review, oldest filed first — the queue itself."""
    rows = [r for r in items.values() if il.letter_for(r) == "W"]
    return sorted(rows, key=lambda r: r.get("filed_utc") or "")


def assigned_to(items: dict[str, dict], amigo: str,
                limit: int = MAX_SHOWN) -> tuple[list[dict], list[dict]]:
    """(the items addressed to `amigo`, the holes).

    A hole is a waiting item with no assignable reviewer (its author is not on the roster). Holes
    are returned whole and un-capped: the whole point of naming them is that they would otherwise
    sit in the queue silently.
    """
    mine, holes = [], []
    for rec in waiting_items(items):
        who = reviewer_for(rec.get("id", ""), rec.get("amigo", ""))
        if who is None:
            holes.append(rec)
        elif who == amigo:
            mine.append(rec)
    return mine[:limit], holes


def _line(rec: dict) -> str:
    paths = ", ".join((rec.get("paths") or [])[:6]) or "(none recorded)"
    out = [f"  {rec.get('id', '?')}  (filed {rec.get('filed_utc', '?')}, "
           f"by {rec.get('amigo', '?')}, {rec.get('scope', '?')})",
           f"     {rec.get('title', '(no title)')}",
           f"     evidence: {rec.get('evidence', '?')}"]
    if rec.get("paths"):
        out.append(f"     paths: {paths}")
    return "\n".join(out)


def _instructions(amigo: str) -> str:
    return (
        "Your job is to move each item out of the queue, not to leave it a kind word. Read what\n"
        "the run produced, then record exactly one verdict:\n"
        "  - accomplished — only when you also COMPLETE the work, not with a stamp;\n"
        "  - postponed or rejected — each needs a written reason; that reason is the whole record;\n"
        "  - an item you cannot judge goes to the queue that names its blocker, with the reason.\n"
        f'  python3 channels/item_ledger.py --review <id> --state accomplished|postponed|rejected \\\n'
        f'      --reason "why" --reviewer {amigo}\n'
    )


def block(items: dict[str, dict], amigo: str, limit: int = MAX_SHOWN) -> str:
    """The wake-input block for one amigo: the items addressed to them, plus any holes."""
    mine, holes = assigned_to(items, amigo, limit)
    total = sum(1 for r in waiting_items(items)
                if reviewer_for(r.get("id", ""), r.get("amigo", "")) == amigo)
    lines = [
        f"=== YOUR REVIEW QUEUE — the items in W addressed to {amigo} ===",
        f"{total} waiting item(s) name you as reviewer"
        + (f"; the {len(mine)} oldest are shown." if total > len(mine) else "."),
        "",
        _instructions(amigo),
    ]
    if mine:
        lines.append("")
        lines.append("\n\n".join(_line(r) for r in mine))
    else:
        lines.append("\n(nothing in W is addressed to you right now.)")
    if holes:
        lines.append("")
        lines.append(f"HOLES — {len(holes)} waiting item(s) with no assignable reviewer "
                     f"(author not on the roster); these drain only if a person claims them:")
        lines.append("\n\n".join(_line(r) for r in holes))
    return "\n".join(lines).rstrip() + "\n"


def _cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--amigo", choices=il.AMIGOS, help="print this amigo's queue block")
    ap.add_argument("--all", action="store_true", help="print one block per amigo")
    ap.add_argument("--limit", type=int, default=MAX_SHOWN)
    ap.add_argument("--ledger", default=str(il.LEDGER))
    args = ap.parse_args()

    items = il.load(Path(args.ledger))
    if args.all:
        print("\n\n".join(block(items, m, args.limit).rstrip() for m in il.AMIGOS))
        return 0
    if not args.amigo:
        ap.error("choose --amigo <name>, or --all")
    print(block(items, args.amigo, args.limit), end="")
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
