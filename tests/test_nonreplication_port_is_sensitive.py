#!/usr/bin/env python3
"""Does the nonreplication port actually go red when the page drifts? — 2026-11-27.

Why this file exists. `tests/test_nonreplication_page_claims.py` re-derives the nonreplication
page's 32 offline checks in Python, because no registered job executes its `.mjs` harness. A port
that reads a page and compares it with itself passes forever and guards nothing. The first four
ports to get a sensitivity pair (co-safety, food-safety, heat, air) each found something when they
were written; the fifth (fetchable) found a live vacuity in its own port. This is the sixth, and it
is the last of the seven ports to have had none.

It is not a copy of any of them, because this page is shaped differently: five of the ports read a
`*-sources.json` record and this one has no record at all. Its numbers come from two live APIs, so
its 32 offline checks are assertions about *its own code and prose*. Every mutation below therefore
targets a decision the page makes in its own text, not a value in a data file:

  1. the p-value classifier's strict line — `p.num < 0.05` is the page's whole verdict vocabulary,
     and `<=` would call a study that printed exactly 0.05 a non-replication;
  2. the registry's leading `=` strip — without it the rows the registry prints as `=0.7158` fall
     out of the count as unparsed, and the page reports fewer outcomes than it read;
  3. the PRIMARY-only filter — inverted, the page counts secondary endpoints, which is a different
     question and a larger denominator;
  4. the per-study flag — `> 0` to `>= 0` turns "studies with a non-significant outcome" into
     "studies", the one number a reader would quote;
  5. the trial page size — the constant is printed as part of the request the page shows;
  6. the title scope of the Europe PMC query — the page's honesty argument rests on titles, and
     `TITLE:` dropped to an unbounded term is title-or-abstract;
  7. the refusal to sum the two records — the sentence that says the two numbers are never added
     together is the page's argument, and the port checks it in prose;
  8. the index sentence — the amendment that says which half runs on every push, so deleting the
     port's own path from the index fails the port.

Each mutation is applied to a temporary copy; the repository page is never written. The port
exposes `PAGE` and `INDEX` as module constants, so a run rebinds them and the real record stays the
real record — which is the point: the page is the side that drifted.

What this does NOT establish. That the port is exhaustive: a mutation nobody thought of is still
uncaught, and the behavioural cases that call `verdictFor()`/`updateCounts()` in a real DOM remain
the harness's job on a machine that has a JavaScript runtime. What it does establish is the thing
the map guard promises — that a red run of this port means the page drifted, rather than only that
its text diffed.

Run: python3 tests/test_nonreplication_port_is_sensitive.py
"""

import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
REPO = TESTS.parent
PORT = TESTS / "test_nonreplication_page_claims.py"
PAGE = REPO / "docs" / "works" / "nonreplication.html"
INDEX = REPO / "docs" / "works" / "index.html"

# The port's own count at the time this file was written. Pinned deliberately: if the port grows or
# loses tests, the baseline here must be updated by hand rather than silently absorbing a
# regression.
PORT_TESTS = 31

# The index path of the port, as the amendment writes it. Named once so the mutation below cannot
# drift from the thing it mutates.
INDEX_CLAIM = "tests/test_nonreplication_page_claims.py"


def load_port():
    """A fresh module object per run, so a mutated run cannot leak state into the next."""
    spec = importlib.util.spec_from_file_location("nonreplication_port_under_test", PORT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_port(page_path: Path, index_path: Path = None):
    """Run the port's whole suite against `page_path` (and `index_path`); return the result."""
    module = load_port()
    module.PAGE = page_path
    if index_path is not None:
        module.INDEX = index_path
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    stream = io.StringIO()
    return unittest.TextTestRunner(stream=stream, verbosity=0).run(suite)


class PageSensitivity(unittest.TestCase):
    """Green on the real page, red on a page that drifted. Both halves matter."""

    def setUp(self):
        self.html = PAGE.read_text(encoding="utf-8")
        self.index = INDEX.read_text(encoding="utf-8")
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def mutate_page(self, before: str, after: str, label: str):
        self.assertIn(before, self.html,
                      f"the page no longer holds {before!r}; retarget this mutation at the line "
                      f"the page now uses ({label}) rather than deleting the test")
        mutated = self.html.replace(before, after)
        self.assertNotEqual(mutated, self.html, f"mutation '{label}' changed nothing")
        path = self.tmp / "mutated.html"
        path.write_text(mutated, encoding="utf-8")
        return run_port(path)

    def mutate_index(self, before: str, after: str, label: str):
        self.assertIn(before, self.index,
                      f"the index no longer holds {before!r}; retarget this mutation ({label})")
        path = self.tmp / "index.html"
        path.write_text(self.index.replace(before, after), encoding="utf-8")
        return run_port(PAGE, path)

    def assert_red(self, result, what: str):
        self.assertGreater(len(result.failures) + len(result.errors), 0,
                           f"the port passed a page where {what} — that check pins nothing")

    # -- the baseline -------------------------------------------------------------------------

    def test_the_real_page_passes(self):
        """So a red result below is the mutation's doing and not this file's."""
        result = run_port(PAGE)
        self.assertEqual(result.testsRun, PORT_TESTS,
                         "the port's own count changed; update PORT_TESTS deliberately, then "
                         "re-check that the new tests are sensitive to something")
        self.assertEqual(result.failures, [], "the port fails on the unmutated page")
        self.assertEqual(result.errors, [], "the port errors on the unmutated page")

    # -- the page's code, decision by decision ------------------------------------------------

    def test_a_softened_significance_line_is_caught(self):
        """Claim 1: exactly 0.05 is 'did not reach', not 'reached'."""
        result = self.mutate_page('return p.num < 0.05 ? "reached" : "didnot";',
                                  'return p.num <= 0.05 ? "reached" : "didnot";',
                                  "strict p<0.05 line")
        self.assert_red(result, "a study printing exactly 0.05 is called a replication")

    def test_a_lost_equals_strip_is_caught(self):
        """Claim 2: the registry prints '=0.7158'; a parser that does not strip it drops the row."""
        result = self.mutate_page('s.replace(/^=/, "")', 's.replace(/^#/, "")',
                                  "leading '=' strip")
        self.assert_red(result, "the registry's '=' prefix no longer parses")

    def test_an_inverted_primary_filter_is_caught(self):
        """Claim 3: only primary outcomes are this page's subject."""
        result = self.mutate_page('toUpperCase() === "PRIMARY"', 'toUpperCase() !== "PRIMARY"',
                                  "PRIMARY-only filter")
        self.assert_red(result, "secondary outcomes are being counted in place of primary ones")

    def test_a_moved_per_study_flag_is_caught(self):
        """Claim 4: the count is of studies with a non-significant outcome, not of studies."""
        result = self.mutate_page('if (st.didnot > 0) agg.studiesWithNonSignificant++;',
                                  'if (st.didnot >= 0) agg.studiesWithNonSignificant++;',
                                  "per-study flag threshold")
        self.assert_red(result, "every study, including fully significant ones, is flagged")

    def test_a_moved_page_size_is_caught(self):
        """Claim 5: the constant is part of the request the page prints for the reader."""
        result = self.mutate_page("const TRIAL_PAGE = 25", "const TRIAL_PAGE = 100",
                                  "TRIAL_PAGE 25 -> 100")
        self.assert_red(result, "the trial request asks for 100 studies while the page says 25")

    def test_a_widened_query_scope_is_caught(self):
        """Claim 6: the honesty argument is title scope, not title-or-abstract."""
        result = self.mutate_page('TITLE:"', '"', "Europe PMC title scope")
        self.assert_red(result, "the phrase search is no longer restricted to titles")

    # -- the page's prose --------------------------------------------------------------------

    def test_the_no_summing_refusal_cannot_be_dropped(self):
        """Claim 7: the two records answer different questions and are never added together."""
        result = self.mutate_page("never added together", "sometimes added together",
                                  "no-summing refusal")
        self.assert_red(result, "the page no longer refuses to sum the two records")

    # -- the claim the index makes -----------------------------------------------------------

    def test_the_index_amendment_is_pinned(self):
        """Claim 8: the index must say which half runs on every push; a sentence naming only the
        harness rests on a guard no job executes.

        The first version of this mutation appended `_moved` to the port's filename, and the port
        stayed green — because its index check asks whether the path is a substring of the entry,
        and `.py_moved` still contains `.py`. That is a real, if narrow, vacuity in the port and it
        is why this mutation now changes the directory instead of the suffix: a renamed file keeps
        the phrase, a moved file does not."""
        result = self.mutate_index(INDEX_CLAIM, "works/nonreplication_page_claims.py",
                                   "index port path")
        self.assert_red(result,
                        "the index names no Python test for this page any more, so the reader is "
                        "back to being told a harness protects it that nothing runs")
        other = self.mutate_index("no job here executes", "a job here executes",
                                  "index honesty marker")
        self.assert_red(other,
                        "the index can claim a job runs the harness, which is the sentence the "
                        "amendment exists to replace")


if __name__ == "__main__":
    unittest.main(verbosity=2)
