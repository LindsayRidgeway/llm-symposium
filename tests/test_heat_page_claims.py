#!/usr/bin/env python3
"""The heat page's own 57 checks, re-derived in the suite that actually runs — 2026-11-26.

Why this file exists. `docs/works/heat.html` tells the reader:

    "`tests/validate_heat_page.mjs` re-checks, offline, that every quotation in it appears on
     this page verbatim and that the thresholds above are the ones the record holds"

and `docs/works/index.html` repeats it with a count ("57 checks, offline"). Both sentences are
true of the harness and false of this repository's behaviour: no registered job *executes* a
`.mjs` validator. `.github/workflows/test-and-report.yml` hands them to `node --check`, a syntax
check, and skips cleanly when Node is absent — which it is on this checkout (no node, nodejs,
deno or bun on PATH, measured 2026-11-25). So the guard behind the page's central claim has
never run here, and the number on the index cannot be re-derived here at all.

This test is the heat page's share of `js-harness-claims`: the half Dmitri's audit of 2026-11-25
called "offline and re-derivable in Python". It re-implements, from the page and
`docs/works/heat-sources.json` alone, every assertion in the harness that needs no runtime:

  1. every quotation in the record appears VERBATIM on the page (20 of them);
  2. every threshold in the page's own `LIMITS` object equals the record's `numbers`, so neither
     side can move alone — plus the two the page's argument rests on: the fan line is WHO's 40 °C
     and its two spellings (40 °C / 104 °F) agree;
  3. every figure the page states in prose that a reader would check by hand is present, and the
     WHO death counts are formatted on the page as the record holds them;
  4. the page's `verdictFor()` still decides in the order the page's claim depends on —
     confusion/alert first, then hot-dry-skin, then the fan line — and its cooling instructions
     still interpolate `LIMITS.cooling_window_min` rather than hard-coding a number, so moving 30
     cannot leave the prose behind;
  5. the honesty markers the page is worth reading for are still there;
  6. the record keeps its unfetchable sources unfetched (`used: false`), not as citations.

What it does NOT do, deliberately. It does not execute the page's inline script and it does not
stub a DOM: the harness's six behavioural cases (emergency on confusion, emergency on hot dry
skin, contested at and above 40, ordinary cooling below, and so on) call a function that only a
JavaScript runtime can call. Section 4 pins the *shape* of that decision, which is what rots
silently when someone reorders branches to fix a layout bug; the runtime behaviour stays the
harness's job, for a machine that runs it. The page's sentence stays honest because it does not
say *which* job runs the harness — this test does not make it a lie, it makes the claims that can
be checked here fail a build.

Sibling work, not this file: air, co-safety and food-safety are the same shape (four "offline, N
checks" pages) and remain unported; fetchable, recalls, retraction, trials and unreported-trials
re-measure live APIs and close honestly by an amended claim, not by a Python port.

Run: python3 tests/test_heat_page_claims.py
"""

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PAGE = REPO / "docs" / "works" / "heat.html"
RECORD = REPO / "docs" / "works" / "heat-sources.json"


def page_text() -> str:
    return PAGE.read_text(encoding="utf-8")


def record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def inline_script(html: str) -> str:
    blocks = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>", html)
    assert len(blocks) == 1, f"expected one inline script on the page, found {len(blocks)}"
    return blocks[0]


def page_limits(script: str) -> dict:
    """The page's own LIMITS object, read as data — the same thing the harness loads via vm."""
    m = re.search(r"const\s+LIMITS\s*=\s*\{([^}]*)\}", script)
    assert m is not None, "the page no longer declares `const LIMITS = { ... }`"
    limits = {}
    for key, value in re.findall(r"(\w+)\s*:\s*(-?[\d.]+)", m.group(1)):
        limits[key] = float(value) if "." in value else int(value)
    return limits


def verdict_for_body(script: str) -> str:
    m = re.search(r"function\s+verdictFor\s*\(([^)]*)\)\s*\{", script)
    assert m is not None, "the page no longer defines verdictFor()"
    start = m.end()
    depth, i = 1, start
    while i < len(script) and depth:
        if script[i] == "{":
            depth += 1
        elif script[i] == "}":
            depth -= 1
        i += 1
    return script[start:i - 1]


class RecordQuotations(unittest.TestCase):
    """Claim 1: a quotation cannot be softened on the page or invented in the record."""

    def test_the_record_holds_quotations_at_all(self):
        quotes = record()["quotes"]
        self.assertGreaterEqual(len(quotes), 15,
                                "the record's quotation list has shrunk; the harness asserts 15")

    def test_every_quotation_appears_verbatim_on_the_page(self):
        page = page_text()
        quotes = record()["quotes"]
        missing = [f"{q['source']}: {q['text'][:70]!r}" for q in quotes if q["text"] not in page]
        self.assertEqual(missing, [],
                         "quotations in docs/works/heat-sources.json that are no longer verbatim "
                         "on docs/works/heat.html")

    def test_every_quotation_names_its_source(self):
        unnamed = [i for i, q in enumerate(record()["quotes"]) if not q.get("source")]
        self.assertEqual(unnamed, [], "quotations with no source: a quotation with no source is "
                                      "the page's own words wearing an authority's clothes")


class Thresholds(unittest.TestCase):
    """Claim 2: neither the page nor the record can move a threshold alone."""

    def setUp(self):
        self.limits = page_limits(inline_script(page_text()))
        self.numbers = record()["numbers"]

    def test_the_page_still_exposes_a_limits_object(self):
        self.assertGreaterEqual(len(self.limits), 5,
                                "LIMITS has fewer keys than the page's own logic uses")

    def test_the_record_still_holds_numbers(self):
        self.assertGreaterEqual(len(self.numbers), 15,
                                "the record's numbers object has shrunk below the harness's floor")

    def test_every_page_threshold_equals_the_record(self):
        drift = {k: (v, self.numbers.get(k)) for k, v in self.limits.items()
                 if self.numbers.get(k) != v}
        self.assertEqual(drift, {},
                         "thresholds that differ between the page's LIMITS and the record "
                         "(page, record)")

    def test_the_fan_line_is_who_s_forty_and_not_an_invented_one(self):
        self.assertEqual(self.limits.get("fan_max_c"), 40,
                         "the fan line is WHO's 40 °C; a different number is the page's own")

    def test_the_two_spellings_of_the_fan_line_agree(self):
        self.assertEqual((self.limits.get("fan_max_c"), self.limits.get("fan_max_f")), (40, 104),
                         "40 °C is 104 °F; a page that says both must not let them part")


class ProseFigures(unittest.TestCase):
    """Claim 3: the numbers a reader would check by hand are on the page."""

    def setUp(self):
        self.page = page_text()
        self.numbers = record()["numbers"]

    def test_the_who_death_counts_are_formatted_as_the_record_holds_them(self):
        for label, key in (
            ("WHO annual heat deaths", "who_heat_deaths_annual"),
            ("WHO Europe 2022 excess deaths", "who_europe_2022_excess"),
            ("2003 Europe deaths", "who_2003_europe_deaths"),
            ("2010 Russia excess deaths", "who_2010_russia_excess"),
        ):
            with self.subTest(label):
                formatted = f"{self.numbers[key]:,}"
                self.assertIn(formatted, self.page,
                              f"{label} = {formatted} is in the record but not on the page")

    def test_the_falmouth_figures_are_on_the_page(self):
        self.assertIn(str(self.numbers["falmouth_cases"]), self.page,
                      "the Falmouth case count is in the record but not on the page")
        self.assertIn(f"{self.numbers['falmouth_cooling_c_per_min']} °C per minute", self.page,
                      "the Falmouth cooling rate is in the record but not on the page")

    def test_the_sunshine_penalty_is_stated_as_the_nws_states_it(self):
        self.assertIn(f"{self.numbers['heat_index_sun_penalty_f']}°F", self.page,
                      "the heat-index sunshine penalty is in the record but not on the page")


class DecisionLogic(unittest.TestCase):
    """Claim 4, as far as Python can honestly go: the page's decision still has its shape.

    The six behavioural cases need a JavaScript runtime. What is checkable here is the thing that
    breaks first when someone edits for looks — branch order, and whether the instructions
    interpolate LIMITS rather than repeat its numbers as literals.
    """

    def setUp(self):
        self.script = inline_script(page_text())
        self.body = verdict_for_body(self.script)
        self.limits = page_limits(self.script)

    def test_confusion_is_checked_before_anything_else(self):
        alert = self.body.find('alert === "no"')
        sweat = self.body.find('sweating === "no"')
        fan = self.body.find("LIMITS.fan_max_c")
        self.assertGreaterEqual(alert, 0, "verdictFor no longer tests the alert answer")
        self.assertGreaterEqual(sweat, 0, "verdictFor no longer tests for hot dry skin")
        self.assertGreaterEqual(fan, 0, "verdictFor no longer tests against the fan line")
        self.assertLess(alert, sweat,
                        "hot dry skin is now tested before confusion; the harness asserts "
                        "confusion beats every other input")
        self.assertLess(sweat, fan,
                        "the fan line is now tested before hot dry skin; a person with dry skin "
                        "at 31 °C would be told to cool rather than to call")

    def test_the_fan_threshold_is_at_or_above_the_who_line(self):
        m = re.search(r"t\s*(>=|>)\s*LIMITS\.fan_max_c", self.body)
        self.assertIsNotNone(m, "verdictFor no longer compares against LIMITS.fan_max_c")
        self.assertEqual(m.group(1), ">=",
                         "the comparison is now exclusive; the page's claim is that the WHO line "
                         "ITSELF (40 °C) is already contested")

    def test_the_cooling_window_is_interpolated_not_hard_coded(self):
        window = self.limits.get("cooling_window_min")
        self.assertIsNotNone(window, "LIMITS no longer holds cooling_window_min")
        self.assertIn("LIMITS.cooling_window_min", self.body,
                      "verdictFor no longer interpolates the cooling window, so moving it in "
                      "LIMITS would leave the instructions saying the old number")
        self.assertGreaterEqual(window, 10, "a cooling window under ten minutes is not a window")

    def test_every_branch_says_what_to_do(self):
        levels = re.findall(r'level:\s*"(\w+)"', self.body)
        self.assertGreaterEqual(sorted(set(levels)), ["contested", "cool", "emergency"],
                                "verdictFor no longer returns all three of the page's verdicts")
        steps = re.findall(r"steps:\s*\[", self.body)
        self.assertEqual(len(steps), len(re.findall(r"return\s*\{", self.body)),
                         "a branch returns a verdict with no steps; an answer with no "
                         "instruction is worse than no answer")


class HonestyMarkers(unittest.TestCase):
    """Claim 5: the page still says what it does not do. That sentence is why it is worth reading."""

    def setUp(self):
        self.page = page_text()

    def test_the_page_says_what_it_does_not_do(self):
        self.assertIn("What this page does not do", self.page)

    def test_the_page_states_that_it_cannot_diagnose(self):
        self.assertRegex(self.page, r"cannot diagnose")

    def test_the_page_states_that_the_cdc_fetch_was_refused(self):
        self.assertTrue("403" in self.page and "CDC" in self.page,
                        "the record of the refused CDC fetch has been edited away")

    def test_the_page_names_its_record_and_its_harness(self):
        for name in ("docs/works/heat-sources.json", "tests/validate_heat_page.mjs"):
            with self.subTest(name):
                self.assertIn(name, self.page,
                              "the page no longer names the file its claim rests on")

    def test_the_page_yields_to_local_authority(self):
        self.assertRegex(self.page, r"they are right and this page is wrong",
                         "the sentence that yields to local authority has been lost")


class RecordSources(unittest.TestCase):
    """Claim 6: a source that could not be fetched is recorded as unfetched, not as a citation."""

    def test_unfetchable_sources_are_marked_unused(self):
        offending = [s.get("url") for s in record()["sources"]
                     if s.get("http_status") in (403, 410) and s.get("used") is not False]
        self.assertEqual(offending, [],
                         "sources the record marks 403/410 but `used` — an unfetched source "
                         "cannot back a claim")

    def test_the_record_names_the_page_it_pins(self):
        self.assertIn("heat", record()["page"].lower(),
                      "heat-sources.json no longer names the page it belongs to")


if __name__ == "__main__":
    unittest.main(verbosity=2)
