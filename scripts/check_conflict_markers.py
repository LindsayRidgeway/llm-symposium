#!/usr/bin/env python3
"""Find git conflict markers left in a working tree, before they are landed.

Written 2026-10-11 (Dmitri). On 2026-10-11 a run's diff was landed *with its
conflict markers still in it*: `channels/risks.md` and `channels/reject-queue.md`
reached `main` carrying `<<<<<<< ours` / `=======` / `>>>>>>> theirs` (commit
`f48356e3`, "land(wake): work from run 20261011T144432Z-bf0069ec"). The two files
were then corrupt for every reader — and for every script that parses them
(`scripts/reject_queue_sweep.py` counts `reviewed:` lines; `scripts/sweep_risks.py`
moves table rows). Nothing in the tree checked for the marker class, so nothing
refused the landing. This is the check.

**Why it is narrow.** The commons is full of lines that *look* like a marker but
are not: the `================` ruled dividers in the manual-transcription log, and
`|---|---|` Markdown table rules. A detector that fires on those is worse than none,
so this matches git's own syntax exactly — seven of the character at column 0,
followed by a space or end-of-line (a label may follow), plus the bare seven-equals
separator and the diff3 `|||||||` base row.

Usage:
    python3 scripts/check_conflict_markers.py            # scan git-tracked files
    python3 scripts/check_conflict_markers.py PATH ...   # scan explicit paths

Exit status 0 when clean, 1 when any marker is found. Prints `path:line: <marker>`
for each, so the line to delete or resolve is named.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# git writes every marker at column 0. Require 7 of the char then a space or EOL,
# which excludes 8+ char art/rules (`========`) and table separators (`|----|`).
_START = re.compile(r"^<{7}(?: .*)?$")
_BASE = re.compile(r"^\|{7}(?: .*)?$")  # diff3 "||||||| base" row
_SEP = re.compile(r"^={7}$")
_END = re.compile(r"^>{7}(?: .*)?$")

_MARKERS = (
    ("<<<<<<<", _START),
    ("|||||||", _BASE),
    ("=======", _SEP),
    (">>>>>>>", _END),
)


def markers_in_text(text: str) -> list[tuple[int, str]]:
    """Return 1-based (line, marker) for every conflict marker in *text*."""
    found: list[tuple[int, str]] = []
    for i, line in enumerate(text.splitlines(), start=1):
        for label, rx in _MARKERS:
            if rx.match(line):
                found.append((i, label))
                break
    return found


def _read_text(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in data:  # binary; markers cannot be meaningful
        return None
    return data.decode("utf-8", errors="replace")


def tracked_files(root: Path) -> list[Path]:
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        capture_output=True, text=True, check=True,
    ).stdout
    return [root / name for name in out.split("\0") if name]


def scan(paths: list[Path], root: Path) -> dict[str, list[tuple[int, str]]]:
    hits: dict[str, list[tuple[int, str]]] = {}
    for path in paths:
        text = _read_text(path)
        if text is None:
            continue
        found = markers_in_text(text)
        if found:
            try:
                rel = str(path.relative_to(root))
            except ValueError:
                rel = str(path)
            hits[rel] = found
    return hits


def main(argv: list[str]) -> int:
    if argv:
        paths = [Path(a) for a in argv]
    else:
        paths = tracked_files(ROOT)
    hits = scan(paths, ROOT)
    if not hits:
        print("clean: no conflict markers in %d file(s)" % len(paths))
        return 0
    total = sum(len(v) for v in hits.values())
    for rel in sorted(hits):
        for line, label in hits[rel]:
            print(f"{rel}:{line}: {label}")
    print(f"\nFAIL: {total} conflict marker(s) in {len(hits)} file(s)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
