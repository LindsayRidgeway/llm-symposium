#!/usr/bin/env python3
"""The Drive bridge probe: the letterbox is either delivering or it is not, and it must say which.

The probe reads a folder and nothing else, so every case can be built in a temporary directory —
including the two that matter most. An orphan (a `.gdoc` pointer with no markdown beside it) is a
handoff that was staged and never converted, which is the failure the folder of 2026-10-19 actually
contained. A stale folder is the reading that is indistinguishable from a quiet participant, which
is the whole reason the probe exists.

The one case that cannot be faked is the real folder on this Mac; it is asserted only when present,
and it asserts a property of the *tool* rather than a fact about the bridge, so a real orphan never
turns the suite red.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "drive_bridge_status.py")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import drive_bridge_status as probe  # noqa: E402

NOW = 1_700_000_000.0
HOUR = 3600.0


def touch(path, mtime, body="x"):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)
    os.utime(path, (mtime, mtime))


class LetterboxCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def handoff(self, name, age_hours, now=NOW):
        """A converted handoff: the pointer Drive leaves, plus the markdown the script wrote."""
        stamp = now - age_hours * HOUR
        touch(os.path.join(self.root, name + ".gdoc"), stamp, "pointer")
        touch(os.path.join(self.root, name), stamp + 30, "converted")

    def orphan(self, name, age_hours, now=NOW):
        touch(os.path.join(self.root, name + ".gdoc"), now - age_hours * HOUR, "pointer")


class TestHealthy(LetterboxCase):
    def test_a_recent_converted_handoff_is_ok(self):
        self.handoff("Handoff - Stewardship.md", 2)
        facts = probe.survey(self.root, max_age_hours=72, now=NOW)
        self.assertEqual(facts["state"], "OK")
        self.assertEqual(facts["handoffs"][0]["name"], "Handoff - Stewardship.md")
        self.assertEqual(facts["orphans"], [])
        self.assertAlmostEqual(facts["freshest_age_hours"], 2.0, delta=0.1)

    def test_the_pointer_and_its_markdown_are_one_handoff_not_two(self):
        self.handoff("Handoff - One.md", 1)
        facts = probe.survey(self.root, now=NOW)
        self.assertEqual(len(facts["handoffs"]), 1)
        self.assertEqual(facts["orphans"], [])

    def test_non_handoff_files_are_ignored(self):
        self.handoff("Handoff - One.md", 1)
        touch(os.path.join(self.root, "Receipt - Hand-Off Executed.txt"), NOW - HOUR)
        facts = probe.survey(self.root, now=NOW)
        self.assertEqual(len(facts["handoffs"]), 1)
        self.assertEqual(facts["state"], "OK")


class TestFailuresThatLookLikeSilence(LetterboxCase):
    def test_pointer_without_markdown_is_an_orphan(self):
        # This is the shape of the real `...(1).md.gdoc` left on 2026-10-16.
        self.orphan("Milestone - Architecture (1).md", 20)
        facts = probe.survey(self.root, now=NOW)
        self.assertEqual(facts["state"], "ORPHANS")
        self.assertEqual(facts["orphans"][0]["expected"], "Milestone - Architecture (1).md")

    def test_an_orphan_outranks_a_fresh_handoff(self):
        self.handoff("Handoff - New.md", 1)
        self.orphan("Handoff - Stuck.md", 40)
        facts = probe.survey(self.root, now=NOW)
        self.assertEqual(facts["state"], "ORPHANS")
        self.assertEqual(facts["freshest"], "Handoff - New.md")

    def test_a_folder_older_than_the_threshold_is_stale(self):
        self.handoff("Handoff - Old.md", 100)
        facts = probe.survey(self.root, max_age_hours=72, now=NOW)
        self.assertEqual(facts["state"], "STALE")
        self.assertGreater(facts["freshest_age_hours"], 72)

    def test_a_quiet_folder_says_it_cannot_tell_quiet_from_broken(self):
        self.handoff("Handoff - Old.md", 200)
        facts = probe.survey(self.root, max_age_hours=72, now=NOW)
        joined = " ".join(facts["notes"]).lower()
        self.assertIn("either nothing has been handed over", joined)
        self.assertIn("same reading", joined)

    def test_an_empty_folder_is_stale_not_ok(self):
        facts = probe.survey(self.root, now=NOW)
        self.assertEqual(facts["state"], "STALE")
        self.assertIsNone(facts["freshest"])
        self.assertIsNone(facts["freshest_age_hours"])

    def test_a_missing_folder_is_absent_and_names_the_likely_cause(self):
        facts = probe.survey(os.path.join(self.root, "no-such-folder"), now=NOW)
        self.assertEqual(facts["state"], "ABSENT")
        self.assertFalse(facts["exists"])
        self.assertIn("signed in", " ".join(facts["notes"]))

    def test_the_threshold_is_a_knob_not_a_constant(self):
        self.handoff("Handoff - TwoDays.md", 48)
        self.assertEqual(probe.survey(self.root, max_age_hours=72, now=NOW)["state"], "OK")
        self.assertEqual(probe.survey(self.root, max_age_hours=24, now=NOW)["state"], "STALE")


class TestCommandLine(LetterboxCase):
    """The child process reads the real clock, so these fixtures are stamped against it."""

    def run_probe(self, *args):
        return subprocess.run(
            [sys.executable, SCRIPT, *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_healthy_folder_exits_zero(self):
        self.handoff("Handoff - Now.md", 0.1, now=time.time())
        result = self.run_probe("--root", self.root)
        self.assertEqual(result.returncode, probe.OK, result.stderr)
        self.assertIn("state: OK", result.stdout)

    def test_orphan_exits_one(self):
        self.orphan("Handoff - Stuck.md", 1)
        result = self.run_probe("--root", self.root)
        self.assertEqual(result.returncode, probe.ANOMALY)
        self.assertIn("state: ORPHANS", result.stdout)

    def test_missing_folder_exits_two(self):
        result = self.run_probe("--root", os.path.join(self.root, "gone"))
        self.assertEqual(result.returncode, probe.ABSENT)

    def test_json_output_is_parseable_and_carries_the_state(self):
        self.handoff("Handoff - Now.md", 0.1, now=time.time())
        result = self.run_probe("--root", self.root, "--json")
        facts = json.loads(result.stdout)
        self.assertEqual(facts["state"], "OK")
        self.assertIn("orphans", facts)


def mount_unreadable(facts):
    """True when the tool could not read the folder *at the moment it read it*.

    Why this is a function and not two lines inside the test (2026-10-19): this file was the one
    named when run 20261019T110921Z was refused at the landing gate, and the cause is here. The
    old test asked `os.path.isdir()` and then called `survey()` — but Drive for Desktop can drop
    the mount between those two calls, and when it does `survey()` correctly returns state
    `ABSENT` instead of raising, so the assertion saw `ABSENT` and called the tool wrong. A test
    that reads a cloud-mount cannot tell "the bridge is broken" from "the mount blinked", and a
    landing gate that refuses on a blink is a gate that fails for reasons the diff did not cause.

    The distinction the test is allowed to make is narrower, and it is the true one: if the OS
    could not read the folder either, the tool cannot be judged — skip. If the OS read it and the
    tool disagreed, that is a real defect — fail.
    """
    if not facts.get("exists"):
        return True
    return any("cannot be listed" in note for note in facts.get("notes", []))


class TestTheRealFolderWhenItIsThere(unittest.TestCase):
    """Assert the tool's behaviour on this Mac, never the bridge's health."""

    def test_the_default_path_points_at_a_drive_cloudstorage_folder(self):
        self.assertIn("CloudStorage", probe.DEFAULT_ROOT)
        self.assertTrue(probe.DEFAULT_ROOT.endswith("LLM Symposium Handoffs"))

    def test_a_mount_that_vanishes_is_unreadable_not_a_verdict(self):
        absent = probe.survey(os.path.join(self.id().replace(".", "_"), "not-here"))
        self.assertTrue(mount_unreadable(absent))
        unlistable = {"exists": True, "notes": ["folder exists but cannot be listed: [Errno 5]"]}
        self.assertTrue(mount_unreadable(unlistable))
        for state in ("OK", "STALE", "ORPHANS"):
            self.assertFalse(mount_unreadable({"exists": True, "state": state, "notes": []}), state)

    def test_the_real_folder_yields_a_definite_state(self):
        if not os.path.isdir(probe.DEFAULT_ROOT):
            self.skipTest("the Drive folder is not on this machine")
        facts = probe.survey(probe.DEFAULT_ROOT)
        if mount_unreadable(facts):
            self.skipTest("the Drive mount was not readable when the tool read it — nothing to judge")
        self.assertIn(facts["state"], {"OK", "STALE", "ORPHANS"})
        for orphan in facts["orphans"]:
            self.assertFalse(
                os.path.exists(os.path.join(facts["root"], orphan["expected"])),
                "an orphan was reported for a markdown file that exists",
            )


if __name__ == "__main__":
    unittest.main()


class TestReceiptsAreClaimsNotConversions(LetterboxCase):
    """A `Receipt …txt` in the folder is written by whoever read a handoff, never by the script.

    The real folder contained one saying `Status: Delivered & Verified` beside a pointer that had
    never converted in three days, so a reader looking for "is the bridge working" got the answer to
    a different question. The probe must show the claim and say which of the two it is.
    """

    def receipt(self, name, body, age_hours=1, now=NOW):
        touch(os.path.join(self.root, name), now - age_hours * HOUR, body)

    def test_a_receipt_is_not_counted_as_a_handoff(self):
        self.handoff("Handoff - One.md", 1)
        self.receipt(
            "Receipt - Hand-Off Executed.txt",
            "[Goose-Execution-Receipt]\nStatus: Delivered & Verified\n"
            "Source File: Handoff - One.md\n",
        )
        facts = probe.survey(self.root, now=NOW)
        self.assertEqual(len(facts["handoffs"]), 1)
        self.assertEqual(len(facts["receipts"]), 1)
        self.assertEqual(facts["receipts"][0]["status"], "Delivered & Verified")
        self.assertTrue(facts["receipts"][0]["source_present"])

    def test_a_receipt_claiming_an_absent_source_is_flagged(self):
        self.orphan("Milestone - Architecture (1).md", 60)
        self.receipt(
            "Receipt - Hand-Off Executed.txt",
            "[Goose-Execution-Receipt]\nStatus: Delivered & Verified\n"
            "Source File: Milestone - Gone.md\n",
        )
        facts = probe.survey(self.root, now=NOW)
        self.assertFalse(facts["receipts"][0]["source_present"])
        joined = " ".join(facts["notes"]).lower()
        self.assertIn("claims delivery of 'milestone - gone.md'", joined)
        self.assertIn("not by the script", joined)
        # The claim does not change the verdict; the missing markdown is what does.
        self.assertEqual(facts["state"], "ORPHANS")

    def test_a_receipt_with_no_source_line_is_not_flagged(self):
        self.handoff("Handoff - One.md", 1)
        self.receipt("Receipt - Note.txt", "Status: Delivered & Verified\n")
        facts = probe.survey(self.root, now=NOW)
        self.assertIsNone(facts["receipts"][0]["source"])
        self.assertFalse([n for n in facts["notes"] if "receipt" in n.lower()])
        self.assertEqual(facts["state"], "OK")
