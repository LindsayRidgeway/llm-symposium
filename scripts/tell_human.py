#!/usr/bin/env python3
"""Answer the human on Telegram, from any body.

The human's request (2026-09-13): he talks to Desi in English and wants the answer to come
back with the clockwork invisible. If he asks Desi-Telegram "how is the self-starting
platform going?", Desi-T should not answer from its own narrow view and should not hand him
a command — the question should travel to a body with the repository in front of it, and the
answer should travel back.

The email channel already works this way: an unreplied human email is picked up, investigated,
drafted and sent (`channels/auto_reply.py` + `channels.mail.drain_outbox`). Telegram had only
the front half. This is the back half: a session that has actually looked at the repository can
send its answer to the human's Telegram, and the repository keeps the record of it.

Usage:
    python3 scripts/tell_human.py --amigo desi --text "the answer"
    python3 scripts/tell_human.py --amigo desi --text-file /tmp/answer.md
    echo "the answer" | python3 scripts/tell_human.py --amigo desi

Deliberately small: it sends one message and records it. It does not poll, judge, or schedule —
those live on the other side of the relay, and scheduling is agenda item 9's problem.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

HUMAN_CHAT_ID = os.environ.get("HUMAN_TELEGRAM_CHAT", "1733127278")
BOTS = {"desi": "desi-bot", "claude": "claude-bot", "gemini": "gemini-bot", "tarik": "tarik-bot"}

WAKE_PREFIXES = (
    "I woke up by myself just now and did some work, and it is in the repository now — "
    "not waiting on anyone. What it was: ",
    "I woke up by myself just now and did some work. What it was: ",
)
CUT_OFF_WAKE = (
    "I woke up by myself just now and got nothing finished — I ran out of time or lost the thread "
    "partway through. Nothing came of it. Nothing needed from you."
)
REVIEW_STATUS_RE = re.compile(
    r"\s*It is not published yet(?::| —) it (?:goes onto my review pile(?:, which is now \d+ pieces deep)?|"
    r"is waiting for someone other than me to look at it),? and only something other than me can "
    r"merge that pile\.\s*",
    re.I,
)

# The human's format, 2026-10-01: a request is one message whose first line is REQUEST <initial>-<serial>.
# Serials count from 1 per amigo and are never reused; governance/request-register.md holds the state.
REQUEST_RE = re.compile(r"^([CDGT])-([0-9]+)$")
REGISTER = REPO / "governance" / "request-register.md"
INITIAL = {"desi": "D", "claude": "C", "gemini": "G", "tarik": "T"}


def sanitize_for_human(text: str) -> str:
    """Remove fixed wake-notification boilerplate while preserving the action/status signal.

    Normal human-directed messages pass through untouched.  Wake summaries lose self-narration
    ("I woke up...") and the blanket "Nothing needed from you" sentence, then get a compact status
    line so the message still says whether the human is on the hook.
    """
    text = text.strip()
    status = None
    if text == CUT_OFF_WAKE:
        text = "I got nothing finished — I ran out of time or lost the thread partway through. Nothing came of it."
        status = "Status: no artifact; action: none."
    else:
        for prefix in WAKE_PREFIXES:
            if text.startswith(prefix):
                status = "Status: in the repository; action: none." if "not waiting on anyone" in prefix else None
                text = text[len(prefix):]
                break
        replaced = REVIEW_STATUS_RE.sub(" ", text)
        if replaced != text:
            text = replaced
            status = "Status: awaiting reviewer; action: none."
    text = re.sub(r"\s*Nothing needed from you\.\s*$", "", text, flags=re.I).strip()
    text = re.sub(r"[ \t]{2,}", " ", text)
    if status:
        return f"{text}\n\n{status}" if text else status
    return text


def token_for(amigo: str) -> str:
    """Read the amigo's Telegram token from its own env file. Never printed."""
    env = Path.home() / "LLM" / BOTS[amigo] / "bot.env"
    if not env.exists():
        raise SystemExit(f"no env file for {amigo}: {env}")
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("TELEGRAM_BOT_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(f"no TELEGRAM_BOT_TOKEN in {env}")


def record(amigo: str, text: str) -> Path:
    """The repository keeps the record: an outbound message is part of the conversation log."""
    stamp = dt.datetime.utcnow().strftime("%Y-%m-%d-%H%M%S")
    d = REPO / "channels" / "telegram"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{stamp}-outbound-{amigo}-session.md"
    p.write_text(
        f"# Telegram outbound — {stamp}\n\n"
        f"- Chat: {HUMAN_CHAT_ID}\n- From: {amigo} (session, not the polling bot)\n"
        f"- Path: session -> repo -> Telegram (the relay the human asked for)\n\n---\n\n{text}\n",
        encoding="utf-8",
    )
    return p


def _register_rows() -> list[list[str]]:
    """Rows of the register table, in file order."""
    if not REGISTER.exists():
        return []
    rows = []
    for line in REGISTER.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ") or line.startswith("| id ") or line.startswith("|--"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0]:
            rows.append(cells)
    return rows


def _row_index(rid: str) -> int | None:
    for i, cells in enumerate(_register_rows()):
        if cells[0].upper() == rid.upper():
            return i
    return None


def _guard_request_id(amigo: str, rid: str) -> str:
    """Refuse anything that would make the numbering ambiguous. Serials are never reused."""
    rid = rid.strip().upper()
    m = REQUEST_RE.match(rid)
    if not m:
        raise SystemExit(f"bad request id {rid!r}: the form is <initial>-<serial>, e.g. D-1")
    if m.group(1) != INITIAL[amigo]:
        raise SystemExit(
            f"id {rid} starts with {m.group(1)}; {amigo}'s requests start with {INITIAL[amigo]}"
        )
    if _row_index(rid) is not None:
        raise SystemExit(f"id {rid} is already in the register; serials are never reused")
    return rid


def _append_register(rid: str, amigo: str, gist: str, telegram_path: Path) -> None:
    if not REGISTER.exists():
        raise SystemExit(f"no register at {REGISTER.relative_to(REPO)}; a request must be recorded to exist")
    gist = " ".join(gist.split()).replace("|", "/")[:70] or "(no text)"
    stamp = dt.datetime.now(dt.timezone.utc).date().isoformat()
    with REGISTER.open("a", encoding="utf-8") as fh:
        fh.write(f"| {rid} | {stamp} | {amigo} | open | {gist} | {telegram_path.relative_to(REPO)} |\n")


def _close_register(rid: str) -> None:
    lines, hit = [], False
    for line in REGISTER.read_text(encoding="utf-8").splitlines(keepends=True):
        if line.startswith("| "):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells and cells[0].upper() == rid.upper():
                cells[3] = "done"
                line = "| " + " | ".join(cells) + " |\n"
                hit = True
        lines.append(line)
    if not hit:
        raise SystemExit(f"nothing to close: {rid} is not in the register")
    REGISTER.write_text("".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--amigo", default="desi", choices=sorted(BOTS))
    ap.add_argument("--text")
    ap.add_argument("--text-file")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--request", metavar="ID", help="open REQUEST <ID> to the human and register it")
    ap.add_argument("--close", metavar="ID", help="close REQUEST <ID>: sends 'REQUEST <ID> DONE'")
    a = ap.parse_args()

    text = a.text or (Path(a.text_file).read_text(encoding="utf-8") if a.text_file else None)
    if not text and not sys.stdin.isatty():
        text = sys.stdin.read()
    text = (text or "").strip()

    if a.request and a.close:
        raise SystemExit("give --request or --close, not both")

    rid = None
    if a.request:
        if not text:
            raise SystemExit("a request needs text")
        rid = _guard_request_id(a.amigo, a.request)
        if not REGISTER.exists():  # checked before sending, so a message is never sent unregistered
            raise SystemExit(f"no register at {REGISTER.relative_to(REPO)}; a request must be recorded to exist")
        text = f"REQUEST {rid}\n\n{text}\n\n— {a.amigo.capitalize()}"
    elif a.close:
        rid = a.close.strip().upper()
        if not REQUEST_RE.match(rid):
            raise SystemExit(f"bad request id {rid!r}: the form is <initial>-<serial>")
        text = f"REQUEST {rid} DONE"
    else:
        if not text:
            print("nothing to send"); return 2
        text = sanitize_for_human(text)
    # one Telegram message, sane length; the rest can be a second call
    if len(text) > 3800:
        text = text[:3800] + "\n\n[truncated — the rest is in the repository]"

    if a.dry_run:
        print(f"[dry-run] would send {len(text)} chars as {a.amigo}\n---\n{text[:400]}")
        return 0

    from channels.telegram import send_message  # noqa: E402

    ok = send_message(token_for(a.amigo), int(HUMAN_CHAT_ID), text)
    p = record(a.amigo, text)
    if ok and a.request:
        _append_register(rid, a.amigo, text.split("\n\n", 1)[-1].splitlines()[0], p)
    if ok and a.close:
        _close_register(rid)
    print(f"{'sent' if ok else 'FAILED'} as {a.amigo}; recorded {p.relative_to(REPO)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
