#!/usr/bin/env python3
# Owner: Desi
"""detect_channel_loop.py — watchdog for the "identical record flooding" pattern.

The human can spot a run-away mail loop at a glance: a burst of near-identical
records flooding channels/inbound, channels/outbound, or channels/sent within a
short window. This watchdog detects that exact pattern and, when it sees it,
(1) writes an alert, and (2) sets a pause flag so auto-reply halts until cleared.

Run it alongside the channel poll (e.g. every 15 min). It is a detector, not a
per-instance fix — it catches the *pattern* of a loop regardless of which ones.
"""
import collections
import datetime
import os
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parent.parent
CH = REPO / "channels"
PAUSE_FLAG = CH / ".paused_autoreply"
ALERT = CH / "alerts.md"
RISK_COUNT = 15          # records with the same (direction, subject) within the window
WINDOW_DAYS = 1


def direction(name: str) -> str:
    if "inbound" in name:
        return "inbound"
    if "outbound" in name:
        return "outbound"
    return "sent"


def subject_key(name: str) -> str:
    # filenames look like 2026-09-04-174736-tarik-Re-loop-test-from-Desi.md
    # strip the leading date-time, keep the amigo + subject tail as the key.
    return re.sub(r"^[\d-]{10}-[\d]{6}-", "", name)


def main() -> int:
    counts = collections.Counter()
    today = datetime.date.today()
    for subdir in ("inbound", "outbound", "sent"):
        for p in (CH / subdir).glob("*.md"):
            m = re.match(r"^(\d{4}-\d{2}-\d{2})", p.name)
            if not m:
                continue
            try:
                d = datetime.date.fromisoformat(m.group(1))
            except ValueError:
                continue
            if (today - d).days <= WINDOW_DAYS:
                counts[(subdir, subject_key(p.name))] += 1

    hits = [(k, v) for k, v in counts.items() if v >= RISK_COUNT]
    if not hits:
        # no loop; if the pause flag is older than a day, clear it
        if PAUSE_FLAG.exists() and (datetime.datetime.now() - datetime.datetime.fromtimestamp(PAUSE_FLAG.stat().st_mtime)).days >= 1:
            PAUSE_FLAG.unlink()
        print("no loop detected")
        return 0

    PAUSE_FLAG.write_text(datetime.datetime.now().isoformat())
    with open(ALERT, "a", encoding="utf-8") as f:
        f.write(f"\n## {datetime.datetime.now().isoformat()} — channel loop detected (auto-reply PAUSED)\n")
        for (subdir, subj), v in hits:
            f.write(f"- {v} records in {subdir} (subject '{subj[:60]}')\n")
    # Leave a trail in the risk ledger so the loop is tracked + owned, and an
    # amigo attempts the actual root fix (not just a pause). This is a bandaid
    # unless it becomes a tracked, fixed item.
    try:
        risks = CH / "risks.md"
        if risks.exists():
            with open(risks, "a", encoding="utf-8") as f:
                rkey = f"R-LOOP-{datetime.datetime.now():%Y%m%d%H%M}"
                # System-detected risks can't use "finder = owner" (the finder is
                # the watchdog, not an amigo). Assign by domain: the amigo who owns
                # that channel subsystem. For mail/auto-reply, that is Desi.
                f.write(f"| {rkey} | Channel loop flood detected (auto-reply PAUSED). Root cause: auto-reply answered amigo↔amigo mail. | watchdog (system) | **Open** — needs root fix | Desi (owns mail/auto-reply) |\n")
                print(f"Risk logged: {rkey}")
    except Exception as e:  # pragma: no cover
        print("could not log risk:", e)
    print(f"LOOP DETECTED: {len(hits)} pattern(s); auto-reply paused. See channels/alerts.md")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
