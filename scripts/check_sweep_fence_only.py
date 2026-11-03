#!/usr/bin/env python3
"""Refuse to let a scheduled job commit a change to channels/tasks.md outside the sweep fence.

Why this exists (2026-11-02). The channel poll stages all of `channels/` and commits it, twelve
times a day. `scripts/sweep_risks.py` used to rebuild `channels/tasks.md` wholesale, so each of
those commits could carry the deletion of every section below the Open Risks heading — with no
conflict, no failing test, and a message about mail and telegram. Measured: 53,793 characters of the
live file were inside the region it rewrote.

The sweep now owns a fenced block and nothing else, and this is the belt to that braces: whatever the
sweep does in future, **nothing a scheduled job commits to tasks.md may remove a line that was
outside the fence.**

Usage:
  python3 scripts/check_sweep_fence_only.py                 # HEAD vs the staged copy
  python3 scripts/check_sweep_fence_only.py --after FILE    # a working-tree file vs HEAD
Exit 0 means the staged change is confined to the fence, or the file is untouched.
"""
from __future__ import annotations

import argparse
import collections
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = "channels/tasks.md"
BEGIN = "<!-- sweep-risks:begin -->"
END = "<!-- sweep-risks:end -->"


def git(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)


def outside_fence(text: str) -> list[str]:
    """The file's lines that the sweep does not own. Blank lines are ignored: they move freely."""
    i, j = text.find(BEGIN), text.find(END)
    body = text if not (0 <= i < j) else text[:i] + text[j + len(END):]
    return [l.rstrip() for l in body.splitlines() if l.strip()]


def removed_lines(before: str, after: str) -> list[str]:
    """Lines present outside the fence before, and fewer times outside it after."""
    had = collections.Counter(outside_fence(before))
    has = collections.Counter(outside_fence(after))
    return sorted((had - has).elements())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--after", help="compare HEAD against this working-tree file instead of the index")
    args = ap.parse_args()

    head = git("show", "HEAD:%s" % TARGET)
    if head.returncode != 0:
        print("sweep-fence: %s is not in HEAD; nothing to guard" % TARGET)
        return 0
    if args.after:
        staged = Path(args.after).read_text(encoding="utf-8")
        where = args.after
    else:
        s = git("show", ":%s" % TARGET)
        if s.returncode != 0:
            print("sweep-fence: %s is not staged; nothing to guard" % TARGET)
            return 0
        staged = s.stdout
        where = "the index"

    if staged == head.stdout:
        return 0
    lost = removed_lines(head.stdout, staged)
    if not lost:
        print("sweep-fence: the change to %s is confined to the fenced risk block" % TARGET)
        return 0
    print("sweep-fence: REFUSED — %d line(s) outside the sweep fence would be removed from %s in %s:"
          % (len(lost), TARGET, where))
    for line in lost[:12]:
        print("  - %s" % line[:160])
    if len(lost) > 12:
        print("  … and %d more" % (len(lost) - 12))
    print("sweep-fence: a scheduled job may only rewrite what is between %s and %s. If this removal is"
          % (BEGIN, END))
    print("sweep-fence: intended, it belongs in a named commit by a person or a wake, not a poll.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
