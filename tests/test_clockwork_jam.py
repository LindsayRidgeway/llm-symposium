#!/usr/bin/env python3
"""The de-jamming procedure's own defect, pinned (2026-11-19).

The founder's procedure: examine the head, run a wake, examine again, and call an unchanged head a
jam. Run by hand it found a real jam within the hour. Run a second time it called a healthy idle day a
jam too, because a head dated tomorrow is identical before and after a wake and nothing is wrong with
it. A test that fires on a healthy day teaches its reader to ignore it, so the distinction is pinned
here: unchanged-and-due is jammed, unchanged-and-future is waiting, moved is fine.
"""
import datetime
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import clockwork_jam as cj  # noqa: E402

TODAY = datetime.date(2026, 11, 19)


def snap(block, ident="x", when=None, size=None):
    return {"block": block, "id": ident, "when": when, "kind": None, "size": size}


class Verdict(unittest.TestCase):
    def test_a_due_item_that_is_still_the_head_after_a_wake_is_a_jam(self):
        v = cj.verdict(snap("due", "letter", "2026-11-19"), snap("due", "letter", "2026-11-19"), TODAY)
        self.assertTrue(v["jam"])
        self.assertIn("is still the head after the wake", v["why"])

    def test_a_head_dated_tomorrow_is_waiting_not_jammed(self):
        v = cj.verdict(snap("due", "artefact", "2026-11-20"), snap("due", "artefact", "2026-11-20"), TODAY)
        self.assertFalse(v["jam"])
        self.assertIn("future", v["why"])

    def test_a_moving_head_is_never_a_jam(self):
        v = cj.verdict(snap("due", "letter", "2026-11-19"), snap("reading", "20261105-x"), TODAY)
        self.assertFalse(v["jam"])
        self.assertIn("moved", v["why"])

    def test_a_review_head_that_never_moves_is_a_jam(self):
        v = cj.verdict(snap("review", "20261118-a"), snap("review", "20261118-a"), TODAY)
        self.assertTrue(v["jam"])
        self.assertIn("no clock will move it", v["why"])

    def test_a_worked_value_item_is_not_a_jam_even_though_the_head_did_not_move(self):
        """The failure this file's own procedure had: it could not see the value queue at all.

        Measured 2026-11-20: the head read as the weekly letter dated 2026-11-26, six days out, so a
        wake that spent the night on the value queue left the head byte-identical. The procedure
        would have called a productive night jammed, which is the same defect as the one it was
        written to catch — a check that cannot see the work cannot judge it.
        """
        v = cj.verdict(snap("value", "history-long-piece", None),
                       snap("value", "history-long-piece", "2026-11-20"), TODAY)
        self.assertFalse(v["jam"])
        self.assertIn("last_worked advanced", v["why"])

    def test_the_head_staying_put_while_the_pile_falls_is_not_a_jam(self):
        """Measured 2026-11-20: the head was an item named to claude, the wake read a different one,
        and the pile went 102 -> 101. The check called that jammed. In arrears every unread item
        already carries somebody's name, so the head is a suggestion and the pile is the work.
        """
        v = cj.verdict(snap("reading", "20261107T011021Z-5e909443", size=102),
                       snap("reading", "20261107T011021Z-5e909443", size=101), TODAY)
        self.assertFalse(v["jam"])
        self.assertIn("the pile fell", v["why"])

    def test_a_reading_head_with_the_same_pile_is_a_jam(self):
        v = cj.verdict(snap("reading", "20261107T011021Z-5e909443", size=102),
                       snap("reading", "20261107T011021Z-5e909443", size=102), TODAY)
        self.assertTrue(v["jam"])

    def test_a_value_item_that_is_the_head_and_unworked_is_a_jam(self):
        v = cj.verdict(snap("value", "history-long-piece", None),
                       snap("value", "history-long-piece", None), TODAY)
        self.assertTrue(v["jam"])
        self.assertIn("no clock will move it", v["why"])

    def test_a_calendar_whose_next_row_is_in_the_future_is_waiting_not_due(self):
        v = cj.verdict(snap("waiting", "weekly letter", "2026-11-26"),
                       snap("waiting", "weekly letter", "2026-11-26"), TODAY)
        self.assertFalse(v["jam"])
        self.assertIn("waiting rather than stuck", v["why"])

    def test_an_empty_agenda_is_a_jam_not_a_rest(self):
        v = cj.verdict(snap("none", ""), snap("none", ""), TODAY)
        self.assertTrue(v["jam"])
        self.assertIn("defect, not a rest", v["why"])

    def test_the_head_of_this_repository_is_readable(self):
        head = cj.head("desi")
        self.assertIn(head["block"], ("due", "review", "reading", "value", "waiting", "none"))


class Head(unittest.TestCase):
    """What the head is, on a fixture whose only content is a calendar row six days out.

    The old `head()` called that row the head and stopped, so the check could never reach the queue
    the wake actually works. Pinned here: a soon row is `waiting`, and a due row still outranks
    everything.
    """

    def setUp(self):
        import tempfile
        self.dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.dir.name) / "repo"
        (self.repo / "to-do-lists").mkdir(parents=True)
        (self.repo / "channels").mkdir()
        (self.repo / "scripts").mkdir()
        (self.repo / "channels" / "items.jsonl").write_text("", encoding="utf-8")
        (self.repo / "channels" / "wake_engine.py").write_text(
            (ROOT / "channels" / "wake_engine.py").read_text(encoding="utf-8"), encoding="utf-8")
        (self.repo / "channels" / "item_ledger.py").write_text(
            (ROOT / "channels" / "item_ledger.py").read_text(encoding="utf-8"), encoding="utf-8")
        (self.repo / "scripts" / "value_queue.py").write_text(
            (ROOT / "scripts" / "value_queue.py").read_text(encoding="utf-8"), encoding="utf-8")
        (self.repo / "channels" / "value-queue.json").write_text(
            '{"items": [{"id": "essay", "title": "long piece", "status": "open", "done_when": "a page a stranger reads"}]}',
            encoding="utf-8")

    def tearDown(self):
        self.dir.cleanup()

    def test_a_row_six_days_out_leaves_the_value_queue_as_the_head(self):
        (self.repo / "to-do-lists" / "desi.md").write_text(
            "- [ ] 2026-11-26 — Weekly: one letter to a person outside the commons\n", encoding="utf-8")
        h = cj.head("desi", repo=self.repo, today=TODAY)
        self.assertEqual(h["block"], "value")
        self.assertEqual(h["id"], "essay")

    def test_a_row_due_today_outranks_the_value_queue(self):
        (self.repo / "to-do-lists" / "desi.md").write_text(
            "- [ ] 2026-11-19 — Weekly: one letter to a person outside the commons\n", encoding="utf-8")
        h = cj.head("desi", repo=self.repo, today=TODAY)
        self.assertEqual(h["block"], "due")

    def test_a_named_unread_item_still_reports_the_size_of_the_whole_pile(self):
        """Fixed 2026-11-23 (Desi). `whole` was computed only when this seat had nothing named, so
        a seat with a named unread item reported `size: 0` — and the pile-fell rule in `verdict()`,
        the only thing that can tell a healthy night from an idle one, could never fire there.
        Measured on the live ledger: head 20261121T193324Z-b2064d65, size 0, a hundred items unread.
        """
        import json
        (self.repo / "to-do-lists" / "desi.md").write_text("# nothing due\n", encoding="utf-8")
        rows = [
            {"id": "readmine", "amigo": "claude", "filed_utc": "2026-11-15T17:10:52Z",
             "state": "accomplished", "reviewer": "auto:path",
             "reading_assigned_to": "desi", "short_title": "carries my name"},
            {"id": "readother", "amigo": "gemini", "filed_utc": "2026-11-18T17:10:52Z",
             "state": "accomplished", "reviewer": "auto:path",
             "reading_assigned_to": "dmitri", "short_title": "somebody else's"},
        ]
        (self.repo / "channels" / "items.jsonl").write_text(
            "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        h = cj.head("desi", repo=self.repo, today=TODAY)
        self.assertEqual(h["block"], "reading")
        self.assertEqual(h["id"], "readmine")
        self.assertEqual(h["size"], 2)
        # and with that size, the pile-fell rule can actually fire
        after = dict(h, size=1)
        self.assertFalse(cj.verdict(h, after, TODAY)["jam"])

    def test_nothing_due_and_no_value_item_is_waiting_only_if_a_date_exists(self):
        (self.repo / "channels" / "value-queue.json").write_text('{"items": []}', encoding="utf-8")
        (self.repo / "to-do-lists" / "desi.md").write_text(
            "- [ ] 2026-11-26 — Weekly: one letter\n", encoding="utf-8")
        h = cj.head("desi", repo=self.repo, today=TODAY)
        self.assertEqual(h["block"], "waiting")
        (self.repo / "to-do-lists" / "desi.md").write_text("# nothing\n", encoding="utf-8")
        self.assertEqual(cj.head("desi", repo=self.repo, today=TODAY)["block"], "none")


if __name__ == "__main__":
    unittest.main()
