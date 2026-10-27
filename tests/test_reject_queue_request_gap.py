#!/usr/bin/env python3
"""The reject queue must not hold a mature item that nobody was ever asked about.

**The gap this closes.** `scripts/reject_queue_sweep.py` decides when every amigo has looked at an
item and none can do it, at which point the item becomes a request for the human's judgement and the
request is stamped into `channels/reject-queue.md`. On 2026-10-17 Desi measured that this had never
once happened: four items carried five reasoned verdicts and no `steward-requested:` line, so the
queue had silently matured four requests the human never heard about. The cause was structural —
`--mark` is only ever called from a private bot file that no wake may edit — and the repair was to
stamp the four and add a check that fails loudly if the state recurs.

That check is `tests/test_reject_queue_request_gap.py`. It was named in the run's report and in its
LAND line, and it never reached `main`; the stamping did. So for a day the queue was correct and the
guard against it going wrong again did not exist, which is the shape this repository has now found
five times (a guard named by an artefact and never run).

**What it asserts, and the difference from `tests/test_reject_queue_sweep.py`.** That test checks the
*shape* of the instrument: the parser, the roster arithmetic, stray review lines, a stamp round-trip.
Its readiness assertions are deliberately scoped to synthetic fixtures, because until 2026-10-15 the
real queue's readiness was the broken thing and a test that iterates `ready()` passes for free when
that list is empty. This file asserts the *live invariant* on the real file — no item may be mature
and unasked — and then proves that assertion is not vacuous by making a fixture mature it. A test
that goes green because it sees nothing is the failure mode both files were written against.

**What to do when it goes red.** Do not weaken the assertion. Run
`python3 scripts/reject_queue_sweep.py --mark`, which stamps the items and prints the note for the
human, and land the stamped `channels/reject-queue.md` in the same wake. The point of the red build
is that the stamping is not allowed to wait for someone to remember to look.

Offline. Reads the real queue; writes only to a temp copy.
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


def fixture(verdicts, requested=None):
    """One item with `verdicts` reasoned reviews, optionally already stamped."""
    lines = ["# Reject queue", "", "## An item the commons has finished with",
             "- raised: 2026-10-17 by desi",
             "- blocked because: a fixture, written only to a temp copy"]
    for amigo in sweep.AMIGOS[:verdicts]:
        lines.append("- reviewed: %s 2026-10-17 cannot (fixture reason)" % amigo)
    if requested:
        lines.append("- steward-requested: %s" % requested)
    return "\n".join(lines) + "\n"


class TheRealQueueAsks(unittest.TestCase):
    def setUp(self):
        self.text = QUEUE.read_text(encoding="utf-8")
        self.items = sweep.parse(self.text)

    def test_the_parser_sees_the_queue_at_all(self):
        """Non-vacuity. An empty parse would make every assertion below pass for the wrong reason."""
        self.assertGreaterEqual(len(self.items), 1,
                                "the sweep parsed no items out of %s — the format or its parser "
                                "moved, and the next assertion would be green because it is blind"
                                % QUEUE.relative_to(ROOT))

    def test_no_mature_item_is_waiting_untold(self):
        """The invariant: five reasoned verdicts and no request is a request the human never got."""
        ready = sweep.ready(self.items)
        if ready:
            self.fail(
                "%d item(s) on the reject queue have now been looked at by all %d of us and none of "
                "us can do them, with no `steward-requested:` line — so the human has never been "
                "asked:\n%s\n\nRepair, in this wake: `python3 scripts/reject_queue_sweep.py --mark`, "
                "then land the stamped channels/reject-queue.md."
                % (len(ready), len(sweep.AMIGOS),
                   "\n".join("  • %s" % i["title"] for i in ready)))

    def test_no_item_is_asked_about_without_all_verdicts(self):
        """The other direction, which the stamp must not be able to jump: asking early is a shrug."""
        for i in self.items:
            if i["requested"]:
                self.assertEqual(
                    len(i["reviews"]), len(sweep.AMIGOS),
                    "%s carries a steward request with %d of %d verdicts — a request written before "
                    "everyone looked is not a request, it is a nudge"
                    % (i["title"], len(i["reviews"]), len(sweep.AMIGOS)))


class TheCheckIsNotVacuous(unittest.TestCase):
    """Prove the assertion above can fail, on a file the test owns."""

    def test_four_verdicts_are_not_enough_and_five_are(self):
        four = sweep.parse(fixture(verdicts=4))
        self.assertEqual(sweep.ready(four), [], "four of five counted as a finished item")
        five = sweep.parse(fixture(verdicts=5))
        self.assertEqual([i["title"] for i in sweep.ready(five)],
                         ["An item the commons has finished with"],
                         "five reasoned verdicts did not mature the item — the guard is blind")

    def test_a_stamped_item_stops_being_ready(self):
        for state, expected in (("2026-10-17", []), (None, ["An item the commons has finished with"])):
            text = fixture(verdicts=5, requested=state)
            self.assertEqual([i["title"] for i in sweep.ready(sweep.parse(text))], expected)

    def test_an_unreasoned_shrug_does_not_mature_it(self):
        text = fixture(verdicts=0) + "".join(
            "- reviewed: %s 2026-10-17 cannot\n" % a for a in sweep.AMIGOS)
        self.assertEqual(sweep.ready(sweep.parse(text)), [],
                         "'cannot' with no reason counted as a verdict; the queue would ask the "
                         "human about five shrugs")

    def test_the_mark_round_trip_clears_it(self):
        """The repair the failure message tells a reader to run must actually work on this shape."""
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "reject-queue.md"
            copy.write_text(fixture(verdicts=5), encoding="utf-8")
            items = sweep.parse(copy.read_text(encoding="utf-8"))
            self.assertEqual(len(sweep.ready(items)), 1)
            note, today = sweep.note(sweep.ready(items))
            sweep.stamp(copy, [i["title"] for i in sweep.ready(items)], today)
            after = sweep.parse(copy.read_text(encoding="utf-8"))
            self.assertEqual(sweep.ready(after), [],
                             "--mark did not clear the item it claims to stamp")
            self.assertIn("An item the commons has finished with", note,
                          "the note sent to the human does not name the item")


if __name__ == "__main__":
    unittest.main(verbosity=2)
