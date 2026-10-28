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
import contextlib
import io
import os
from pathlib import Path
from unittest import mock

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


class ImmutableStaging(unittest.TestCase):
    def items(self, title="First request"):
        return sweep.parse(fixture(requested="2026-10-17").replace(
            "An item the commons has finished with", title))

    def stage(self, root, queue, *extra):
        output = io.StringIO()
        with mock.patch.object(sweep, "REPO_ROOT", Path(root)), mock.patch.object(
                sys, "argv", ["sweep", "--stage", "--path", str(queue), *extra]), contextlib.redirect_stdout(output):
            self.assertEqual(sweep.main(), 0)
        return output.getvalue()

    def test_same_day_cohorts_keep_both_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = sweep.write_note(self.items(), "2026-10-28", root=tmp)
            before = (Path(tmp) / first).read_bytes()
            second = sweep.write_note(self.items("Second request"), "2026-10-28", root=tmp)
            self.assertNotEqual(first, second)
            self.assertEqual((Path(tmp) / first).read_bytes(), before)
            self.assertIn("Second request", (Path(tmp) / second).read_text())

    def test_identical_retry_does_not_rewrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            rel = sweep.write_note(self.items(), "2026-10-28", root=tmp)
            path = Path(tmp) / rel
            os.utime(path, ns=(1, 1))
            self.assertEqual(sweep.write_note(self.items(), "2026-10-28", root=tmp), rel)
            self.assertEqual(path.stat().st_mtime_ns, 1)

    def test_conflicting_existing_content_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            rel = sweep.write_note(self.items(), "2026-10-28", root=tmp)
            path = Path(tmp) / rel
            path.write_text("retained conflicting bytes")
            with self.assertRaises(ValueError):
                sweep.write_note(self.items(), "2026-10-28", root=tmp)
            self.assertEqual(path.read_text(), "retained conflicting bytes")

    def test_record_note_preserves_existing_pointers_without_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            queue = Path(tmp) / "queue.md"
            original = fixture(requested="2026-10-17", note="notes/old.md")
            queue.write_text(original)
            title = sweep.parse(original)[0]["title"]
            sweep.record_note(queue, [title], "notes/new.md")
            sweep.record_note(queue, [title], "notes/new.md")
            self.assertEqual(queue.read_text(), original)

    def test_stage_of_noted_requests_is_a_true_noop(self):
        with tempfile.TemporaryDirectory() as tmp:
            queue = Path(tmp) / "queue.md"
            original = fixture(requested="2026-10-17", note="notes/old.md")
            queue.write_text(original)
            output = self.stage(tmp, queue)
            self.assertIn("nothing written", output)
            self.assertEqual(queue.read_text(), original)
            self.assertEqual(list(Path(tmp).rglob("*.md")), [queue])

    def test_two_staging_passes_only_add_the_new_cohort(self):
        with tempfile.TemporaryDirectory() as tmp:
            queue = Path(tmp) / "queue.md"
            queue.write_text(fixture(requested="2026-10-17").replace(
                "An item the commons has finished with", "First request"))
            self.stage(tmp, queue)
            first = sweep.parse(queue.read_text())[0]
            first_bytes = (Path(tmp) / first["note"]).read_bytes()
            with queue.open("a") as fh:
                fh.write("\n" + fixture(requested="2026-10-17").replace(
                    "An item the commons has finished with", "Second request"))
            self.stage(tmp, queue)
            items = sweep.parse(queue.read_text())
            self.assertEqual((Path(tmp) / first["note"]).read_bytes(), first_bytes)
            self.assertNotEqual(items[0]["note"], items[1]["note"])
            second_text = (Path(tmp) / items[1]["note"]).read_text()
            self.assertIn("Second request", second_text)
            self.assertNotIn("First request", second_text)
            self.assertEqual(queue.read_text().count("- steward-note:"), 2)

    def test_same_titles_are_checked_per_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            queue = Path(tmp) / "queue.md"
            queue.write_text(fixture(requested="2026-10-17", note="old.md") +
                             "\n" + fixture(requested="2026-10-18"))
            title = sweep.parse(queue.read_text())[0]["title"]
            sweep.record_note(queue, [title], "new.md")
            self.assertEqual([i["note"] for i in sweep.parse(queue.read_text())],
                             ["old.md", "new.md"])

    def test_fenced_example_note_is_not_an_existing_pointer(self):
        with tempfile.TemporaryDirectory() as tmp:
            queue = Path(tmp) / "queue.md"
            original = fixture(requested="2026-10-17")
            original = original.replace("- steward-requested:",
                                        "```\n- steward-note: example.md\n```\n- steward-requested:")
            queue.write_text(original)
            title = sweep.parse(original)[0]["title"]
            sweep.record_note(queue, [title], "real.md")
            self.assertEqual(sweep.parse(queue.read_text())[0]["note"], "real.md")
            self.assertIn("```\n- steward-note: example.md\n```", queue.read_text())

    def test_mark_and_stage_together_do_not_duplicate_new_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            queue = Path(tmp) / "queue.md"
            queue.write_text(fixture())
            self.stage(tmp, queue, "--mark")
            self.assertEqual(queue.read_text().count("- steward-note:"), 1)
            self.assertEqual(len(list((Path(tmp) / "channels/steward-notes").glob("*.md"))), 1)
            self.assertEqual(len(sweep.undelivered(sweep.parse(queue.read_text()))), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
