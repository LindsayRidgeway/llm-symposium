#!/usr/bin/env python3
"""The value queue: a head, and a rule that closes it — added 2026-11-19.

The founder's question is the whole reason this file exists: *three wakes have gone into one piece of
research; will your wakes ever move on to a different value-work item?* The measured answer was no —
review work rotates because the draw assigns it, value work had no owner of its pointer, so a wake
picked what was already at the front of its own prompt and the front did not change.

Pinned here: a head exists and is shown with its closing condition; an item cannot be closed without
an artefact; closing moves the pointer; an empty queue is a defect rather than a rest; and the block
arrives through orientation(), not only through a helper.
"""
import datetime
import importlib.util
import json
import sys
import tempfile
import pathlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import value_queue as vq  # noqa: E402

QUEUE = {"items": [
    {"id": "a", "title": "first thing", "done_when": "an artefact exists",
     "status": "in-progress", "progress": "half"},
    {"id": "b", "title": "second thing", "done_when": "another artefact", "status": "open"},
]}


class ValueQueue(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "value-queue.json"
        self.path.write_text(json.dumps(QUEUE), encoding="utf-8")

    def tearDown(self):
        self.dir.cleanup()

    def test_the_head_is_the_first_open_item_with_its_closing_condition(self):
        text = (vq.load(self.path), vq.head(vq.load(self.path)))
        data, item = text
        self.assertEqual(item["id"], "a")
        self.assertEqual(item["done_when"], "an artefact exists")

    def test_working_an_item_pushes_it_to_the_back_even_unfinished(self):
        """The founder's follow-up, 2026-11-19: closure and rotation are different jobs.

        A task may never finish; it must not therefore hold the head for a week. Push-to-bottom is
        the rule the to-do lists already use for repeats.
        """
        first = vq.head(vq.load(self.path))["id"]
        vq.worked(first, "did a slice", path=self.path)
        self.assertEqual(vq.head(vq.load(self.path))["id"], "b")
        data = vq.load(self.path)
        self.assertEqual([i["id"] for i in data["items"]], ["b", "a"])

    def test_working_an_item_records_a_date_and_a_note(self):
        vq.worked("a", "read two rows", path=self.path)
        item = [i for i in vq.load(self.path)["items"] if i["id"] == "a"][0]
        self.assertEqual(item["last_worked"], datetime.date.today().isoformat())
        self.assertIn("read two rows", item["progress"])
        self.assertIn("half", item["progress"])          # the earlier progress is kept

    def test_working_something_that_is_not_there_is_an_error(self):
        with self.assertRaises(LookupError):
            vq.worked("nope", "x", path=self.path)

    def test_closing_an_item_moves_the_pointer(self):
        vq.done("a", "research/x.md", path=self.path)
        self.assertEqual(vq.head(vq.load(self.path))["id"], "b")

    def test_an_item_cannot_be_closed_without_an_artefact(self):
        with self.assertRaises(ValueError):
            vq.done("a", "   ", path=self.path)

    def test_closing_something_that_is_not_there_is_an_error(self):
        with self.assertRaises(LookupError):
            vq.done("nope", "research/x.md", path=self.path)

    def test_the_repository_queue_is_not_empty(self):
        """An empty value queue means wakes have nothing to make and will read until someone notices."""
        data = vq.load(ROOT / "channels" / "value-queue.json")
        self.assertTrue(vq.head(data), "the value queue is empty")
        for item in data["items"]:
            self.assertTrue(item.get("done_when"), f"{item['id']} has no closing condition")

    def test_orientation_carries_the_value_head(self):
        spec = importlib.util.spec_from_file_location("we_vq", ROOT / "channels" / "wake_engine.py")
        we = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(we)                 # type: ignore[union-attr]
        we.AMIGO = "desi"
        text = we.orientation(str(ROOT), str(ROOT))
        self.assertIn("=== YOUR VALUE QUEUE", text)
        self.assertIn("closes when:", text)
        self.assertIn("value_queue.py --done", text)

    def test_filing_an_item_puts_it_at_the_back_and_does_not_move_the_head(self):
        vq.add("c", "third thing", "something that finishes it", path=self.path)
        data = vq.load(self.path)
        self.assertEqual([i["id"] for i in data["items"]], ["a", "b", "c"])
        self.assertEqual(vq.head(data)["id"], "a")
        self.assertEqual(data["items"][-1]["status"], "open")

    def test_an_item_cannot_be_filed_without_the_condition_that_closes_it(self):
        """The queue's own header rule, applied to the door items come in by.

        An item with no closing condition is a project; the queue already refuses to *show* one at
        the head as work, and it must not be able to *become* one either.
        """
        with self.assertRaises(ValueError):
            vq.add("c", "third thing", "   ", path=self.path)

    def test_an_item_needs_a_title_and_an_id(self):
        with self.assertRaises(ValueError):
            vq.add("  ", "third thing", "closes when x", path=self.path)
        with self.assertRaises(ValueError):
            vq.add("c", "", "closes when x", path=self.path)

    def test_filing_an_id_that_exists_is_refused_not_merged(self):
        with self.assertRaises(ValueError):
            vq.add("a", "the same thing again", "closes when x", path=self.path)

    def test_closing_the_last_item_empties_the_queue_and_filing_a_successor_refills_it(self):
        """The exact state that got three landings refused, pinned (2026-11-21, Desi).

        `done()` and the repository test have met at one item since the queue was written in
        2026-11-19: closing moves the pointer, and `test_the_repository_queue_is_not_empty` refuses
        the empty queue that the last close produces. Runs 20261121T004751Z, 20261121T024804Z and
        20261120T224733Z each did the good work and were refused on this file, and nothing in the
        tool named the missing half until the warning above was added — with no command to run.
        """
        for item_id in ("a", "b"):
            vq.done(item_id, "research/%s.md" % item_id, path=self.path)
        self.assertIsNone(vq.head(vq.load(self.path)),
                          "closing every item must leave no head — that is the state to repair")
        vq.add("c", "the successor", "one artefact a stranger can read", path=self.path)
        self.assertEqual(vq.head(vq.load(self.path))["id"], "c")

    def test_the_repository_queue_still_has_a_head_and_every_item_a_closing_condition(self):
        """Holds `test_the_repository_queue_is_not_empty`'s subject on the real file (unchanged
        behaviour), so a diff that drains it fails here first and with a name."""
        data = vq.load(ROOT / "channels" / "value-queue.json")
        self.assertTrue(data["items"])
        self.assertIsNotNone(vq.head(data))

    def test_the_add_command_is_in_the_prompt_not_only_in_the_tool(self):
        """The retention.py lesson: a command a wake is told about in a warning it never reaches is
        the same as no command. The prompt block is where the wake reads it."""
        spec = importlib.util.spec_from_file_location("we_vq3", ROOT / "channels" / "wake_engine.py")
        we = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(we)                 # type: ignore[union-attr]
        text = we.value_block(str(ROOT), amigo="desi")
        self.assertIn("value_queue.py --add", text)
        self.assertIn("--closes", text)

    def test_the_prompt_names_the_record_command_not_only_the_closing_one(self):
        """2026-11-20 (Desi): the block named only `--done`, so a wake that advanced the head and
        did not finish it left no record, the age still read "never worked", and the founder's
        procedure called the night jammed. Same defect as the calendar's: the command existed and
        the prompt that needed it did not print it.
        """
        spec = importlib.util.spec_from_file_location("we_vq2", ROOT / "channels" / "wake_engine.py")
        we = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(we)                 # type: ignore[union-attr]
        text = we.value_block(str(ROOT), amigo="desi")
        self.assertIn("value_queue.py --worked", text)
        self.assertIn("value_queue.py --done", text)


class TheStepIsOneConsistentStep(unittest.TestCase):
    """The prompt has to say what the gate will accept, or the gate refuses what the prompt asked for.

    Added 2026-11-25 (Desi), from the measurement: two wakes in a row took the same value head, spent
    1.18M and 1.60M tokens, were cut off at the action cap, and were refused for nine assertions that
    restated counts the generator had already moved. What they had finished — three rows read against
    their primaries, a hundred lines of working — landed nowhere, and the queue counted the two days
    as "not worked". The line is cheap; the alternative is a queue that cannot tell a busy wake from
    an idle one.
    """

    def test_the_block_names_the_cost_of_a_refused_landing(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("we_step", ROOT / "channels" / "wake_engine.py")
        we = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(we)
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            (pathlib.Path(d) / "channels").mkdir()
            (pathlib.Path(d) / "channels" / "value-queue.json").write_text(json.dumps(
                {"items": [{"id": "x", "title": "a thing", "status": "open",
                            "done_when": "the thing exists"}]}), encoding="utf-8")
            text = we.value_block(d, amigo="desi")
        self.assertIn("one consistent step", text)
        self.assertIn("action cap", text)
        self.assertIn("regenerate the artefact", text)


if __name__ == "__main__":
    unittest.main()
