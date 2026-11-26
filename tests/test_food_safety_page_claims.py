#!/usr/bin/env python3
"""The food-safety page's own offline checks, re-derived in the suite that actually runs — 2026-11-26.

Why this file exists. `docs/works/food-safety.html` tells the reader, in its own Sources section:

    "The page's own numbers are checked against that file by
     `tests/validate_food_safety_page.mjs`, so a later edit cannot move a threshold without
     failing a test."

The sentence is true of the harness and false of this repository's behaviour. No registered job
*executes* a `.mjs` validator: `.github/workflows/test-and-report.yml` hands them to
`node --check`, a syntax check, and skips cleanly when Node is absent — which it is on this
checkout (no node, nodejs, deno or bun on PATH, measured 2026-11-25). The guard the page's central
promise rests on has never run here.

This test is the food-safety page's share of `js-harness-claims`, the half Dmitri's audit of
2026-11-25 called "offline and re-derivable in Python". It re-implements, from the page and
`docs/works/food-safety-sources.json` alone, every harness assertion that needs no runtime:

  1. exactly one inline script, and the thresholds live in it;
  2. every threshold on the page equals the record's, key for key, with no page-only threshold;
  3. the record's measured numbers are the numbers the page prints (the harness's own claim about
     itself: "the page's thresholds equal the numbers in ...food-safety-sources.json");
  4. `verdictFor()` still decides in the order the page's argument rests on — a measured reading
     before any clock, "keep it" before "cook it", the cooler refused, a full freezer before a half
     one — and still reads its thresholds out of `THRESHOLDS` rather than hard-coding them;
  5. the harness's fourteen behavioural cases re-derived against a Python model built from the
     page's own numbers, including the case the page exists for: 2 h < hours <= 4 h on a
     refrigerator, where FDA and FEMA disagree and the page must show both clocks rather than pick
     a side;
  6. the quotations the harness calls verbatim are on the page AND in the record, except one
     sentence the record does not hold (see `PAGE_ONLY_PHRASE`);
  7. the honesty markers: the 403s are marked, the two refused authorities are recorded as unused,
     the page says nothing was measured in a real kitchen, and it says a clock is not a clearance.

What it does NOT do, deliberately. It does not execute the page's inline script and it does not
stub a DOM: the harness's behavioural cases call `verdictFor()` and `updateCalculator()`, which only
a JavaScript runtime can call. Section 5 pins the *decision* behind those cases, re-derived from
the page's own numbers, so a threshold moved on one side fails here; the DOM plumbing stays the
harness's job, for a machine that runs it.

Sibling work: `tests/test_heat_page_claims.py`, `tests/test_air_page_claims.py`,
`tests/test_co_safety_page_claims.py` and `tests/test_fetchable_page_claims.py` are the same port
for four other pages. nonreplication and warming remain unported; recalls, retraction, trials and
unreported-trials re-measure live APIs and close honestly by an amended claim, not by a port.

Run: python3 tests/test_food_safety_page_claims.py
"""

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PAGE = REPO / "docs" / "works" / "food-safety.html"
RECORD = REPO / "docs" / "works" / "food-safety-sources.json"

# The record and the page use the same names here, which is itself worth pinning: the co-safety
# record renames several keys, and a silent rename on one side is what a key map exists to catch.
NUMBER_KEYS = (
    "fridge_hours",
    "freezer_full_hours",
    "freezer_half_hours",
    "room_temp_hours",
    "room_temp_hot_hours",
    "hot_outdoor_F",
    "cold_F",
    "cook_now_F",
    "fema_hours",
    "dry_ice_lb",
    "dry_ice_freezer_cuft",
    "dry_ice_days",
)

# The harness checks this sentence with `/cannot rely on appearance or odour/i` and calls it "the
# FDA's own warning". It is not in the record's `verbatim` list — the record holds the FDA's
# discard rule and the cooking sentence, not the appearance-and-odour sentence. Pinned here as a
# page-only claim so the gap is written down instead of hidden behind a passing check.
PAGE_ONLY_PHRASE = "cannot rely on appearance or odour"

# The harness's section 7, as (phrase, whether the record must hold it verbatim).
QUOTED_CLAIMS = (
    ("for 4 hours or more", True),                                 # FDA discard rule
    ("40 degrees or higher for two hours or more", True),           # FEMA / Ready.gov
    ("warmer than 40 degrees F", True),                             # Red Cross, no time stated
    ("even when they are thoroughly cooked", True),                 # FDA: cooking does not save it
    (PAGE_ONLY_PHRASE, False),                                      # FDA wording, not in our record
)

# The harness's fourteen cases, verbatim from tests/validate_food_safety_page.mjs: appliance,
# hours input, temperature input, expected level, a phrase the headline must carry.
CASES = (
    ("fridge", 1, "", "safe", "inside every published window"),
    ("fridge", 3, "", "disagree", "the authorities disagree"),
    ("fridge", 6, "", "discard", "past both clocks"),
    ("fridge", 3, 38, "safe", "keep it"),
    ("fridge", 3, 43, "cook", "cook it now"),
    ("fridge", 3, 50, "discard", "throw it out"),
    ("freezer-full", 20, "", "safe", "holding time"),
    ("freezer-full", 60, "", "discard", "treat it as a refrigerator"),
    ("freezer-half", 10, "", "safe", "holding time"),
    ("freezer-half", 30, "", "discard", "treat it as a refrigerator"),
    ("freezer-full", 10, 35, "safe", "keep it"),
    ("freezer-full", 10, 50, "discard", "throw it out"),
    ("cooler", 5, "", "unknown", "no published clock"),
    ("fridge", "", "", "unknown", "Enter how long"),
)


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
    """The page's own THRESHOLDS, read as data — the same thing the harness loads at runtime."""
    body = js_object(script, "THRESHOLDS")
    out = {}
    for key, value in re.findall(r'(\w+)\s*:\s*("(?:[^"]*)"|-?[\d.]+)', body):
        if value.startswith('"'):
            out[key] = value.strip('"')
        else:
            out[key] = float(value) if "." in value else int(value)
    return out


def appliance_keep_hours(script: str) -> dict:
    """APPLIANCES: appliance -> the keepHours it reads out of THRESHOLDS (None for the cooler)."""
    body = js_object(script, "APPLIANCES")
    out = {}
    for name, table in re.findall(r'"([\w-]+)"\s*:\s*\{([^}]*)\}', body):
        m = re.search(r"keepHours\s*:\s*([\w.]+)", table)
        if m is not None:
            token = m.group(1)
            out[name] = None if token == "null" else token.split(".")[-1]
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


def model_verdict(page_t: dict, keep_hours: dict, appliance: str, hours, temp) -> dict:
    """verdictFor's decision, rebuilt from the page's OWN numbers and its own branch order.

    This is a re-derivation, not a copy of the page's prose: every bound below is read out of the
    page's THRESHOLDS at test time, so a page whose `fridge_hours` moved to 6 fails the 6-hour case
    here exactly as it would fail the harness.
    """
    T = page_t
    if appliance not in keep_hours:
        return {"level": "unknown", "bothClocks": False, "headline": "Choose what is holding the food."}
    frozen = appliance in ("freezer-full", "freezer-half")

    measured = str(temp).strip() != "" and _is_number(temp)
    if measured:
        t = float(temp)
        if t <= T["cold_F"]:
            return {"level": "safe", "bothClocks": False, "headline": "At or below 40 °F — keep it."}
        if not frozen and t <= T["cook_now_F"]:
            return {"level": "cook", "bothClocks": False,
                    "headline": "Between 40 °F and 45 °F — cook it now, eat it now."}
        return {"level": "discard", "bothClocks": False, "headline": "Above 45 °F — throw it out."}

    if str(hours).strip() == "" or not _is_number(hours):
        return {"level": "unknown", "bothClocks": False,
                "headline": "Enter how long the power has been out."}
    h = float(hours)

    if appliance == "cooler":
        return {"level": "unknown", "bothClocks": False,
                "headline": "There is no published clock for a cooler."}

    key = keep_hours[appliance]
    if frozen:
        keep = T[key]
        if h <= keep:
            return {"level": "safe", "bothClocks": False,
                    "headline": f"{h:g} h: still inside the published holding time"}
        return {"level": "discard", "bothClocks": False,
                "headline": f"{h:g} h: past the published holding time — treat it as a refrigerator now."}

    if h <= T["fema_hours"]:
        return {"level": "safe", "bothClocks": True,
                "headline": f"{h:g} h: inside every published window"}
    if h <= T["fridge_hours"]:
        return {"level": "disagree", "bothClocks": True,
                "headline": f"{h:g} h: the authorities disagree about your food."}
    return {"level": "discard", "bothClocks": True,
            "headline": f"{h:g} h: past both clocks — throw it out."}


def _is_number(value) -> bool:
    try:
        float(str(value))
        return True
    except (TypeError, ValueError):
        return False


class PageShape(unittest.TestCase):
    """Claim 1: one script, and it is where the numbers live."""

    def test_the_page_has_exactly_one_inline_script(self):
        self.assertEqual(len(re.findall(r"<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>",
                                        page_text())), 1,
                         "the harness fails unless the page has exactly one inline script; a "
                         "second one can hold a number the checks never read")

    def test_the_page_names_its_record_and_its_harness(self):
        page = page_text()
        for name in ("docs/works/food-safety-sources.json", "tests/validate_food_safety_page.mjs"):
            with self.subTest(name):
                self.assertIn(name, page, "the page no longer names the file its claim rests on")


class Thresholds(unittest.TestCase):
    """Claim 2: neither the page nor the record can move a number alone."""

    def setUp(self):
        self.script = inline_script(page_text())
        self.page_t = page_thresholds(self.script)
        self.record_t = record()["thresholds"]

    def test_the_page_exposes_the_thresholds_the_harness_reads(self):
        missing = [k for k in NUMBER_KEYS if k not in self.page_t]
        self.assertEqual(missing, [], "the page dropped a threshold the harness compares")
        self.assertGreaterEqual(len(self.page_t), 10,
                                "the harness asserts the measurement file carries at least 10 "
                                "thresholds; the page holds fewer")

    def test_every_threshold_equals_the_record(self):
        drift = {}
        for key in NUMBER_KEYS:
            with self.subTest(key):
                self.assertIn(key, self.record_t, "the record dropped a number the page prints")
                self.assertEqual(self.page_t[key], self.record_t[key],
                                 f"page {key} and record {key} have parted; the page says a "
                                 f"threshold the record does not back")
                drift[key] = True
        self.assertEqual(len(drift), len(NUMBER_KEYS))

    def test_the_page_holds_no_threshold_outside_the_record(self):
        unmapped = sorted(set(self.page_t) - set(NUMBER_KEYS) - set(self.record_t))
        self.assertEqual(unmapped, [], "the page gained a threshold the harness does not compare "
                                       "with the record — add it to NUMBER_KEYS here and there")

    def test_the_record_speaks_of_the_same_page(self):
        rec = record()
        self.assertIn("food-safety", rec["artifact"])
        self.assertRegex(rec["measured_utc"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
                         "the record's measurement date is not the format it claims")

    def test_the_page_prints_the_numbers_the_record_holds(self):
        """The harness's own first sentence: the thresholds equal the numbers in the record.

        The record's `thresholds` block IS that comparison on this page, so the check that carries
        weight is that the record's *prose* numbers are the same ones — the four FDA published
        figures the page is built on, each of which the record also quotes verbatim.
        """
        page, rec = page_text(), record()
        verbatim = "\n".join(v for s in rec["sources"] for v in s.get("verbatim", []))
        for phrase, figure in (("about 4 hours", "fridge_hours"),
                               ("approximately 48 hours", "freezer_full_hours"),
                               ("24 hours if it is half full", "freezer_half_hours"),
                               ("Fifty pounds of dry ice", "dry_ice_lb")):
            with self.subTest(figure):
                self.assertIn(phrase, verbatim,
                              f"the record no longer quotes the sentence behind {figure}")
        self.assertEqual(rec["thresholds"]["fridge_hours"], 4)
        self.assertEqual(rec["thresholds"]["freezer_full_hours"], 48)
        self.assertEqual(rec["thresholds"]["freezer_half_hours"], 24)
        self.assertEqual(rec["thresholds"]["dry_ice_lb"], 50)
        self.assertIn("4 hours", page)


class DecisionLogic(unittest.TestCase):
    """Claim 4, as far as Python can honestly go: the page's decision still has its shape."""

    def setUp(self):
        self.script = inline_script(page_text())
        self.body = verdict_for_body(self.script)
        self.page_t = page_thresholds(self.script)

    def test_a_measured_reading_is_decided_before_any_clock(self):
        measured = self.body.find("if (measured)")
        clocks = self.body.find("const h =")
        self.assertGreaterEqual(measured, 0, "verdictFor no longer branches on a measured reading")
        self.assertGreaterEqual(clocks, 0, "verdictFor no longer reads the hours")
        self.assertLess(measured, clocks,
                        "the time branch is now reached first; the page's claim is that a "
                        "thermometer reading overrules the clock")

    def test_the_keep_line_is_tested_before_the_cook_line(self):
        cold = self.body.find("T.cold_F")
        cook = self.body.find("T.cook_now_F")
        self.assertGreaterEqual(cold, 0, "verdictFor no longer reads T.cold_F")
        self.assertGreaterEqual(cook, 0, "verdictFor no longer reads T.cook_now_F")
        self.assertLess(cold, cook,
                        "'cook it' is now tested before 'keep it'; a 38 °F fridge would be "
                        "answered 'cook', which the harness's 38 °F case fails")

    def test_the_cook_branch_excludes_freezers(self):
        self.assertIn("!frozen && t <= T.cook_now_F", self.body,
                      "the 45 °F cook branch is no longer restricted to appliances that are not "
                      "frozen; the FDA's 45 °F sentence is about refrigerated food")

    def test_the_thresholds_are_read_from_the_table_not_hard_coded(self):
        for token in ("T.cold_F", "T.cook_now_F", "T.fema_hours", "T.fridge_hours", "a.keepHours"):
            with self.subTest(token):
                self.assertIn(token, self.body,
                              f"verdictFor no longer reads {token}, so moving the number in "
                              f"THRESHOLDS would leave the advice quoting the old one")

    def test_the_cooler_is_refused_before_the_freezer_and_fridge_branches(self):
        cooler = self.body.find('appliance === "cooler"')
        frozen = self.body.find("if (frozen)")
        fema = self.body.find("T.fema_hours")
        self.assertGreaterEqual(cooler, 0, "the cooler is no longer refused explicitly")
        self.assertLess(cooler, frozen, "the cooler now falls into the freezer branch")
        self.assertLess(cooler, fema, "the cooler now gets a refrigerator clock")

    def test_the_fridge_disagreement_is_testing_fema_before_fda(self):
        fema = self.body.find("withinFema = h <= T.fema_hours")
        fda = self.body.find("withinFda = h <= T.fridge_hours")
        self.assertGreaterEqual(fema, 0, "verdictFor no longer computes FEMA's window")
        self.assertGreaterEqual(fda, 0, "verdictFor no longer computes FDA's window")
        self.assertLess(fema, fda, "the two clocks are no longer named in the page's order")
        if_fema = self.body.find("if (withinFema)")
        if_fda = self.body.find("if (withinFda)")
        self.assertLess(if_fema, if_fda,
                        "the disagreement branch is now tested before the agreement branch; a "
                        "3-hour fridge would lose its 'both clocks' answer")

    def test_every_branch_says_what_to_do(self):
        self.assertEqual(len(re.findall(r"headline:", self.body)),
                         len(re.findall(r"return\s*\{", self.body)),
                         "a branch returns a verdict with no headline; an answer with no "
                         "instruction is worse than no answer")

    def test_the_page_still_names_the_disagreement_in_words(self):
        self.assertIn("the authorities disagree", self.body)
        self.assertIn("past both clocks", self.body)


class BehaviouralCases(unittest.TestCase):
    """Claim 5: the harness's fourteen cases, re-derived against the page's own numbers."""

    def setUp(self):
        script = inline_script(page_text())
        self.page_t = page_thresholds(script)
        self.keep = appliance_keep_hours(script)

    def test_the_fourteen_cases_still_come_out_as_the_harness_expects(self):
        self.assertEqual(len(CASES), 14, "the harness's case list has changed length")
        failures = []
        for appliance, hours, temp, level, phrase in CASES:
            v = model_verdict(self.page_t, self.keep, appliance, hours, temp)
            label = f"{appliance} {hours}h {temp or '(no temp)'}"
            if v["level"] != level or phrase.lower() not in v["headline"].lower():
                failures.append(f"{label}: got {v['level']} / {v['headline']!r}, "
                                f"wanted {level} / {phrase!r}")
        self.assertEqual(failures, [], "cases whose outcome no longer follows the page's numbers:\n"
                                       + "\n".join(failures))

    def test_the_cooler_appliance_is_the_one_with_no_clock(self):
        self.assertEqual(sorted(self.keep), ["cooler", "freezer-full", "freezer-half", "fridge"])
        self.assertIsNone(self.keep["cooler"], "an appliance was given a clock by editing APPLIANCES")
        self.assertEqual(self.keep["fridge"], "fridge_hours")
        self.assertEqual(self.keep["freezer-full"], "freezer_full_hours")
        self.assertEqual(self.keep["freezer-half"], "freezer_half_hours")

    def test_the_case_the_page_exists_for_shows_both_clocks(self):
        """2 h < hours <= 4 h on a refrigerator: the authorities disagree and the page says so."""
        straddle = model_verdict(self.page_t, self.keep, "fridge", 3, "")
        self.assertEqual(straddle["level"], "disagree",
                         "the 3-hour fridge case is no longer flagged as a disagreement")
        self.assertTrue(straddle["bothClocks"], "the disagreement case stopped showing both clocks")
        for hours in (1, 6):
            with self.subTest(hours=hours):
                self.assertTrue(model_verdict(self.page_t, self.keep, "fridge", hours, "")["bothClocks"],
                                "both clocks are now hidden in a case where the authorities speak")
        self.assertFalse(model_verdict(self.page_t, self.keep, "fridge", 3, 38)["bothClocks"],
                         "a measured temperature now sits beside the clocks instead of replacing them")

    def test_the_window_between_the_clocks_is_not_empty(self):
        """If the two clocks ever crossed, 'disagree' would be unreachable and the page a liar."""
        self.assertLess(self.page_t["fema_hours"], self.page_t["fridge_hours"],
                        "FEMA's window is no longer inside FDA's, so there is no window between "
                        "them for the page to report")
        mid = (self.page_t["fema_hours"] + self.page_t["fridge_hours"]) / 2
        self.assertEqual(model_verdict(self.page_t, self.keep, "fridge", mid, "")["level"],
                         "disagree", "the midpoint of the two clocks is not a disagreement")

    def test_a_measured_reading_overrides_time(self):
        for temp, level in ((38, "safe"), (43, "cook"), (50, "discard")):
            with self.subTest(temp=temp):
                self.assertEqual(model_verdict(self.page_t, self.keep, "fridge", 3, temp)["level"],
                                 level, "a measured reading no longer decides the verdict")


class Quotations(unittest.TestCase):
    """Claim 6: the sentences the page quotes are the record's, and they are on the page."""

    def test_every_quoted_claim_is_on_the_page(self):
        page = page_text()
        missing = [p for p, _ in QUOTED_CLAIMS if p not in page]
        self.assertEqual(missing, [], "sentences the harness calls verbatim are no longer verbatim "
                                      "on docs/works/food-safety.html")

    def test_what_the_record_holds_it_holds_verbatim(self):
        verbatim = "\n".join(v for s in record()["sources"] for v in s.get("verbatim", []))
        for phrase, in_record in QUOTED_CLAIMS:
            with self.subTest(phrase):
                if in_record:
                    self.assertIn(phrase, verbatim,
                                  "the page quotes this and the record no longer does")
                else:
                    self.assertNotIn(phrase, verbatim,
                                     "the record now holds this sentence — drop it from "
                                     "PAGE_ONLY_PHRASE and check it against the record instead")

    def test_the_record_keeps_a_real_quotation_set(self):
        n = sum(len(s.get("verbatim", [])) for s in record()["sources"])
        self.assertGreaterEqual(n, 10, f"the record holds only {n} verbatim strings; the page's "
                                       f"argument rests on sentences, not paraphrases")


class Refusals(unittest.TestCase):
    """Claim 7: what the session could not read is marked, not silently dropped."""

    def setUp(self):
        self.page = page_text()
        self.rec = record()
        self.by_id = {s["id"]: s for s in self.rec["sources"]}

    def test_the_page_marks_the_unreachable_authorities_with_their_status(self):
        self.assertIn("HTTP 403", self.page, "the blocked fetches are no longer marked")
        self.assertEqual(self.page.count("NOT VERIFIED HERE"), 2,
                         "the harness asserts both refused sources are labelled; the page now "
                         "labels a different number of them")

    def test_the_record_records_them_as_refused_and_unused(self):
        for sid in ("fsis", "cdc"):
            with self.subTest(sid):
                self.assertEqual(self.by_id[sid]["http_status"], 403)
                self.assertIs(self.by_id[sid]["used_by_page"], False,
                              f"{sid} returned 403; an unfetched page cannot back a figure")

    def test_the_authorities_the_page_does_use_were_actually_read(self):
        for sid in ("fda", "fema", "redcross"):
            with self.subTest(sid):
                self.assertEqual(self.by_id[sid]["http_status"], 200)
                self.assertIs(self.by_id[sid]["used_by_page"], True)
                self.assertTrue(self.by_id[sid].get("verbatim"),
                                f"{sid} backs the page and holds no quoted sentence")

    def test_the_windows_the_page_reports_are_recorded_as_disagreements(self):
        self.assertGreaterEqual(len(self.rec["discrepancies"]), 2,
                                "the record no longer preserves the disagreements it exists for")
        first = self.rec["discrepancies"][0]
        self.assertIn("2", json.dumps(first["fema"]))
        self.assertIn("4", json.dumps(first["fda"]))


class HonestyMarkers(unittest.TestCase):
    """Claim 8: the page still says what it does not do. That sentence is why it is worth reading."""

    def setUp(self):
        self.page = page_text()

    def test_the_page_says_nothing_was_measured_here(self):
        self.assertIn("no fridge or freezer was measured", self.page,
                      "the sentence admitting no kitchen was measured has been edited away")

    def test_the_page_says_it_cannot_judge_a_particular_item(self):
        self.assertIn("cannot tell you whether a specific item is safe", self.page)

    def test_the_page_says_a_clock_is_not_a_clearance(self):
        self.assertIn("A clock measures hours, not bacteria", self.page)
        self.assertRegex(self.page, r"When in doubt, throw it out")

    def test_the_page_reports_the_disagreement_rather_than_resolving_it(self):
        self.assertIn("reported rather than resolved", self.page)


if __name__ == "__main__":
    unittest.main(verbosity=2)
