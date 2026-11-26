#!/usr/bin/env python3
"""Does the food-safety port actually go red when the page drifts? — 2026-11-26.

Why this file exists. `tests/test_food_safety_page_claims.py` re-derives the food-safety page's
offline checks in Python, because no registered job executes its `.mjs` harness. A port can pass
perfectly and still be vacuous: if it reads the page and compares it with itself, or pins something
the page would never lose, it guards nothing and looks exactly like a guard. The first port to be
tested this way (`tests/test_co_safety_port_is_sensitive.py`, same day) found that nothing in this
repository had ever run a port against a page that was *wrong*. This is the second instance, chosen
against this page's own claims, not copied across.

The page answers "is this still good?" after a power cut, so its two consequential claims are:

  1. the twelve threshold numbers cannot part company with `food-safety-sources.json` — moving
     `fridge_hours` from 4 to 5 is the page telling a household to keep food a day-hour longer than
     the FDA sentence printed below it allows;
  2. it cannot soften a quotation it presents as verbatim — "for 4 hours or more" is the FDA's own
     sentence, and 5 hours is a different rule;
  3. it cannot drop the honesty marker that two authorities returned HTTP 403 to the session that
     measured the numbers, because the page's whole claim to trustworthiness is that it says which
     sources it could and could not read.

Each mutation is applied to a temporary copy; the repository page is never written. The port reads
its page through a module-level `PAGE`, so the mutation is pointed at by rebinding that constant —
and the record stays the real one, which is the point: the page is the side that drifted.

What it found, on the day it was written. The fourth mutation was RED against the port as it
landed that morning: softening the last character of the fda discard rule — the longest quotation
the page prints — left `tests/test_food_safety_page_claims.py` green, because the port checked only
the five phrases the harness itself names. The gap was in the port, not in this file. It is fixed
there now by `PAGE_VERBATIMS`, five recorded sentences pinned as literals, with two tests (the port
went from 31 to 33, which is why `PORT_TESTS` reads 33); re-run this file and the mutation is
caught. A sensitivity test that fails is doing its job — that is what the landing gate saw.

What this does NOT establish. Every mutation replaces ALL occurrences of its target, because each
of these strings appears more than once on the page (the FDA sentence and the 403 marker each
twice) — and a single-occurrence edit of a sentence that is NOT in `PAGE_VERBATIMS` is still not
caught: the page can say "5 hours" in its detail text while the quote block below still says 4, and
the port asks only whether some copy of the old sentence survives. Widening `PAGE_VERBATIMS` closes
that for the sentences it pins and not for the rest.

Also not established: that the port is exhaustive; a mutation this file does not think of
is still uncaught. The behavioural cases that call `verdictFor()` and `updateCalculator()` in a
real DOM remain the harness's job on a machine that has a JavaScript runtime.

Sibling work still owed: the same sensitivity pair for `air`, `heat` and `fetchable` ports, each
against its own record's shape (heat and co-safety hold a `quotes` key; air, fetchable and this one
do not, so the food-safety mutation is not transferable blind).

Run: python3 tests/test_food_safety_port_is_sensitive.py
"""

import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
REPO = TESTS.parent
PORT = TESTS / "test_food_safety_page_claims.py"
PAGE = REPO / "docs" / "works" / "food-safety.html"
RECORD = REPO / "docs" / "works" / "food-safety-sources.json"

# The port's own count at the time this file was written. Pinned deliberately: if the port grows or
# loses tests, the baseline here must be updated by hand rather than silently absorbing a regression.
PORT_TESTS = 33


def load_port():
    """A fresh module object per run, so a mutated run cannot leak state into the next."""
    spec = importlib.util.spec_from_file_location("food_safety_port_under_test", PORT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_port(page_path: Path):
    """Run the port's whole suite against `page_path`; return the TextTestResult."""
    module = load_port()
    module.PAGE = page_path
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

    def test_the_real_page_passes(self):
        """The baseline, so a red run below is the mutation's doing and not this file's."""
        result = run_port(PAGE)
        self.assertEqual(result.testsRun, PORT_TESTS,
                         "the port's own count changed; update PORT_TESTS deliberately, then "
                         "re-check that the new tests are sensitive to something")
        self.assertEqual(result.failures, [], "the port fails on the unmutated page")
        self.assertEqual(result.errors, [], "the port errors on the unmutated page")

    def test_a_moved_threshold_is_caught(self):
        """Claim 1: the page's THRESHOLDS cannot part company with the record."""
        self.assertIn("fridge_hours: 4", self.html,
                      "the page no longer holds 'fridge_hours: 4' literally; retarget this "
                      "mutation at the line the page now uses rather than deleting the test")
        result = self.run_mutated(self.html.replace("fridge_hours: 4", "fridge_hours: 5", 1),
                                  "fridge_hours 4 -> 5")
        self.assertGreater(len(result.failures) + len(result.errors), 0,
                           "the port passed a page that keeps food an hour longer than the FDA "
                           "sentence it prints — its threshold checks are not reading the record")

    def test_a_softened_quotation_is_caught(self):
        """Claim 2: a quotation the page calls verbatim cannot be altered into a different rule."""
        phrase = "for 4 hours or more"
        self.assertIn(phrase, self.html,
                      "the FDA sentence is no longer on the page in this form; retarget the "
                      "mutation rather than deleting the test")
        result = self.run_mutated(self.html.replace(phrase, "for 5 hours or more"),
                                  "FDA '4 hours' -> '5 hours'")
        self.assertGreater(len(result.failures) + len(result.errors), 0,
                           "the port passed a page that misquotes the FDA's four-hour rule — its "
                           "verbatim check is comparing the page with itself")

    def test_a_recorded_verbatim_from_the_measurement_file_is_caught(self):
        """Claim 2 again, from the other side: the longest recorded quotation, one letter altered."""
        data = json.loads(RECORD.read_text(encoding="utf-8"))
        quotes = [v for s in data["sources"] for v in s.get("verbatim", []) if v in self.html]
        self.assertTrue(quotes, "no recorded verbatim appears on the page in the first place")
        quote = max(quotes, key=len)
        softened = quote[:-1] + ("X" if quote[-1] != "X" else "Y")
        result = self.run_mutated(self.html.replace(quote, softened),
                                  f"recorded quotation ({len(quote)} chars) last character altered")
        self.assertGreater(len(result.failures) + len(result.errors), 0,
                           "the port passed a page that misquotes an authority by one letter")

    def test_a_dropped_403_marker_is_caught(self):
        """Claim 3: the page must keep saying which authorities it could not read, and why."""
        self.assertIn("HTTP 403", self.html,
                      "the page no longer marks the 403s; retarget this mutation")
        result = self.run_mutated(self.html.replace("HTTP 403", "HTTP 200"),
                                  "every 'HTTP 403' -> 'HTTP 200'")
        self.assertGreater(len(result.failures) + len(result.errors), 0,
                           "the port passed a page claiming it read a source it never read — its "
                           "honesty-marker checks pin nothing")


if __name__ == "__main__":
    unittest.main(verbosity=2)
