#!/usr/bin/env python3
"""The CO-safety page's own offline checks, re-derived in the suite that actually runs — 2026-11-26.

Why this file exists. `docs/works/co-safety.html` tells the reader:

    "`tests/validate_co_safety_page.mjs`, so a later edit cannot move a number or alter a quote
     without failing a check"

and `docs/works/index.html` says the same harness runs "offline". Both sentences are true of the
harness and false of this repository's behaviour: no registered job *executes* a `.mjs` validator.
`.github/workflows/test-and-report.yml` hands them to `node --check`, a syntax check, and skips
cleanly when Node is absent — which it is on this checkout (no node, nodejs, deno or bun on PATH,
measured 2026-11-25). So the guard behind the page's central claim has never run here.

This test is the co-safety page's share of `js-harness-claims`, the half Dmitri's audit of
2026-11-25 called "offline and re-derivable in Python". It re-implements, from the page and
`docs/works/co-safety-sources.json` alone, every harness assertion that needs no runtime:

  1. every quotation in the record appears VERBATIM on the page (18 of them), and the record's
     floor of 8 is not crept below;
  2. every threshold in the page's own `THRESHOLDS` object equals the record's `numbers`, through
     an explicit record-key -> page-key map, so a rename cannot quietly pass;
  3. the figures the page states in prose are the record's, and the two refusal markers
     ("NOT VERIFIED HERE", the 403) are still there;
  4. the page's `verdictFor()` still decides in the order the page's argument rests on — indoors
     first, then "under 20 feet, move it", then permitted — still interpolates `T.distance_feet`
     rather than hard-coding 20, still appends the no-alarm note to all three verdicts, and still
     has a fallback that refuses to guess;
  5. the honesty markers the page is worth reading for are still there: no air measured, four
     disagreements reported rather than resolved, local authority wins;
  6. the record keeps its refused source refused (`used: false`, HTTP 403) and names its own page
     and fetch date.

What it does NOT do, deliberately. It does not execute the page's inline script and it does not
stub a DOM: the harness's behavioural cases call `verdictFor()`, which only a JavaScript runtime can
call. Section 4 pins the *shape* of that decision, which is what rots silently when someone edits
for looks; the runtime behaviour stays the harness's job, for a machine that runs it.

Sibling work: `tests/test_heat_page_claims.py`, `tests/test_air_page_claims.py` and
`tests/test_fetchable_page_claims.py` are the same port for the other three offline pages.
food-safety, nonreplication and warming remain unported; recalls, retraction, trials and
unreported-trials re-measure live APIs and close honestly by an amended claim, not by a port.

Run: python3 tests/test_co_safety_page_claims.py
"""

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PAGE = REPO / "docs" / "works" / "co-safety.html"
RECORD = REPO / "docs" / "works" / "co-safety-sources.json"

# The harness's own map, kept explicit so a key renamed on one side fails here rather than passing.
NUMBER_MAP = {
    "distance_feet": "distance_feet",
    "cdc_deaths_unintentional": "cdc_deaths",
    "cpsc_deaths_consumer_products": "cpsc_deaths",
    "cpsc_deaths_generators": "cpsc_generator_deaths",
    "cdc_ed_visits": "cdc_ed_visits",
    "cdc_hospitalizations": "cdc_hospitalizations",
    "alarm_replace_years_cdc": "alarm_replace_years",
    "emergency_number": "emergency_number",
}


def page_text() -> str:
    return PAGE.read_text(encoding="utf-8")


def record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def inline_script(html: str) -> str:
    blocks = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>", html)
    assert len(blocks) == 1, f"expected one inline script on the page, found {len(blocks)}"
    return blocks[0]


def js_object(script: str, name: str) -> str:
    """The raw text of `const NAME = { ... }`, matched to its closing brace."""
    m = re.search(rf"const\s+{name}\s*=\s*\{{", script)
    assert m is not None, f"the page no longer declares `const {name} = {{ ... }}`"
    start = m.end()
    depth, i = 1, start
    while i < len(script) and depth:
        if script[i] == "{":
            depth += 1
        elif script[i] == "}":
            depth -= 1
        i += 1
    return script[start:i - 1]


def page_thresholds(script: str) -> dict:
    """The page's own THRESHOLDS, read as data — the same thing the harness loads via vm."""
    body = js_object(script, "THRESHOLDS")
    out = {}
    for key, value in re.findall(r'(\w+)\s*:\s*("(?:[^"]*)"|-?[\d.]+)', body):
        if value.startswith('"'):
            out[key] = value.strip('"')
        else:
            out[key] = float(value) if "." in value else int(value)
    return out


def page_indoor(script: str) -> dict:
    """INDOOR: appliance -> the authority's own sentence, as {who, quote}."""
    body = js_object(script, "INDOOR")
    out = {}
    for key, quote in re.findall(r'(\w+)\s*:\s*\{[^}]*?quote\s*:\s*"((?:[^"\\]|\\.)*)"', body):
        out[key] = quote.replace('\\"', '"')
    return out


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

    def test_the_record_holds_a_real_quotation_set(self):
        quotes = record()["quotes"]
        self.assertGreaterEqual(len(quotes), 8,
                                "the record's quotation set has fallen below the harness's floor "
                                "of 8; the harness fails at 8 and this repository should fail at "
                                "the same number")

    def test_every_quotation_appears_verbatim_on_the_page(self):
        page = page_text()
        missing = [k for k, v in record()["quotes"].items() if v not in page]
        self.assertEqual(missing, [],
                         "quotations in docs/works/co-safety-sources.json that are no longer "
                         "verbatim on docs/works/co-safety.html")

    def test_every_quotation_is_a_sentence_and_not_a_stub(self):
        short = [k for k, v in record()["quotes"].items() if len(v.strip()) < 20]
        self.assertEqual(short, [], "quotations too short to be an authority's sentence — a stub "
                                    "here makes every verbatim check above vacuous")


class Thresholds(unittest.TestCase):
    """Claim 2: neither the page nor the record can move a number alone."""

    def setUp(self):
        self.script = inline_script(page_text())
        self.page_t = page_thresholds(self.script)
        self.numbers = record()["numbers"]

    def test_the_page_still_exposes_the_thresholds_object(self):
        self.assertGreaterEqual(len(self.page_t), 8,
                                "THRESHOLDS has fewer keys than the page's own logic uses")

    def test_every_mapped_number_equals_the_record(self):
        drift = {}
        for rec_key, page_key in NUMBER_MAP.items():
            with self.subTest(rec_key):
                self.assertIn(page_key, self.page_t,
                              f"the page no longer holds {page_key}, which the harness reads")
                self.assertEqual(self.page_t[page_key], self.numbers.get(rec_key),
                                 f"record {rec_key} and page {page_key} have parted")
                drift[rec_key] = True
        self.assertEqual(len(drift), len(NUMBER_MAP))

    def test_the_record_keeps_the_keys_the_map_names(self):
        missing = [k for k in NUMBER_MAP if k not in self.numbers]
        self.assertEqual(missing, [], "the record dropped a number the page still prints")

    def test_the_page_holds_no_threshold_outside_the_map(self):
        unmapped = sorted(set(self.page_t) - set(NUMBER_MAP.values()))
        self.assertEqual(unmapped, [], "the page gained a threshold the harness does not compare "
                                       "with the record — add it to NUMBER_MAP here and there")

    def test_the_distance_is_twenty_feet_in_both_places(self):
        self.assertEqual(self.numbers["distance_feet"], 20,
                         "20 feet is the number all three agencies print; a different one is the "
                         "page's own")
        self.assertEqual(self.page_t["distance_feet"], 20)


class ProseFigures(unittest.TestCase):
    """Claim 3: the numbers a reader would check by hand are on the page, as the record holds them."""

    def setUp(self):
        self.page = page_text()
        self.numbers = record()["numbers"]

    def test_the_death_tolls_are_stated_as_each_agency_states_them(self):
        self.assertRegex(self.page, r"[Mm]ore than 400",
                         "the CDC's 400 is in the record but no longer on the page")
        self.assertRegex(self.page, r"[Mm]ore than 200",
                         "the CPSC's 200 is in the record but no longer on the page")

    def test_the_ed_visit_and_hospitalisation_counts_are_formatted_as_the_record_holds_them(self):
        for label, key in (("ED visits", "cdc_ed_visits"),
                           ("hospitalisations", "cdc_hospitalizations")):
            with self.subTest(label):
                formatted = f"{self.numbers[key]:,}"
                self.assertIn(formatted, self.page,
                              f"{label} = {formatted} is in the record but not on the page")

    def test_the_emergency_number_and_alarm_life_are_on_the_page(self):
        self.assertIn(str(self.numbers["emergency_number"]), self.page,
                      "the emergency number is in the record but not on the page")
        self.assertIn(f"every {self.numbers['alarm_replace_years_cdc']} years", self.page,
                      "the alarm replacement interval is in the record but not on the page")

    def test_the_fetch_date_is_on_the_page(self):
        self.assertIn(record()["fetched"], self.page,
                      "the page no longer names the date its numbers were fetched")


class DecisionLogic(unittest.TestCase):
    """Claim 4, as far as Python can honestly go: the page's decision still has its shape.

    The behavioural cases (indoors refused, under 20 feet moves it, 20 feet or more permitted) need
    a JavaScript runtime. What is checkable here is what breaks first when someone edits for looks:
    branch order, whether the distance is interpolated, and whether every verdict still carries what
    to do.
    """

    def setUp(self):
        self.script = inline_script(page_text())
        self.body = verdict_for_body(self.script)
        self.page_t = page_thresholds(self.script)

    def test_indoors_is_refused_before_distance_is_considered(self):
        indoors = self.body.find('where === "indoors"')
        close = self.body.find('where === "outdoors_close"')
        far = self.body.find('where === "outdoors_far"')
        self.assertGreaterEqual(indoors, 0, "verdictFor no longer tests for indoors")
        self.assertGreaterEqual(close, 0, "verdictFor no longer tests the under-20-feet case")
        self.assertGreaterEqual(far, 0, "verdictFor no longer tests the permitted case")
        self.assertLess(indoors, close,
                        "the distance branch is now tested before indoors; the page's claim is "
                        "that indoors is refused whatever the distance")
        self.assertLess(close, far,
                        "the permitted case is now tested before the too-close one")

    def test_the_three_verdict_levels_are_still_what_the_claim_says(self):
        levels = re.findall(r'level:\s*"(\w+)"', self.body)
        self.assertEqual(sorted(set(levels)), ["deadly", "move", "ok", "unknown"],
                         "verdictFor no longer returns the page's verdict set; the harness asserts "
                         "deadly / move / ok and a fallback that refuses to guess")

    def test_the_distance_is_interpolated_not_hard_coded(self):
        self.assertIn("T.distance_feet", self.body,
                      "verdictFor no longer reads the distance out of THRESHOLDS, so moving it "
                      "there would leave the advice saying the old number")
        self.assertNotRegex(self.body, r"\b20\s*feet",
                            "verdictFor hard-codes 20 feet instead of interpolating THRESHOLDS")
        self.assertGreaterEqual(len(re.findall(r"T\.distance_feet", self.body)), 3,
                                "the distance is used in fewer places than the page's three "
                                "spellings of it (too-close headline, too-close detail, permitted)")

    def test_the_no_alarm_note_reaches_every_outdoor_verdict(self):
        self.assertIn('alarm === "no"', self.body,
                      "verdictFor no longer reads the alarm answer")
        self.assertGreaterEqual(len(re.findall(r"alarmNote", self.body)), 4,
                                "the no-alarm note is defined but no longer appended to each "
                                "outdoor verdict, which is where a listener needs it")

    def test_every_verdict_says_what_to_do(self):
        self.assertEqual(len(re.findall(r"headline:", self.body)),
                         len(re.findall(r"return\s*\{", self.body)),
                         "a branch returns a verdict with no headline; an answer with no "
                         "instruction is worse than no answer")

    def test_the_indoor_rule_is_quoted_from_the_record(self):
        page = page_text()
        indoor = page_indoor(self.script)
        quotes = set(record()["quotes"].values())
        self.assertGreaterEqual(len(indoor), 5,
                                "INDOOR has fewer appliances than the page offers in its selector")
        for appliance, quote in sorted(indoor.items()):
            with self.subTest(appliance):
                self.assertIn(quote, quotes,
                              f"the indoor rule for {appliance} is no longer one of the record's "
                              f"quotations")
                self.assertIn(quote, page,
                              f"the indoor rule for {appliance} is not verbatim on the page")


class HonestyMarkers(unittest.TestCase):
    """Claim 5: the page still says what it does not do. That sentence is why it is worth reading."""

    def setUp(self):
        self.page = page_text()

    def test_the_page_says_nothing_was_measured_here(self):
        self.assertIn("no air was measured", self.page,
                      "the sentence admitting no room was measured has been edited away")
        self.assertIn("no appliance was run", self.page)

    def test_the_page_says_the_disagreements_are_reported_not_resolved(self):
        self.assertIn("four disagreements", self.page)
        self.assertIn("reported rather than resolved", self.page)

    def test_the_page_yields_to_local_authority(self):
        self.assertIn("If a local fire department", self.page,
                      "the sentence that yields to a local alert has been lost")

    def test_the_page_marks_the_source_it_could_not_fetch(self):
        self.assertIn("NOT VERIFIED HERE", self.page,
                      "the unfetched source is no longer marked on the page")

    def test_the_page_names_its_record_and_its_harness(self):
        for name in ("docs/works/co-safety-sources.json", "tests/validate_co_safety_page.mjs"):
            with self.subTest(name):
                self.assertIn(name, self.page,
                              "the page no longer names the file its claim rests on")


class RecordSources(unittest.TestCase):
    """Claim 6: a source that could not be fetched is recorded as unfetched, not as a citation."""

    def setUp(self):
        self.rec = record()

    def test_an_unfetchable_source_is_marked_unused(self):
        offending = [s.get("name") for s in self.rec["sources"]
                     if s.get("http_status") in (403, 410) and s.get("used") is not False]
        self.assertEqual(offending, [],
                         "sources the record marks 403/410 but `used` — an unfetched source cannot "
                         "back a claim")

    def test_the_record_still_keeps_its_refused_source(self):
        refused = [s for s in self.rec["sources"] if s.get("used") is False]
        self.assertGreaterEqual(len(refused), 1,
                                "the refused source was dropped rather than recorded as refused; "
                                "the harness asserts at least one")
        for s in refused:
            self.assertEqual(s.get("http_status"), 403)

    def test_the_record_names_the_page_it_pins(self):
        self.assertIn("co-safety", self.rec["page"],
                      "co-safety-sources.json no longer names the page it belongs to")
        self.assertRegex(self.rec["fetched"], r"^\d{4}-\d{2}-\d{2}$",
                         "the record's fetch date is not a date")

    def test_every_disagreement_names_what_disagrees(self):
        for d in self.rec["disagreements"]:
            with self.subTest(d.get("id")):
                self.assertTrue(d.get("what"))
                self.assertGreaterEqual(len([k for k in d if k not in ("id", "what")]), 2,
                                        "a disagreement with one side is not a disagreement")


if __name__ == "__main__":
    unittest.main(verbosity=2)
