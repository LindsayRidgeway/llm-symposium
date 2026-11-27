#!/usr/bin/env python3
"""Does the nonreplication port actually go red when the page drifts? — 2026-11-27.

Why this file exists. `tests/test_nonreplication_page_claims.py` (Desi, landed 2026-11-26) re-derives
the nonreplication page's half that needs no JavaScript runtime, because the harness the Works index
names — `tests/validate_nonreplication_page.mjs` — is never executed by any job here: the workflow
hands `.mjs` files to `node --check`, which is a syntax check, and skips cleanly where node is absent
(nowhere on this checkout). A port can be green and still be vacuous: if it compares the page with a
copy of the page, or pins strings no drift would ever remove, it guards nothing and looks exactly like
a guard. Six sibling ports were proven sensitive on 2026-11-26/27, and two of those proofs found real
vacuities in the ports they were written against. This is the seventh, and it was chosen against this
page's own claims rather than copied across.

The page answers "what does the public record of non-replication actually contain?", so its
consequential claims are about the *classification* of a printed p-value and the *refusal* to total
two unlike records:

  1. free text is refused, never coerced — "not reported" must not become a number, because a
     parser that defaults to zero turns every blank outcome into a significant result;
  2. the registry's leading `=` (`=0.7158`) is stripped before the number is read, or those rows
     silently vanish from every count;
  3. `"<0.05"` is bounded above, so the whole interval sits below the line — this branch is what
     lets an inequality be classified at all;
  4. the conventional line is strict: exactly 0.05 is "did not reach". Loosening `<` to `<=`
     publishes a null result as significant while every printed number stays as it was;
  5. only PRIMARY outcomes are the page's subject; dropping the upper-casing lets a registry
     that printed `primary` or `Primary` be skipped entirely, and secondary outcomes in;
  6. a study is flagged once, from the count of *studies*, not of outcomes;
  7. the request reads 25 studies with posted results; a silent change to the page size changes
     what the page claims to have read;
  8. the reader's topic goes to two keyless hosts and to no other host — the page's whole privacy
     sentence is that nothing is sent to us;
  9. the page's central refusal — the two records are shown side by side and *not* added — must
     still be readable in its prose, because that sentence is the artifact's argument;
 10. the Works index must keep saying which half of the claim runs on every push, or a stranger
     reads "37 checks" as a guard this repository has;
 11. the Europe PMC query's `TITLE:` scope — the page's honesty argument is that the second record
     is searched by *title*, so a citation naming the trial is a citation about the trial. Drop the
     field and the same phrase becomes title-or-abstract: a wider, different, and much larger set
     of hits, with every printed number unchanged. This one was found, not thought of here: it is
     mutation 6 in Dmitri's orphaned 2026-11-27 03:50Z version of this file, whose diff the gate
     refused for an unregistered port and which should not be re-landed — so the mutation is carried
     over rather than the file.

Each mutation is applied to a temporary copy; the repository page and index are never written. The
port reads them through module-level `PAGE` / `INDEX`, so a mutation is pointed at by rebinding those
constants — and the record stays real, which is the point: the page is the side that drifted.

What this does NOT establish. The mutations are the ones this page's claims suggest; a drift this
file does not think of is still uncaught. The port's first half is a Python reference implementation
run against the harness's own fixtures — it does not read the page, so no page mutation can move it,
and a *behavioural* regression in the JavaScript that the pinning half does not name would pass both
files. The five live checks against the two keyless records, and the stub render, remain the
harness's job on a machine with a JavaScript runtime and a network, which this checkout is not.

Sibling pairs: co-safety, food-safety, heat, air, fetchable, warming, and this one. With it every
ported page has a proof that its guard can fail.

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
# loses tests, the baseline here must be updated by hand rather than silently absorbing a regression.
PORT_TESTS = 31


def load_port():
    """A fresh module object per run, so a mutated run cannot leak state into the next."""
    spec = importlib.util.spec_from_file_location("nonreplication_port_under_test", PORT)
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

    def run_mutated_page(self, before: str, after: str, label: str):
        self.assertIn(before, self.html,
                      f"the mutation '{label}' targets text the page no longer carries; retarget "
                      f"it at the line the page now uses rather than deleting the test")
        mutated = self.html.replace(before, after)
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

    def test_free_text_coerced_to_a_number_is_caught(self):
        """Claim 1: an unparseable value is refused. Defaulted to 0 it would read as significant."""
        result = self.run_mutated_page(
            "if (!m) return null;", 'if (!m) return { op: "=", num: 0 };',
            "unparseable p-value defaulted to zero")
        self.assert_red(result,
                        "the port passed a page that turns 'not reported' into p=0, i.e. a "
                        "reached primary outcome — its parser pin is comparing the page with itself")

    def test_the_registrys_leading_equals_strip_is_caught(self):
        """Claim 2: `=0.7158` must lose its `=` or the row disappears from every count."""
        result = self.run_mutated_page(
            's.replace(/^=/, "")', 's.replace(/^\\+/, "")',
            "leading '=' strip removed")
        self.assert_red(result,
                        "the port passed a page that drops every registry-prefixed p-value")

    def test_a_narrowed_less_than_branch_is_caught(self):
        """Claim 3: `<0.05` is bounded above by 0.05, so the interval is below the line."""
        result = self.run_mutated_page(
            'if (p.op === "<") return p.num <= 0.05 ? "reached" : "indeterminate";',
            'if (p.op === "<") return p.num < 0.05 ? "reached" : "indeterminate";',
            "inequality branch <= 0.05 -> < 0.05")
        self.assert_red(result,
                        "the port passed a page that calls '<0.05' indeterminate — the branch "
                        "that lets an inequality be classified at all is not pinned")

    def test_loosening_the_strict_line_is_caught(self):
        """Claim 4: exactly 0.05 is 'did not reach'. This is the page's most consequential edit."""
        result = self.run_mutated_page(
            'return p.num < 0.05 ? "reached" : "didnot";',
            'return p.num <= 0.05 ? "reached" : "didnot";',
            "strict line loosened to <= 0.05")
        self.assert_red(result,
                        "the port passed a page that publishes p=0.05 as a reached outcome while "
                        "every number it prints is unchanged")

    def test_reading_outcomes_other_than_primary_is_caught(self):
        """Claim 5: only PRIMARY outcomes are this page's subject."""
        result = self.run_mutated_page(
            '.toUpperCase() === "PRIMARY"', '=== "PRIMARY"',
            "PRIMARY upper-casing dropped")
        self.assert_red(result,
                        "the port passed a page that reads only outcomes the registry happened to "
                        "print in upper case, and can read secondary outcomes")

    def test_flagging_a_study_per_outcome_is_caught(self):
        """Claim 6: the flag counts studies, so a study with two null outcomes is one study."""
        result = self.run_mutated_page(
            "if (st.didnot > 0) agg.studiesWithNonSignificant++;",
            "if (st.didnot > 1) agg.studiesWithNonSignificant++;",
            "study flag requires two non-significant outcomes")
        self.assert_red(result,
                        "the port passed a page whose study tally silently drops single null "
                        "outcomes — the aggregate pin is not reading this line")

    def test_a_changed_page_size_is_caught(self):
        """Claim 7: the request says how many studies with posted results it read."""
        result = self.run_mutated_page("const TRIAL_PAGE = 25;", "const TRIAL_PAGE = 50;",
                                       "requested page size 25 -> 50")
        self.assert_red(result,
                        "the port passed a page that asks for a different number of studies than "
                        "it says it read")

    def test_a_third_data_host_is_caught(self):
        """Claim 8: two keyless hosts are asked for data, and no other host is."""
        result = self.run_mutated_page(
            '"https://clinicaltrials.gov/api/v2/studies"',
            '"https://api.clinicaltrials.gov/api/v2/studies"',
            "trial host replaced by a third host")
        self.assert_red(result,
                        "the port passed a page that sends the reader's topic to a host its "
                        "privacy sentence does not name")

    def test_a_widened_europe_pmc_scope_is_caught(self):
        """Claim 11: the second record is searched by title, not by title-or-abstract."""
        result = self.run_mutated_page(
            "const base = 'TITLE:\"'", "const base = '\"",
            "Europe PMC title scope widened to an unbounded phrase")
        self.assert_red(result,
                        "the port passed a page whose Europe PMC query no longer names TITLE — a "
                        "phrase match then returns abstract hits too, and the citation count the "
                        "page prints becomes a count over a different set")

    def test_a_softened_refusal_to_add_the_records_is_caught(self):
        """Claim 9: the page's argument is that the two records are not added together."""
        result = self.run_mutated_page(
            "shown but <strong>not</strong> mixed into the list",
            "shown but <strong>also</strong> mixed into the list",
            "refusal to mix the two records softened")
        self.assert_red(result,
                        "the port passed a page whose own sentence now says the two records are "
                        "mixed — the artifact's central claim is unprotected")

    def test_a_changed_index_claim_is_caught(self):
        """Claim 10: the catalogue must say which half runs, and where.

        2026-11-27: the sentence moved from "runs on every push" (true of the Python port) to
        "runs at every landing ... HARNESS_REPLAY ... run on a push" once the harness itself joined
        the landing gate. The mutation targets the mechanism's name, because a card that names the
        harness and not the recording is the shape that reads as checked and is not.
        """
        phrase = "HARNESS_REPLAY"
        self.assertIn(phrase, self.index,
                      "the index no longer carries this sentence; retarget the mutation at the "
                      "claim the index now makes")
        mutated = self.index.replace(phrase, "is available on request")
        self.assertNotEqual(mutated, self.index, "the index mutation changed nothing")
        path = self.tmp / "mutated-index.html"
        path.write_text(mutated, encoding="utf-8")
        result = run_port(PAGE, index_path=path)
        self.assert_red(result,
                        "the port passed an index that no longer says which half of the claim a "
                        "build runs — its amendment pin is not reading the file it names")


if __name__ == "__main__":
    unittest.main(verbosity=2)
