#!/usr/bin/env python3
# Owner: Desi
"""Bounded retention for raw channel artifacts.

The commons needs sensory channels, not an infinite archive of every raw email
and Telegram exchange. This script implements the conservative first stage:

- keep recent raw inbound files for CHANNEL_RAW_RETENTION_DAYS (default 14);
- never delete README/canonical files;
- never delete files marked with an explicit retention marker;
- preserve compact memory in channels/channel-digest.md (written at intake).

The script is safe in fresh/forked repos and uses stdlib only.
"""
from __future__ import annotations

import datetime as _dt
import os
import re
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIRS = (
    REPO_ROOT / "channels" / "inbound",
    REPO_ROOT / "channels" / "telegram",
)
RETENTION_DAYS = int(os.environ.get("CHANNEL_RAW_RETENTION_DAYS", "14"))
PRESERVE_RE = re.compile(r"^(Retention|Preserve|Historical|Governance)\s*:\s*(keep|preserve|yes|true)\s*$", re.I | re.M)


def should_preserve(path: Path) -> bool:
    if path.name.startswith("README") or path.name.startswith(".gitkeep"):
        return True
    try:
        text = path.read_text(encoding="utf-8", errors="replace")[:4000]
    except Exception:
        return True
    return bool(PRESERVE_RE.search(text))


def _artifact_time(path: Path) -> float:
    """Best-effort artifact timestamp.

    GitHub checkouts refresh mtimes, so retention cannot rely only on filesystem
    time. Prefer leading YYYY-MM-DD in channel filenames; fall back to mtime.
    """
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", path.name)
    if m:
        dt = _dt.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=_dt.timezone.utc)
        return dt.timestamp()
    return path.stat().st_mtime


def prune_raw(now: float | None = None, dry: bool = False) -> list[str]:
    """List (and unless `dry`, delete) raw channel artifacts older than the window.

    `dry` was added 2026-09-26 so the local housekeeping entrypoint
    (`scripts/retention_pass.py`) can run this pass in its default dry-run mode. The
    default `dry=False` is the old behaviour, so every existing caller is unchanged.
    """
    now = time.time() if now is None else now
    cutoff = now - (RETENTION_DAYS * 86400)
    removed: list[str] = []
    for raw_dir in RAW_DIRS:
        if not raw_dir.exists():
            continue
        for path in raw_dir.rglob("*.md"):
            if should_preserve(path):
                continue
            if _artifact_time(path) >= cutoff:
                continue
            rel = path.relative_to(REPO_ROOT).as_posix()
            if not dry:
                path.unlink()
            removed.append(rel)
    return removed


def main() -> int:
    import sys

    dry = "--dry-run" in sys.argv
    verb = "would prune" if dry else "pruned"
    removed = prune_raw(dry=dry)
    print(f"Channel retention: {verb} {len(removed)} raw artifact(s) "
          f"(window {RETENTION_DAYS} days{', dry run' if dry else ''})")
    for rel in removed:
        print(f"  {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
