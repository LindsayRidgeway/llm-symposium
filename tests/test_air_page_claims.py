#!/usr/bin/env python3
"""The air page's own 56 checks, re-derived in the suite that actually runs — 2026-11-26.

Why this file exists. `docs/works/air.html` tells the reader:

    "Mirrored exactly in `docs/works/air-quality-sources.json`, which
     `tests/validate_air_quality_page.mjs` checks these against, so a guideline value cannot be
     edited on the page alone"

and `docs/works/index.html` repeats it with a count ("56 checks, offline"). Both sentences are
true of the harness and false of this repository's behaviour: no registered job *executes* a
`.mjs` validator. `.github/workflows/test-and-report.yml` hands them to `node --check`, a syntax
check, and skips cleanly when Node is absent — which it is on this checkout (no node, nodejs,
deno or bun on PATH, measured 2026-11-25). So the guard behind the page's central claim has never
run here.

This test is the air page's share of `js-harness-claims`, second of the four "offline, N checks"
pages (heat landed first). It re-implements, from the page and `docs/works/air-quality-sources.json`
alone, every assertion in `tests/validate_air_quality_page.mjs` that needs no runtime:

  1. the page declares exactly one inline script, no external one, so the numbers it prints are
     the numbers in its own source;
  2. the page's `WHO_GUIDELINES` and `EXAMPLES` objects equal the record's, field for field, so
     neither side can move alone — and `EXAMPLES_DATE` / `GUIDELINE_SOURCE` agree too;
  3. the record's own guideline values equal the WHO's published 2021 numbers, hard-coded here,
     so pinning the page to the record cannot pin it to a wrong record;
  4. the page's verdict rule, read out of its source and re-applied here, gives the same answers
     the harness asserts case by case — including the honest blanks: a missing reading is
     "unknown", never a zero, and exactly at a guideline is "under", not "over";
  5. the demonstration table still demonstrates the disagreement it is quoted for (six measured
     rows, at least two disagreeing by 10+ index points, the London row the prose points at
     really differing), rather than asserting it in prose;
  6. the measured internal inconsistency (Beijing: 1.7 µg/m³ next to a sub-index of 114) is in
     the record and printed on the page;
  7. the honesty markers the page is worth reading for are still there, and the sources it names
     are the ones it links.

What it does NOT do, deliberately. It does not execute the page's inline script: the harness's
behavioural cases call `whoVerdict` / `timesGuideline` / `comparables` as JavaScript functions.
Section 4 pins the *rule* those functions implement — read from the function bodies — and applies
it to the record's numbers, which is what rots silently when someone rewrites a comparison to fix
a layout bug. Runtime behaviour stays the harness's job, for a machine that runs it. The page's
sentence stays honest either way: this test makes the claims that can be checked here fail a build.

Sibling work, not this file: co-safety and food-safety are the same shape (the other two
"offline, N checks" pages) and remain unported; recalls, retraction, trials and
unreported-trials re-measure live APIs and close honestly by an amended claim, not by a
Python port. fetchable.html was on that side too, but the half of its harness that reads the
page and the dated file ported on 2026-11-26 (tests/test_fetchable_page_claims.py); its five
live re-measurements stay the harness's job and its claim was amended to say so.

Run: python3 tests/test_air_page_claims.py
"""

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PAGE = REPO / "docs" / "works" / "air.html"
RECORD = REPO / "docs" / "works" / "air-quality-sources.json"

WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10,
}
ORDINALS = {
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7,
    "eighth": 8, "ninth": 9, "tenth": 10,
}


def page_text() -> str:
    return PAGE.read_text(encoding="utf-8")


def record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def inline_script(html: str) -> str:
    blocks = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>", html)
    assert len(blocks) == 1, f"expected one inline script on the page, found {len(blocks)}"
    return blocks[0]


GUIDELINE_ROW = re.compile(
    r"(\w+):\s*\{\s*label:\s*\"([^\"]*)\",\s*average:\s*\"([^\"]*)\",\s*"
    r"value:\s*(-?[\d.]+),\s*annual:\s*(null|-?[\d.]+)\s*\}"
)


def page_guidelines(script: str) -> dict:
    """The page's own WHO_GUIDELINES, read as data — the object the harness compares to the record."""
    return {
        key: {
            "label": label,
            "average": average,
            "value": float(value) if "." in value else int(value),
            "annual": None if annual == "null" else (float(annual) if "." in annual else int(annual)),
        }
        for key, label, average, value, annual in GUIDELINE_ROW.findall(script)
    }


EXAMPLE_ROW = re.compile(
    r"\{\s*place:\s*\"([^\"]*)\",\s*pm2_5:\s*(-?[\d.]+),\s*"
    r"us_aqi:\s*(-?[\d.]+),\s*european_aqi:\s*(-?[\d.]+)\s*\}"
)


def _num(text: str):
    return float(text) if "." in text else int(text)


def page_examples(script: str) -> list:
    """The page's own EXAMPLES table, read as data."""
    return [
        {"place": place, "pm2_5": _num(pm), "us_aqi": _num(us), "european_aqi": _num(eu)}
        for place, pm, us, eu in EXAMPLE_ROW.findall(script)
    ]


def const_string(script: str, name: str) -> str:
    m = re.search(r"const\s+" + name + r"\s*=\s*\"([^\"]*)\"", script)
    assert m is not None, f"the page no longer declares `const {name} = \"...\"`"
    return m.group(1)


def function_body(script: str, name: str) -> str:
    m = re.search(r"function\s+" + name + r"\s*\(([^)]*)\)\s*\{", script)
    assert m is not None, f"the page no longer defines {name}()"
    start = m.end()
    depth, i = 1, start
    while i < len(script) and depth:
        if script[i] == "{":
            depth += 1
        elif script[i] == "}":
            depth -= 1
        i += 1
    return script[start:i - 1]


# ---- the page's rule, re-applied from the record's numbers ---------------------------------
# These two functions are the harness's section 5, rewritten in Python. They are fed the page's
# own parsed constants, so a guideline edited on the page alone changes their answers.

def times_guideline(guidelines: dict, pollutant: str, measured):
    guideline = guidelines.get(pollutant)
    if guideline is None or measured is None:
        return None
    return measured / guideline["value"]


def who_verdict(guidelines: dict, pollutant: str, measured):
    times = times_guideline(guidelines, pollutant, measured)
    if times is None:
        return {"verdict": "unknown", "times": None,
                "guideline": guidelines.get(pollutant, {}).get("value")}
    return {"verdict": "over" if times > 1 else "under", "times": times,
            "guideline": guidelines[pollutant]["value"]}


def comparables(guidelines: dict, current: dict) -> list:
    return [p for p in guidelines if current.get(p) is not None]


class PageAndRecordAgree(unittest.TestCase):
    """Claims 1 and 2: one self-contained script, and its constants are the record's."""

    def test_one_inline_script_and_no_external_one(self):
        html = page_text()
        self.assertEqual(len(re.findall(r"<script(?![^>]*\bsrc=)[^>]*>", html)), 1,
                         "the page no longer has exactly one inline script")
        self.assertNotRegex(html, r"<script[^>]*\bsrc=",
                            "the page gained an external script; its numbers are no longer its own")

    def test_page_guidelines_equal_the_record(self):
        page = page_guidelines(inline_script(page_text()))
        self.assertEqual(page, record()["who_guidelines"],
                         "docs/works/air.html and air-quality-sources.json disagree on a guideline")

    def test_page_examples_equal_the_record(self):
        page = page_examples(inline_script(page_text()))
        self.assertEqual(page, record()["demonstration"]["examples"],
                         "the page's demonstration table is not the one the record holds")

    def test_example_date_and_guideline_source_agree(self):
        script = inline_script(page_text())
        self.assertEqual(const_string(script, "EXAMPLES_DATE"),
                         record()["demonstration"]["date"],
                         "the page prints a different measurement date than the record")
        self.assertEqual(const_string(script, "GUIDELINE_SOURCE"),
                         record()["guideline_source"]["name"],
                         "the page names a different guideline document than the record")

    def test_the_record_says_when_each_source_was_checked(self):
        rec = record()
        self.assertTrue(rec["_checked"], "the record lost the date it was checked")
        self.assertIn("2021", rec["guideline_source"]["name"])
        self.assertRegex(rec["guideline_source"]["url"], r"9789240034228",
                         "the guideline URL no longer points at the 2021 document")

    def test_the_record_counts_the_same_rows_it_lists(self):
        """A note that says "seven places" beside a six-row list is a record disagreeing with itself."""
        rec = record()
        note = rec["demonstration"]["note"]
        mentioned = [WORD_NUMBERS[w] for w in WORD_NUMBERS if re.search(r"\b" + w + r"\s+places", note)]
        self.assertEqual(mentioned, [len(rec["demonstration"]["examples"])],
                         f"the demonstration note names {mentioned} places; the list holds "
                         f"{len(rec['demonstration']['examples'])}")


class TheRecordIsTheWHOsNumbers(unittest.TestCase):
    """Claim 3: pinning the page to the record must not pin it to a wrong record."""

    # WHO global air quality guidelines, 2021 — hard-coded, not read from the record.
    WHO_PUBLISHED = {
        "pm2_5":            {"average": "24-hour", "value": 15, "annual": 5},
        "pm10":             {"average": "24-hour", "value": 45, "annual": 15},
        "ozone":            {"average": "8-hour",  "value": 100, "annual": None},
        "nitrogen_dioxide": {"average": "24-hour", "value": 25, "annual": 10},
        "sulphur_dioxide":  {"average": "24-hour", "value": 40, "annual": None},
    }

    def test_the_record_holds_exactly_the_five_who_pollutants(self):
        self.assertEqual(sorted(record()["who_guidelines"]), sorted(self.WHO_PUBLISHED),
                         "the record holds a pollutant set the WHO 2021 guidelines do not define")

    def test_each_value_window_and_annual_value_is_the_who_published_one(self):
        rec = record()["who_guidelines"]
        for pollutant, expected in self.WHO_PUBLISHED.items():
            got = rec.get(pollutant, {})
            self.assertEqual(got.get("value"), expected["value"],
                             f"{pollutant}: 24-hr/8-hr guideline is not the WHO's {expected['value']}")
            self.assertEqual(got.get("average"), expected["average"],
                             f"{pollutant}: averaging window is not the WHO's {expected['average']}")
            self.assertEqual(got.get("annual"), expected["annual"],
                             f"{pollutant}: annual guideline is not the WHO's {expected['annual']}")

    def test_every_guideline_names_what_it_measures(self):
        for pollutant, row in record()["who_guidelines"].items():
            self.assertTrue(row.get("label"), f"{pollutant} has no label for the reader")


class TheVerdictRule(unittest.TestCase):
    """Claim 4: the comparison itself, including the blanks — the half a page gets wrong silently."""

    def setUp(self):
        self.script = inline_script(page_text())
        self.guidelines = page_guidelines(self.script)

    def test_the_rule_read_off_the_page_is_a_ratio_of_the_guideline(self):
        body = function_body(self.script, "timesGuideline")
        self.assertIn("/ g.value", body,
                      "timesGuideline no longer divides by the guideline it looked up")
        self.assertRegex(body, r"if\s*\(\s*!g\b",
                         "timesGuideline no longer returns the honest blank for an unknown pollutant")
        self.assertRegex(body, r"measured\s*==\s*null", "the null guard is gone: a missing reading "
                                                       "would now divide or print NaN")
        self.assertRegex(body, r"isNaN\(measured\)", "the NaN guard is gone from timesGuideline")

    def test_exactly_at_the_guideline_is_under_not_over(self):
        body = function_body(self.script, "whoVerdict")
        self.assertRegex(body, r"t\s*>\s*1\s*\?\s*\"over\"\s*:\s*\"under\"",
                         "whoVerdict changed its boundary: the harness asserts a value exactly at the "
                         "guideline counts as under")
        self.assertEqual(who_verdict(self.guidelines, "pm2_5", 15)["verdict"], "under")

    def test_the_harness_cases_answer_the_same_way(self):
        cases = [
            ("pm2_5", 30, "over", 2.0, 15),
            ("pm2_5", 15, "under", 1.0, 15),
            ("pm2_5", 7.5, "under", 0.5, 15),
            ("pm10", 45, "under", 1.0, 45),
            ("ozone", 50, "under", 0.5, 100),
            ("nitrogen_dioxide", 50, "over", 2.0, 25),
            ("sulphur_dioxide", 40, "under", 1.0, 40),
        ]
        for pollutant, value, verdict, times, guideline in cases:
            got = who_verdict(self.guidelines, pollutant, value)
            self.assertEqual(got["verdict"], verdict, f"{pollutant}={value}: {got}")
            self.assertAlmostEqual(got["times"], times, places=9, msg=f"{pollutant}={value}")
            self.assertEqual(got["guideline"], guideline, f"{pollutant}={value}")

    def test_a_missing_reading_is_unknown_never_a_zero(self):
        for pollutant in ("pm2_5", "ozone"):
            got = who_verdict(self.guidelines, pollutant, None)
            self.assertEqual(got, {"verdict": "unknown", "times": None,
                                   "guideline": self.guidelines[pollutant]["value"]})
        self.assertIsNone(times_guideline(self.guidelines, "pm2_5", None),
                          "timesGuideline must return None, not NaN, for a missing value")

    def test_a_pollutant_with_no_guideline_is_unknown_not_an_invented_zero(self):
        got = who_verdict(self.guidelines, "carbon_monoxide", 200)
        self.assertEqual(got, {"verdict": "unknown", "times": None, "guideline": None})
        self.assertIsNone(times_guideline(self.guidelines, "nope", 5))

    def test_only_pollutants_with_a_reading_and_a_guideline_are_compared(self):
        body = function_body(self.script, "comparables")
        self.assertIn("Object.keys(WHO_GUIDELINES)", body,
                      "comparables no longer walks the guided pollutants")
        self.assertIn("!= null", body, "comparables no longer drops a missing reading")
        self.assertIn("isNaN", body, "comparables no longer drops a non-number")
        self.assertEqual(
            comparables(self.guidelines, {"pm2_5": 3, "ozone": 50, "carbon_monoxide": 100}),
            ["pm2_5", "ozone"],
            "carbon monoxide has no WHO 2021 guideline and must be dropped")
        self.assertEqual(comparables(self.guidelines, {}), [],
                         "no readings means nothing to compare")
        self.assertEqual(comparables(self.guidelines, {"pm2_5": None}), [],
                         "a null reading is not compared")


class TheDisagreementIsShown(unittest.TestCase):
    """Claim 5: the page's central claim is a table, and the table still disagrees with itself."""

    def setUp(self):
        self.examples = page_examples(inline_script(page_text()))

    def test_six_measured_rows(self):
        self.assertEqual(len(self.examples), 6, "the harness asserts six measured examples")

    def test_every_row_holds_the_three_numbers(self):
        for row in self.examples:
            for key in ("pm2_5", "us_aqi", "european_aqi"):
                self.assertIsInstance(row.get(key), (int, float),
                                      f"{row.get('place')} lost its {key}")

    def test_at_least_two_rows_disagree_by_ten_points(self):
        gaps = [abs(r["us_aqi"] - r["european_aqi"]) for r in self.examples]
        self.assertGreaterEqual(sum(1 for g in gaps if g >= 10), 2,
                                f"the two indexes no longer visibly disagree: gaps {gaps}")

    def test_at_least_one_row_disagrees_by_twenty_points(self):
        gaps = [abs(r["us_aqi"] - r["european_aqi"]) for r in self.examples]
        self.assertGreaterEqual(max(gaps), 20, f"largest disagreement is now {max(gaps)}")

    def test_the_london_row_the_prose_points_at_really_differs(self):
        london = next((r for r in self.examples if r["place"] == "London"), None)
        self.assertIsNotNone(london, "the prose points at a London row that is gone")
        self.assertNotEqual(london["us_aqi"], london["european_aqi"],
                            "the London row now agrees with itself; the prose's example is void")

    def test_the_prose_points_at_the_row_it_quotes(self):
        """The demo note used to say "the second and third rows" while discussing London, the third."""
        html = page_text()
        place = self.examples[2]["place"]
        m = re.search(r"Read the (\w+) row([^<]*)", html)
        self.assertIsNotNone(m, "the demo note no longer points the reader at a row")
        self.assertEqual(ORDINALS.get(m.group(1)), 3,
                         f"the note points at row {m.group(1)!r}; the row it discusses is the third")
        self.assertIn(place, m.group(2) + html[m.end():m.end() + 300],
                      "the note no longer names the row it points at")

    def test_the_ratio_column_is_the_measured_value_over_the_guideline(self):
        body = function_body(inline_script(page_text()), "renderDemo")
        self.assertIn("e.pm2_5 / WHO_GUIDELINES.pm2_5.value", body,
                      "the demonstration's fifth column no longer divides by the WHO 24-hour value")
        ratios = {r["place"]: r["pm2_5"] / 15 for r in self.examples}
        for place, ratio in ratios.items():
            self.assertIsInstance(ratio, float, place)
        self.assertGreater(ratios["Delhi"], 7, "Delhi's row no longer reads as far over the guideline")
        self.assertLess(ratios["Reykjavik"], 1, "Reykjavik's row no longer reads as under")


class TheMeasuredInconsistency(unittest.TestCase):
    """Claim 6: the reason the page shows a concentration next to an index is still printed."""

    def test_the_record_holds_it(self):
        inc = record()["measured_inconsistency"]
        self.assertEqual(inc["pm2_5"], 1.7)
        self.assertEqual(inc["us_aqi_pm2_5"], 114)
        self.assertEqual(inc["european_aqi"], 20)
        self.assertIn("Beijing", inc["place"])

    def test_the_page_prints_both_numbers(self):
        html = page_text()
        inc = record()["measured_inconsistency"]
        self.assertIn("1.7", html, "the page no longer prints the contradiction's concentration")
        self.assertIn(str(inc["us_aqi_pm2_5"]), html,
                      "the page no longer prints the sub-index that contradicts it")
        self.assertRegex(html, r"cannot both describe the same hour",
                         "the page no longer says why the pair matters")


class HonestyMarkers(unittest.TestCase):
    """Claim 7: the sentences that make the page worth reading, and the sources it cites."""

    def setUp(self):
        self.html = page_text()
        self.rec = record()

    def test_the_limits_are_stated(self):
        for pattern, why in [
            (r"model, not a monitor", "says it is a model, not a monitor"),
            (r"index is not a diagnosis", "says an index is not a diagnosis"),
            (r"worst pollutant, not the particles", "explains that the index is the worst pollutant"),
            (r"different rulers|two agencies draw their bands",
             "says the two indexes are different rulers"),
            (r"not reported", "prints 'not reported' rather than a zero"),
            (r"One hour is not a trend", "says one reading is one reading"),
        ]:
            self.assertRegex(self.html, pattern, why)

    def test_the_sources_it_names_are_linked(self):
        self.assertIn("https://open-meteo.com/en/docs/air-quality-api", self.html)
        self.assertIn("https://www.who.int/publications/i/item/9789240034228", self.html)
        self.assertRegex(self.html, r"Copernicus")
        self.assertIn("free, no key", self.html)
        self.assertEqual(self.rec["data_source"]["auth"], "none (keyless)",
                         "the record no longer says the API is keyless")
        self.assertIn("Copernicus", self.rec["data_source"]["upstream"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
