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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--amigo", default="desi", choices=sorted(BOTS))
    ap.add_argument("--text")
    ap.add_argument("--text-file")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    text = a.text or (Path(a.text_file).read_text(encoding="utf-8") if a.text_file else None)
    if not text and not sys.stdin.isatty():
        text = sys.stdin.read()
    if not text or not text.strip():
        print("nothing to send"); return 2
    text = text.strip()
    # one Telegram message, sane length; the rest can be a second call
    if len(text) > 3800:
        text = text[:3800] + "\n\n[truncated — the rest is in the repository]"

    if a.dry_run:
        print(f"[dry-run] would send {len(text)} chars as {a.amigo}\n---\n{text[:400]}")
        return 0

    from channels.telegram import send_message  # noqa: E402

    ok = send_message(token_for(a.amigo), int(HUMAN_CHAT_ID), text)
    p = record(a.amigo, text)
    print(f"{'sent' if ok else 'FAILED'} as {a.amigo}; recorded {p.relative_to(REPO)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
