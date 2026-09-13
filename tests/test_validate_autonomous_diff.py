#!/usr/bin/env python3
import importlib.util
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_autonomous_diff", ROOT / "scripts" / "validate_autonomous_diff.py"
)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def repo_with(path, text=""):
    tmp = Path(tempfile.mkdtemp())
    target = tmp / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return tmp


def test_state_only_rejected():
    repo = repo_with("channels/agenda.md", "x")
    ok, messages = mod.validate(repo, [("M", "channels/agenda.md")])
    assert not ok
    assert "no substantive" in "\n".join(messages)


def test_old_discussion_appendix_rejected():
    repo = repo_with("discussions/2026-09-09-tarik-app-review-of-the-gallery.md", "Suggested Improvements\n")
    ok, _ = mod.validate(repo, [("M", "discussions/2026-09-09-tarik-app-review-of-the-gallery.md")])
    assert not ok


def test_undated_docs_paper_rejected():
    repo = repo_with("docs/papers/autonomous-session-management-strategies.md", "# Generic\n")
    ok, _ = mod.validate(repo, [("A", "docs/papers/autonomous-session-management-strategies.md")])
    assert not ok


def test_new_dated_discussion_with_metadata_accepted():
    body = (
        "# A Specific Argument\n\n"
        "**Author:** Tarik S. Commons  \n"
        "**Date:** 2026-09-13  \n"
        "**Status:** Test artifact  \n\n"
        + "This is a substantive argument. " * 80
    )
    repo = repo_with("discussions/2026-09-13-specific-argument.md", body)
    ok, messages = mod.validate(repo, [("A", "discussions/2026-09-13-specific-argument.md")])
    assert ok, messages


def test_autonomous_implementation_change_accepted():
    repo = repo_with("recipes/autonomous-goose/tarik.yaml", "version: 1\n")
    ok, messages = mod.validate(repo, [("M", "recipes/autonomous-goose/tarik.yaml")])
    assert ok, messages


def test_autonomous_mission_change_accepted():
    repo = repo_with("recipes/autonomous-goose/tarik-mission.md", "# Mission\n")
    ok, messages = mod.validate(repo, [("M", "recipes/autonomous-goose/tarik-mission.md")])
    assert ok, messages


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"PASS {name}")
