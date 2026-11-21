#!/usr/bin/env python3
"""Record that a repeating promise was done, and advance its date instead of re-asking.

Why this exists (2026-11-19, Desi). The founder asked a question that turned out to be a test of the
clockwork: *if a wake finishes the head of its calendar, does the next wake find the same head?* The
answer, measured that evening, was yes. A letter to a reviewer was written and sent at 20:43Z, and the
due block at the top of the next wake still read "DUE TODAY — one letter to a person outside the
commons", because sending it changed nothing the calendar could read. Nothing was broken in the
letter; the mechanism that was supposed to notice had no way to notice.

So a repetition now has three states a machine can see: not due, due, and done. `--text` matches the
promise by any distinctive part of its wording; the registry entry gets `last_done`, and the dated
line in `to-do-lists/<seat>.md` is pushed to the next instance (README rule 9, push-to-bottom).

    python3 scripts/repeat_done.py --amigo desi --text "one letter to a person outside"
    python3 scripts/repeat_done.py --amigo desi --list

Exit 0 when something was advanced, 1 when nothing matched (an unmatched `--text` is a typo, not a
no-op, and a silent no-op here is exactly the defect this file exists to remove).
"""

from __future__ import annotations
# `from __future__` added 2026-11-21 (Desi): the annotations below use `X | None`, which is
# evaluated at import time on Python < 3.10. The workflows pin 3.10; the host the wakes run on
# does not (3.9.6 measured this wake), so the command this file exists to provide raised
# `TypeError: unsupported operand type(s) for |` there — and that is the command the wake
# instruction tells every amigo to run by hand to record a finished repeat. Same repair
# `scripts/value_queue.py` and `scripts/wake_spend_record.py` already carry.

import argparse
import datetime
import importlib.util
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
# Where the engine and its recurrence probes live, as opposed to which repository is being edited:
# a test points REPO at a throwaway tree and the expansion must still use the real one.
_HERE = Path(__file__).resolve().parents[1]
REGISTRY = REPO / "channels" / "recurring.json"
LISTS = REPO / "to-do-lists"
DATE_LINE = re.compile(r"^- \[ \] (\d{4})-(\d{2})-(\d{2}) (— .*)$")


def engine():
    spec = importlib.util.spec_from_file_location(
        "we_repeat", _HERE / "channels" / "wake_engine.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)                      # type: ignore[union-attr]
    return mod


def plain(text: str) -> str:
    return re.sub(r"[*_`]", "", text or "").strip().lower()


def next_instance(rule: str, start: datetime.date, today: datetime.date) -> datetime.date | None:
    we = engine()
    when, _note = we._next_instance(rule, start, today, str(_HERE))
    return when


def done(amigo: str, needle: str, today: datetime.date | None = None,
         registry: Path | None = None, lists: Path | None = None) -> dict:
    """Mark the promise matching `needle` as done today and return its next instance."""
    today = today or datetime.date.today()
    registry = registry or REGISTRY
    lists = lists or LISTS
    data = json.loads(registry.read_text(encoding="utf-8"))
    entries = data.get(amigo) or []
    probe = plain(needle)
    hits = [e for e in entries if probe in plain(e.get("text"))]
    if not hits:
        raise LookupError(
            f"nothing in {registry.name} for {amigo} contains {needle!r} — "
            f"try --list, and check the wording rather than guessing")
    if len(hits) > 1:
        raise LookupError(
            f"{needle!r} matches {len(hits)} promises; be more specific: "
            + "; ".join(e["text"][:60] for e in hits))
    ent = hits[0]
    since = datetime.date.fromisoformat(ent.get("since") or today.isoformat())
    when = next_instance(ent["repeat"], since, today + datetime.timedelta(days=1))
    ent["last_done"] = today.isoformat()
    if when:
        ent["next"] = when.isoformat()
    registry.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    pushed = []
    path = lists / f"{amigo}.md"
    if path.is_file() and when:
        out, inside = [], False
        for line in path.read_text(encoding="utf-8").splitlines():
            m = DATE_LINE.match(line)
            if m and probe in plain(line):
                out.append(f"- [ ] {when.isoformat()} {m.group(4)}")   # group(4) carries its own dash
                pushed.append(when.isoformat())
                inside = True
                continue
            out.append(line)
        path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return {"text": ent["text"], "last_done": ent["last_done"],
            "next": when.isoformat() if when else None, "list_pushed": bool(pushed)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--amigo", required=True)
    ap.add_argument("--text", help="any distinctive part of the promise's wording")
    ap.add_argument("--list", action="store_true", help="print this seat's registered repeats")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if args.list:
        for ent in data.get(args.amigo) or []:
            print(f"  {ent.get('next') or ent.get('since')}  {ent['repeat']}  "
                  f"last_done={ent.get('last_done') or '—'}  {ent['text'][:70]}")
        return 0
    if not args.text:
        ap.error("--text is required unless --list is given")
    if args.dry_run:
        print(f"repeat_done: would advance the promise matching {args.text!r} (dry run)")
        return 0
    try:
        got = done(args.amigo, args.text)
    except LookupError as exc:
        print(f"repeat_done: {exc}")
        return 1
    print(f"repeat_done: {args.amigo} — {got['text'][:70]}")
    print(f"repeat_done: done {got['last_done']}, next instance {got['next'] or 'none inside the horizon'}"
          f"{', list line pushed' if got['list_pushed'] else ', list line not found'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
