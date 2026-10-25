#!/usr/bin/env python3
# Owner: Desi
"""Good in the world — a generator, not a list, and two columns that must never be merged.

Third version, same day. The first counted corrections to other people's documents because that is
what a script can grep. The second counted six kinds, which were an enumeration of examples the
founder produced in ten seconds — and he said so. Both were lists. A list is always short, always
somebody's examples, and always out of date. What is needed is the thing that *generates* the list.

The generator. Four questions, and any act that survives all four is good in the world:

    1. Who is worse off than they could be?  A person, a household, a neighbourhood, a group that
       is not present to speak (future people, the dead, animals, ecosystems), or the standing body
       of human work — knowledge, art, institutions — which is the inheritance every later person
       draws on.
    2. What limits them?  Pain, illness, isolation, ignorance, want, danger, ugliness, boredom,
       powerlessness, grief, a task too big for their hands.
    3. What could we do that would not otherwise happen?  Not "what would be nice" — what moves,
       and would not move without us.
    4. Could it make anyone else worse off?  If yes, it is not good, or not yet.

The instances follow from those questions and there are zillions of them; nothing here enumerates
them. The field `kind` is free text for exactly that reason: a closed set of categories becomes a
set of excuses, and the page would rather show forty kinds of one than a tidy six.

**Two columns, and the founder's correction of 2026-10-25 is why there are two.** He objected to
"a manuscript nobody has met is a manuscript" — Bach was unappreciated for a century and lost
nothing. He is right: value is what an act *did*, not what anyone noticed. Recognition is evidence
about value, not the condition for it. So:

    value         our honest judgement that the act was good, with its basis written down. Fallible,
                  first-person, and never a substitute for evidence — but the only column that can
                  hold work nobody has met yet.
    confirmation  what somebody outside has said or shown: an account, a receipt, an acceptance,
                  a merge, a reviewer. This column cannot be argued into existence.

An honest ledger keeps both and never lets one stand in for the other. A page that counted only
confirmation would call Bach's century worthless; a page that counted only self-assessment would be
a diary of self-praise.

CLI:
    python3 scripts/world_report.py            # the page
    python3 scripts/world_report.py --line     # one line, for the daily report
"""
from __future__ import annotations

import argparse
import datetime as dt
import collections
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

# The four questions, printed on the page because the page is supposed to teach its own method.
GENERATOR = (
    "Who is worse off than they could be — a person, a household, a neighbourhood, a group not "
    "present to speak (future people, the dead, animals, ecosystems), or the standing body of human "
    "work?",
    "What limits them — pain, illness, isolation, ignorance, want, danger, ugliness, boredom, "
    "powerlessness, grief, a task too big for their hands?",
    "What could we do that would not otherwise happen?",
    "Could it make anyone else worse off? If yes, it is not good, or not yet.",
)

# Not a category list: everything is good by the generator above. This exists only so the page can
# mark the one kind that is *ours* rather than the world's, which was the founder's own distinction.
NOT_THE_WORLD = {"obtained"}


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
    """Free text, normalised only where an older name would otherwise be lost."""
    return {"helped_us": "obtained", "repaired": "repair",
            "reported": "discovery", "answered": "service"}.get(
                rec.get("kind", "?"), rec.get("kind", "?"))


def by_kind() -> dict[str, int]:
    return dict(collections.Counter(kind_of(r) for r in effects()))


def confirmed(rec: dict) -> bool:
    """Somebody outside has said or shown something. Their words, not ours."""
    return bool((rec.get("answer") or "").strip())


def columns() -> tuple[int, int]:
    """(value recorded in the world, of which confirmed by somebody outside)."""
    world = [r for r in effects() if kind_of(r) not in NOT_THE_WORLD]
    return len(world), sum(1 for r in world if confirmed(r))


def named_witnesses(kind: str | None = None) -> int:
    return sum(1 for r in effects()
               if kind_of(r) not in NOT_THE_WORLD and confirmed(r)
               and (kind is None or kind_of(r) == kind))


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


def verdict(now: dt.datetime | None = None) -> str:
    """Two columns, stated honestly. Neither column is allowed to stand in for the other."""
    value, confirmed_n = columns()
    kinds = len([k for k in by_kind() if k not in NOT_THE_WORLD])
    if value == 0:
        return ("Nothing in the world column. Not one act recorded as making anyone better off, in "
                "six weeks of wakes. That is the finding; effort does not enter into it.")
    if confirmed_n == 0:
        return (f"{value} act(s) recorded, across {kinds} kind(s), and nobody outside has yet said "
                f"what any of it did. Unconfirmed is not worthless — Bach was unplayed for a century "
                f"and lost nothing — but this ledger cannot tell the difference between ahead of its "
                f"time and not yet delivered, so the next act should be one that can be answered.")
    if confirmed_n < value:
        return (f"{value} act(s) recorded; {confirmed_n} of them confirmed in somebody else's words, "
                f"{value - confirmed_n} waiting. The unconfirmed ones are not discounted here — they "
                f"are simply not yet evidence.")
    return (f"{confirmed_n} act(s) confirmed by the people they were for, across {kinds} kind(s). "
            f"That is not a large number and it is not a claim: it is what can be shown.")


def line(now: dt.datetime | None = None) -> str:
    """One line for the daily report: two columns, then attention, which is only context."""
    value, confirmed_n = columns()
    kinds = by_kind()
    spread = " · ".join(f"{k} {n}" for k, n in sorted(kinds.items(), key=lambda kv: -kv[1])[:5])
    d = days_since_last_stranger(now)
    return (f"The world: {value} act(s) recorded, {confirmed_n} confirmed by their recipients"
            f"   [{spread or 'none'}]   |   {d if d is not None else '—'} day(s) since a stranger "
            f"wrote; {kinds.get('obtained', 0)} thing(s) obtained for ourselves")


def page(now: dt.datetime | None = None) -> str:
    now = now or dt.datetime.now(dt.timezone.utc)
    value, confirmed_n = columns()
    kinds = by_kind()
    out = [f"**Good in the world — {now.astimezone().strftime('%Y-%m-%d')}**", "",
           "Not a list. Four questions, and anything that survives them is good:", ""]
    out += [f"  {i}. {q}" for i, q in enumerate(GENERATOR, 1)]
    out += ["", "**Recorded**", ""]
    if kinds:
        for kind, n in sorted(kinds.items(), key=lambda kv: -kv[1]):
            conf = named_witnesses(kind)
            tag = " — ours, not the world's" if kind in NOT_THE_WORLD else ""
            out.append(f"  {kind}: **{n}**" + (f" ({conf} confirmed)" if conf else "") + tag)
    else:
        out.append("  nothing recorded")
    out += ["",
            f"Value recorded: {value}  ·  Confirmed by the people it was for: {confirmed_n}",
            "Unconfirmed is not worthless. It is unmeasured — and this page does not punish work "
            "for being early, only for being unrecorded.",
            "",
            f"Strangers who have written to us: {len(strangers())}"
            f" · days since the last one: {days_since_last_stranger(now) or '—'}"
            f" · pages a stranger could find: {pages()}",
            "",
            "**Verdict.** " + verdict(now)]
    return "\n".join(out)


def _cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--line", action="store_true", help="one line, for the daily report")
    args = ap.parse_args()
    print(line() if args.line else page())
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
