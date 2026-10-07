#!/usr/bin/env python3
"""Tests for scripts/draft_pile.py — the review gate's classifier, pinned offline.

`scripts/draft_pile.py` decides, for every `drafts/tick-*` branch, whether the content it
holds is already on `main` (`LANDED`/`ADDED_LANDED`), demonstrably absent (`NEW`/
`EDIT_UNLANDED`), ambiguous (`MOVED_ON`/`ADD_CONFLICT`), or a removal (`DELETED`). The
gate's closer turns on that verdict — a false `LANDED` prints a `git push origin --delete`
that discards real work, and a false `NEW` keeps a landed branch alive — so the seven
states are each pinned here against a throwaway repo.

The script had no test when it was written (run 20261006T023805Z); it sat unlanded on
`drafts/tick-20261006T023805Z-7796e151`. This is that missing test.

No network. The script's own `git()` runs in the current directory, so each test chdirs
into its temp repo and back.
"""
import os
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import draft_pile as dp  # noqa: E402


def _git(repo, *args):
    subprocess.run(["git", *args], cwd=str(repo), check=True, capture_output=True, text=True)


def _rev(repo, ref):
    return subprocess.run(["git", "rev-parse", ref], cwd=str(repo),
                          check=True, capture_output=True, text=True).stdout.strip()


def _commit(repo, msg):
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", msg)


class _chdir:
    def __init__(self, p):
        self.p = p

    def __enter__(self):
        self.old = os.getcwd()
        os.chdir(self.p)

    def __exit__(self, *a):
        os.chdir(self.old)


def _make_repo(tmp):
    repo = Path(tmp) / "r"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.invalid")
    _git(repo, "config", "user.name", "test")
    (repo / "a.txt").write_text("1\n")
    (repo / "to-do-lists").mkdir()
    (repo / "to-do-lists" / "dmitri.md").write_text("churn\n")
    _commit(repo, "init")
    return repo


def test_new_edit_unlanded_and_deleted_before_main_moves():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(tmp)
        base = _rev(repo, "main")
        # tick-1 adds a file and edits a.txt; tick-4 deletes a.txt
        _git(repo, "checkout", "-q", "-b", "drafts/tick-1")
        (repo / "new.txt").write_text("n\n")
        (repo / "a.txt").write_text("2\n")
        _commit(repo, "t1")
        _git(repo, "checkout", "-q", "main")
        _git(repo, "checkout", "-q", "-b", "drafts/tick-4")
        _git(repo, "rm", "-q", "a.txt")
        _commit(repo, "t4")
        _git(repo, "checkout", "-q", "main")
        with _chdir(repo):
            assert dp.classify("main", base, "drafts/tick-1", "new.txt") == "NEW"
            # main's a.txt still equals the merge-base's: the edit never landed
            assert dp.classify("main", base, "drafts/tick-1", "a.txt") == "EDIT_UNLANDED"
            assert dp.classify("main", base, "drafts/tick-4", "a.txt") == "DELETED"


def test_landed_added_landed_conflict_moved_on():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(tmp)
        base = _rev(repo, "main")
        # tick-2 adds landed.txt; tick-3 adds conflict.txt with other content; tick-5 edits a.txt
        for br, fn, content in [("drafts/tick-2", "landed.txt", "L\n"),
                                ("drafts/tick-3", "conflict.txt", "C\n")]:
            _git(repo, "checkout", "-q", "main")
            _git(repo, "checkout", "-q", "-b", br)
            (repo / fn).write_text(content)
            _commit(repo, br)
        # tick-5 edits a.txt to 3 (which main will adopt); tick-7 edits it to 9 (which it won't)
        for br, val in [("drafts/tick-5", "3\n"), ("drafts/tick-7", "9\n")]:
            _git(repo, "checkout", "-q", "main")
            _git(repo, "checkout", "-q", "-b", br)
            (repo / "a.txt").write_text(val)
            _commit(repo, br)
        # main moves on: adopts landed.txt verbatim, conflicts with conflict.txt, edits a.txt to 3
        _git(repo, "checkout", "-q", "main")
        (repo / "landed.txt").write_text("L\n")
        (repo / "conflict.txt").write_text("DIFFERENT\n")
        (repo / "a.txt").write_text("3\n")
        _commit(repo, "main advances")
        with _chdir(repo):
            assert dp.classify("main", base, "drafts/tick-2", "landed.txt") == "ADDED_LANDED"
            assert dp.classify("main", base, "drafts/tick-3", "conflict.txt") == "ADD_CONFLICT"
            assert dp.classify("main", base, "drafts/tick-5", "a.txt") == "LANDED"
            # main has its own, newer version: neither present nor provably absent
            assert dp.classify("main", base, "drafts/tick-7", "a.txt") == "MOVED_ON"


def test_verdicts_and_build_pile():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _make_repo(tmp)
        # tick-1 holds work (a NEW file); tick-6 only touches churn
        _git(repo, "checkout", "-q", "-b", "drafts/tick-1")
        (repo / "work.txt").write_text("w\n")
        _commit(repo, "t1")
        _git(repo, "checkout", "-q", "main")
        _git(repo, "checkout", "-q", "-b", "drafts/tick-6")
        (repo / "to-do-lists" / "dmitri.md").write_text("more churn\n")
        _commit(repo, "t6")
        _git(repo, "checkout", "-q", "main")
        with _chdir(repo):
            assert dp._verdict({"x": "NEW"}) == "HOLDS_WORK"
            assert dp._verdict({"x": "LANDED"}) == "SAFE_TO_DELETE"
            assert dp._verdict({"x": "ADD_CONFLICT"}) == "REVIEW"
            assert dp._verdict({}) == "SAFE_TO_DELETE"
            reports, skipped = dp.build_pile("drafts/tick-*", "main", "to-do-lists/*")
            by = {r["branch"]: r for r in reports}
            assert len(reports) == 2 and skipped == [], (len(reports), skipped)
            assert by["drafts/tick-1"]["paths"] == {"work.txt": "NEW"}
            # the churn file is recorded apart and does not make the branch hold work
            assert by["drafts/tick-6"]["paths"] == {}
            assert by["drafts/tick-6"]["ignored"] == {"to-do-lists/dmitri.md": "EDIT_UNLANDED"}
            assert dp.render_text(reports, skipped).count("HOLDS_WORK") >= 1
            md = dp.render_markdown(reports, skipped, "main", "drafts/tick-*")
            assert "draft pile" in md and "work.txt" in md


def _run_all():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
            passed += 1
        except Exception:
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    print(f"\n{passed}/{len(tests)} tests passed")
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    sys.exit(_run_all())
