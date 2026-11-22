"""A landing must never empty a file silently.

Measured on 2026-11-21.  Commit 0df32fd7 ("land(wake): work from run
20261121T124923Z-5fcff724") truncated `docs/gallery/islamic/generate-girih.py`
from 5504 bytes to 0.  The commit message lists the paths that run changed, and
that file is not among them, so nothing in the landing's own record says a file
was emptied.  Nothing in the repository read the file either, so no test failed
and the loss sat in main for two hours until a review found it by hand.

The rule this test holds: a tracked source file is either present with content
or absent, never present-and-empty.  An empty file is not a valid state for any
of these extensions, so any zero-byte one is either a truncation or a file that
should have been deleted.  Both are repairs, and neither can be found by a test
that reads files through their own contents.

Deliberately not covered: `.gitkeep`-style markers and empty `__init__.py`,
which are empty on purpose.
"""
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Extensions where zero bytes means "something went wrong", not "empty on purpose".
CHECKED = {
    ".py", ".html", ".htm", ".svg", ".css", ".js", ".json", ".jsonl",
    ".yml", ".yaml", ".md", ".abc", ".tex", ".sh", ".csv", ".txt",
}
# VCS and editor leftovers that a merge or a rebase leaves behind.
LEFTOVER_SUFFIXES = (".new", ".orig", ".rej", ".patch.bak")


def _tracked_files():
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=REPO, capture_output=True, check=True
    ).stdout.decode()
    return [p for p in out.split("\0") if p]


def _zeroed(files):
    empty = []
    for rel in files:
        path = REPO / rel
        if not path.is_file():
            continue
        if path.stat().st_size != 0:
            continue
        name = path.name
        if name in {".gitkeep", "__init__.py"}:
            continue
        empty.append(rel)
    return empty


def test_no_tracked_source_file_is_zero_bytes():
    empty = _zeroed([p for p in _tracked_files() if Path(p).suffix.lower() in CHECKED])
    assert not empty, (
        "tracked source file(s) are present but empty, which no landing should "
        "produce: restore them from the commit that still has content "
        "(git log --oneline -- <path>) or delete them deliberately: "
        + ", ".join(sorted(empty))
    )


def test_no_version_control_leftovers_are_tracked():
    leftovers = [p for p in _tracked_files() if p.endswith(LEFTOVER_SUFFIXES)]
    assert not leftovers, (
        "these look like merge or rebase leftovers and should not be in the "
        "tree: " + ", ".join(sorted(leftovers))
    )
