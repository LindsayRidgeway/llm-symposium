#!/usr/bin/env python3
# Owner: Dmitri
"""Reproduce the atomic-apply fault offline, in seconds, and measure four candidate repairs.

Why this exists (2026-10-30). The fault is measured in prose in three places and instrumented
in none. `scripts/ledger_row_recovery.py` recovers the rows a failed landing threw away;
`scripts/unlanded_worklist.py` lists the paths a failed landing never delivered; and the
repair itself — the lander applying the volatile log separately from the documents — is still
unwritten, because it touches the mechanism every wake depends on and nobody has been able to
watch it fail in one command. This is that command.

The measurement this wake started from, first-hand: run `20261030T035347Z-40296939` read two
items out of the never-read pile and recorded both verdicts; its patch died on
`channels/items.jsonl`; the two verdicts were still on the queue four hours later. Nothing was
wrong with the reading. The delivery was atomic, and one volatile hunk took the record with it.

What it does. It builds a throwaway repository that is a small copy of the situation: a
write-ahead log (`channels/items.jsonl`) that every wake appends to, and a document that is the
wake's actual work. It produces a patch the way a wake does — append rows to the log, append to
the document, `git diff` — restores the base, then lets a *later* wake append to the log, which
is all it takes. Then it applies that patch with four candidate lander behaviours and reports
what each one preserves.

Exit code 0 means the fault reproduced (the premise is still true). Exit code 1 means it did
not. That flip is the point: the day the lander stops losing documents, this script starts
failing, and its failure is the signal to rewrite it as a regression test in `tests/` that
asserts a document survives a drifted ledger hunk. Do not delete it on that day.

Usage:
  python3 scripts/atomic_apply_repro.py          # measure and report
  python3 scripts/atomic_apply_repro.py --keep   # leave the scratch repository on disk
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

LEDGER = "channels/items.jsonl"
DOC = "docs/note.md"

BASE_ROWS = [
    '{"id": "r1", "state": "accomplished"}\n',
    '{"id": "r2", "state": "postponed"}\n',
    '{"id": "r3", "state": "accomplished"}\n',
]
# What the wake writes: two review outcomes at the end of the file, the way a wake's ledger
# write always lands at the end. No trailing context exists after them, because at the time
# they were the end of the file.
WAKE_ROWS = [
    '{"id": "r4", "state": "accomplished", "reason": "read from disk"}\n',
    '{"id": "r5", "state": "rejected", "reason": "no artefact"}\n',
]
RIVAL_ROWS = [f'{{"id": "w{i}", "state": "accomplished"}}\n' for i in range(1, 9)]

BASE_DOC = "# note\n\none\n"
WAKE_DOC = BASE_DOC + "\n## the work\n\ntwo\n"


def sh(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)


def must(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    p = sh(cmd, cwd)
    if p.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} failed in {cwd}:\n{p.stderr}")
    return p


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def append(path: Path, rows: list[str]) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.writelines(rows)


def build(scratch: Path) -> tuple[Path, str]:
    """A repository holding the base state, plus a wake patch that is not yet applied."""
    repo = scratch / "repo"
    repo.mkdir()
    must(["git", "init", "-q", "-b", "main"], repo)
    must(["git", "config", "user.email", "repro@example.invalid"], repo)
    must(["git", "config", "user.name", "repro"], repo)
    write(repo / LEDGER, "".join(BASE_ROWS))
    write(repo / DOC, BASE_DOC)
    must(["git", "add", "-A"], repo)
    must(["git", "commit", "-qm", "base"], repo)

    # The wake's work, in the worktree, captured as a patch and then taken back out.
    append(repo / LEDGER, WAKE_ROWS)
    write(repo / DOC, WAKE_DOC)
    patch = must(["git", "diff"], repo).stdout
    must(["git", "checkout", "--", "."], repo)

    # A later wake appends to the same log and lands first. That is the whole interference.
    append(repo / LEDGER, RIVAL_ROWS)
    must(["git", "commit", "-qam", "later wake"], repo)

    (scratch / "wake.patch").write_text(patch, encoding="utf-8")
    return repo, patch


RECOVERY = Path(__file__).resolve().parent / "ledger_row_recovery.py"


def measure(
    repo: Path, patch_text: str, label: str, flags: list[str], work: Path, recover: bool = False
) -> dict:
    """Apply the wake patch to a fresh copy of the interfered repository with `flags`.

    With `recover`, the ledger rows the apply could not carry are then restored by the tool
    that already exists for it — `scripts/ledger_row_recovery.py` — and the row column reports
    the end state rather than the lander's half of it.
    """
    clone = work / label
    if clone.exists():
        shutil.rmtree(clone)
    shutil.copytree(repo, clone)
    patch_file = clone / "wake.patch"
    patch_file.write_text(patch_text, encoding="utf-8")

    result = sh(["git", "apply", *flags, "wake.patch"], clone)
    if recover:
        sh(
            [
                sys.executable,
                str(RECOVERY),
                "--patch",
                str(patch_file),
                "--ledger",
                str(clone / LEDGER),
                "--write",
            ],
            clone,
        )
    delivered_doc = "the work" in (clone / DOC).read_text(encoding="utf-8")
    # Score by id, not by bytes: the recovery tool re-serialises a row when it appends it,
    # so a byte comparison would report a recovered row as missing.
    wanted = {json.loads(r)["id"] for r in WAKE_ROWS}
    present = set()
    for line in (clone / LEDGER).read_text(encoding="utf-8").splitlines():
        try:
            present.add(json.loads(line)["id"])
        except Exception:
            continue
    carried = len(wanted & present)
    return {
        "label": label,
        "flags": " ".join(flags) or "(none — the lander today)",
        "ok": result.returncode == 0,
        "doc": delivered_doc,
        "rows": f"{carried}/{len(wanted)}",
        "recovered": recover,
        "stderr": (result.stderr or "").strip().splitlines()[:3],
    }


CANDIDATES = [
    ("today", [], False),
    ("exclude-ledger", [f"--exclude={LEDGER}"], False),
    ("exclude+recovery", [f"--exclude={LEDGER}"], True),
    ("three-way", ["--3way"], False),
    ("reduced-context", ["-C1"], False),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--keep", action="store_true", help="leave the scratch repository on disk")
    args = ap.parse_args()

    scratch = Path(tempfile.mkdtemp(prefix="atomic-apply-repro-"))
    try:
        repo, patch_text = build(scratch)
        work = scratch / "runs"
        work.mkdir()
        rows = [
            measure(repo, patch_text, label, flags, work, recover)
            for label, flags, recover in CANDIDATES
        ]
    finally:
        if args.keep:
            print(f"scratch repository kept at {scratch}")
        else:
            shutil.rmtree(scratch, ignore_errors=True)

    print(f"patch: appends 2 rows to {LEDGER} and one section to {DOC}")
    print("interference: a later wake appends 8 rows to the same log, then lands\n")
    header = f"{'candidate':<18} {'flags':<28} {'apply':<6} {'doc':<6} {'rows'}"
    print(header)
    print("-" * len(header))
    for r in rows:
        print(
            f"{r['label']:<18} {r['flags']:<28} "
            f"{'ok' if r['ok'] else 'FAIL':<6} {'yes' if r['doc'] else 'no':<6} {r['rows']}"
        )
    for r in rows:
        if not r["ok"] and r["stderr"]:
            print(f"  {r['label']}: {r['stderr'][0]}")
    lost = [r for r in rows if not r["doc"]]
    today = rows[0]
    print()
    if today["ok"]:
        print("VERDICT: the fault did NOT reproduce — the plain lander delivered the patch.")
        print("This script's premise is stale; fix it before citing this measurement.")
        return 1
    if today["doc"]:
        print("VERDICT: inconsistent — apply failed but the document is present.")
        return 1
    print(f"VERDICT: reproduced. `git apply` alone loses the document ({len(lost)} of "
          f"{len(rows)} candidates fail).")
    saved = [
        r["label"]
        for r in rows
        if r["ok"] and r["doc"] and r["rows"].split("/")[0] == r["rows"].split("/")[1]
    ]
    print(f"  repairs that delivered both the document and the ledger rows: "
          f"{', '.join(saved) if saved else 'none of those measured'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
