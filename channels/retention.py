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


def prune_raw(now: float | None = None) -> list[str]:
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
            path.unlink()
            removed.append(rel)
    return removed


def main() -> int:
    removed = prune_raw()
    if removed:
        print(f"Channel retention: pruned {len(removed)} raw artifact(s):")
        for rel in removed:
            print(f"  {rel}")
    else:
        print(f"Channel retention: no raw artifacts pruned (retention {RETENTION_DAYS} days)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
