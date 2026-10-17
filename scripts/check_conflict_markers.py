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
    python3 scripts/check_conflict_markers.py            # scan tracked + untracked files
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


# A marker block is never megabytes; a cap keeps the scan off a stray untracked blob that
# some checkout's `.gitignore` happens to miss. 2 MB was too low: it skipped
# `channels/channel-digest.md` (2.5 MB), an append log that is a real tracked text file and
# therefore a real place a conflicted merge can land. 20 MB reads every text artefact in
# this repository in well under a second; binaries are caught by the NUL test below, so the
# cap only protects against pathology, it is not a filter. Skipped files are named, never
# silently eaten -- see `scan()`.
MAX_BYTES = 20_000_000


def _ls_files(root: Path, *flags: str) -> list[Path]:
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", *flags],
        capture_output=True, text=True, check=True,
    ).stdout
    return [root / name for name in out.split("\0") if name]


def tracked_files(root: Path) -> list[Path]:
    """Files git knows about."""
    return _ls_files(root)


def untracked_files(root: Path) -> list[Path]:
    """Files git has never seen and would not ignore: what a landing is about to add.

    Added 2026-10-17 (Desi), on review of Tarik's recovery of this guard. The lander runs
    the suite *before* it commits (`land_runs.py`: `before = failing_tests()` ... `git apply`
    ... `after = failing_tests()` ... `git add` ... `git commit`), so a file this run
    **created** is still untracked at the moment this test looks at the tree. Scanning only
    `git ls-files` therefore caught the original f48356e3 case — markers inside files that
    were already on `main` — and could never catch the same corruption in a *new* file, which
    is how most artefacts arrive: a fresh report, a research note, a new script.

    It does not make the suite red on unrelated dirt: the lander grades *new* failures
    against a baseline taken before the patch, so an untracked conflicted file that was
    already lying there is in both sets and blocks nothing. `--exclude-standard` keeps
    `.gitignore` honoured, which is the only reason this is safe to point at a live checkout.
    """
    return _ls_files(root, "--others", "--exclude-standard")


def candidate_files(root: Path) -> list[Path]:
    """Every file the guard should read: tracked, plus about-to-be-tracked."""
    return tracked_files(root) + untracked_files(root)


def scan(paths: list[Path], root: Path,
         skipped: list[str] | None = None) -> dict[str, list[tuple[int, str]]]:
    """Markers found, keyed by repo-relative path.

    Files too large to be a marker block are skipped and named in *skipped* when the caller
    passes a list: a silent skip would be the same defect as a silent pass.
    """
    hits: dict[str, list[tuple[int, str]]] = {}
    for path in paths:
        try:
            if path.stat().st_size > MAX_BYTES:
                if skipped is not None:
                    try:
                        skipped.append(str(path.relative_to(root)))
                    except ValueError:
                        skipped.append(str(path))
                continue
        except OSError:
            pass
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
        mode = "explicit"
    else:
        paths = candidate_files(ROOT)
        mode = "tracked + untracked"
    skipped: list[str] = []
    hits = scan(paths, ROOT, skipped)
    if skipped:
        print("notice: %d file(s) over %d bytes not scanned: %s"
              % (len(skipped), MAX_BYTES, ", ".join(sorted(skipped)[:5])))
    if not hits:
        print("clean: no conflict markers in %d file(s) (%s)" % (len(paths), mode))
        return 0
    total = sum(len(v) for v in hits.values())
    for rel in sorted(hits):
        for line, label in hits[rel]:
            print(f"{rel}:{line}: {label}")
    print(f"\nFAIL: {total} conflict marker(s) in {len(hits)} file(s)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
