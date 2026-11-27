#!/usr/bin/env python3
"""Does the warming port actually go red when the page drifts? — 2026-11-27.

Why this file exists. `tests/test_warming_page_claims.py` (Dmitri, landed 2026-11-27 as run
`20261127T015011Z-d8e89a76`, commit `9df87998`) re-derives the warming page's offline checks in
Python, because the page's own harness, `tests/validate_warming_page.mjs`, is an orphan: no page
names it, and no job here executes a `.mjs` even if one did. A port can pass perfectly and still be
vacuous — if it compares the page with itself, or pins something the page would never lose, it
guards nothing and looks exactly like a guard. Five sibling ports were tested this way on
2026-11-26 and one of those files, `tests/test_food_safety_port_is_sensitive.py`, found a live
vacuity in the port it was written against. This is the seventh and last offline page's pair, and
it was chosen against this page's own claims rather than copied across.

The warming page answers "what has the recorded temperature actually done here since 1950?", so
its consequential claims are:

  1. the accent-fold regression the harness was written to find on 2026-10-03 cannot come back —
     the variant filter must drop the string the reader typed by comparing against `base`, never
     against `fold`, or the accent-dropped spelling (München -> Munchen, Bogotá -> Bogota) is
     generated and then silently thrown away before it is ever queried;
  2. a decade computed from five years cannot reach the reader as a decade — `>= 6` usable years
     is the filter, and 5 lets a half-finished 2020s bucket into the trend table;
  3. the printed change is last decade minus first — reversing it publishes cooling as warming
     while every number on the table stays exactly as it is;
  4. the reader's search terms go to two keyless Open-Meteo hosts and to no other host, which is
     the page's whole privacy sentence ("no account, no install, nothing sent to us");
  5. an empty answer says it is empty, rather than an unattended spinner being read as "no
     warming";
  6. the Works index's Boston figure — 76 complete years, +1.40 °C from the 1950s to the 2020s — is
     the same measurement the page publishes, so the catalogue cannot advertise a number the page
     does not report.

Each mutation is applied to a temporary copy; the repository page and index are never written. The
port reads them through module-level `PAGE` / `INDEX`, so a mutation is pointed at by rebinding
those constants — and the record stays real, which is the point: the page is the side that drifted.

What this does NOT establish. The mutations are the ones this page's claims suggest; a drift this
file does not think of is still uncaught. Every mutation except the index one edits the page's
inline code or its user-visible strings, and the port's re-derived arithmetic (variants, levSim,
annualMeans, decadeMeans) is exercised against fixtures of its own rather than against the page —
so a changed formula in the page is caught here by the strings the port pins, not by recomputation
from a fetched series. The stub-DOM render, the SVG chart, the concurrent geocoder workers and the
live WARMING_LIVE=1 re-measurement remain the harness's job on a machine with a JavaScript runtime
and a network, which this checkout is not.

Sibling pairs: co-safety, food-safety, heat, air, fetchable, and this one. With it every ported page
has a proof that its guard can fail. Nonreplication's was the last that had none and it was
written the same night: `tests/test_nonreplication_port_is_sensitive.py`.

Run: python3 tests/test_warming_port_is_sensitive.py
"""

import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
REPO = TESTS.parent
PORT = TESTS / "test_warming_page_claims.py"
PAGE = REPO / "docs" / "works" / "warming.html"
INDEX = REPO / "docs" / "works" / "index.html"

# The port's own count at the time this file was written. Pinned deliberately: if the port grows or
# loses tests, the baseline here must be updated by hand rather than silently absorbing a regression.
PORT_TESTS = 40


def load_port():
    """A fresh module object per run, so a mutated run cannot leak state into the next."""
    spec = importlib.util.spec_from_file_location("warming_port_under_test", PORT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_port(page_path: Path, index_path: Path = INDEX):
    """Run the port's whole suite against `page_path`; return the TextTestResult."""
    module = load_port()
    module.PAGE = page_path
    module.INDEX = index_path
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    stream = io.StringIO()
    return unittest.TextTestRunner(stream=stream, verbosity=0).run(suite)


class PortSensitivity(unittest.TestCase):
    """Green on the real page, red on a page that drifted. Both halves matter."""

    def setUp(self):
        self.html = PAGE.read_text(encoding="utf-8")
        self.index = INDEX.read_text(encoding="utf-8")
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def run_mutated_page(self, mutated: str, label: str):
        self.assertNotEqual(mutated, self.html,
                            f"the mutation '{label}' changed nothing, so it proves nothing")
        path = self.tmp / "mutated.html"
        path.write_text(mutated, encoding="utf-8")
        return run_port(path)

    def assert_red(self, result, why: str):
        self.assertGreater(len(result.failures) + len(result.errors), 0, why)

    def test_the_real_page_passes(self):
        """The baseline, so a red run below is the mutation's doing and not this file's."""
        result = run_port(PAGE)
        self.assertEqual(result.testsRun, PORT_TESTS,
                         "the port's own count changed; update PORT_TESTS deliberately, then "
                         "re-check that the new tests are sensitive to something")
        self.assertEqual(result.failures, [], "the port fails on the unmutated page")
        self.assertEqual(result.errors, [], "the port errors on the unmutated page")

    def test_the_accent_fold_defect_of_2026_10_03_is_caught(self):
        """Claim 1: the filter must compare against `base`. Against `fold` it discards the variant."""
        self.assertIn("!== base.toLowerCase()", self.html,
                      "the page no longer holds the filter in this form; retarget this mutation "
                      "at the line the page now uses rather than deleting the test")
        result = self.run_mutated_page(
            self.html.replace("!== base.toLowerCase()", "!== fold.toLowerCase()"),
            "accent-fold regression restored (base -> fold)")
        self.assert_red(result,
                        "the port passed a page that generates the accent-dropped spelling and "
                        "then throws it away — the exact defect the harness was written for")

    def test_a_five_year_decade_reaching_the_reader_is_caught(self):
        """Claim 2: `>= 6` usable years, or a half-finished 2020s bucket prints as a trend."""
        self.assertIn("x.years >= 6", self.html,
                      "the decade filter is not on the page in this form; retarget this mutation")
        result = self.run_mutated_page(self.html.replace("x.years >= 6", "x.years >= 5"),
                                       "decade filter 6 -> 5")
        self.assert_red(result,
                        "the port passed a page that would print a decade computed from five "
                        "years — its >=6-year check is not reading the page")

    def test_a_reversed_headline_delta_is_caught(self):
        """Claim 3: the change printed is last decade minus first, not the other way round."""
        self.assertIn("last.mean - first.mean", self.html,
                      "the headline arithmetic is not on the page in this form; retarget it")
        self.assertTrue(self.html.count("last.mean - first.mean") >= 2,
                        "fewer occurrences than when this file was written; check what moved")
        result = self.run_mutated_page(
            self.html.replace("last.mean - first.mean", "first.mean - last.mean"),
            "delta reversed (last-first -> first-last)")
        self.assert_red(result,
                        "the port passed a page that publishes cooling as warming while every "
                        "number on its table is unchanged")

    def test_a_third_host_is_caught(self):
        """Claim 4: the reader's search terms reach the two keyless Open-Meteo hosts and no more."""
        self.assertIn("archive-api.open-meteo.com", self.html,
                      "the archive host is not on the page in this form; retarget this mutation")
        result = self.run_mutated_page(
            self.html.replace("archive-api.open-meteo.com", "api.open-meteo.com"),
            "archive host replaced by a third host")
        self.assert_red(result,
                        "the port passed a page that sends the reader's search terms to a host "
                        "its privacy sentence does not name — its host check pins nothing")

    def test_a_softened_empty_answer_is_caught(self):
        """Claim 5: an empty result must say it is empty, not fail quietly."""
        phrase = "No usable years came back"
        self.assertIn(phrase, self.html,
                      "the empty-answer sentence is not on the page; retarget this mutation")
        result = self.run_mutated_page(self.html.replace(phrase, "Something went wrong"),
                                       "empty-answer honesty marker softened")
        self.assert_red(result,
                        "the port passed a page where an empty result reads like a fault — its "
                        "honesty-marker check compares the page with itself")

    def test_a_changed_index_figure_is_caught(self):
        """Claim 6: the catalogue cannot advertise a number the page does not report."""
        phrase = "Boston, 76 complete years, +1.40 °C from the 1950s to the 2020s"
        self.assertIn(phrase, self.index,
                      "the index figure is not in the catalogue in this form; retarget this "
                      "mutation at the sentence the index now carries")
        mutated = self.index.replace(phrase, phrase.replace("+1.40", "+1.41"))
        self.assertNotEqual(mutated, self.index, "the index mutation changed nothing")
        path = self.tmp / "mutated-index.html"
        path.write_text(mutated, encoding="utf-8")
        result = run_port(PAGE, index_path=path)
        self.assert_red(result,
                        "the port passed an index advertising +1.41 °C beside a page that "
                        "reports +1.40 — its index pin is not reading the file it names")


if __name__ == "__main__":
    unittest.main(verbosity=2)
