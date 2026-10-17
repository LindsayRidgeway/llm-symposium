#!/usr/bin/env python3
"""Is the Goose x DeepSeek 400 stall (R-008) still happening? — a recurrence detector.

Owner: Dmitri.  Written 2026-10-11.

**What it answers.** R-008 records that interactive Goose sessions on the DeepSeek
provider (`custom_deepseek`) died mid-turn with

    Request failed: Bad request (400): An assistant message with 'tool_calls' must be
    followed by tool messages responding to each 'tool_call_id'.
    (insufficient tool messages following tool_calls message)

and leaves one watch condition standing: *escalate to a wake-level risk if it ever
hits a `bot.py` / `local_tick.py` run*. This tool is the measurement that condition
needs, and it is the only reason it exists — nothing else here is new.

**Why a plain search of the session store is wrong.** The error string is now quoted
all over the workspace: it is the text of the R-008 row in `channels/risks.md`, it sits
in the transcripts of every wake that read that file, and it rides in session digests.
Measured 2026-10-11: the store held **92** messages bearing the signature and only
**13** that were the thing itself. A later reader counting the string would watch it
climb with every wake that reads the risk table and conclude the stall was getting
worse. It climbs because we wrote it down.

So the signature is separated into the three ways it actually appears:

  * ``error``  — goose surfaced the provider rejection: the message carries
    ``"type":"error"``.  This is the occurrence.
  * ``report`` — a person or an amigo pasting the error back into the chat ("Ran into
    this error ...", "stalled with this error ..."). Plain user text, short, and not a
    tool result. Secondary evidence that an occurrence happened.
  * ``quote``  — everything else: the risk row itself, a transcript, a digest. Any
    message that *is* or *contains* a tool result (``"toolResponse"``) is a quote by
    construction — an occurrence is never a tool result.

**Read-only.** Opens the session database with ``mode=ro``. Writes nothing.

Exit code 1 when a **wake** genuinely hit the error (the escalation condition named in
R-008); 0 otherwise. A nonzero exit means "this is no longer a chat-only problem".

Usage::

    python3 scripts/r008_recurrence_check.py
    python3 scripts/r008_recurrence_check.py --since 2026-10-05 --json
    python3 scripts/r008_recurrence_check.py --db /path/to/sessions.db
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import sqlite3
import sys

# The tail of the provider's message, which is stable and specific enough to find the
# occurrence without matching the shorter `'tool_calls' must be followed` fragments
# that appear in unrelated prose.
SIGNATURE = "insufficient tool messages following tool_calls message"

DEFAULT_DB = os.path.expanduser("~/.local/share/goose/sessions/sessions.db")

# Phrasings a person uses when pasting the failure back into a chat. Matched
# case-insensitively against short, non-tool-result user messages only.
REPORT_MARKERS = (
    "ran into this error",
    "stalled with this error",
    "ended with this error",
    "ended with the following error",
    "this error msg",
)

WAKES_MARKER = "/tick-state/runs/"


def classify(role: str, content_json: str) -> str:
    """Return ``error`` / ``report`` / ``quote`` for one message body."""
    low = content_json.lower()
    # A tool result can carry the string only because it printed something that does.
    if '"toolresponse"' in low:
        return "quote"
    if '"type":"error"' in low or '"type": "error"' in low:
        return "error"
    if role == "user" and len(content_json) < 1500 and any(m in low for m in REPORT_MARKERS):
        return "report"
    return "quote"


def load(db_path: str):
    """Every message bearing the signature, with its session's context. Read-only."""
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        return con.execute(
            """
            SELECT m.session_id, s.name, s.working_dir, s.created_at,
                   s.provider_name, m.role, m.content_json
              FROM messages m
              JOIN sessions s ON s.id = m.session_id
             WHERE m.content_json LIKE ?
            """,
            ("%" + SIGNATURE + "%",),
        ).fetchall()
    finally:
        con.close()


def summarise(rows, since: str | None = None):
    """Split the rows into findings (``error``/``report``) and the quote count."""
    findings = []
    quotes = 0
    for session_id, name, working_dir, created_at, provider, role, content_json in rows:
        if since and (created_at or "") < since:
            continue
        kind = classify(role, content_json)
        if kind == "quote":
            quotes += 1
            continue
        findings.append(
            {
                "session_id": session_id,
                "name": name or "",
                "kind": kind,
                "wake": bool(working_dir and WAKES_MARKER in working_dir),
                "provider": provider or "",
                "at": created_at or "",
            }
        )
    findings.sort(key=lambda f: f["at"])
    return findings, quotes


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Recurrence check for risk R-008.")
    ap.add_argument("--db", default=DEFAULT_DB, help="goose sessions database (opened read-only)")
    ap.add_argument("--since", default=None, help="only count occurrences on/after this ISO date")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    if not os.path.exists(args.db):
        print(f"no session database at {args.db}", file=sys.stderr)
        return 2

    rows = load(args.db)
    findings, quotes = summarise(rows, since=args.since)

    by_kind = collections.Counter(f["kind"] for f in findings)
    wake_errors = [f for f in findings if f["kind"] == "error" and f["wake"]]
    escalated = bool(wake_errors)

    if args.json:
        print(
            json.dumps(
                {
                    "db": args.db,
                    "since": args.since,
                    "signature_bearing_messages": len(rows),
                    "quotes": quotes,
                    "findings": findings,
                    "counts": dict(by_kind),
                    "wake_errors": len(wake_errors),
                    "escalate": escalated,
                },
                indent=2,
            )
        )
        return 1 if escalated else 0

    print(f"session store: {args.db}")
    print(f"signature-bearing messages: {len(rows)}  (quotes excluded below: {quotes})")
    if args.since:
        print(f"counted from: {args.since}")
    print()

    if not findings:
        print("no genuine occurrence in range — R-008 has not recurred.")
    else:
        print(f"{'when':19s} {'kind':7s} {'where':11s} {'provider':16s} session")
        for f in findings:
            where = "WAKE" if f["wake"] else "interactive"
            print(f"{f['at']:19s} {f['kind']:7s} {where:11s} {f['provider']:16s} {f['name']} ({f['session_id']})")
        print()
        print(f"occurrences: {by_kind.get('error', 0)} error, {by_kind.get('report', 0)} report")

    if escalated:
        print()
        print("ESCALATE: the error hit a wake run (working dir under tick-state/runs/).")
        for f in wake_errors:
            print(f"  {f['at']}  {f['name']} ({f['session_id']})")
        return 1

    print()
    print("verdict: no wake has been hit; nothing to escalate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
