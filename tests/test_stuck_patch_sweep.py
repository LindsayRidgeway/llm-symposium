#!/usr/bin/env python3
"""The stuck-patch sweep must split a patch the way `git apply` refuses to, and put back only what
is clean.

Written 2026-10-30 (Dmitri) with `scripts/stuck_patch_sweep.py`. The defect it is aimed at was measured
on 2026-10-29 and again by the tool's own first run: of 40 patches written since 2026-10-29, 24 would
be thrown away whole by an atomic `git apply`, and 22 of those fail on `channels/items.jsonl` alone —
that is, the rest of those 22 patches was recoverable and was lost.

Four things are worth guarding, and each is a way the tool could do harm rather than good:

1. **The split must be per file.** If one section's context bleed into another, a stale hunk in the log
   would still block the run's documents and the tool would be the defect it repairs.

2. **A report must not edit anything, and the register needs its own word.** A tool that changes the
   tree while reporting what it *would* recover is worse than no tool, and the append-only ledger is
   a shared register: documents may be put back with `--recover`, rows only with `--write`.

3. **It must not apply the volatile log itself.** Appending the log's hunk wholesale is what fails;
   the rows have their own tool, and recovery must route them there rather than duplicating it.

4. **A section already in the tree is not "blocked".** Calling it blocked would put successful landings
   on the lost list, and the count is the whole point of the exercise.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts import stuck_patch_sweep as S  # noqa: E402

LEDGER_OLD = {"id": "old", "amigo": "desi", "filed_utc": "2026-01-01T00:00:00Z"}
LEDGER_NEW = {"id": "new", "amigo": "dmitri", "filed_utc": "2026-02-02T00:00:00Z"}


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=str(repo), check=True, capture_output=True)


def _pane(rows: list[dict] | None = None, stale_log: bool = True, doc: bool = True) -> Path:
    """A throwaway checkout holding a ledger and a note, plus a patch shaped like a lander's."""
    root = Path(tempfile.mkdtemp())
    repo = root / "repo"
    (repo / "channels").mkdir(parents=True)
    (repo / "channels" / "items.jsonl").write_text(
        json.dumps(LEDGER_OLD, sort_keys=True) + "\n", encoding="utf-8")
    if doc:
        (repo / "notes.md").write_text("hello\n", encoding="utf-8")
    _git(repo, "init", "-q", ".")

    parts = []
    if stale_log:
        rows = rows or [LEDGER_NEW]
        parts.append("\n".join([
            "diff --git a/channels/items.jsonl b/channels/items.jsonl",
            "--- a/channels/items.jsonl",
            "+++ b/channels/items.jsonl",
            f"@@ -1,1 +1,{1 + len(rows)} @@",
            '-{"id": "a-line-this-ledger-does-not-have"}',
            "+" + json.dumps(LEDGER_OLD, sort_keys=True),
            *["+" + json.dumps(r, sort_keys=True) for r in rows],
        ]))
    if doc:
        parts.append("\n".join([
            "diff --git a/notes.md b/notes.md",
            "--- a/notes.md",
            "+++ b/notes.md",
            "@@ -1,1 +1,2 @@",
            " hello",
            "+world",
        ]))
    (root / "changes.patch").write_text("\n".join(parts) + "\n", encoding="utf-8")
    return root


def test_split_is_per_file() -> None:
    """Case 1: two files in, two sections out, each carrying only its own lines."""
    run = _pane()
    sections = S.split_sections((run / "changes.patch").read_text(encoding="utf-8"))
    assert [p for p, _ in sections] == ["channels/items.jsonl", "notes.md"], sections
    _, log = sections[0]
    _, note = sections[1]
    assert "+world" not in log and "a-line-this-ledger-does-not-have" not in note


def test_stale_log_blocks_one_section_not_the_patch() -> None:
    """Case 2: the log's hunk is stale, the note's is clean, and the sweep says exactly that."""
    run = _pane()
    res = S.classify_patch(run / "changes.patch", repo=run / "repo")
    assert res["verdict"] == "blocked", res
    assert res["blocked"] == ["channels/items.jsonl"], res
    assert res["blocked_only_ledger"] is True, res
    verdicts = {s["path"]: s["verdict"] for s in res["sections"]}
    assert verdicts["notes.md"] == "clean", res


def test_the_register_is_not_written_without_write() -> None:
    """Case 3: the documents half may be done alone; the register half may not.

    A document put back in a checkout is an undoable tree change. The ledger is a shared append-only
    register that the landing machine itself rewrites, so appending to it is the act that needs the
    extra word — exactly the convention `ledger_row_recovery.py` already uses.
    """
    run = _pane()
    repo = run / "repo"
    before = (repo / "channels" / "items.jsonl").read_text(encoding="utf-8")
    rec = S.recover_patch(run / "changes.patch", repo=repo, write=False)
    assert rec["ledger_rows_recovered"] == ["new"], rec
    assert rec["ledger_rows_written"] is False, rec
    assert (repo / "notes.md").read_text(encoding="utf-8") == "hello\nworld\n", rec
    assert (repo / "channels" / "items.jsonl").read_text(encoding="utf-8") == before, "ledger moved"


def test_classifying_alone_changes_nothing() -> None:
    """Case 3b: the sweep's default mode is the report, and the report must be free of side effects."""
    run = _pane()
    repo = run / "repo"
    S.classify_patch(run / "changes.patch", repo=repo)
    assert (repo / "notes.md").read_text(encoding="utf-8") == "hello\n", "classify touched the tree"
    assert "new" not in (repo / "channels" / "items.jsonl").read_text(encoding="utf-8")


def test_recovery_lands_the_documents_and_hands_the_log_over() -> None:
    """Case 4: the note is applied, the log is not patched, and the row arrives by its own tool."""
    run = _pane()
    repo = run / "repo"
    rec = S.recover_patch(run / "changes.patch", repo=repo, write=True)
    assert rec["applied"] == ["notes.md"], rec
    assert rec["skipped"] == ["channels/items.jsonl"], rec
    assert rec["ledger_rows_written"] is True, rec
    assert (repo / "notes.md").read_text(encoding="utf-8") == "hello\nworld\n"
    rows = [json.loads(line) for line in
            (repo / "channels" / "items.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [r["id"] for r in rows] == ["old", "new"], rows


def test_a_landed_section_is_not_counted_as_lost() -> None:
    """Case 5: once the note is applied, the same patch reads `blocked` on the log only — never
    `clean`, and never `in-tree` while the log's rows are still missing."""
    run = _pane()
    repo = run / "repo"
    S.recover_patch(run / "changes.patch", repo=repo, write=True)
    # Re-applying the note must now read as already-in-tree, and the recovery must leave it alone.
    again = S.classify_section("notes.md", S.split_sections(
        (run / "changes.patch").read_text(encoding="utf-8"))[1][1], repo)
    assert again == "in-tree", again
    rec = S.recover_patch(run / "changes.patch", repo=repo, write=True)
    assert rec["applied"] == [], rec
    assert (repo / "notes.md").read_text(encoding="utf-8") == "hello\nworld\n", "applied twice"


def test_an_empty_patch_is_not_a_failure() -> None:
    """Case 6: a run that wrote nothing is `empty`, not blocked — 7 of 40 real patches are this."""
    run = Path(tempfile.mkdtemp())
    (run / "changes.patch").write_text("", encoding="utf-8")
    res = S.classify_patch(run / "changes.patch", repo=run)
    assert res["verdict"] == "empty", res
    assert res["blocked"] == [], res


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL {t.__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
