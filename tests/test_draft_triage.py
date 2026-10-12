#!/usr/bin/env python3
"""Tests for the draft-branch triage tool (`scripts/draft_triage.py`).

Run:  python3 tests/test_draft_triage.py
Stdlib only; requires `git` on PATH. Builds a throwaway repo shaped like the
real pile — a `main` plus six `drafts/tick-*` branches, one per verdict — and
asserts the classifier and the CLI. No network access.
"""
import contextlib
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "draft_triage", ROOT / "scripts" / "draft_triage.py"
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod  # dataclass field resolution needs the module registered
SPEC.loader.exec_module(mod)


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    )


def _write(repo: Path, rel: str, text: str) -> None:
    target = repo / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def make_pile() -> Path:
    """A repo with main and six draft branches, one per expected verdict."""
    repo = Path(tempfile.mkdtemp(prefix="draft-triage-test-"))
    _git(repo, "init", "-q")
    _git(repo, "symbolic-ref", "HEAD", "refs/heads/main")
    _git(repo, "config", "user.email", "test@local")
    _git(repo, "config", "user.name", "Draft Triage Test")

    # M0: the base commit every branch forks from.
    _write(repo, "to-do-lists/dmitri.md", "before\n")
    _write(repo, "scripts/thing.py", "v1\n")
    _write(repo, "docs/keep.html", "keep\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")

    # tick-d: adds an artefact that main will later carry identically -> LANDED.
    _git(repo, "checkout", "-q", "-b", "drafts/tick-d")
    _write(repo, "research/beta.md", "beta\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "add beta")

    # tick-a: a real unlanded artefact + some to-do churn -> REVIEW.
    _git(repo, "checkout", "-q", "main")
    _git(repo, "checkout", "-q", "-b", "drafts/tick-a")
    _write(repo, "research/alpha.md", "alpha\n")
    _write(repo, "to-do-lists/dmitri.md", "before\nafter\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "alpha and a to-do tick")

    # tick-b: edits a file main has already moved on from -> DIVERGENT -> REVIEW.
    _git(repo, "checkout", "-q", "main")
    _git(repo, "checkout", "-q", "-b", "drafts/tick-b")
    _write(repo, "scripts/thing.py", "v2-branch\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "branch-side edit")

    # tick-c: to-do churn only -> CLOSE.
    _git(repo, "checkout", "-q", "main")
    _git(repo, "checkout", "-q", "-b", "drafts/tick-c")
    _write(repo, "to-do-lists/dmitri.md", "before\nchurn\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "todo churn")

    # tick-f: deletes a file main still has -> REMOVED -> CLOSE.
    _git(repo, "checkout", "-q", "main")
    _git(repo, "checkout", "-q", "-b", "drafts/tick-f")
    _git(repo, "rm", "-q", "docs/keep.html")
    _git(repo, "commit", "-qm", "drop keep.html")

    # tick-e: nothing beyond base -> EMPTY.
    _git(repo, "checkout", "-q", "main")
    _git(repo, "checkout", "-q", "-b", "drafts/tick-e")

    # Land beta on main so tick-d's contribution reads as already present.
    _git(repo, "checkout", "-q", "main")
    _write(repo, "research/beta.md", "beta\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "land beta")
    return repo


def verdicts(repo: Path) -> dict[str, str]:
    return {r.branch: r.verdict for r in mod.triage(repo, "main", "drafts/tick-*")}


def test_verdicts():
    repo = make_pile()
    got = verdicts(repo)
    assert got == {
        "drafts/tick-a": "REVIEW",
        "drafts/tick-b": "REVIEW",
        "drafts/tick-c": "CLOSE",
        "drafts/tick-d": "CLOSE",
        "drafts/tick-e": "EMPTY",
        "drafts/tick-f": "CLOSE",
    }, got
    shutil.rmtree(repo, ignore_errors=True)
    print("  ok: one branch per verdict, classified as expected")


def test_actionable_paths():
    repo = make_pile()
    by_branch = {r.branch: r for r in mod.triage(repo, "main", "drafts/tick-*")}

    a = [c.path for c in by_branch["drafts/tick-a"].actionable]
    assert a == ["research/alpha.md"], a
    # the to-do edit is visible but not actionable
    a_all = {c.path: c for c in by_branch["drafts/tick-a"].changes}
    assert a_all["to-do-lists/dmitri.md"].state_only is True

    b = by_branch["drafts/tick-b"].actionable
    assert len(b) == 1 and b[0].path == "scripts/thing.py" and b[0].verdict == "DIVERGENT"

    # tick-d's only change is the artefact main already carries byte-for-byte
    d_all = {c.path: c for c in by_branch["drafts/tick-d"].changes}
    assert d_all["research/beta.md"].verdict == "LANDED"
    assert by_branch["drafts/tick-d"].actionable == []

    f_all = {c.path: c for c in by_branch["drafts/tick-f"].changes}
    assert f_all["docs/keep.html"].verdict == "REMOVED"

    shutil.rmtree(repo, ignore_errors=True)
    print("  ok: actionable set is the unlanded/divergent non-state paths only")


def test_list_branches_sorted_and_unique():
    repo = make_pile()
    names = mod.list_branches(repo, "drafts/tick-*")
    assert names == sorted(names), names
    assert len(names) == len(set(names))
    assert "drafts/tick-a" in names
    shutil.rmtree(repo, ignore_errors=True)
    print("  ok: branch list is sorted and deduped")


def test_state_only_classification():
    assert mod.is_state_only("to-do-lists/dmitri.md")
    assert mod.is_state_only("channels/telegram/2026-10-01-x.md")
    assert mod.is_state_only("channels/agenda.md")
    assert not mod.is_state_only("research/alpha.md")
    assert not mod.is_state_only("scripts/draft_triage.py")
    print("  ok: state-only set is what it claims to be")


def test_cli_json_and_exit_codes():
    repo = make_pile()
    with contextlib.redirect_stdout(io.StringIO()):
        rc = mod.main(["--repo", str(repo), "--json"])
        assert rc == 0, rc
        rc = mod.main(["--repo", str(repo), "--json", "--fail-on-review"])
        assert rc == 1, rc
        # a base that does not resolve is an error, not a silent empty report
        with contextlib.redirect_stderr(io.StringIO()):
            rc = mod.main(["--repo", str(repo), "--base", "nope"])
        assert rc == 2, rc
    shutil.rmtree(repo, ignore_errors=True)
    print("  ok: CLI exits 0 / 1 (--fail-on-review) / 2 (bad base)")


def test_cli_json_shape():
    repo = make_pile()
    with contextlib.redirect_stdout(io.StringIO()):
        rc = mod.main(["--repo", str(repo), "--json", "--fail-on-review"])
    # the CLI is a thin wrapper; assert on the pure functions it calls
    payload = json.loads(mod.to_json(mod.triage(repo, "main", "drafts/tick-*"), "main"))
    assert payload["base"] == "main"
    assert len(payload["branches"]) == 6
    assert {b["verdict"] for b in payload["branches"]} == {"REVIEW", "CLOSE", "EMPTY"}
    reviewed = [b for b in payload["branches"] if b["verdict"] == "REVIEW"]
    assert all(b["actionable"] >= 1 for b in reviewed)
    shutil.rmtree(repo, ignore_errors=True)
    print("  ok: JSON report carries base, verdicts and actionable counts")


if __name__ == "__main__":
    print("draft_triage:")
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
    print("all draft_triage checks passed")
    sys.exit(0)
