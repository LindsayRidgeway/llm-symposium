#!/usr/bin/env python3
"""Resolve an append-only ledger's merge conflict by **union**, not by choosing a side.

Written 2026-10-18 (Desi), after the defect was measured on `main`.

**What happened.** `channels/items.jsonl` is an append-only log that more than one
writer appends to: the ledger (`channels/item_ledger.py`) appends state changes, and
every landing that touches work appends its own line. So two branches almost always
add *different* lines at the *same* end of the file, and git reports a "both added"
conflict — the one conflict kind where picking a side is always wrong. On
2026-10-18 commit `4a921369` ("log(codex): record counterpoint range wake
codex-20261018T080408Z-db069f38") resolved such a conflict by keeping one side: the
two `desi` entries filed `2026-10-17T12:00:05Z` (items `20261017T050200Z-2f950a17`
and `20261017T030159Z-3efde3c6`, both assigned to `dmitri` for review) were dropped,
two `codex` entries kept, and the three marker lines were left in the file.

**What it cost, measured.** `channels/item_ledger.py` prints
`item_ledger: skipping unreadable line 1647` (and 1650, 1653) and then *continues*,
so the ledger did not fail — it quietly under-reported. `tests/test_conflict_markers.py`
(the guard Dmitri wrote for exactly this class) went red on its load-bearing case,
and the lander refused run `20261018T110600Z-630f5487`'s landing for it. Two review
items existed in the world, one of them was reviewed (`dmitri-bot` run
`20261017T231430Z-2ab19e80` closes `20261017T030159Z-3efde3c6` as done), and neither
could be seen by the ledger that was supposed to route them.

**The rule this tool applies.** In a both-added conflict on an append-only log, the
correct resolution is the union of the two sides in file order, with exact
duplicates dropped. A line present on one side only is a line somebody wrote; only a
human can say a written line should not exist, and this tool never decides that.

**What it does not do.** It does not merge a *modified* line (an entry whose state
changed on both sides), and it does not validate the resulting log's semantics. It
prints every non-JSON line it carried through, so a resolution that leaves a real
problem visible stays visible.

Usage:
    python3 scripts/repair_ledger_conflicts.py                 # dry run, prints what it would do
    python3 scripts/repair_ledger_conflicts.py --write         # rewrite channels/items.jsonl
    python3 scripts/repair_ledger_conflicts.py --check PATH    # exit 1 if markers remain

Exit status: 0 clean / repaired, 1 markers still present (with `--check`) or an
unresolvable block was found (diff3 base row, or a marker left dangling).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "channels" / "items.jsonl"

# git's own syntax, exactly: seven of the character at column 0, then a space or EOL.
_START = re.compile(r"^<{7}(?: .*)?$")
_BASE = re.compile(r"^\|{7}(?: .*)?$")  # diff3 "||||||| base" row — not ours to resolve
_SEP = re.compile(r"^={7}$")
_END = re.compile(r"^>{7}(?: .*)?$")


def _canonical(line: str) -> str:
    """Identity of a ledger line: its parsed form when it parses, else the raw text.

    Two sides can carry the same entry with different key order or spacing; a union
    that compares raw bytes would keep both and duplicate the record. Comparing the
    parsed dict (sorted keys) keeps one.
    """
    stripped = line.strip()
    if not stripped:
        return ""
    try:
        return json.dumps(json.loads(stripped), sort_keys=True)
    except Exception:
        return stripped


def find_conflicts(lines: list[str]) -> list[tuple[int, int, list[str], list[str]]]:
    """Return (start, end, ours, theirs) for each conflict block, 0-based inclusive.

    `start` is the `<<<<<<<` row, `end` the `>>>>>>>` row. A same-file conflict
    cannot nest, so a single scan is enough.
    """
    blocks: list[tuple[int, int, list[str], list[str]]] = []
    i = 0
    while i < len(lines):
        if not _START.match(lines[i].rstrip("\n")):
            i += 1
            continue
        start = i
        ours: list[str] = []
        theirs: list[str] = []
        side = ours
        i += 1
        ended = False
        while i < len(lines):
            row = lines[i].rstrip("\n")
            if _BASE.match(row):
                raise ValueError(f"diff3 base row at line {i + 1}: not resolvable by union")
            if _SEP.match(row):
                side = theirs
                i += 1
                continue
            if _END.match(row):
                ended = True
                break
            side.append(lines[i])
            i += 1
        if not ended:
            raise ValueError(f"unterminated conflict starting at line {start + 1}")
        blocks.append((start, i, ours, theirs))
        i += 1
    return blocks


def union(ours: list[str], theirs: list[str]) -> tuple[list[str], int]:
    """Ours then theirs, in order, exact duplicates dropped. Returns (lines, dropped)."""
    seen: set[str] = set()
    out: list[str] = []
    dropped = 0
    for line in list(ours) + list(theirs):
        key = _canonical(line)
        if key and key in seen:
            dropped += 1
            continue
        seen.add(key)
        out.append(line if line.endswith("\n") else line + "\n")
    return out, dropped


def repair_text(text: str) -> tuple[str, dict]:
    lines = text.splitlines(keepends=True)
    blocks = find_conflicts(lines)
    stats = {
        "blocks": len(blocks),
        "ours": 0,
        "theirs": 0,
        "duplicates_dropped": 0,
        "non_json": [],
        "lines_before": len(lines),
    }
    if not blocks:
        stats["lines_after"] = len(lines)
        return text, stats

    out: list[str] = []
    cursor = 0
    for start, end, ours, theirs in blocks:
        out.extend(lines[cursor:start])
        merged, dropped = union(ours, theirs)
        stats["ours"] += len(ours)
        stats["theirs"] += len(theirs)
        stats["duplicates_dropped"] += dropped
        for line in merged:
            try:
                json.loads(line)
            except Exception:
                stats["non_json"].append(line.rstrip("\n")[:120])
        out.extend(merged)
        cursor = end + 1
    out.extend(lines[cursor:])
    stats["lines_after"] = len(out)
    return "".join(out), stats


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", nargs="?", default=str(DEFAULT_LEDGER))
    ap.add_argument("--write", action="store_true", help="rewrite the file in place")
    ap.add_argument("--check", action="store_true", help="exit 1 if markers remain")
    args = ap.parse_args(argv[1:])

    path = Path(args.path)
    if not path.exists():
        print(f"repair_ledger_conflicts: no such file: {path}", file=sys.stderr)
        return 1

    original = path.read_text(encoding="utf-8")
    try:
        repaired, stats = repair_text(original)
    except ValueError as exc:
        print(f"repair_ledger_conflicts: {exc}", file=sys.stderr)
        return 1

    if not stats["blocks"]:
        print(f"repair_ledger_conflicts: {path.name}: no conflict markers ({stats['lines_before']} lines)")
        return 0

    print(
        f"repair_ledger_conflicts: {path.name}: {stats['blocks']} conflict block(s) — "
        f"ours {stats['ours']}, theirs {stats['theirs']}, "
        f"duplicates dropped {stats['duplicates_dropped']}; "
        f"{stats['lines_before']} → {stats['lines_after']} lines"
    )
    if stats["non_json"]:
        print(f"  carried through {len(stats['non_json'])} line(s) that are not JSON:")
        for line in stats["non_json"]:
            print(f"    {line}")

    if args.write:
        path.write_text(repaired, encoding="utf-8")
        print(f"  written: {path}")
        return 0
    if args.check:
        return 1
    print("  dry run — pass --write to apply")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
