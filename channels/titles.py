#!/usr/bin/env python3
# Owner: Desi
"""Short titles for ledger items, written by a model rather than cut by a regex.

Why this exists (2026-10-06). The daily report shortened an item's description by truncating it, and
the human's verdict was exact: "Using truncation to create titles produces mostly boilerplate with
little if anything to describe the actual work." He is right. A 160-character sentence cut at 42
characters yields `fixed the bug that made the commons'…`, which names nothing. A title is *authored*
— that was the point of the COBOL paragraph-name budget he cited — and the commons has five models
sitting right here, so the honest fix is to ask one.

His instruction, used verbatim as the prompt:

    Please convert this to a short title, 30 characters or less: <the full description>

The result is stored on the item as `short_title` in the append-only ledger, so each description is
paid for once and never re-titled. A failure is not fatal: the report falls back to truncation and
says nothing, because a missing title must not cost the report.

Usage:
    python3 channels/titles.py --backfill          # every item that has no short title yet
    python3 channels/titles.py --backfill --limit 5
    python3 channels/titles.py --one "the full description of the work"
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from channels.item_ledger import LEDGER, append, load  # noqa: E402

API = "https://api.deepseek.com/chat/completions"
TITLE_MODEL = os.environ.get("TITLE_MODEL", "deepseek-chat")
MAX_TITLE = 30
INSTRUCTION = "Please convert this to a short title, {} characters or less: {}"
SYSTEM = ("You write very short labels for a work log. Reply with the title and nothing else — no "
          "quotes, no trailing period, no explanation. Name the work itself, not the wake: not "
          "'worked on infrastructure' but 'lander refused dirty tree'. Keep it under {} characters.")
# A title that runs long is the one case where this code may cut, at a word boundary, rather than
# spend a second call. It should be rare.
CLEAN_RE = re.compile(r'^[\s"\'`*_]+|[\s"\'`*_.]+$')


def api_key() -> str:
    """Desi's key, from her own env file or the environment. Never printed."""
    for name in ("DEEPSEEK_API_KEY", "DEEPSEEK_API_KEY_DESI"):
        if os.environ.get(name):
            return os.environ[name].strip()
    env = Path.home() / "LLM" / "desi-bot" / "bot.env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith(("DEEPSEEK_API_KEY=", "DEEPSEEK_API_KEY_DESI=")) and "=" in line:
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("titles: no DeepSeek key available")


def clean(raw: str) -> str:
    """The model's answer, as a title: unquoted, unpunctuated, and inside the budget."""
    t = CLEAN_RE.sub("", " ".join((raw or "").split()))
    if len(t) > MAX_TITLE:
        cut = t[:MAX_TITLE + 1]
        t = cut.rsplit(" ", 1)[0] if " " in cut else t[:MAX_TITLE]
    return t


def short_title(description: str, key: str | None = None) -> str:
    """One model call. His prompt, verbatim, with the description appended."""
    description = " ".join((description or "").split())[:1200]
    if not description:
        return ""
    body = json.dumps({
        "model": TITLE_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM.format(MAX_TITLE)},
            {"role": "user", "content": INSTRUCTION.format(MAX_TITLE, description)},
        ],
        "max_tokens": 24,
        "temperature": 0.2,
    }).encode()
    req = urllib.request.Request(
        API, data=body, method="POST",
        headers={"Authorization": "Bearer " + (key or api_key()),
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = json.loads(resp.read().decode())
    return clean(data["choices"][0]["message"]["content"])


def backfill(limit: int = 0, workers: int = 6, path: Path = LEDGER) -> tuple[int, int]:
    """Give every untitled item a title. Returns (titled, failed). Idempotent by construction."""
    items = load(path)
    todo = [rec for rec in items.values() if not rec.get("short_title") and rec.get("title")]
    todo.sort(key=lambda r: r.get("filed_utc") or "")
    if limit:
        todo = todo[:limit]
    if not todo:
        return 0, 0
    key = api_key()

    def work(rec: dict):
        try:
            return rec, short_title(rec.get("title", ""), key), None
        except Exception as exc:                      # noqa: BLE001 — one failure must not stop the rest
            return rec, None, f"{type(exc).__name__}: {exc}"

    done = failed = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for rec, title, err in pool.map(work, todo):
            if title:
                rec = dict(rec, short_title=title)
                append([rec], path)
                done += 1
                print(f"  {title:<32s} <- {rec.get('title','')[:60]}")
            else:
                failed += 1
                print(f"  FAILED {rec['id']}: {err}", file=sys.stderr)
    return done, failed


def _cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--backfill", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--one")
    a = ap.parse_args()
    if a.one:
        print(short_title(a.one))
        return 0
    if a.backfill:
        done, failed = backfill(a.limit, a.workers)
        print(f"titles: {done} titled, {failed} failed")
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
