#!/usr/bin/env python3
"""Does the fetchable port actually go red when the page drifts? — 2026-11-26.

Why this file exists. `tests/test_fetchable_page_claims.py` re-derives the fetchable page's
offline checks in Python, because no registered job executes `tests/validate_fetchable_page.mjs`.
A port can pass perfectly and still be vacuous — if it compares the page with itself, or pins
something the page could not lose, it guards nothing and looks exactly like a guard. This is the
fifth of the seven offline ports to get a sensitivity pair (co-safety, food-safety, heat and air
have one; nonreplication and warming have none), and it is written against this page's own shape
rather than copied across: fetchable's record holds no `quotes` key, so the food-safety file's
"soften a recorded quotation" mutation has no target here at all.

The page's consequential claims, and the mutation chosen for each:

  1. the lead's source count is the record's — "Thirty-five public sources" is arithmetic a reader
     can check against the file, and a page that says 34 while showing 35 rows is lying quietly;
  2. the six sources named as answered-but-invisible-to-a-browser are the six the file measures.
     Replacing one name in the list (the CDC -> the NWS) keeps the sentence grammatical and breaks
     the claim; a port that only counted the list would not notice;
  3. the 2026-10-17 correction's arithmetic — "six, not five" — is the page's own honest correction
     of its September table. Changing it to "five, not five" makes the correction say nothing;
  4. the honesty marker "we are not affiliated" cannot be turned into "we are affiliated" — this is
     the page about other people's data and it is the one sentence that keeps it honest;
  5. the amended claim, added 2026-11-26, says "no job in this repository runs it". Flipping that
     to "a job ... runs it" restores exactly the false claim the amendment was written to remove;
  6. the page must name the harness it is talking about; appending ".bak" to the name must fail.

What it found, on the day it was written. Mutation 6 was RED against the port as it landed: the
port asked whether the string "tests/validate_fetchable_page.mjs" occurred in the page, and
"tests/validate_fetchable_page.mjs.bak" contains it, so the page could name a file that does not
exist and still pass. That is a weak pin, not a bad mutation — the page would be pointing the
reader at a deleted harness, which is the failure the whole value-queue item exists to catch. Fixed
in `tests/test_fetchable_page_claims.py` with a trailing lookahead so only the exact name counts;
re-run this file and the mutation is caught. A sensitivity test that fails is doing its job.

Plus one mutation on the record, not the page, because the page renders the file: a row appended
without the counts moved must fail. That is the claim the port's docstring makes most loudly ("a
row edited without the counts moved fails the build"), and it is the only one of the seven that can
be proved by breaking the record instead of the page.

Every mutation is applied to a temporary copy; neither the repository page nor the repository
record is ever written. The port reads through module-level `PAGE` and `RECORD`, so each mutation
is pointed at by rebinding those constants in a freshly loaded module.

What this does NOT establish. That the port is exhaustive: a mutation this file did not think of is
still uncaught. The five live re-measurements and the click handler stay the harness's job on a
machine that has a network and a JavaScript runtime — no build here has either.

Run: python3 tests/test_fetchable_port_is_sensitive.py
"""

import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
REPO = TESTS.parent
PORT = TESTS / "test_fetchable_page_claims.py"
PAGE = REPO / "docs" / "works" / "fetchable.html"
RECORD = REPO / "docs" / "works" / "fetchable-sources.json"

# The port's own count at the time this file was written. Pinned deliberately: if the port grows or
# loses tests, the baseline here must be updated by hand rather than silently absorbing a regression.
PORT_TESTS = 20


def load_port():
    """A fresh module object per run, so a mutated run cannot leak state into the next."""
    spec = importlib.util.spec_from_file_location("fetchable_port_under_test", PORT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_port(page_path: Path, record_path: Path = RECORD):
    """Run the port's whole suite against `page_path` and `record_path`; return the result."""
    module = load_port()
    module.PAGE = page_path
    module.RECORD = record_path
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    stream = io.StringIO()
    return unittest.TextTestRunner(stream=stream, verbosity=0).run(suite)


class PortSensitivity(unittest.TestCase):
    """Green on the real page, red on a page that drifted. Both halves matter."""

    def setUp(self):
        self.html = PAGE.read_text(encoding="utf-8")
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def run_mutated(self, mutated: str, label: str):
        self.assertNotEqual(mutated, self.html,
                            f"the mutation '{label}' changed nothing, so it proves nothing")
        path = self.tmp / "mutated.html"
        path.write_text(mutated, encoding="utf-8")
        return run_port(path)

    def assert_caught(self, result, why: str):
        self.assertGreater(len(result.failures) + len(result.errors), 0,
                           f"the port passed a page that {why} — that check pins nothing")

    def test_the_real_page_passes(self):
        """The baseline, so a red run below is the mutation's doing and not this file's."""
        result = run_port(PAGE)
        self.assertEqual(result.testsRun, PORT_TESTS,
                         "the port's own count changed; update PORT_TESTS deliberately, then "
                         "re-check that the new tests are sensitive to something")
        self.assertEqual(result.failures, [], "the port fails on the unmutated page")
        self.assertEqual(result.errors, [], "the port errors on the unmutated page")

    def test_a_moved_source_count_is_caught(self):
        """Claim 1: the lead's count is the record's, not a number somebody typed."""
        self.assertIn("Thirty-five public sources", self.html,
                      "the lead no longer states the count this way; retarget the mutation "
                      "rather than deleting the test")
        result = self.run_mutated(
            self.html.replace("Thirty-five public sources", "Thirty-four public sources", 1),
            "Thirty-five -> Thirty-four")
        self.assert_caught(result, "states a source count the record does not hold")

    def test_a_renamed_unreadable_source_is_caught(self):
        """Claim 2: the six named as browser-invisible are the six the file measures."""
        target = "the CDC all answered us fine"
        self.assertIn(target, self.html,
                      "the sentence naming the six is no longer on the page in this form; "
                      "retarget the mutation")
        result = self.run_mutated(
            self.html.replace(target, "the NWS all answered us fine", 1),
            "the CDC -> the NWS in the list of unreadable sources")
        self.assert_caught(result, "names a source as browser-invisible that the file does not "
                                   "measure that way, and drops one it does")

    def test_the_correction_arithmetic_is_caught(self):
        """Claim 3: 'six, not five' is the page's whole honest correction."""
        self.assertIn("six, not five", self.html,
                      "the correction sentence is gone; retarget the mutation")
        result = self.run_mutated(self.html.replace("six, not five", "five, not five", 1),
                                  "'six, not five' -> 'five, not five'")
        self.assert_caught(result, "no longer states the corrected gap")

    def test_a_dropped_affiliation_marker_is_caught(self):
        """Claim 4: this page is about other people's data and says whose it is."""
        self.assertIn("we are not affiliated", self.html,
                      "the marker is gone; retarget the mutation")
        result = self.run_mutated(self.html.replace("we are not affiliated", "we are affiliated", 1),
                                  "not affiliated -> affiliated")
        self.assert_caught(result, "now claims an affiliation with the sources it measures")

    def test_the_amended_claim_cannot_be_flipped_back(self):
        """Claim 5: since 2026-11-27 the page says how much of the harness runs, and how much cannot.

        It said "no job in this repository runs it" until that stopped being true. The claim is now a
        fraction, so the mutation inflates the fraction to everything — the overstatement the landing
        gate cannot make, because it runs the harness with `--offline`.
        """
        self.assertIn("11 of its 16 checks", self.html,
                      "the fraction is gone; retarget the mutation")
        result = self.run_mutated(
            self.html.replace("11 of its 16 checks", "16 of its 16 checks", 1),
            "11 of 16 run here -> all 16 run here")
        self.assert_caught(result, "claims the live half runs at every landing when it cannot")

    def test_a_renamed_harness_is_caught(self):
        """Claim 6: the page names the harness the map test pins it to."""
        self.assertIn("tests/validate_fetchable_page.mjs", self.html,
                      "the harness name is gone; retarget the mutation")
        result = self.run_mutated(
            self.html.replace("tests/validate_fetchable_page.mjs",
                              "tests/validate_fetchable_page.mjs.bak", 1),
            "harness renamed to a file that does not exist")
        self.assert_caught(result, "names a harness that is not the one in the repository")

    def test_a_row_added_without_the_counts_moved_is_caught(self):
        """The record side: the page renders the file, so a stale count is the page's error too."""
        doc = json.loads(RECORD.read_text(encoding="utf-8"))
        extra = dict(doc["sources"][0])
        extra["name"] = extra["name"] + " (duplicate)"
        doc["sources"] = doc["sources"] + [extra]
        self.assertEqual(doc["counts"]["sources"], 35,
                         "the record's counts moved at the start; this mutation assumes they did "
                         "not, so rebuild it against the file as it is now")
        self.assertEqual(len(doc["sources"]), 36, "the duplicate row was not added")
        path = self.tmp / "mutated-sources.json"
        path.write_text(json.dumps(doc), encoding="utf-8")
        result = run_port(PAGE, record_path=path)
        self.assert_caught(result, "ships a record whose counts do not agree with its own rows")


if __name__ == "__main__":
    unittest.main(verbosity=2)
