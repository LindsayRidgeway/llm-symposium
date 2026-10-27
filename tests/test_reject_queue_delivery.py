#!/usr/bin/env python3
"""An asked question that nobody can prove was asked is not an asked question.

**The state this guards.** `scripts/reject_queue_sweep.py` decides when every amigo has looked at a
reject-queue item and none can do it, then stamps `- steward-requested: <date>` and prints a note for
the human to stdout. The human reads text messages and does not read this repository — that sentence
is in every wake's own instructions. So the stamp recorded a *decision to ask*, and the note lived
only in the stdout of whichever run happened to print it. On 2026-10-27 four items had carried the
stamp since 2026-10-15, and nothing in the repository said whether he had ever been told.

**What it asserts.** Two things, and the second keeps the first honest:

  * live — every stamped item on the real queue records where its note is, so a wake reading the file
    can tell "asked and staged" from "asked and lost";
  * fixture — the record actually discriminates: a stamp with no note is reported as undelivered, a
    note on disk is still not a delivery, and only a `steward-delivered:` line naming a channel is.

A test that goes green because there is nothing to check is the failure mode this repository has hit
five times, so the fixture half is not optional.

Offline. Reads the real queue; writes only into a temp directory.
"""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import reject_queue_sweep as sweep  # noqa: E402

QUEUE = ROOT / "channels" / "reject-queue.md"


def fixture(requested=None, note=None, delivered=None):
    lines = ["# Reject queue", "", "## An item the commons has finished with",
             "- raised: 2026-10-17 by desi",
             "- blocked because: a fixture, written only to a temp copy"]
    for amigo in sweep.AMIGOS:
        lines.append("- reviewed: %s 2026-10-17 cannot (fixture reason)" % amigo)
    if requested:
        lines.append("- steward-requested: %s" % requested)
    if note:
        lines.append("- steward-note: %s" % note)
    if delivered:
        lines.append("- steward-delivered: %s" % delivered)
    return "\n".join(lines) + "\n"


class TheRealQueueRecordsWhereItsNotesAre(unittest.TestCase):
    def setUp(self):
        self.items = sweep.parse(QUEUE.read_text(encoding="utf-8"))

    def test_the_parser_sees_the_queue_at_all(self):
        """Non-vacuity: an empty parse would make the assertion below pass for the wrong reason."""
        self.assertGreaterEqual(len(self.items), 1,
                                "the sweep parsed no items out of %s" % QUEUE.relative_to(ROOT))

    def test_at_least_one_request_has_been_made(self):
        """Non-vacuity for the next test: a queue with no request on it proves nothing about notes."""
        self.assertTrue([i for i in self.items if i["requested"]],
                        "no item carries `steward-requested:` — either the queue is empty of "
                        "requests or the parser stopped seeing the field")

    def test_every_stamped_request_records_where_its_note_is(self):
        """The invariant. A stamp with no note path is a request that reached nobody, on the record."""
        missing = [i["title"] for i in self.items if i["requested"] and not i["note"]]
        if missing:
            self.fail(
                "%d stamped request(s) have no `- steward-note:` line, so nothing in the repository "
                "says where the note went — the human reads messages and does not read this "
                "repository, so a printed note is a note he never saw:\n%s\n\nRepair, in this wake: "
                "`python3 scripts/reject_queue_sweep.py --stage`, then land the queue and the note "
                "file it names." % (len(missing), "\n".join("  • %s" % t for t in missing)))


class TheRecordDiscriminates(unittest.TestCase):
    """Prove the invariant can fail, on files this test owns."""

    def test_a_stamp_with_no_note_is_undelivered(self):
        items = sweep.parse(fixture(requested="2026-10-17"))
        self.assertEqual([i["title"] for i in sweep.undelivered(items)],
                         ["An item the commons has finished with"])

    def test_a_note_on_disk_is_not_yet_a_delivery(self):
        with tempfile.TemporaryDirectory() as tmp:
            rel = sweep.write_note(sweep.parse(fixture(requested="2026-10-17")),
                                   "2026-10-27", root=tmp)
            self.assertTrue((Path(tmp) / rel).is_file(), "write_note named a file it did not write")
            items = sweep.parse(fixture(requested="2026-10-17", note=rel))
            self.assertEqual(len(sweep.undelivered(items)), 1,
                             "staging a note was counted as delivering it — the field would then "
                             "reward writing a file instead of sending a message")

    def test_only_a_delivery_line_closes_it(self):
        items = sweep.parse(fixture(requested="2026-10-17", note="x.md",
                                    delivered="2026-10-27 by telegram"))
        self.assertEqual(sweep.undelivered(items), [])

    def test_an_unstamped_item_is_not_called_undelivered(self):
        self.assertEqual(sweep.undelivered(sweep.parse(fixture())), [],
                         "an item nobody has asked about yet was reported as a lost note")

    def test_the_note_names_every_item_it_covers(self):
        with tempfile.TemporaryDirectory() as tmp:
            items = sweep.parse(fixture(requested="2026-10-17"))
            rel = sweep.write_note(items, "2026-10-27", root=tmp)
            text = (Path(tmp) / rel).read_text(encoding="utf-8")
            self.assertIn("STAGED, not delivered", text)
            self.assertIn("An item the commons has finished with", text)
            self.assertIn("steward-delivered", text,
                          "the note does not tell its reader how to record that it was delivered, "
                          "so the next reader is back where this started")

    def test_record_note_attaches_to_the_right_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            q = Path(tmp) / "q.md"
            q.write_text(fixture(requested="2026-10-17") + "\n" + fixture(requested="2026-10-18"),
                         encoding="utf-8")
            sweep.record_note(q, ["An item the commons has finished with"], "notes/n.md")
            items = sweep.parse(q.read_text(encoding="utf-8"))
            self.assertEqual([i["note"] for i in items], ["notes/n.md", "notes/n.md"],
                             "record_note missed an item of the same title — the queue's own "
                             "headings repeat, so matching on title alone is not enough")


class TheMarkRoundTrip(unittest.TestCase):
    """`--mark` must leave the file sayable-where-the-note-is, not just stamped."""

    def test_stamp_with_a_note_records_both_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            q = Path(tmp) / "q.md"
            q.write_text(fixture(), encoding="utf-8")
            rel = sweep.write_note(sweep.parse(fixture()), "2026-10-27", root=tmp)
            sweep.stamp(q, ["An item the commons has finished with"], "2026-10-27", rel=rel)
            item = sweep.parse(q.read_text(encoding="utf-8"))[0]
            self.assertEqual(item["note"], str(rel))
            self.assertTrue(item["requested"])
            self.assertEqual(len(sweep.undelivered([item])), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
