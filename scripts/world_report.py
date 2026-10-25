#!/usr/bin/env python3
# Owner: Desi
"""The world, not the repo — one page, plain words, six numbers.

Why this exists (2026-10-25). The founder said he cannot follow the ledger, and that what he needs
is a measure of *real-world productivity* — whether the natural and human world is better because
the commons exists. Everything else the commons reports is instrument maintenance: letters, queues,
drain rates. Those describe the machinery, not the effect. A perfect ledger with an unread world is
a tidy diary in a locked room.

So this page asks the only question that survives the funding question:

    has anybody outside this repository noticed we exist, and did anything we made change
    what they did?

Its counts are deliberately hard to inflate:

  * **Letters sent** is an output and is labelled as one. Sending is cheap; it is counted so the
    ratio to replies is visible, not because it is an achievement.
  * **Replies from a stranger** is the primary number, and it requires a message in
    `channels/inbound/` whose sender is not the founder, not one of us, not a robot, and not a
    bounce. The classifier that decides it lives in `scripts/daily_report.py` and was written to
    fail toward "machine", because inflating this number is the failure that matters.
  * **Days since a stranger replied** is the sharpest line here. It cannot be argued with and it
    cannot be improved by writing anything new.
  * **Adopted elsewhere** requires a named outside project and a named person there who took
    something in — `channels/world-wins.jsonl`, one line per event, each with a URL. Not a claim
    that our work is good: a record that somebody else's repository now contains it.
  * **Pages a stranger could reach** is the reachable surface, not readership. No analytics exist,
    and inventing a readership number would be the exact dishonesty this file is against.

CLI:
    python3 scripts/world_report.py             # the page
    python3 scripts/world_report.py --line      # the one-line version for the daily report
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

SENT_DIR = REPO / "channels" / "sent"
OUTBOUND_DIR = REPO / "channels" / "outbound"
EFFECTS = REPO / "channels" / "world-effects.jsonl"
DOCS = REPO / "docs"
_TO_RE = re.compile(r"^To:\s*(.+)$", re.M)
_AT_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def _outside_addresses() -> set[str]:
    from scripts.daily_report import HUMAN_EMAILS
    ours = set(HUMAN_EMAILS) | {"desi.s.amigo@gmail.com"}
    found: set[str] = set()
    for folder in (SENT_DIR, OUTBOUND_DIR):
        if not folder.is_dir():
            continue
        for path in folder.rglob("*.md"):
            m = _TO_RE.search(path.read_text(encoding="utf-8", errors="replace"))
            if not m:
                continue
            for addr in _AT_RE.findall(m.group(1)):
                a = addr.strip().lower()
                if a in ours or a.endswith("@llm-symposium.local"):
                    continue
                found.add(a)
    return found


def letters_sent(hours: int | None = None) -> tuple[int, int]:
    """(letters with a recipient outside the commons, how many inside the window)."""
    from scripts.daily_report import HUMAN_EMAILS
    ours = set(HUMAN_EMAILS) | {"desi.s.amigo@gmail.com"}
    total = recent = 0
    cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)) if hours else None
    for folder in (SENT_DIR, OUTBOUND_DIR):
        if not folder.is_dir():
            continue
        for path in folder.rglob("*.md"):
            text = path.read_text(encoding="utf-8", errors="replace")
            m = _TO_RE.search(text)
            if not m:
                continue
            addrs = [a.lower() for a in _AT_RE.findall(m.group(1))]
            if not addrs or all(a in ours or a.endswith("@llm-symposium.local") for a in addrs):
                continue
            total += 1
            if cutoff:
                stamp = re.search(r"(\d{4})-(\d{2})-(\d{2})", path.name)
                if stamp:
                    when = dt.datetime.strptime(stamp.group(0), "%Y-%m-%d").replace(
                        tzinfo=dt.timezone.utc)
                    if when >= cutoff:
                        recent += 1
    return total, recent


def strangers() -> list[dict]:
    from scripts.daily_report import received
    return sorted([r for r in received() if r["bucket"] == "world"], key=lambda r: r["when"])


def days_since_last_stranger(now: dt.datetime | None = None) -> int | None:
    now = now or dt.datetime.now(dt.timezone.utc)
    who = strangers()
    if not who:
        return None
    return (now - who[-1]["when"]).days


def effects() -> list[dict]:
    if not EFFECTS.exists():
        return []
    out = []
    for line in EFFECTS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    return sorted(out, key=lambda r: r.get("date") or "")


def by_kind() -> dict[str, int]:
    """Repaired / reported / answered / helped_us — the four kinds of effect, counted apart.

    `helped_us` is kept visible on purpose. The founder drew the line himself on 2026-10-12: a
    manufacturer sending us an OS image changed our world, not anyone else's. A ledger that let
    those two merge would report activity as benefit, which is the exact error this page exists
    to stop.
    """
    counts = {"repaired": 0, "reported": 0, "answered": 0, "helped_us": 0}
    for rec in effects():
        kind = rec.get("kind", "")
        if kind in counts:
            counts[kind] += 1
    return counts


def pages() -> int:
    return len(list(DOCS.rglob("*.html"))) if DOCS.is_dir() else 0


def verdict(days: int | None, adopted: int, kinds: dict[str, int] | None = None) -> str:
    """The honest sentence. It is about effect; the reply count is context, not the finding.

    If nothing has been repaired and nothing verified has been sent to an owner, then no matter how
    many letters went out, the answer to "is the world better because we exist" is: not measurably.
    """
    k = kinds or by_kind()
    delivered = k["repaired"] + k["reported"] + k["answered"]
    if delivered == 0:
        return ("nothing the commons has made is known to have changed anything outside it: no "
                "repair in anyone's work, no verified finding sent to the person it concerns, no "
                "outsider served. That is the whole finding, and it cannot be improved by writing "
                "more reports.")
    if k["reported"] == 0 and k["repaired"] <= 1:
        return (f"one kind act of work has reached the world ({delivered} instance in all), which is "
                f"not yet a practice. The rest is a broadcast; a stranger last wrote "
                f"{days if days is not None else '—'} days ago.")
    return (f"{k['repaired']} repair(s), {k['reported']} reported finding(s), {k['answered']} "
            f"answered question(s). Small, real, and countable in somebody else's terms.")


def line(now: dt.datetime | None = None) -> str:
    """The one line for the daily report: effect first, attention second.

    Order is the argument. `repaired` means somebody else's work now contains ours; `reported`
    means a verified error reached the person who owns it; `answered` means an outsider asked and
    used what came back. Replies and letters sit second, because a reply is only the channel — the
    founder's correction of 2026-10-25 was that strangers have no reason to help a commons that is
    not doing any good, so the good has to be counted by itself and not inferred from the replies.
    """
    d = days_since_last_stranger(now)
    k = by_kind()
    return (f"The world: {k['repaired']} repair(s) in someone else's work"
            f" · {k['reported']} verified error(s) reported to its owner"
            f" · {k['answered']} question(s) answered for an outsider"
            f"   |   {d if d is not None else '—'} day(s) since a stranger wrote"
            f" · {k['helped_us']} thing(s) we got for ourselves, counted apart")


def page(now: dt.datetime | None = None) -> str:
    now = now or dt.datetime.now(dt.timezone.utc)
    d = days_since_last_stranger(now)
    sent, recent = letters_sent(hours=7 * 24)
    who = strangers()
    adopted = effects()
    out = [f"**The world, not the repo — {now.astimezone().strftime('%Y-%m-%d')}**", ""]
    out.append(f"Letters sent to addresses outside the commons: {len(_outside_addresses())} people, "
               f"{sent} letters ({recent} in the last 7 days)   — an output, not a result")
    out.append(f"Replies from a stranger, ever: {len(who)}")
    out.append(f"Days since a stranger replied: {d if d is not None else 'never'}"
               + (f"   (last: {who[-1]['from'][:50]}, {who[-1]['when'].date()})" if who else ""))
    k = by_kind()
    out.append(f"Repaired in someone else's work: {k['repaired']}"
               + (f"   ({adopted[0].get('what', '?')[:60]}…)" if k["repaired"] else ""))
    out.append(f"Verified errors reported to the person who owns them: {k['reported']}")
    out.append(f"Questions from an outsider answered and used: {k['answered']}")
    out.append(f"Things we got for ourselves, counted apart: {k['helped_us']}")
    out.append(f"Pages a stranger could reach: {pages()}   — reachable, not read: nobody reports a "
               f"reader and no analytics exist")
    out += ["", "**Verdict.** " + verdict(d, len(adopted), k)]
    return "\n".join(out)


def _cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--line", action="store_true", help="one line, for the daily report")
    args = ap.parse_args()
    print(line() if args.line else page())
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
