#!/usr/bin/env python3
"""Does the CO-safety port actually go red when the page drifts? — asked and answered, 2026-11-26.

Why this file exists. The value-queue item behind the page ports closes only when "a red run means
the page drifted rather than only that its script parses". Every port so far has been checked for
the first half of that sentence — it passes on the real page — and none of them for the second: a
port can pass perfectly and still be vacuous, if its assertions read the page and then compare it
with itself, or pin something the page would never lose. Nothing in the repository had ever run a
port against a page that was *wrong*.

So this test takes `tests/test_co_safety_page_claims.py`, hand-mutates `docs/works/co-safety.html`
in a temporary copy — no write to the repository file, ever — and asserts the port fails. Two
mutations, one per central claim:

  1. a number moved: `distance_feet: 20` becomes 25, which is the page printing a distance its own
     record does not hold;
  2. a quotation softened: the longest recorded quotation loses its final character, which is the
     page misquoting an authority by one letter.

Both must produce a non-empty failure/error list. The mutations are applied to a temp file and the
port's module-level `PAGE` is pointed at it, because every port in this directory reads its page
through a module constant — the same reason the ports are importable at all.

What this does NOT establish. That the port is complete: a mutation this file does not think of is
still uncaught here, and the harness's behavioural cases (`verdictFor()` indoors / under 20 feet /
permitted) remain the harness's job on a machine with a JavaScript runtime. This test proves
sensitivity on the two claims the page is worth reading for, not exhaustiveness.

Scope, deliberately one page. `test_heat_page_claims.py`, `test_air_page_claims.py`,
`test_fetchable_page_claims.py` and `test_food_safety_page_claims.py` are the same port for four
other pages and have no such check; each needs its own pair of mutations chosen against its own
assertions, and their records are not shaped like this one (heat and co-safety hold `quotes`,
air-quality, fetchable and food-safety do not), so the same mutation cannot be reused blind. This
file is the pattern and the first instance; the other four are the queue.

Run: python3 tests/test_co_safety_port_is_sensitive.py
"""

import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
REPO = TESTS.parent
PORT = TESTS / "test_co_safety_page_claims.py"
PAGE = REPO / "docs" / "works" / "co-safety.html"
RECORD = REPO / "docs" / "works" / "co-safety-sources.json"


def load_port():
    """A fresh module object per run, so one mutated run cannot leak state into the next."""
    spec = importlib.util.spec_from_file_location("co_safety_port_under_test", PORT)
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
        self.assertEqual(result.testsRun, 27,
                         "the port's own count changed; update this file's baseline deliberately")
        self.assertEqual(result.failures, [], "the port fails on the unmutated page")
        self.assertEqual(result.errors, [], "the port errors on the unmutated page")

    def test_a_moved_number_is_caught(self):
        """Claim 2: the page's THRESHOLDS cannot part company with the record."""
        self.assertIn("distance_feet: 20", self.html,
                      "the page no longer holds 'distance_feet: 20' literally; retarget this "
                      "mutation at the line the page now uses rather than deleting the test")
        result = self.run_mutated(self.html.replace("distance_feet: 20", "distance_feet: 25", 1),
                                  "distance_feet 20 -> 25")
        self.assertGreater(len(result.failures) + len(result.errors), 0,
                           "the port passed a page whose distance disagrees with its own record — "
                           "its number checks are not reading what they claim to read")

    def test_a_softened_quotation_is_caught(self):
        """Claim 1: a quotation cannot be altered on the page by one letter."""
        quotes = json.loads(RECORD.read_text(encoding="utf-8"))["quotes"]
        key = max(quotes, key=lambda k: len(quotes[k]))
        quote = quotes[key]
        self.assertIn(quote, self.html,
                      f"the quotation '{key}' is not verbatim on the page in the first place")
        softened = quote[:-1] + ("X" if quote[-1] != "X" else "Y")
        result = self.run_mutated(self.html.replace(quote, softened, 1),
                                  f"quotation '{key}' last character altered")
        self.assertGreater(len(result.failures) + len(result.errors), 0,
                           "the port passed a page that misquotes an authority — its verbatim "
                           "check is comparing the page with itself")


if __name__ == "__main__":
    unittest.main(verbosity=2)
