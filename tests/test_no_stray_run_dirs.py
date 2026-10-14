#!/usr/bin/env python3
"""Repo-root hygiene: a wake must never commit its own run directory.

Origin (2026-10-14): the wake of run `20261014T085323Z-2408b85d` wrote its
report to a path *relative to its working directory* — which is the repository
checkout — instead of to the absolute run-directory path it was given. The
landing then carried the new file `20261014T085323Z-2408b85d/report.txt`, so a
directory named exactly like a run id reached `main` (commit `ebf8d47a`) with
the report inside it.

A run directory (`report.txt`, `changes.patch`, `worker.jsonl.gz`) belongs
beside the checkout, at `<bot>/tick-state/runs/<id>/`, never inside it. Inside
the tree it is not art but litter: every reader and every file listing has to
step over it, and it is the only reason this repository's root has ever held a
name that is not a project name.

This test fails if any top-level entry of the repository is named like a wake
run id (`YYYYMMDDThhmmssZ-<8 hex>`). Offline; no network; no git required.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUN_ID = re.compile(r"^\d{8}T\d{6}Z-[0-9a-f]{8}$")


def stray_run_dirs(root: Path = REPO) -> list:
    """Top-level entries of `root` whose name is a wake run id."""
    return sorted(p.name for p in root.iterdir() if RUN_ID.match(p.name))


def main() -> int:
    found = stray_run_dirs()
    for name in found:
        print("FAIL stray wake run directory at repo root: %s/" % name)
    if found:
        print(
            "A run directory (report.txt, changes.patch, worker.jsonl.gz) belongs "
            "beside the checkout at <bot>/tick-state/runs/<id>/, not inside it."
        )
        return 1
    print("PASS repo root holds no stray wake run directory")
    return 0


if __name__ == "__main__":
    sys.exit(main())
