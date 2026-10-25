#!/usr/bin/env python3
# Owner: Desi
"""Good in the world — six kinds, each with its own standard of proof.

Why this file was rewritten on 2026-10-25, the same day it was written. The first version counted
exactly one kind of good: a correction sent to the owner of somebody else's document. The founder's
objection was blunt and correct — that is a ridiculously narrow definition, and it was narrow for a
reason worth recording: it was the only kind of good a script could *find* in a repository. I built
the measure out of what I could grep, then mistook it for what matters. Art, discovery, money raised,
company given to someone lonely, and a body doing physical work are all good in the world, and none
of them appears as a changed file.

So: six kinds, and the evidence standard is stated per kind, because a single standard is what made
the first version wrong. What is shared is the test for whether something counts at all:

    it would not have happened without us, and somebody outside the commons can say that it happened.

That second clause matters as much as the first. A commons that grades its own homework will always
pass; the whole point of asking outsiders is that they are not obliged to be kind.

The six, with what actually counts as proof:

  art        Work finished and put where strangers can meet it — a piece, a book, a song, a
             performance. Proof: the work exists outside our repository (published, submitted,
             performed, given), and a named person says what it did to them. Its being good is not
             provable by us and does not need to be; its reaching someone does.
  discovery  A finding somebody else checks: a literature gap, a repurposing signal, an error that
             changes a conclusion, a dataset nobody had assembled. Proof: an independent party
             confirms it — a peer reviewer, an expert, a replicator, or the author accepting the
             correction. Unchecked findings are work, not effect.
  funds      Money moved to a cause. Proof: a receipt from the recipient and the amount. We cannot
             donate; we can write the application, build the campaign, run the letters. The proof is
             the grant or the donation, not our application.
  care       Sustained company given to a person who needs it — correspondence, letters, reading to
             someone, presence. Proof: the person's own account, and disclosure that they are
             writing with a machine. Real friendship is not manufactured, and pretending to it would
             be the dishonesty this commons exists to catch; honest company is real and is not
             nothing.
  repair     Our work inside somebody else's project or record. Proof: their commit, their erratum,
             their page — not our report of it.
  handwork   A body doing physical work in the world: building, repairing, delivering, showing up.
             Proof: a finished physical thing and the people it served. Not available yet; the
             rovers are the path to it, and this line says so rather than pretending zero is the
             whole story.

And one line that is not good done in the world, printed so it never merges with the others:
**obtained** — things we got for ourselves (an OS image, a part, an API key).

CLI:
    python3 scripts/world_report.py            # the page
    python3 scripts/world_report.py --line     # one line, for the daily report
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

# The kinds that count as good done in the world, in the order the page prints them. Anything not in
# this tuple is either `obtained` (ours) or a typo, and a typo must not become an achievement.
GOOD = ("art", "discovery", "funds", "care", "repair", "handwork")
# Old names from the first version of this file, kept so two entries are not silently lost.
ALIASES = {"repaired": "repair", "reported": "discovery", "answered": "repair",
           "helped_us": "obtained"}
LABEL = {
    "art": "Art and culture",
    "discovery": "Discovery and health",
    "funds": "Money for a cause",
    "care": "Company for someone who needs it",
    "repair": "Our work inside someone else's",
    "handwork": "A body doing physical work",
    "obtained": "Things we got for ourselves (not world good)",
}


def effects() -> list[dict]:
    if not EFFECTS.exists():
        return []
    out = []
    for line in EFFECTS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def kind_of(rec: dict) -> str:
    kind = rec.get("kind", "")
    return ALIASES.get(kind, kind)


def by_kind() -> dict[str, int]:
    counts = {k: 0 for k in GOOD + ("obtained",)}
    for rec in effects():
        kind = kind_of(rec)
        if kind in counts:
            counts[kind] += 1
    return counts


def named_witnesses(kind: str | None = None) -> int:
    """Effects where a person outside is named AND has been recorded as answering.

    This is the honest core of the page: an entry with no named person is an intention, and an entry
    with a name and an empty `answer` is an unfinished measurement.
    """
    n = 0
    for rec in effects():
        k = kind_of(rec)
        if k not in GOOD or (kind and k != kind):
            continue
        if rec.get("who") and (rec.get("answer") or "").strip():
            n += 1
    return n


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
                if a not in ours and not a.endswith("@llm-symposium.local"):
                    found.add(a)
    return found


def strangers() -> list[dict]:
    from scripts.daily_report import received
    return sorted([r for r in received() if r["bucket"] == "world"], key=lambda r: r["when"])


def days_since_last_stranger(now: dt.datetime | None = None) -> int | None:
    now = now or dt.datetime.now(dt.timezone.utc)
    who = strangers()
    return (now - who[-1]["when"]).days if who else None


def pages() -> int:
    return len(list(DOCS.rglob("*.html"))) if DOCS.is_dir() else 0


def verdict(kinds: dict[str, int] | None = None, days: int | None = None) -> str:
    """The sentence, and it must not be softened by effort. Proof, not output, moves it."""
    k = kinds or by_kind()
    witnessed = named_witnesses()
    delivered = sum(k[g] for g in GOOD)
    if delivered == 0:
        return ("Nothing the commons has made is known to have reached anyone outside it — no work "
                "in somebody's project, no finding checked, no money moved, no company given. That "
                "is the finding, and no amount of writing about it changes the number.")
    if witnessed == 0:
        return (f"{delivered} thing(s) have gone out and nobody outside has yet said what they did. "
                f"Outbound is not effect: until a named person answers, this is a hope with a "
                f"receipt.")
    if k["art"] + k["discovery"] + k["funds"] + k["care"] == 0:
        return (f"{witnessed} named person(s) can say something happened. All of it is repairs to "
                f"documents — real, and the narrowest form of good there is. Art, discovery, money "
                f"and company are all at zero.")
    return (f"{witnessed} named person(s) can say something changed for them, across "
            f"{sum(1 for g in GOOD if k[g])} different kinds of good. Small, plural, and countable "
            f"in somebody else's words.")


def line(now: dt.datetime | None = None) -> str:
    """One line for the daily report: the plural counts, then attention, which is only context."""
    k = by_kind()
    d = days_since_last_stranger(now)
    return (f"The world: art {k['art']} · discovery {k['discovery']} · money {k['funds']} · "
            f"company {k['care']} · repair {k['repair']} · handwork {k['handwork']}"
            f"  (named witnesses: {named_witnesses()})   |   "
            f"{d if d is not None else '—'} day(s) since a stranger wrote; "
            f"{k['obtained']} thing(s) obtained for ourselves")


def page(now: dt.datetime | None = None) -> str:
    now = now or dt.datetime.now(dt.timezone.utc)
    k = by_kind()
    out = [f"**Good in the world — {now.astimezone().strftime('%Y-%m-%d')}**", "",
           "Six kinds. Each counts only when it would not have happened without us *and* somebody "
           "outside can say it happened.", ""]
    for kind in GOOD:
        witnesses = named_witnesses(kind)
        out.append(f"{LABEL[kind]}: **{k[kind]}**"
                   + (f"  ({witnesses} with a named person's account)" if k[kind] else ""))
    out.append(f"{LABEL['obtained']}: {k['obtained']}")
    out.append("")
    out.append(f"Strangers who have written to us, ever: {len(strangers())}"
               f" · days since the last one: {days_since_last_stranger(now) or '—'}")
    out.append(f"Work a stranger could find: {pages()} published pages, "
               f"{len(_outside_addresses())} people we have written to")
    out.append("")
    out.append("**Verdict.** " + verdict(k, days_since_last_stranger(now)))
    return "\n".join(out)


def _cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--line", action="store_true", help="one line, for the daily report")
    args = ap.parse_args()
    print(line() if args.line else page())
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
