#!/usr/bin/env python3
"""Does the air port go red when the page drifts? — asked and answered, 2026-11-26.

Why this file exists. The value-queue item behind the page ports closes only when "a red run means
the page drifted rather than only that its script parses". `tests/test_co_safety_port_is_sensitive.py`
built the pattern, food-safety and heat followed; this is the fourth instance and the first whose
record holds no `quotes` key at all — the air record's shape is numbers (WHO guideline values), a
six-row demonstration table, and one stated internal inconsistency. So the mutations are chosen
against that shape, not copied from the quotation-based ports.

`tests/test_air_page_claims.py` (26 tests) passes on the real page. Passing is only half of the
sentence: a port can pass perfectly and still be vacuous. This file hand-mutates
`docs/works/air.html` in a temporary copy — never the repository file — and asserts the port fails.

  1. a guideline moved: the page's PM2.5 24-hour value 15 becomes 12, which is the page printing
     a limit the WHO did not publish while still reading as a coherent page — it must disagree
     with both its own record and the hard-coded WHO numbers in the port;
  2. a demonstration row flattened: London's European index 59 becomes 41, so the two indices no
     longer disagree by ten points — the disagreement the table exists to demonstrate is gone,
     though every individual number is still a plausible one.

What this does NOT establish. That the port is complete: a mutation this file does not think of is
still uncaught here, and the harness's behavioural cases (calling `whoVerdict` / `timesGuideline` /
`comparables` as JavaScript) still need a runtime this checkout does not have. Two central claims,
not every claim.

Run: python3 tests/test_air_page_port_is_sensitive.py
"""

import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
REPO = TESTS.parent
PORT = TESTS / "test_air_page_claims.py"
PAGE = REPO / "docs" / "works" / "air.html"
RECORD = REPO / "docs" / "works" / "air-quality-sources.json"

GUIDELINE_LINE_OLD = 'pm2_5:            { label: "PM2.5 (fine particles)", average: "24-hour", value: 15,'
GUIDELINE_LINE_NEW = 'pm2_5:            { label: "PM2.5 (fine particles)", average: "24-hour", value: 12,'
LONDON_ROW_OLD = '{ place: "London",      pm2_5: 9.2,  us_aqi: 38,  european_aqi: 59 }'
LONDON_ROW_NEW = '{ place: "London",      pm2_5: 9.2,  us_aqi: 38,  european_aqi: 41 }'


def load_port():
    """A fresh module object per run, so one mutated run cannot leak state into the next."""
    spec = importlib.util.spec_from_file_location("air_port_under_test", PORT)
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
        self.assertEqual(result.testsRun, 26,
                         "the port's own count changed; update this file's baseline deliberately")
        self.assertEqual(result.failures, [], "the port fails on the unmutated page")
        self.assertEqual(result.errors, [], "the port errors on the unmutated page")

    def test_a_moved_guideline_is_caught(self):
        """The page's guideline table cannot part company with the record's numbers."""
        self.assertIn(GUIDELINE_LINE_OLD, self.html,
                      "the page no longer holds the PM2.5 guideline line literally; retarget this "
                      "mutation at the line the page now uses rather than deleting the test")
        result = self.run_mutated(self.html.replace(GUIDELINE_LINE_OLD, GUIDELINE_LINE_NEW, 1),
                                  "PM2.5 24-hour guideline 15 -> 12")
        self.assertGreater(len(result.failures) + len(result.errors), 0,
                           "the port passed a page whose guideline value disagrees with its own "
                           "record and with WHO's published number — its number checks are not "
                           "reading what they claim to read")

    def test_a_flattened_disagreement_is_caught(self):
        """The demonstration table must still demonstrate the disagreement it is quoted for."""
        self.assertIn(LONDON_ROW_OLD, self.html,
                      "the page's London row is no longer the literal this mutation targets; "
                      "retarget it rather than deleting the test")
        result = self.run_mutated(self.html.replace(LONDON_ROW_OLD, LONDON_ROW_NEW, 1),
                                  "London European index 59 -> 41, gap now 3 not 21")
        self.assertGreater(len(result.failures) + len(result.errors), 0,
                           "the port passed a demonstration table whose rows no longer disagree, "
                           "so its 'at least two rows differ by 10+ points' assertion is not "
                           "reading the table it claims to read")


if __name__ == "__main__":
    unittest.main(verbosity=2)
