#!/usr/bin/env python3
"""Does the air-quality port actually go red when the page or its record drifts? — 2026-11-26.

`tests/test_air_page_claims.py` (26 tests) re-derives the air page's offline checks in Python
because no registered job executes `validate_air_page.mjs`. Passing on the real page is half the
proof; this file is the other half, the fourth port put against a page that is wrong (co-safety,
food-safety, heat and fetchable have theirs). Chosen against this page's own claims — a table of
WHO guideline numbers, a demonstration table, one measured contradiction, honesty sentences:

  1. the page's WHO 24-hour PM2.5 value cannot part company with the record (15 -> 25);
  2. the record is the side that drifts: a changed guideline value in a temp copy of the record;
  3. the measured contradiction (Beijing PM2.5 1.7 with a US sub-index of 114) cannot lose its
     'cannot both describe the same hour' sentence;
  4. 'One hour is not a trend' — the sentence that says a single reading is a single reading;
  5. the page cannot swap the WHO 2021 document link for another.

Each mutation is applied to a temporary copy; the repository page and record are never written.

  6. a demonstration-row number (London PM2.5 9.2 -> 19.2) cannot be edited alone — measured
     2026-11-26: the port catches it (1 failure), so the demonstration table is not decoration.

NOT established: exhaustiveness; a mutation this file does not think of is uncaught, and the live
Open-Meteo fetch the .mjs makes is not exercised anywhere offline.

Run: python3 tests/test_air_port_is_sensitive.py
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

# Pinned deliberately: if the port grows or shrinks, update by hand and re-check sensitivity.
PORT_TESTS = 26


def run_port(page_path: Path = PAGE, record_path: Path = RECORD):
    spec = importlib.util.spec_from_file_location("air_port_under_test", PORT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.PAGE = page_path
    module.RECORD = record_path
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    return unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)


class PortSensitivity(unittest.TestCase):
    def setUp(self):
        self.html = PAGE.read_text(encoding="utf-8")
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    @staticmethod
    def red(result) -> int:
        return len(result.failures) + len(result.errors)

    def mutated_page(self, old: str, new: str):
        self.assertIn(old, self.html, f"the page no longer holds {old!r}; retarget the mutation")
        path = self.tmp / "mutated.html"
        path.write_text(self.html.replace(old, new, 1), encoding="utf-8")
        return run_port(page_path=path)

    def test_the_real_page_passes(self):
        result = run_port()
        self.assertEqual(result.testsRun, PORT_TESTS,
                         "the port's count changed; update PORT_TESTS and re-check sensitivity")
        self.assertEqual(result.failures, [])
        self.assertEqual(result.errors, [])

    def test_a_moved_who_guideline_in_the_page_is_caught(self):
        result = self.mutated_page('average: "24-hour", value: 15, annual: 5',
                                   'average: "24-hour", value: 25, annual: 5')
        self.assertGreater(self.red(result), 0,
                           "the port passed a page that tells readers PM2.5 is fine up to 25")

    def test_a_moved_guideline_in_the_record_is_caught(self):
        data = json.loads(RECORD.read_text(encoding="utf-8"))
        data["who_guidelines"]["pm2_5"]["value"] = 25
        path = self.tmp / "record.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        result = run_port(record_path=path)
        self.assertGreater(self.red(result), 0,
                           "the port passed a record whose guideline no longer matches the page")

    def test_a_dropped_contradiction_sentence_is_caught(self):
        result = self.mutated_page("cannot both describe the same hour",
                                   "may describe different hours")
        self.assertGreater(self.red(result), 0,
                           "the port passed a page that stopped saying why the pair matters")

    def test_a_dropped_one_hour_caveat_is_caught(self):
        result = self.mutated_page("One hour is not a trend", "One hour is a trend")
        self.assertGreater(self.red(result), 0,
                           "the port passed a page that calls one reading a trend")

    def test_a_single_demonstration_number_is_caught(self):
        result = self.mutated_page('{ place: "London",      pm2_5: 9.2,',
                                   '{ place: "London",      pm2_5: 19.2,')
        self.assertGreater(self.red(result), 0,
                           "the port passed a demonstration row whose number was edited alone")

    def test_a_swapped_who_link_is_caught(self):
        result = self.mutated_page("https://www.who.int/publications/i/item/9789240034228",
                                   "https://www.who.int/publications/i/item/0000000000000")
        self.assertGreater(self.red(result), 0,
                           "the port passed a page that cites a different WHO document")


if __name__ == "__main__":
    unittest.main(verbosity=2)
