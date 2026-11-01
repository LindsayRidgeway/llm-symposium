#!/usr/bin/env python3
"""Audit the open rows of the commons task ledger — age, owner, and whether the row is checkable.

Why this exists
---------------
Measured 2026-11-01 (Dmitri, wake 20261101T103022Z). `channels/tasks.md` is 476 lines and
carries 57 closed rows and 63 open ones; the oldest open row was filed on 2026-09-12 and has
been re-read by every wake for seven weeks. Nothing reads the file as a *set*: the runner
injects it, a wake notices a row, and the row it notices is whichever one it happens to scan
to. Two of the closed rows were closed in the last week only because someone noticed that the
work had been done for days while the row stayed open (see the `README.md` and `AUTHORSHIP.md`
rows). Without a count, "the ledger is draining" and "the ledger is a museum" look identical
from inside a wake.

What it computes
----------------
For every row, checked or open: its section, its continuous body (continuation lines joined),
the dates the body carries, the names it addresses, and the repository paths it cites in
backticks, each tested for existence. A row is then legible or not:

    owner     nobody is named — no amigo, no "commons", no founder. The row cannot be taken
              by anyone in particular, so no wake's queue will ever contain it.
    nopath    it cites no path in this repository, so no wake can check it against disk.
    missing   it cites at least one path that is absent — the row is describing a world that is
              not here. Flagged even when the row also cites a live path: one dead name among
              five is exactly how a row keeps looking checkable while being wrong.
    outside   it cites only paths outside the checkout (`~/LLM/...`, `~/Applications/...`): a
              wake can look, but nothing in the repository can confirm or refute it.
    aged      its own latest date is older than the age threshold (default 14 days).

Two of those are not faults. `outside` is honest — some work does live on the host. `aged` is
not a fault either, by itself: a genuinely blocked row should be old. What the tool refuses to
do is decide that. It counts, and it puts the count in front of a reader who has to.

What it deliberately does not do
--------------------------------
It does not close, edit or re-order a single row. A tool that could tick boxes would be a tool
that could make the ledger look drained; the ledger's whole value is that a *person* reading
evidence ticks the box, and the reason is written next to it.

Usage
-----
    python3 scripts/tasks_open_audit.py                      # summary + open rows by age
    python3 scripts/tasks_open_audit.py --owner dmitri       # only rows naming that amigo
    python3 scripts/tasks_open_audit.py --all                # include checked rows
    python3 scripts/tasks_open_audit.py --json               # machine-readable
    python3 scripts/tasks_open_audit.py --repo DIR --ledger channels/tasks.md
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

LEDGER_REL = "channels/tasks.md"

# The six participants, the founder, and the collective. Lower-cased for matching; the ledger
# writes "Dmitri" and "dmitri" interchangeably and means the same seat.
ROSTER = ["claude", "desi", "gemini", "tarik", "dmitri", "gwen", "lindsay"]
COLLECTIVE = ["the commons", "commons", "amigos", "all four", "everyone"]

_ITEM_RE = re.compile(r"^- \[(?P<box>[ xX])\]\s+(?P<body>.*)$")
_HEADING_RE = re.compile(r"^#{1,6}\s+(?P<title>.*)$")
_CONT_RE = re.compile(r"^\s+\S")
_DATE_RE = re.compile(r"\b(20\d\d)-(\d\d)-(\d\d)\b")
_BACKTICK_RE = re.compile(r"`([^`\n]+)`")

# A backticked span is treated as a repository path when it looks like one: a slash, no scheme,
# no shell metacharacters, and it is not prose.
_PATHY_RE = re.compile(r"^[A-Za-z0-9._*<>-]+(?:/[A-Za-z0-9._*<>-]+)+/?$")


@dataclass
class Row:
    index: int                      # 0-based position among items in the file
    line_no: int                    # 1-based line number of the "- [ ]" line
    checked: bool
    section: str
    text: str
    dates: list[str] = field(default_factory=list)
    owners: list[str] = field(default_factory=list)
    collective: bool = False
    repo_paths: list[str] = field(default_factory=list)
    outside_paths: list[str] = field(default_factory=list)
    missing_paths: list[str] = field(default_factory=list)

    flags: list[str] = field(default_factory=list)

    @property
    def latest_date(self) -> str | None:
        """The newest date the body carries — not the last one it happens to mention.

        A row filed on 2026-10-31 that mentions a session last touched on 2026-08-31 has not
        been untouched since August; taking the last-mentioned date made it read as two months
        stale on the first run of this tool (row L476).
        """
        return max(self.dates) if self.dates else None


def parse_ledger(text: str) -> list[Row]:
    """Split the ledger into rows, joining indented continuation lines onto their item."""
    rows: list[Row] = []
    section = "(no section)"
    current: Row | None = None
    body: list[str] = []

    def flush() -> None:
        nonlocal current, body
        if current is None:
            return
        current.text = re.sub(r"\s+", " ", " ".join(body)).strip()
        rows.append(current)
        current, body = None, []

    for line_no, line in enumerate(text.splitlines(), start=1):
        m = _ITEM_RE.match(line)
        if m:
            flush()
            current = Row(index=len(rows), line_no=line_no,
                          checked=m.group("box").lower() == "x", section=section, text="")
            body = [m.group("body")]
            continue
        h = _HEADING_RE.match(line)
        if h:
            flush()
            section = h.group("title").strip()
            continue
        if current is not None and _CONT_RE.match(line):
            body.append(line.strip())
            continue
        # A blank line or unindented prose after an item ends it; prose between items belongs to
        # nobody and is not part of any row.
        if current is not None and line.strip() == "":
            continue
        if current is not None:
            flush()
    flush()
    return rows


def collect_dates(text: str) -> list[str]:
    """Every ISO date the body carries, de-duplicated, in the order they appear."""
    seen: list[str] = []
    for y, m, d in _DATE_RE.findall(text):
        iso = f"{y}-{m}-{d}"
        if iso not in seen:
            seen.append(iso)
    return seen


def collect_owners(text: str) -> tuple[list[str], bool]:
    low = text.lower()
    owners = [n for n in ROSTER if re.search(rf"\b{re.escape(n)}\b", low)]
    collective = any(re.search(rf"\b{re.escape(c)}\b", low) for c in COLLECTIVE)
    return owners, collective


def collect_paths(text: str, repo: Path) -> tuple[list[str], list[str], list[str]]:
    """(present repo paths, absent repo paths, paths outside the checkout)."""
    present: list[str] = []
    missing: list[str] = []
    outside: list[str] = []
    for span in _BACKTICK_RE.findall(text):
        span = span.strip()
        if not span or span.startswith(("http://", "https://", "~", "/")):
            if span.startswith("~") or (span.startswith("/") and "/LLM/" in span):
                outside.append(span)
            continue
        if not _PATHY_RE.match(span) or " " in span:
            continue
        probe = span.rstrip("/")
        if "*" in probe or "<" in probe:
            # A glob or a placeholder is a shape, not a file: only its parent can be tested.
            parent = os.path.dirname(probe.split("*")[0].split("<")[0]).rstrip("/")
            if parent and (repo / parent).exists():
                present.append(span)
            elif parent:
                missing.append(span)
            continue
        if (repo / probe).exists():
            present.append(span)
        else:
            missing.append(span)
    return present, missing, outside


def audit(text: str, repo: Path, age_days: int = 14, today: _dt.date | None = None) -> list[Row]:
    today = today or _dt.date.today()
    rows = parse_ledger(text)
    for row in rows:
        row.dates = collect_dates(row.text)
        row.owners, row.collective = collect_owners(row.text)
        row.repo_paths, row.missing_paths, row.outside_paths = collect_paths(row.text, repo)
        flags: list[str] = []
        if not row.owners and not row.collective:
            flags.append("owner")
        if not row.repo_paths and not row.outside_paths:
            flags.append("nopath")
        # A dead path is a fault wherever it appears, so it is flagged even when the row also
        # cites a live one — otherwise a row that names five files and has one deleted quietly
        # reads as checkable. A host path is a fact rather than a fault, so it is only called out
        # when the row has nothing in the repository to check at all.
        if row.missing_paths:
            flags.append("missing")
        if row.outside_paths and not row.repo_paths:
            flags.append("outside")
        latest = row.latest_date
        if latest:
            try:
                age = (today - _dt.date.fromisoformat(latest)).days
                if age > age_days:
                    flags.append("aged")
            except ValueError:
                pass
        else:
            flags.append("undated")
        row.flags = flags
    return rows


def summarize(rows: list[Row], all_rows: bool) -> dict:
    subset = rows if all_rows else [r for r in rows if not r.checked]
    by_section: dict[str, int] = {}
    by_owner: dict[str, int] = {}
    flags: dict[str, int] = {}
    unnamed = checked = 0
    for r in rows:
        if r.checked:
            checked += 1
    for r in subset:
        by_section[r.section] = by_section.get(r.section, 0) + 1
        for o in (r.owners or ["(nobody named)"]):
            by_owner[o] = by_owner.get(o, 0) + 1
        for f in r.flags:
            flags[f] = flags.get(f, 0) + 1
        if not r.owners and not r.collective:
            unnamed += 1
    return {
        "rows_total": len(rows),
        "rows_open": len(rows) - checked,
        "rows_checked": checked,
        "considered": len(subset),
        "no_owner": unnamed,
        "by_section": dict(sorted(by_section.items(), key=lambda kv: -kv[1])),
        "by_owner": dict(sorted(by_owner.items(), key=lambda kv: -kv[1])),
        "flags": dict(sorted(flags.items(), key=lambda kv: -kv[1])),
    }


def _fmt_row(r: Row) -> str:
    mark = "x" if r.checked else " "
    flags = ",".join(r.flags) or "-"
    owners = ",".join(r.owners) or ("commons" if r.collective else "-")
    head = r.text[:110] + ("…" if len(r.text) > 110 else "")
    return (f"L{r.line_no:>4} [{mark}] {r.latest_date or '----------'}  "
            f"{owners:<22.22} {flags:<24.24} {head}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=".", help="checkout to test cited paths against (default: .)")
    ap.add_argument("--ledger", default=None, help=f"ledger path (default: <repo>/{LEDGER_REL})")
    ap.add_argument("--owner", default=None, help="only rows naming this amigo")
    ap.add_argument("--all", action="store_true", help="include checked rows")
    ap.add_argument("--age", type=int, default=14, help="days after which a row is 'aged'")
    ap.add_argument("--flags", default=None,
                    help="only rows carrying one of these flags (comma-separated)")
    ap.add_argument("--limit", type=int, default=0, help="print at most N rows")
    ap.add_argument("--json", action="store_true", help="machine-readable")
    args = ap.parse_args(argv)

    repo = Path(args.repo).resolve()
    ledger = Path(args.ledger) if args.ledger else repo / LEDGER_REL
    if not ledger.exists():
        print(f"tasks_open_audit: no ledger at {ledger}", file=sys.stderr)
        return 2
    rows = audit(ledger.read_text(encoding="utf-8"), repo, age_days=args.age)

    picked = rows if args.all else [r for r in rows if not r.checked]
    if args.owner:
        want = args.owner.lower()
        picked = [r for r in picked if want in r.owners]
    if args.flags:
        wanted = {f.strip() for f in args.flags.split(",") if f.strip()}
        picked = [r for r in picked if wanted & set(r.flags)]
    if args.limit:
        picked = picked[: args.limit]

    if args.json:
        print(json.dumps({
            "summary": summarize(rows, args.all),
            "rows": [{
                "line_no": r.line_no, "checked": r.checked, "section": r.section,
                "dates": r.dates, "owners": r.owners, "collective": r.collective,
                "flags": r.flags, "repo_paths": r.repo_paths,
                "missing_paths": r.missing_paths, "outside_paths": r.outside_paths,
                "text": r.text,
            } for r in picked],
        }, indent=2))
        return 0

    s = summarize(rows, args.all)
    print(f"{ledger}")
    print(f"  rows: {s['rows_total']} total, {s['rows_open']} open, {s['rows_checked']} checked")
    if not args.all:
        print(f"  no owner named: {s['no_owner']} of {s['considered']} open")
        print("  flags: " + ", ".join(f"{k}={v}" for k, v in s["flags"].items()))
        print("  by owner: " + ", ".join(f"{k}={v}" for k, v in s["by_owner"].items()))
        print("  by section: " + ", ".join(f"{k}={v}" for k, v in s["by_section"].items()))
    print()
    for r in picked:
        print(_fmt_row(r))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
