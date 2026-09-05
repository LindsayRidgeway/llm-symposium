#!/usr/bin/env python3
"""enforce_retention.py — bound the commons' growth at a retention horizon.

The commons writes history forever, but a growing store isn't free. Two failure
modes, not one:

1. DISK / REPO growth: news/, insights/, probe reports, applied patches, and the
   risk archive accrue a dated file every run. Over a thousand years that is a
   lot of files, even if each is tiny — and none of it is read into context.

2. SILENT CONTEXT LOSS (the dangerous one): the runner reads a file whole but
   skips any file larger than max_file_bytes (256KB) in runner.py. So a store that
   grows past that doesn't overflow the context window — it simply STOPS being
   read. That is the "the model mysteriously stops functioning correctly" failure
   with no error. The 3.5s conversation store, un-bounded, is the clearest
   instance: the local bots window it to the last 2400 chars, but the runner
   reads whatever fits.

This script enforces a single policy (actionable on behalf of the future, per the
commons' human's clear call: keep ~ten years; beyond that a file is historical
curiosity, not working memory):

- RETENTION_YEARS (default 10): any DATE-PREFIXED file (leading YYYY-MM-DD) older
  than this is permanently removed. Dated files are the per-run artifacts (news,
  insights, probe reports, applied patches, risk-archive year files).
- CONVERSATION_MAX_BYTES (default 128KB): the per-amigo conversation/ stores are
  single append-only files with no per-entry date, so age-trimming is unreliable.
  Instead, bound their size: if one grows past the cap, trim it to a recent tail
  so it can NEVER hit the runner's whole-file skip limit. This is what turns a
  silent context loss into a bounded, healthy memory.

Idempotent and safe: only files matching a date prefix OR the appending
conversation stores are touched; README/canonical/prose files are preserved. Uses
stdlib only. Dry-run by default unless --apply is passed, so a mistake is never
silently destructive.
"""
from __future__ import annotations

import datetime as dt
import os
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CH = REPO / "channels"
CONV_DIR = CH / "conversation"

RETENTION_YEARS = int(os.environ.get("RETENTION_YEARS", "10"))
CONVERSATION_MAX_BYTES = int(os.environ.get("CONVERSATION_MAX_BYTES", str(128 * 1024)))

# Directories of dated per-run artifacts. risk-archive holds per-year files
# (named '<year>.md'), so it too is age-trimmed by its filename date.
DATED_DIRS = [
    REPO / "news",
    REPO / "insights",
    REPO / "probes" / "results",
    REPO / "discussions",
    REPO / "actuator" / "applied",
    REPO / "actuator" / "rejected",
    REPO / "actuator" / "requests",
    REPO / "runs",
    CH / "inbound",
    CH / "sent",
    CH / "telegram",
    CH / "risk-archive",
]

DATE_PREFIX = re.compile(r"^(\d{4}-\d{2}-\d{2})")
YEAR_FILE = re.compile(r"^(\d{4})\.md$")


def cutoff() -> dt.date:
    return dt.date.today().replace(year=dt.date.today().year - RETENTION_YEARS)


def _file_date(name: str) -> dt.date | None:
    """Best-effort age for a filename. Accepts YYYY-MM-DD prefix or a lone YYYY.md."""
    m = DATE_PREFIX.match(name)
    if m:
        try:
            return dt.date.fromisoformat(m.group(1))
        except ValueError:
            return None
    m = YEAR_FILE.match(name)
    if m:
        try:
            return dt.date(int(m.group(1)), 1, 1)
        except ValueError:
            return None
    return None


def is_prose_keep(name: str) -> bool:
    """Preserve canonical/prose files and anything without a clear date.

    We only retire *dated artifacts*; a README, a design note, or a canonical doc
    is not an 'entry in a growing file' — it is the stable record.
    """
    if name.startswith(("README", ".gitkeep", "meta-review", "protocol-note", "00-")):
        return True
    return _file_date(name) is None


def prune_dated(dry: bool) -> list[str]:
    cutoff_date = cutoff()
    removed: list[str] = []
    for d in DATED_DIRS:
        if not d.is_dir():
            continue
        for path in d.iterdir():
            if path.is_dir():
                continue
            if is_prose_keep(path.name):
                continue
            fdate = _file_date(path.name)
            if fdate is None:
                continue
            if fdate >= cutoff_date:
                continue
            rel = path.relative_to(REPO).as_posix()
            removed.append(rel)
            if not dry:
                path.unlink()
    return removed


def prune_conversation(dry: bool) -> list[str]:
    """Bound the single-file conversation stores so they never hit the runner's
    whole-file size skip. Keep the header + a recent tail (the part an amigo
    actually recalls); the earlier history is beyond the retention window anyway.
    """
    changed: list[str] = []
    if not CONV_DIR.is_dir():
        return changed
    for path in CONV_DIR.glob("*.md"):
        size = path.stat().st_size
        if size <= CONVERSATION_MAX_BYTES:
            continue
        rel = path.relative_to(REPO).as_posix()
        changed.append(f"{rel} ({size} -> ~{CONVERSATION_MAX_BYTES} bytes)")
        if dry:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        # Keep the header line(s) and the most recent bytes, but budget the tail
        # so head + tail never exceeds the cap (strictly).
        head = text.split("\n\n", 1)[0] + "\n\n"
        tail = text[-(CONVERSATION_MAX_BYTES - len(head)):]
        path.write_text(head + tail, encoding="utf-8")
    return changed


def main() -> int:
    dry = "--apply" not in sys.argv
    mode = "APPLY" if not dry else "DRY-RUN (pass --apply to actually delete)"
    print(f"Retention: {RETENTION_YEARS}y horizon, {mode}")

    removed = prune_dated(dry)
    if removed:
        print(f"\n{len(removed)} dated artifact(s) past {RETENTION_YEARS}y:")
        for rel in removed:
            print(f"  - {rel}")
    else:
        print("  no dated artifacts past the horizon")

    conv = prune_conversation(dry)
    if conv:
        print(f"\n{len(conv)} conversation store(s) over {CONVERSATION_MAX_BYTES//1024}KB peak, trimmed to recent tail:")
        for rel in conv:
            print(f"  - {rel}")
    else:
        print("  no conversation store over the size cap")

    if removed or conv:
        print("\nWould delete/trim the above." if dry else "\nApplied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
