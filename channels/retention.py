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

DRY-RUN BY DEFAULT (2026-10-06, Dmitri). The command line deleted files with no
`--apply` until today: run bare — as a reviewer or a bot would run it to see what
it does — it removed 259 tracked files in a checkout and reported only a count.
Its sibling `scripts/enforce_retention.py` has always been dry-run unless
`--apply` is passed, on the stated principle that "a mistake is never silently
destructive"; two scripts with the same owner, the same job and opposite
conventions is a hazard, and the convention that survives is the safe one. So:
the CLI now prints what it *would* remove and deletes nothing until `--apply` is
given. `prune_raw()` keeps deleting by default, so callers that already ask it to
prune — the tests, and any grouped housekeeping pass — are unchanged; only the
unattended-caller surface (the command line) changed. A housekeeping call site
that means to enforce retention must pass `--apply`; if it forgets, it degrades
to a dry run and prints so, rather than trimming the record.
"""
from __future__ import annotations

import datetime as _dt
import os
import re
import sys
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


def prune_raw(now: float | None = None, apply: bool = True) -> list[str]:
    """List (and, unless apply is False, remove) raw artifacts past the horizon.

    Returns the repo-relative paths either way, so a dry run reports exactly what
    an apply would do. `apply=False` is read-only: it never unlinks.
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
            if apply:
                path.unlink()
            removed.append(rel)
    return removed


USAGE = """usage: retention.py [--apply] [--dry-run]

Bound the raw channel logs (channels/inbound/, channels/telegram/).

  (no flag)   dry run: print what is past the horizon, delete nothing
  --apply     delete the artifacts listed by the dry run
  --dry-run   the default, stated explicitly

Retention is CHANNEL_RAW_RETENTION_DAYS days (default 14). Files marked
"Retention: keep" / "Preserve: keep" / "Historical: keep" / "Governance: keep",
and READMEs, are never touched.
"""


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    unknown = [a for a in argv if a not in ("--apply", "--dry-run", "-h", "--help")]
    if unknown:
        print(f"retention.py: unknown argument(s): {' '.join(unknown)}", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return 2
    if "-h" in argv or "--help" in argv:
        print(USAGE)
        return 0
    apply = "--apply" in argv
    if apply and "--dry-run" in argv:
        print("retention.py: --apply and --dry-run are mutually exclusive", file=sys.stderr)
        return 2

    removed = prune_raw(apply=apply)
    if not removed:
        print(f"Channel retention: no raw artifacts past the horizon (retention {RETENTION_DAYS} days)")
        return 0
    print(f"Channel retention: {'pruned' if apply else 'would prune'} {len(removed)} raw artifact(s):")
    for rel in removed:
        print(f"  {rel}")
    if not apply:
        print("DRY-RUN — nothing was deleted. Re-run with --apply to enforce retention.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
