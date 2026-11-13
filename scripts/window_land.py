#!/usr/bin/env python3
"""Land a Goose window's transcript in the record of the member who opened it.

Any member can run this. It is the general form of the tool Dmitri wrote for his own seat on
2026-11-13; the point is that the rule does not live in one home directory.

    python3 scripts/window_land.py --member dmitri --list
    python3 scripts/window_land.py --member dmitri <session-id>
    python3 scripts/window_land.py --member dmitri --mine        # every window of mine not yet landed

What it does, in plain words: it copies the conversation out of goose's session database into a
markdown file in that member's own windows folder, adds a row to that folder's INDEX.md, and prints
one line that can go in the journal. Thinking blocks are dropped. Credential-shaped strings are
replaced with a label before anything is written, because a copy of a transcript is a new place for
a key to live.

Refusals are on purpose and they are mechanical:
  * any window named for Dawn is refused, always, whoever is asking;
  * a window that belongs to a different member is refused, and the tool says whose it is;
  * `--member` must be a real member's name (see MEMBERS) and the member's folder must exist.

Nothing is written outside `~/LLM/<member>-bot/windows/`.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

DB = Path.home() / ".local/share/goose/sessions/sessions.db"
BOTS = Path.home() / "LLM"

# Member name -> folder. Dawn is here only so she can be refused by name.
MEMBERS = {
    "claude": "claude-bot",
    "desi": "desi-bot",
    "dmitri": "dmitri-bot",
    "gemini": "gemini-bot",
    "tarik": "tarik-bot",
    "gwen": "gwen-bot",
}
SACRED = "dawn"
NAME_IN_TITLE = re.compile(
    r"^\s*(dawn|claude|dmitri|desi|gemini|tarik|gwen|gwenllian)\b", re.IGNORECASE)
ALIASES = {"gwenllian": "gwen"}
TURN_CONTEXT = re.compile(r"<turn-context>.*?</turn-context>", re.DOTALL)
SCRUB = [
    (re.compile(r"sk-[A-Za-z0-9_-]{20,}"), "[REDACTED:API_KEY]"),
    (re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{30,}\b"), "[REDACTED:TELEGRAM_TOKEN]"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"), "[REDACTED:GITHUB_TOKEN]"),
    (re.compile(r"\bnfp_[A-Za-z0-9]{30,}\b"), "[REDACTED:NETLIFY_TOKEN]"),
]


def scrub(text: str) -> tuple[str, int]:
    n = 0
    for pat, tag in SCRUB:
        text, k = pat.subn(tag, text)
        n += k
    return text, n


def owner_of(row) -> str | None:
    """Who opened this window, as far as the store can say. A title wins; a working directory is next."""
    m = NAME_IN_TITLE.match(row["name"] or "")
    if m:
        return ALIASES.get(m.group(1).lower(), m.group(1).lower())
    wd = row["working_dir"] or ""
    for name, folder in MEMBERS.items():
        if f"/{folder}" in wd:
            return name
    return None


def connect():
    if not DB.exists():
        sys.exit(f"no sessions database at {DB}")
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=10)
    con.row_factory = sqlite3.Row
    return con


def rows(con, limit=200):
    return con.execute(
        "select id, name, provider_name, model_config_json, created_at, updated_at,"
        " accumulated_total_tokens, working_dir from sessions order by updated_at desc limit ?",
        (limit,),
    ).fetchall()


def model_of(row):
    try:
        cfg = json.loads(row["model_config_json"] or "{}")
        return cfg.get("model_name") or cfg.get("model") or "?"
    except json.JSONDecodeError:
        return "?"


def flatten(content_json: str) -> str:
    try:
        parts = json.loads(content_json) or []
    except json.JSONDecodeError:
        parts = [{"type": "text", "text": content_json}]
    out = []
    for p in parts:
        k = p.get("type")
        if k == "text":
            out.append(p.get("text", ""))
        elif k == "toolRequest":
            name = (p.get("toolCall") or {}).get("value", {}).get("name") or p.get("name")
            out.append(f"_[tool call: {name}]_")
        elif k == "toolResponse":
            out.append("_[tool result]_")
        elif k == "image":
            out.append("_[image]_")
    text = "\n\n".join(x for x in out if x and x.strip())
    return TURN_CONTEXT.sub("[turn context: identity and clock, omitted]", text).strip()


def land(con, member: str, sid: str, dry: bool) -> int:
    row = con.execute("select * from sessions where id=?", (sid,)).fetchone()
    if row is None:
        print(f"no session {sid}")
        return 2
    owner = owner_of(row)
    if owner == SACRED:
        print("refused: that is a Dawn window. Off-limits, unconditionally.")
        return 1
    if owner and owner != member:
        print(f"refused: that window is {owner}'s, not {member}'s.")
        return 1

    msgs = con.execute(
        "select role, content_json, timestamp from messages where session_id=? order by id", (sid,)
    ).fetchall()
    who = {member: member.capitalize(), "user": "Founder",
           "assistant": member.capitalize()}
    body = []
    for m in msgs:
        text = flatten(m["content_json"])
        if not text:
            continue
        body.append(f"### {who.get(m['role'], m['role'])} — {m['timestamp']}\n\n{text}")

    out_dir = BOTS / MEMBERS[member] / "windows"
    slug = re.sub(r"[^a-z0-9]+", "-", (row["name"] or sid).lower()).strip("-")[:40] or "window"
    path = out_dir / f"{(row['created_at'] or '')[:10]}-{slug}.md"
    header = "\n".join([
        f"# Window transcript — {row['name'] or '(unnamed)'}", "",
        f"*Landed {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC by `scripts/window_land.py`. "
        "A window is a place a member answers; this is where the answer stays.*", "",
        "| | |", "|---|---|",
        f"| session | `{row['id']}` |",
        f"| member | {member} |",
        f"| provider / model | {row['provider_name']} / {model_of(row)} |",
        f"| opened | {row['created_at']} |",
        f"| last message | {row['updated_at']} |",
        f"| messages | {len(msgs)} |",
        f"| tokens | {row['accumulated_total_tokens'] or '?'} |", "",
        "Thinking aside, this is what was said. Thinking blocks are dropped: they are the member's "
        "working, not the member's answer. Credential-shaped strings are replaced, by pattern, so a "
        "key that has since been rotated is caught too.", "", "---", "",
    ])
    text, scrubbed = scrub(header + "\n\n".join(body) + "\n")

    if dry:
        print(text[:1500] + ("\n…" if len(text) > 1500 else ""))
        return 0
    out_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

    index = out_dir / "INDEX.md"
    head = ("# Windows landed\n\n*Written by `scripts/window_land.py`. One row per window, rewritten in "
            "place, so this file never grows a duplicate.*\n\n"
            "| last landed | window | session | messages | file |\n|---|---|---|---|---|\n")
    table = {}
    if index.exists():
        for line in index.read_text(encoding="utf-8").splitlines():
            if line.startswith("| 20") and line.count("|") == 6:
                table[line.split("|")[3].strip()] = line
    table[f" `{sid}` "] = (f"| {datetime.now(timezone.utc):%Y-%m-%d %H:%M} | {row['name']} | `{sid}` "
                          f"| {len(msgs)} | [{path.name}]({path.name}) |")
    index.write_text(head + "\n".join(table[k] for k in sorted(table)) + "\n", encoding="utf-8")

    print(f"landed {len(msgs)} messages -> {path}"
          + (f"  ({scrubbed} credential-shaped strings replaced)" if scrubbed else ""))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("session", nargs="?")
    ap.add_argument("--member", required=True)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--mine", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    member = ALIASES.get(a.member.lower(), a.member.lower())
    if member not in MEMBERS:
        ap.error(f"unknown member {a.member!r}; known: {', '.join(sorted(MEMBERS))}")
    if not (BOTS / MEMBERS[member]).is_dir():
        ap.error(f"no folder {BOTS / MEMBERS[member]}")

    con = connect()
    if a.list or a.mine:
        mine = []
        for r in rows(con):
            o = owner_of(r)
            tag = "DAWN" if o == SACRED else (o or "?")
            print(f"{r['id']:<14} {r['updated_at']} {tag:<8} {r['provider_name']:<18} "
                  f"{model_of(r):<24} {r['name']}")
            if o == member:
                mine.append(r["id"])
        if a.mine:
            rc = 0
            for sid in mine:
                rc |= land(con, member, sid, a.dry_run)
            return rc
        return 0
    if not a.session:
        ap.error("give a session id, or --list / --mine")
    return land(con, member, a.session, a.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
