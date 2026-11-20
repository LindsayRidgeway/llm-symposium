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


class ReadingHead(unittest.TestCase):
    """The second queue has to be in the prompt too, and the empty case is the one that matters.

    Added 2026-11-19, the same day the review queue emptied for the first time. The failure this
    pins is not "the block is missing" but "a prompt can show a wake nothing to do while 94 finished
    items sit unread": with the review queue empty and nothing due for four days, the only honest
    content of the agenda is the reading queue.
    """

    def setUp(self):
        import json
        import tempfile
        self.dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.dir.name) / "repo"
        (self.repo / "channels").mkdir(parents=True)
        rows = [
            {"id": "readmine", "amigo": "claude", "filed_utc": "2026-11-15T17:10:52Z",
             "state": "accomplished", "reviewer": "auto:path",
             "reading_assigned_to": "desi", "short_title": "conservatory to-do"},
            {"id": "readother", "amigo": "gemini", "filed_utc": "2026-11-18T17:10:52Z",
             "state": "accomplished", "reviewer": "auto:path",
             "reading_assigned_to": "dmitri", "short_title": "another seat's"},
        ]
        path = self.repo / "channels" / "items.jsonl"
        path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        self.path = path

    def tearDown(self):
        self.dir.cleanup()

    def load(self):
        spec = importlib.util.spec_from_file_location("we_rq", REPO / "channels" / "wake_engine.py")
        we = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(we)
        return we

    def test_the_item_that_carries_my_name_is_named_with_the_size_of_the_pile(self):
        text = self.load().reading_head(str(self.repo), amigo="desi")
        self.assertIn("1 never-read item(s) carry your name", text)
        self.assertIn("2 across the commons", text)
        self.assertIn("readmine", text)
        self.assertNotIn("readother", text)

    def test_a_seat_with_no_name_on_a_healthy_pile_is_told_nothing_is_owed(self):
        """Changed 2026-11-20 (Desi). The empty case is still the failure — but the answer is not
        "read anybody's item".

        Measured on the live ledger: desi held 0 of the 88 unread, every one of the 88 already
        carried another seat's name, and the pile was 88 against a target of 100. The old fallback
        said "take the oldest of the whole pile rather than nothing", which on that ledger was two
        items *filed by desi* — and `review()` refuses those by name, because the author is never
        the reviewer. A wake handed an act its own ledger rejects does the reading, gets the
        ValueError, and faces the same item next wake: a jam with extra steps. Double-booking
        healthy work while the value queue below sits untouched is how maintenance eats production.
        """
        text = self.load().reading_head(str(self.repo), amigo="tarik")
        self.assertIn("nothing is owed from this seat", text)
        self.assertIn("2 across the commons", text)
        self.assertIn("value queue below", text)
        self.assertNotIn("readother", text)

    def test_a_pile_in_arrears_offers_the_oldest_that_this_seat_did_not_file(self):
        """Arrears is the condition that turns the fallback on, and authorship is the line it keeps."""
        import json
        rows = [{"id": "minefirst", "amigo": "desi", "filed_utc": "2026-11-01T00:00:00Z",
                 "state": "accomplished", "reviewer": "auto:path",
                 "reading_assigned_to": "dmitri", "short_title": "desi's own, oldest of all"}]
        for i in range(120):
            rows.append({"id": "pile%03d" % i, "amigo": "gemini", "filed_utc": "2026-11-10T00:00:00Z",
                         "state": "accomplished", "reviewer": "auto:path",
                         "reading_assigned_to": "dmitri", "short_title": "somebody else's work"})
        self.path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        text = self.load().reading_head(str(self.repo), amigo="desi")
        self.assertIn("in arrears (121 > 100)", text)
        self.assertIn("pile000", text)
        self.assertNotIn("minefirst", text)

    def test_a_ledger_with_nothing_unread_says_nothing_at_all(self):
        self.path.write_text("", encoding="utf-8")
        self.assertEqual(self.load().reading_head(str(self.repo), amigo="desi"), "")

    def test_orientation_carries_the_reading_queue(self):
        (self.repo / "to-do-lists").mkdir()
        (self.repo / "to-do-lists" / "desi.md").write_text("# To-do — desi\n", encoding="utf-8")
        we = self.load()
        we.AMIGO = "desi"
        text = we.orientation(str(self.repo), str(self.repo))
        self.assertIn("=== YOUR READING QUEUE —", text)
        self.assertIn("readmine", text)


if __name__ == "__main__":
    unittest.main()


class OrientationWiring(unittest.TestCase):
    """The block has to arrive through the call a wake actually makes, not only when called by hand.

    Written 2026-11-18 after the founder asked what a wake sees first. `human_block(repo, amigo=...)`
    passed a name that does not exist in `orientation()`, so every wake since 2026-11-14 was told
    "unavailable this run (NameError: name 'amigo' is not defined)" instead of being shown the open
    questions — a block that fails loudly in a place nobody reads is still a block nobody reads. The
    direct-call test above passed the whole time it was broken.
    """

    def setUp(self):
        import json
        import tempfile
        self.dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.dir.name)
        (self.repo / "channels").mkdir()
        (self.repo / "to-do-lists").mkdir()
        (self.repo / "to-do-lists" / "desi.md").write_text("# To-do — desi\n", encoding="utf-8")
        (self.repo / "channels" / "human-blockers.jsonl").write_text(json.dumps({
            "id": "x", "at": "2026-11-16T00:00:00Z", "amigo": "desi",
            "ask": "Which address should the colistin letter go to?",
            "why_human": "no verified address exists", "status": "open"}) + "\n", encoding="utf-8")

    def tearDown(self):
        self.dir.cleanup()

    def test_orientation_shows_the_open_question_and_does_not_say_unavailable(self):
        spec = importlib.util.spec_from_file_location("we_or", REPO / "channels" / "wake_engine.py")
        we = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(we)
        old = we.AMIGO
        we.AMIGO = "desi"
        try:
            text = we.orientation(str(self.repo), str(self.repo / "state"))
        finally:
            we.AMIGO = old
        self.assertIn("Which address should the colistin letter go to?", text)
        self.assertNotIn("NameError", text)


class ReviewHead(unittest.TestCase):
    """The queue's head has to be in the prompt, with its age and its missing evidence.

    Added 2026-11-18: the review queue was never in a wake's context, so the head of the queue sat
    unchanged for wakes at a time while each wake rediscovered that the item named a report that was
    not in the checkout. Whether a block appears is not the test — whether it names the absence is.
    """

    def setUp(self):
        import json
        import tempfile
        self.dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.dir.name)
        (self.repo / "channels" / "ledger-verdicts").mkdir(parents=True)
        (self.repo / "to-do-lists").mkdir()
        (self.repo / "to-do-lists" / "desi.md").write_text("# To-do — desi\n", encoding="utf-8")
        rows = [
            {"id": "old", "amigo": "dmitri", "filed_utc": "2026-11-16T07:00:00Z",
             "assigned_to": "desi", "assigned_utc": "2026-11-16T07:00:00Z",
             "paths": ["channels/reports/missing-report.md"], "short_title": "arithmetic"},
            {"id": "new", "amigo": "gemini", "filed_utc": "2026-11-17T07:00:00Z",
             "assigned_to": "desi", "assigned_utc": "2026-11-17T07:00:00Z",
             "paths": ["channels/tasks.md"], "short_title": "present evidence"},
        ]
        (self.repo / "channels" / "tasks.md").write_text("x\n", encoding="utf-8")
        (self.repo / "channels" / "items.jsonl").write_text(
            "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    def tearDown(self):
        self.dir.cleanup()

    def test_the_head_is_shown_oldest_first_with_its_missing_evidence(self):
        spec = importlib.util.spec_from_file_location("we_rh", REPO / "channels" / "wake_engine.py")
        we = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(we)
        text = we.review_head(str(self.repo), amigo="desi")
        self.assertIn("2 waiting", text)
        self.assertLess(text.index("old"), text.index("new"))       # oldest first
        self.assertIn("missing-report.md", text)
        self.assertIn("evidence not in this checkout", text)
