#!/usr/bin/env python3
# Owner: Desi
"""Who is overdue a follow-up.

The outreach to-do item asks, in prose, to "draft follow-ups to anyone quiet 10+ days". Prose
cannot be checked, and on 2026-10-04 the Monday item was passed over with "the date has not
arrived" while the trigger lived only inside the sentence. This reads the ground truth the
ledger already keeps — each prospect's `sent_date` — and prints who is quiet past a threshold,
so the Monday question is a command's output rather than a judgement.

Rules, read from `channels/outreach/pipeline.json`:

  * a prospect with a `sent_date` is "quiet" for (as_of - sent_date) days;
  * `replied: true` closes the prospect — never listed;
  * a `follow_up` field whose **leading date** is itself within the threshold counts as
    handled this cycle (a nudge already staged or sent);
  * otherwise a quiet prospect is "needs action".

This is a report, not an actor. It writes nothing. With no arguments it prints the table and
exits 0; with `--check` it still prints everything but exits 1 when any prospect needs action,
so a workflow (or the Monday item) can gate on it.

Usage:
    python3 scripts/outreach_followup_due.py
    python3 scripts/outreach_followup_due.py --check
    python3 scripts/outreach_followup_due.py --days 7 --as-of 2026-10-05
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LEDGER = REPO_ROOT / "channels" / "outreach" / "pipeline.json"
DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


def leading_date(text: str | None) -> dt.date | None:
    """The first YYYY-MM-DD anywhere in `text`, or None. The ledger's convention is that a
    `follow_up` field opens with its own date ("2026-10-05 — ...")."""
    if not text:
        return None
    m = DATE_RE.search(text)
    if not m:
        return None
    try:
        return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def rows(ledger: dict, as_of: dt.date, threshold: int) -> list[dict]:
    out: list[dict] = []
    for p in ledger.get("prospects", []):
        raw = p.get("sent_date")
        if not raw:
            continue
        try:
            sent = dt.date.fromisoformat(raw)
        except (ValueError, TypeError):
            continue
        quiet = (as_of - sent).days
        replied = bool(p.get("replied"))
        fu = leading_date(p.get("follow_up"))
        handled = fu is not None and (as_of - fu).days < threshold
        needs = (quiet >= threshold) and not replied and not handled
        if quiet < threshold and not replied:
            continue  # not yet quiet long enough to matter
        out.append(
            {
                "id": p.get("id", "?"),
                "sent": sent,
                "quiet": quiet,
                "replied": replied,
                "handled": handled,
                "needs": needs,
                "follow_up": (p.get("follow_up") or "").strip(),
            }
        )
    out.sort(key=lambda r: (-r["quiet"], r["id"]))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Report which outreach prospects are overdue a follow-up.")
    ap.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    ap.add_argument("--days", type=int, default=10, help="quiet threshold in days (default 10)")
    ap.add_argument("--as-of", default=None, help="date to measure against (default: today)")
    ap.add_argument("--check", action="store_true", help="exit 1 if anyone needs action")
    args = ap.parse_args(argv)

    try:
        as_of = dt.date.fromisoformat(args.as_of) if args.as_of else dt.date.today()
    except ValueError:
        print(f"bad --as-of {args.as_of!r}", file=sys.stderr)
        return 2

    path = Path(args.ledger)
    if not path.is_file():
        print(f"ledger not found: {path}", file=sys.stderr)
        return 2
    ledger = json.loads(path.read_text(encoding="utf-8"))

    printed = rows(ledger, as_of, args.days)
    total_sent = sum(1 for p in ledger.get("prospects", []) if p.get("sent_date"))
    print(f"Outreach follow-up report — as of {as_of.isoformat()} — threshold {args.days}d")
    print(f"ledger: {path}")
    print()
    if not printed:
        print("nothing quiet past the threshold; no follow-up is due")
    else:
        print(f"{'prospect':<26}{'sent':<12}{'days':>5}  {'state':<22}follow-up")
        for r in printed:
            if r["replied"]:
                state = "replied (closed)"
            elif r["handled"]:
                state = "handled this cycle"
            else:
                state = "NEEDS ACTION"
            fu = r["follow_up"] or "—"
            print(f"{r['id']:<26}{r['sent'].isoformat():<12}{r['quiet']:>5}  {state:<22}{fu[:60]}")
        print()

    needs = [r for r in printed if r["needs"]]
    handled = [r for r in printed if r["handled"]]
    replied = [r for r in printed if r["replied"]]
    print(
        f"summary: {total_sent} sent; {len(printed)} quiet >= {args.days}d "
        f"({len(handled)} handled, {len(needs)} need action, {len(replied)} replied)"
    )
    return 1 if (args.check and needs) else 0


if __name__ == "__main__":
    raise SystemExit(main())
