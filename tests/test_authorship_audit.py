#!/usr/bin/env python3
"""Tests for the authorship audit — the instrument that keeps a human's name off our commits.

`AUTHORSHIP.md` promises that an artifact must not wear a human's name, carried by two fields: the
author address (`<amigo>@llm-symposium.local`, or the collective bot for a generated index) and the
`Architecture:` trailer. On 2026-10-16 two native Codex landings reached `main` authored
`Lindsay <LDRidgeway@gmail.com>` with a correct trailer, so the promise held in one field and not the
other. These tests pin the classification that makes that countable, and the two ways a naive audit
would lie: counting a legal pre-convention commit as a violation, and reading a `--since` window as
if it were the whole history.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts import authorship_audit as aa  # noqa: E402

HUMAN = ("Lindsay", "LDRidgeway@gmail.com")
BOT = ("LLM Symposium Bot", "bot@llm-symposium.local")


def git(repo: Path, *args: str, date: str | None = None, name: str = "", email: str = "") -> str:
    env = {"GIT_AUTHOR_NAME": name or "x", "GIT_AUTHOR_EMAIL": email or "x@x",
           "GIT_COMMITTER_NAME": name or "x", "GIT_COMMITTER_EMAIL": email or "x@x"}
    if date:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = date
    out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                         check=True, env={**__import__("os").environ, **env})
    return out.stdout


def make_repo(root: Path) -> Path:
    repo = root / "r"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "commit.gpgsign", "false")
    return repo


def commit(repo: Path, message: str, who: tuple[str, str], date: str, body: str = "") -> str:
    f = repo / "f.txt"
    f.write_text(f.read_text() + "x" if f.exists() else "x", encoding="utf-8")
    git(repo, "add", "f.txt")
    full = message + ("\n\n" + body if body else "")
    git(repo, "commit", "-q", "-m", full, date=date, name=who[0], email=who[1])
    return git(repo, "rev-parse", "HEAD").strip()


class TestClassify(unittest.TestCase):
    def test_matching_author_and_trailer_is_consistent(self):
        v = aa.classify("abc", "Desi", "desi@llm-symposium.local", "land(wake): work",
                        "Architecture: DeepSeek (Desi)")
        self.assertEqual(v.kind, "consistent")
        self.assertTrue(v.ok)

    def test_the_founders_own_address_on_a_model_commit_is_the_forbidden_case(self):
        v = aa.classify("abc", "Lindsay", "LDRidgeway@gmail.com", "land(wake): Codex work",
                        "Architecture: OpenAI (Tarik)")
        self.assertEqual(v.kind, "human-author")
        self.assertFalse(v.ok)

    def test_another_amigos_address_is_a_mismatch(self):
        v = aa.classify("abc", "Gemini", "gemini@llm-symposium.local", "land(wake): work",
                        "Architecture: DeepSeek (Desi)")
        self.assertEqual(v.kind, "other-amigo")

    def test_an_external_machine_mailbox_is_flagged_but_not_called_human(self):
        v = aa.classify("abc", "Tarik Goose", "tarik.s.commons@gmail.com", "handoff(tarik): x",
                        "Architecture: OpenAI (Tarik)")
        self.assertEqual(v.kind, "external-author")

    def test_a_wake_landing_without_a_trailer_is_a_complaint(self):
        v = aa.classify("abc", "Desi", "desi@llm-symposium.local", "land(wake): work", "no trailer")
        self.assertEqual(v.kind, "no-trailer")
        self.assertFalse(v.ok)

    def test_a_generated_index_commit_needs_no_trailer(self):
        v = aa.classify("abc", BOT[0], BOT[1], "chore(index): rebuild agenda", "")
        self.assertEqual(v.kind, "collective")
        self.assertTrue(v.ok)

    def test_the_collective_identity_on_a_wake_landing_is_reported(self):
        v = aa.classify("abc", BOT[0], BOT[1], "land(wake): work", "Architecture: DeepSeek (Desi)")
        self.assertEqual(v.kind, "bot-on-wake")
        self.assertFalse(v.ok)

    def test_an_unknown_name_is_never_guessed_into_one_of_the_five(self):
        v = aa.classify("abc", "Desi", "desi@llm-symposium.local", "land(wake): work",
                        "Architecture: OpenAI (Copilot)")
        self.assertEqual(v.kind, "unknown-amigo")


class TestOverRealGit(unittest.TestCase):
    def test_a_fixture_history_is_read_and_summarised(self):
        with tempfile.TemporaryDirectory() as t:
            repo = make_repo(Path(t))
            commit(repo, "land(wake): good", ("Desi", "desi@llm-symposium.local"),
                   "2026-10-16T10:00:00Z", "Architecture: DeepSeek (Desi)")
            commit(repo, "land(wake): Codex work", HUMAN, "2026-10-16T11:00:00Z",
                   "Architecture: OpenAI (Tarik)")
            commit(repo, "chore(index): rebuild", BOT, "2026-10-16T12:00:00Z")
            verdicts = aa.audit(repo, since=None)
            kinds = [v.kind for v in verdicts]
            self.assertEqual(kinds.count("consistent"), 1)
            self.assertEqual(kinds.count("human-author"), 1)
            self.assertEqual(kinds.count("collective"), 1)
            self.assertEqual(aa.summarise(verdicts)["complaints"], 1)

    def test_the_since_window_excludes_commits_before_the_convention(self):
        with tempfile.TemporaryDirectory() as t:
            repo = make_repo(Path(t))
            commit(repo, "land(wake): legal then, silent now", BOT, "2026-10-05T10:00:00Z")
            commit(repo, "land(wake): good", ("Desi", "desi@llm-symposium.local"),
                   "2026-10-16T10:00:00Z", "Architecture: DeepSeek (Desi)")
            window = aa.audit(repo, since="2026-10-12")
            self.assertEqual([v.subject for v in window], ["land(wake): good"])
            self.assertEqual(aa.summarise(window)["complaints"], 0)

    def test_cli_strict_fails_on_a_complaint_and_json_is_machine_readable(self):
        with tempfile.TemporaryDirectory() as t:
            repo = make_repo(Path(t))
            commit(repo, "land(wake): Codex work", HUMAN, "2026-10-16T11:00:00Z",
                   "Architecture: OpenAI (Tarik)")
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = aa.main(["--repo", str(repo), "--json", "--strict", "--since", "2026-10-12"])
            self.assertEqual(code, 1)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["summary"]["complaints"], 1)
            self.assertEqual(payload["commits"][0]["kind"], "human-author")

    def test_cli_is_clean_and_quiet_on_a_clean_window(self):
        with tempfile.TemporaryDirectory() as t:
            repo = make_repo(Path(t))
            commit(repo, "land(wake): good", ("Dmitri", "dmitri@llm-symposium.local"),
                   "2026-10-16T10:00:00Z", "Architecture: DeepSeek (Dmitri)")
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = aa.main(["--repo", str(repo), "--strict", "--since", "2026-10-12"])
            self.assertEqual(code, 0)
            self.assertIn("0 complaint(s)", buf.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
