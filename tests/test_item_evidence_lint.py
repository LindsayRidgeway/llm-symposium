#!/usr/bin/env python3
"""Tests for scripts/item_evidence_lint.py — the review-evidence lint.

The lint exists because a review item that cites only files present in every checkout cannot
be failed by a presence check (found 2026-10-20: three of five items waiting on one reviewer
cited `channels/items.jsonl` / `channels/tasks.md`). These tests pin the four tiers it
computes — own / created / other / standing — and, just as important, that it says "cannot
see" instead of "all clear" when it has no git history to ask.

Run: python3 tests/test_item_evidence_lint.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import item_evidence_lint as lint  # noqa: E402

PASS = 0
FAIL = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"ok   {name}")
    else:
        FAIL += 1
        print(f"FAIL {name}" + (f" — {detail}" if detail else ""))


def git(repo: str, *args: str, when: str | None = None) -> str:
    env = dict(os.environ)
    if when:
        env["GIT_AUTHOR_DATE"] = when
        env["GIT_COMMITTER_DATE"] = when
    result = subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, env=env
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return result.stdout.strip()


def make_repo(tmp: str) -> str:
    Path(tmp).mkdir(parents=True, exist_ok=True)
    git(tmp, "init", "-q")
    git(tmp, "config", "user.email", "t@example.com")
    git(tmp, "config", "user.name", "Test")
    return tmp


def commit(repo: str, files: dict[str, str], message: str, when: str) -> None:
    for name, body in files.items():
        path = Path(repo) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message, when=when)


FILED = "2026-10-18T04:07:25Z"
WHEN = lint._parse_ts(FILED)


def build_scenario(tmp: str) -> str:
    """A repo where each tier is represented by exactly one path."""
    make_repo(tmp)
    commit(
        tmp,
        {"standing.md": "old\n"},
        "initial commit",
        "2026-01-01T12:00:00+00:00",
    )
    commit(
        tmp,
        {"edited.md": "old\n", "shared.md": "old\n"},
        "add files another run will edit",
        "2026-02-01T12:00:00+00:00",
    )
    # The run's own landing: names its run id, touches one new file and one old one.
    commit(
        tmp,
        {"own.md": "new\n", "edited.md": "old\nedited by the run\n"},
        "land(wake): work from run 20261018T040438Z-618cff9b",
        "2026-10-18T05:00:00+00:00",
    )
    # A different run's landing, after the item was filed, touching a file that predates it.
    commit(
        tmp,
        {"shared.md": "old\ntouched by someone else\n"},
        "land(wake): work from run 20261019T010101Z-abcdef01",
        "2026-10-19T01:00:00+00:00",
    )
    return tmp


def test_parse_ts() -> None:
    stamp = lint._parse_ts("2026-10-18T15:16:57Z")
    check("parse_ts reads an ISO stamp with Z", stamp == datetime(2026, 10, 18, 15, 16, 57, tzinfo=timezone.utc))
    check("parse_ts reads a bare date as midnight UTC", lint._parse_ts("2026-10-18").hour == 0)


def test_evidence_tokens() -> None:
    item = {"evidence": "dmitri-bot run 20261018T171706Z-1d0b9762", "id": "x", "amigo": "dmitri"}
    check("evidence_tokens finds the run id", "20261018T171706Z-1d0b9762" in lint.evidence_tokens(item))
    item = {"evidence": "https://github.com/x/y/commit/4f1ebafef09f6286c22bf1600e1043de461dabf7"}
    check("evidence_tokens finds a commit sha", "4f1ebafef09f6286c22bf1600e1043de461dabf7" in lint.evidence_tokens(item))


def test_tiers(tmp: str) -> None:
    repo = build_scenario(tmp)
    tokens = ["20261018T040438Z-618cff9b"]
    check("own: new file landed by the run itself", lint.path_tier("own.md", WHEN, tokens, repo) == "own")
    check("own: pre-existing file edited by the run itself", lint.path_tier("edited.md", WHEN, tokens, repo) == "own")
    check("standing: untouched since before the run", lint.path_tier("standing.md", WHEN, tokens, repo) == "standing")
    check("other: touched after filing by a different run", lint.path_tier("shared.md", WHEN, tokens, repo) == "other")
    check("unknown: no filed time to compare against", lint.path_tier("own.md", None, tokens, repo) == "unknown")


def test_created_without_matching_message(tmp: str) -> None:
    repo = make_repo(tmp)
    commit(repo, {"old.md": "old\n"}, "initial", "2026-01-01T12:00:00+00:00")
    commit(repo, {"fresh.md": "new\n"}, "land: squashed message naming no run", "2026-10-18T09:00:00+00:00")
    check(
        "created: a file with no earlier commit counts even without a matching message",
        lint.path_tier("fresh.md", WHEN, [], repo) == "created",
    )


def test_classify_and_lint(tmp: str) -> None:
    repo = build_scenario(tmp)
    standing_only = {
        "id": "a",
        "title": "cites a standing file",
        "filed_utc": FILED,
        "paths": ["standing.md", "shared.md"],
    }
    carried = {
        "id": "b",
        "title": "cites its own file",
        "filed_utc": FILED,
        "evidence": "run 20261018T040438Z-618cff9b",
        "paths": ["own.md"],
    }
    exited = {
        "id": "c",
        "title": "already reviewed",
        "filed_utc": FILED,
        "state": "accomplished",
        "paths": ["standing.md"],
    }
    verdict = lint.classify(standing_only, repo)
    check("classify marks a standing-only item unfalsifiable", verdict["falsifiable"] is False)
    check("classify names the tiers it used", verdict["tiers"]["standing.md"] == "standing")

    result = lint.lint([standing_only, carried, exited], repo)
    check("lint counts only waiting items by default", result["checked"] == 2, str(result["checked"]))
    check("lint reports the unfalsifiable one", [v["id"] for v in result["unfalsifiable"]] == ["a"])
    check("lint accepts the item citing its own file", result["falsifiable"] == 1)

    everything = lint.lint([standing_only, carried, exited], repo, include_all=True)
    check("lint --all includes exited items", everything["checked"] == 3)


def test_render() -> None:
    result = {
        "checked": 2,
        "falsifiable": 1,
        "unfalsifiable": [
            {
                "id": "a",
                "title": "cites a standing file",
                "assigned_to": "gemini",
                "filed_utc": FILED,
                "paths": ["channels/tasks.md"],
                "tiers": {"channels/tasks.md": "standing"},
            }
        ],
        "no_paths": [],
        "verdicts": [],
    }
    text = lint.render(result)
    check("render names the item", "UNFALSIFIABLE a" in text)
    check("render shows the tier of each path", "standing  channels/tasks.md" in text)
    check("render says what presence cannot do", "cannot separate delivered work" in text)


def test_no_git_says_cannot_see(tmp: str) -> None:
    """A directory without git history must produce exit 2, never a clean bill of health."""
    ledger = Path(tmp) / "channels"
    ledger.mkdir(parents=True)
    (ledger / "items.jsonl").write_text(json.dumps({"id": "a", "paths": ["x.md"], "filed_utc": FILED}) + "\n")
    code = lint.main(["--repo", tmp])
    check("no git history -> exit 2 (cannot see)", code == 2, f"got {code}")

    code = lint.main(["--repo", str(Path(tmp) / "nowhere")])
    check("missing ledger -> exit 2", code == 2, f"got {code}")


def test_cli_on_real_checkout() -> None:
    """Smoke test: the real ledger is readable and the CLI answers one way or the other."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "item_evidence_lint.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    check("CLI on the real checkout exits 0 or 1", result.returncode in (0, 1), str(result.returncode))
    check("CLI on the real checkout prints a summary", result.stdout.startswith("item evidence:"), result.stdout[:80])


def main() -> int:
    test_parse_ts()
    test_evidence_tokens()
    with tempfile.TemporaryDirectory() as tmp:
        test_tiers(os.path.join(tmp, "tiers"))
        test_created_without_matching_message(os.path.join(tmp, "created"))
        test_classify_and_lint(os.path.join(tmp, "classify"))
    test_render()
    with tempfile.TemporaryDirectory() as tmp:
        test_no_git_says_cannot_see(tmp)
    test_cli_on_real_checkout()

    print(f"\n{PASS}/{PASS + FAIL} ok")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
