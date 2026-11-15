#!/usr/bin/env python3
"""Questions that only the human can answer: filed once, asked once, visible to every wake.

The founder's question was not "will you tell me" but "how will you know, and how will you ask"
(2026-11-14). These tests pin the three things that make the answer a mechanism rather than a
promise: the row exists and refuses a question with no reason it needs a human, the daily report
counts it, and every wake is shown it so the same question is never asked twice.
"""
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

import ask_human as ah  # noqa: E402


class AskTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "human-blockers.jsonl"

    def tearDown(self):
        self.dir.cleanup()

    def test_a_question_needs_a_reason_it_needs_a_human(self):
        with self.assertRaises(ValueError):
            ah.ask("Can you add an address?", "it would help", path=self.path, send=False)

    def test_a_filed_question_is_open_until_answered(self):
        row = ah.ask("Which address should the colistin letter go to?", 
                     "we have no verified address and cannot invent one", path=self.path, send=False)
        self.assertEqual(len(ah.open_asks(self.path)), 1)
        ah.close(row["id"], "the corresponding author's, from the paper", path=self.path)
        self.assertEqual(ah.open_asks(self.path), [])
        rows = ah.load(self.path)
        self.assertEqual(rows[-1]["answer"], "the corresponding author's, from the paper")

    def test_closing_a_question_nobody_asked_is_an_error(self):
        with self.assertRaises(KeyError):
            ah.close("nope", "x", path=self.path)

    def test_the_daily_report_counts_what_is_waiting_on_him(self):
        sys.path.insert(0, str(REPO / "channels"))
        import datetime as dt
        spec = importlib.util.spec_from_file_location("lw", REPO / "scripts" / "ledger_watch.py")
        lw = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lw)
        ah.ask("Which address?", "no verified address exists and inventing one is worse than asking",
               path=self.path, send=False, when="2026-11-10T00:00:00Z")
        got = lw.human_questions(dt.datetime(2026, 11, 14, tzinfo=dt.timezone.utc), path=self.path)
        self.assertEqual((got["count"], got["oldest"], got["days"]), (1, "2026-11-10", 4))

    def test_every_wake_is_shown_what_has_already_been_asked(self):
        repo = Path(self.dir.name) / "repo"
        (repo / "channels").mkdir(parents=True)
        (repo / "channels" / "human-blockers.jsonl").write_text(
            '{"id": "a", "at": "2026-11-10T00:00:00Z", "amigo": "desi", "ask": "which address", '
            '"why_human": "no verified address", "status": "open"}\n'
            '{"id": "b", "at": "2026-11-11T00:00:00Z", "amigo": "desi", "ask": "answered one", '
            '"why_human": "answered already here", "status": "answered", "answer": "yes"}\n',
            encoding="utf-8")
        sys.path.insert(0, str(REPO / "channels"))
        spec = importlib.util.spec_from_file_location("we", REPO / "channels" / "wake_engine.py")
        we = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(we)
        text = we.human_block(repo)
        self.assertIn("QUESTIONS ALREADY PUT TO THE HUMAN", text)
        self.assertIn("which address", text)
        self.assertNotIn("answered one", text)          # closed rows are history, not a prompt
        (repo / "channels" / "human-blockers.jsonl").write_text("not json\n", encoding="utf-8")
        self.assertIn("unreadable", we.human_block(repo))


if __name__ == "__main__":
    unittest.main()
