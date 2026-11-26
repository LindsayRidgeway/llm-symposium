#!/usr/bin/env python3
"""Does the heat port actually go red when the page drifts? — asked and answered, 2026-11-26.

Why this file exists. The value-queue item behind the page ports closes only when "a red run means
the page drifted rather than only that its script parses". `tests/test_co_safety_port_is_sensitive.py`
built the pattern for the first port and named the rest as the queue; this is the second instance.
`tests/test_heat_page_claims.py` (22 tests) passes on the real page, and passing is only half of the
sentence — a port can pass perfectly and still be vacuous, if its assertions read the page and then
compare it with itself, or pin something the page could never lose.

So this file hand-mutates `docs/works/heat.html` in a temporary copy — never the repository file —
and asserts the port fails. Two mutations, one per central claim, chosen against the heat page's own
record because its assertions are not shaped like co-safety's:

  1. a threshold moved: `fan_max_c: 40` becomes 41, which is the page's fan line disagreeing with
     WHO's 40 °C in `heat-sources.json` while the page still reads as a coherent argument;
  2. a quotation softened: the longest recorded quotation loses its final character, which is the
     page misquoting an authority by one letter.

What this does NOT establish. That the port is complete: a mutation this file does not think of is
still uncaught here, and the harness's six behavioural cases still need a JavaScript runtime. Two
central claims, not every claim.

Scope, deliberately one page. `test_air_page_claims.py`, `test_fetchable_page_claims.py`,
`test_food_safety_page_claims.py` and `test_nonreplication_page_claims.py` are the same kind of port
and have no such check except food-safety; each needs its own mutations chosen against its own
assertions.

Run: python3 tests/test_heat_page_port_is_sensitive.py
"""

import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
REPO = TESTS.parent
PORT = TESTS / "test_heat_page_claims.py"
PAGE = REPO / "docs" / "works" / "heat.html"
RECORD = REPO / "docs" / "works" / "heat-sources.json"


def load_port():
    """A fresh module object per run, so one mutated run cannot leak state into the next."""
    spec = importlib.util.spec_from_file_location("heat_port_under_test", PORT)
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


def longest_quotation_on_page(page_text: str) -> str:
    """The longest string in the record that the page prints verbatim, whatever its key is.

    The record's quotations are not a flat mapping like co-safety's, so the field is discovered
    rather than assumed; a key that is not printed verbatim on the page simply drops out.
    """
    record = json.loads(RECORD.read_text(encoding="utf-8"))

    def strings(node):
        if isinstance(node, str):
            yield node
        elif isinstance(node, dict):
            for value in node.values():
                yield from strings(value)
        elif isinstance(node, list):
            for value in node:
                yield from strings(value)

    printed = [s for s in strings(record.get("quotes", [])) if len(s) > 80 and s in page_text]
    assert printed, "no recorded quotation appears verbatim on the page; retarget this test"
    return max(printed, key=len)


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
        self.assertEqual(result.testsRun, 22,
                         "the port's own count changed; update this file's baseline deliberately")
        self.assertEqual(result.failures, [], "the port fails on the unmutated page")
        self.assertEqual(result.errors, [], "the port errors on the unmutated page")

    def test_a_moved_threshold_is_caught(self):
        """The fan line: the page's LIMITS cannot part company with the record's numbers."""
        self.assertIn("fan_max_c: 40", self.html,
                      "the page no longer holds 'fan_max_c: 40' literally; retarget this mutation "
                      "at the line the page now uses rather than deleting the test")
        result = self.run_mutated(self.html.replace("fan_max_c: 40", "fan_max_c: 41", 1),
                                  "fan_max_c 40 -> 41")
        self.assertGreater(len(result.failures) + len(result.errors), 0,
                           "the port passed a page whose fan threshold disagrees with its own "
                           "record — its number checks are not reading what they claim to read")

    def test_a_softened_quotation_is_caught(self):
        """Every quotation: the page cannot alter a word of an authority it quotes."""
        quote = longest_quotation_on_page(self.html)
        softened = quote[:-1] + ("X" if quote[-1] != "X" else "Y")
        result = self.run_mutated(self.html.replace(quote, softened, 1),
                                  "longest recorded quotation, last character altered")
        self.assertGreater(len(result.failures) + len(result.errors), 0,
                           "the port passed a page that misquotes an authority — its verbatim "
                           "check is comparing the page with itself")


if __name__ == "__main__":
    unittest.main(verbosity=2)
