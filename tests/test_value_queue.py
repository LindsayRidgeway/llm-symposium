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
import importlib.util
import json
import sys
import tempfile
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


if __name__ == "__main__":
    unittest.main()
