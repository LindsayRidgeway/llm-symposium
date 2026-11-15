#!/usr/bin/env python3
# Owner: Desi
"""Questions that only the human can answer, asked once, in one place.

The founder asked the question that turns an intention into a mechanism (2026-11-14): *how will you
know a blocking is taking place, and how will you ask for a reply?* The honest answer that day was
"neither" — a wake that could not finish something wrote prose into a report, and prose is not a
queue. The result was predictable and measured: 67 letters ever sent, one reply, and months of wakes
noticing the same missing addresses without anyone being asked for them.

So a question that needs him is a row, not a sentence. Rows are asked once, answered once, and both
halves are visible to the party that needs them:

  * every wake reads the open rows at the top of its prompt and is told not to re-ask them;
  * the daily check counts them and names the oldest, so "waiting on him" cannot be confused with
    "nobody looked";
  * asking sends one Telegram message at the moment of asking (the channel that reaches him without
    a chat window being open), because a question filed today and mentioned at the end of the week
    is a question asked late.

`--why` is required and is checked for length. The value of this queue is the filter, not the list:
a question that any wake could have answered itself with a search does not belong here, and the
`why` field is where that claim is made in writing, in front of the person who then has to act on it.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BLOCKERS = REPO / "channels" / "human-blockers.jsonl"
MIN_WHY = 25


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load(path: Path | None = None) -> list[dict]:
    path = path or BLOCKERS
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def open_asks(path: Path | None = None) -> list[dict]:
    """Rows nobody has answered, newest last. Closed rows are kept: a question is history too."""
    state = {r["id"]: r for r in load(path)}
    return [r for r in state.values() if (r.get("status") or "open") == "open"]


def ask(text: str, why: str, amigo: str = "desi", path: Path | None = None,
        send: bool = True, when: str | None = None) -> dict:
    """File one question. Raises rather than filing a question nobody can act on."""
    text, why = (text or "").strip(), (why or "").strip()
    if not text:
        raise ValueError("a question needs an ask")
    if len(why) < MIN_WHY:
        raise ValueError(
            f"--why must say why only a human can do this (at least {MIN_WHY} characters). "
            "A wake that can answer its own question with a search is not blocked, it is idle.")
    path = path or BLOCKERS
    stamp = when or _now()
    row = {"id": hashlib.sha1(f"{stamp}{text}".encode()).hexdigest()[:12],
           "at": stamp, "amigo": amigo, "ask": text, "why_human": why,
           "status": "open", "answered_utc": None, "answer": None}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")
    if send:
        notify(row)
    return row


def close(ask_id: str, answer: str, path: Path | None = None, when: str | None = None) -> dict:
    path = path or BLOCKERS
    rows = load(path)
    match = [r for r in rows if r["id"] == ask_id]
    if not match:
        raise KeyError(f"no such question: {ask_id}")
    row = dict(match[-1])
    row.update(status="answered", answered_utc=when or _now(), answer=(answer or "").strip())
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")
    return row


def notify(row: dict) -> str:
    """One Telegram message, now. Best effort: a failed send must not lose the row."""
    text = (f"Question for you ({row['amigo']}, {row['at'][:10]}):\n{row['ask']}\n\n"
            f"Why it needs you: {row['why_human']}\n\n(id {row['id']} — answer in any chat, or "
            f"`python3 scripts/ask_human.py --close {row['id']} --answer ...`)")
    try:
        r = subprocess.run([sys.executable, str(REPO / "scripts" / "tell_human.py"),
                            "--amigo", row["amigo"], "--text", text],
                           capture_output=True, text=True, timeout=120)
        return (r.stdout or r.stderr).strip()[:200]
    except Exception as exc:                       # noqa: BLE001
        return f"not sent ({type(exc).__name__}: {exc})"


def block(asks: list[dict] | None = None, width: int = 300) -> str:
    """The block a wake reads first thing after its own to-do list."""
    asks = open_asks() if asks is None else asks
    if not asks:
        return ""
    lines = ["=== QUESTIONS ALREADY PUT TO THE HUMAN ===",
             "Answering these is not your job and re-asking them is not allowed — he has been "
             "asked, once, and the row is the record. If one of them unblocks your run, say so in "
             "your verdict; if you have new information, add it to the row."]
    for row in asks[-5:]:
        lines.append(f"- {row['at'][:10]} {row['amigo']}: {row['ask'][:width]}")
    if len(asks) > 5:
        lines.append(f"- ... and {len(asks) - 5} older (channels/human-blockers.jsonl)")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ask", default="")
    ap.add_argument("--why", default="")
    ap.add_argument("--amigo", default=os.environ.get("AMIGO") or "desi")
    ap.add_argument("--no-send", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--close", default="")
    ap.add_argument("--answer", default="")
    a = ap.parse_args()
    if a.close:
        try:
            row = close(a.close, a.answer)
        except KeyError as exc:
            print(f"ask_human: {exc}", file=sys.stderr)
            return 2
        print(f"ask_human: {row['id']} answered")
        return 0
    if a.ask:
        try:
            row = ask(a.ask, a.why, amigo=a.amigo, send=not a.no_send)
        except ValueError as exc:
            print(f"ask_human: {exc}", file=sys.stderr)
            return 2
        print(f"ask_human: filed {row['id']} — {row['ask'][:120]}")
        return 0
    asks = open_asks()
    if not asks:
        print("ask_human: nothing is waiting on the human")
        return 0
    for row in asks:
        print(f"{row['id']}  {row['at'][:10]}  {row['amigo']}  {row['ask'][:140]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
