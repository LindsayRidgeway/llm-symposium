#!/usr/bin/env python3
"""The fetchable page's own checks, re-derived in the suite that actually runs — 2026-11-26.

Why this file exists. `docs/works/fetchable.html` told the reader:

    "Checked by `tests/validate_fetchable_page.mjs`, which runs this page's own script against
     the shipped data and re-measures a sample of rows live"

Both halves of that sentence are true of the harness and false of this repository's behaviour:
no registered job *executes* a `.mjs` validator. `.github/workflows/test-and-report.yml` hands
them to `node --check`, a syntax check, and skips cleanly when Node is absent — which it is on
this checkout (measured 2026-11-25). So the guard behind the page's claim has never run here,
and the page's sentence said it had.

This test is the fetchable page's share of the value-queue item `js-harness-claims`: every
assertion in `tests/validate_fetchable_page.mjs` that needs no JavaScript runtime and no network,
re-implemented from the page and `docs/works/fetchable-sources.json` alone:

  1. the page has exactly one inline script, loads the shipped record, and retypes no table of
     its own — no `<tr>`, no `data-url`, no hand-written row in the static markup;
  2. the counts line prints the file's totals and nothing else: `counts.sources`,
     `counts.answered`, `counts.browser_usable` and `counts.advertise_key` are re-derived here
     from the rows themselves, so a row edited without the counts moved fails the build;
  3. `browser_usable` is a measurement, not a mood: it is true exactly when the row answered and
     its CORS answer is one a page can use (`*` or the page's own origin). Two rows in the file
     are readable for the narrower reason (NASA APOD, UN SDG: the origin echoed back) and one
     row is not readable despite `*` because it answered 403 and carried nothing (USDA FoodData
     Central) — this pins the rule that gets all three right, so the flag cannot be re-guessed;
  4. the page's central finding — six of the answered sources are invisible to a browser — is the
     arithmetic of the file, and the six named in the prose are exactly those six rows;
  5. the figures the prose states a reader would check by hand: thirty-five sources, six
     unreadable, four asking for a key, and the 2026-10-17 correction ("twenty-nine" carrying
     data, "six, not five") against `research/source-drift.md`, which is where they came from;
  6. every source renders exactly once, under a labelled heading, with its own request printed —
     one `data-url` per row, one row per source, no field falling through to a raw key;
  7. the answers column is decided by the measured status and byte count, and the browser check
     reports a CORS refusal AS the answer rather than as a bug;
  8. the honesty markers the page is worth reading for are still there — the snapshot sentence,
     "we are not affiliated", "which is not review";
  9. the page now states which of its checks run here and which do not (the amended claim this
     change made), and still names the harness.

What it does NOT do, deliberately, and why the page's claim was amended rather than ported
whole: five of the harness's checks re-measure five sources live (ClinicalTrials.gov, arXiv,
Wikidata, Open-Meteo, Crossref) and one exercises the page's click handler in a stub DOM. Neither
can run in a build with no network and no JavaScript runtime, and Dmitri's audit of 2026-11-25
put fetchable on the amended-claim side of the split for exactly that reason. The page says so in
its own words now; this test pins the sentence so the claim and the job cannot drift apart again.

Run: python3 tests/test_fetchable_page_claims.py
"""

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PAGE = REPO / "docs" / "works" / "fetchable.html"
RECORD = REPO / "docs" / "works" / "fetchable-sources.json"
DRIFT = REPO / "research" / "source-drift.md"

# The page's prose spells these six the way a reader would; the record spells them its own way.
UNABLE = (
    ("Europe PMC", "Europe PMC"),
    ("arXiv", "arXiv"),
    ("Wikidata", "Wikidata"),
    ("WHO Global Health Observatory", "the WHO"),
    ("JPL Horizons", "JPL"),
    ("NHANES-style CDC WONDER", "the CDC"),
)

WORDS = {"five": 5, "six": 6, "seven": 7, "eight": 8, "four": 4,
         "thirty-five": 35, "twenty-nine": 29}


def page_text() -> str:
    return PAGE.read_text(encoding="utf-8")


def record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def inline_script(html: str) -> str:
    blocks = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>", html)
    assert len(blocks) == 1, f"expected one inline script on the page, found {len(blocks)}"
    return blocks[0]


def static_markup(html: str) -> str:
    """The page minus every script — what a reader is served before any JS runs."""
    return re.sub(r"<script[\s\S]*?</script>", "", html)


def answered(row: dict) -> bool:
    """The page's definition: a 200 with a body. A 200 with nothing in it is not an answer."""
    return row.get("http_status") == 200 and (row.get("bytes") or 0) > 0


def usable(row: dict) -> bool:
    """Readable from a web page: it answered, and the CORS answer is one a page can use.

    '*' is open to any origin; 'origin' is the page's own origin echoed back, which is readable
    from this site and from nowhere else. Both are usable here; 'absent' is not.
    """
    return answered(row) and row.get("cors") in ("*", "origin")


def recounted(sources) -> dict:
    return {
        "sources": len(sources),
        "answered": sum(1 for s in sources if answered(s)),
        "browser_usable": sum(1 for s in sources if usable(s)),
        "advertise_key": sum(1 for s in sources if s.get("advertised_key")),
    }


class TestFetchablePageShape(unittest.TestCase):
    def test_exactly_one_inline_script(self):
        script = inline_script(page_text())
        self.assertGreater(len(script), 2000, "the page's inline script is suspiciously small")

    def test_the_page_loads_the_shipped_record_and_retypes_no_row(self):
        html = page_text()
        script = inline_script(html)
        self.assertIn('fetch("fetchable-sources.json"', script,
                      "the page no longer loads docs/works/fetchable-sources.json — the whole "
                      "point of the entry is that it renders the dated file rather than numbers "
                      "somebody typed in")
        markup = static_markup(html)
        self.assertNotIn("<tr", markup,
                         "the page now carries a hand-written table row outside its script; "
                         "every row must come from the record or the counts stop being the file's")
        self.assertNotIn('data-url="', markup,
                         "a live-check button is hard-coded in the markup instead of rendered "
                         "from a record row")
        self.assertIn('id="tables"', markup)
        self.assertIn('id="counts"', markup)

    def test_no_hard_coded_counts_in_the_script(self):
        script = inline_script(page_text())
        self.assertIsNone(re.search(r"\b\d{2,}\s+(sources|answered)", script),
                          "the script states a count as a literal; the counts must come from "
                          "the file it fetched")

    def test_the_record_is_parseable_and_dated(self):
        doc = record()
        self.assertEqual(doc["generated_utc"], "2026-09-16T18:56:34Z",
                         "the record's measurement date moved; the page prints this date to the "
                         "reader, so both sides have to be edited on purpose")
        self.assertEqual(doc["origin_sent"], "https://lindsayridgeway.github.io",
                         "the record's Origin header no longer matches the sentence in "
                         "'How it was measured'")
        self.assertIn("a Python client sending Origin: https://lindsayridgeway.github.io",
                      doc["measured_from"])


class TestFetchableCounts(unittest.TestCase):
    def test_the_counts_are_the_rows_recounted(self):
        doc = record()
        self.assertEqual(doc["counts"], recounted(doc["sources"]),
                         "the record's counts do not agree with its own rows. Either a row was "
                         "edited without re-running the measurement, or the counts line was "
                         "hand-edited; the page prints these four numbers to a reader")

    def test_the_counts_line_prints_the_files_own_totals(self):
        script = inline_script(page_text())
        for field in ("sources", "answered", "browser_usable", "advertise_key"):
            self.assertIn("${c.%s}" % field, script,
                          f"the counts line no longer prints c.{field}; a figure the file holds "
                          f"that the page does not show is not being reported by this entry")

    def test_browser_usable_is_a_measurement_not_a_guess(self):
        doc = record()
        wrong = [(s["name"], s.get("cors"), s.get("browser_usable"))
                 for s in doc["sources"] if bool(s.get("browser_usable")) != usable(s)]
        self.assertEqual(wrong, [],
                         "these rows' browser_usable flag disagrees with the rule the page's "
                         "finding depends on (answered AND cors in {*, origin}) — "
                         "(name, cors, flag)")

    def test_the_three_edges_of_the_cors_rule(self):
        """The rows that make the rule non-trivial, named so a re-guess is visible."""
        doc = {s["name"]: s for s in record()["sources"]}
        self.assertEqual(doc["NASA APOD"]["cors"], "origin",
                         "NASA APOD is the row that proves 'origin' counts as readable")
        self.assertTrue(doc["NASA APOD"]["browser_usable"])
        self.assertEqual(doc["UN SDG API"]["cors"], "origin")
        self.assertTrue(doc["UN SDG API"]["browser_usable"])
        self.assertEqual(doc["USDA FoodData Central"]["cors"], "*")
        self.assertFalse(doc["USDA FoodData Central"]["browser_usable"],
                         "USDA answers 403 with no bytes: an open CORS header on an empty "
                         "refusal is not readable data")
        self.assertFalse(answered(doc["USDA FoodData Central"]))

    def test_the_answers_column_uses_the_measured_status(self):
        script = inline_script(page_text())
        self.assertIn("s.http_status === 200 && s.bytes > 0", script,
                      "the 'answers with no key' column no longer applies the record's own "
                      "definition of an answer")
        self.assertIn("yn(s.browser_usable)", script,
                      "the 'readable from a web page' column no longer prints the measured flag")


class TestFetchableFinding(unittest.TestCase):
    def test_the_six_unreadable_sources_are_the_files_arithmetic(self):
        doc = record()
        gap = recounted(doc["sources"])["answered"] - recounted(doc["sources"])["browser_usable"]
        self.assertEqual(gap, WORDS["six"],
                         "the gap between 'answered' and 'readable' is no longer six; the "
                         "page's rule line and its lead paragraph both state it")
        sentence = re.search(r"([A-Z][^.]*?) all answered us fine and send no CORS header",
                             page_text())
        self.assertIsNotNone(sentence,
                             "the page no longer names the six sources that answer a server and "
                             "are invisible to a browser")
        named = sentence.group(1)
        for _, prose in UNABLE:
            self.assertIn(prose, named,
                          f"the page's list of unreadable sources no longer names {prose}")
        unreadable = {s["name"] for s in doc["sources"] if answered(s) and not usable(s)}
        self.assertEqual(unreadable, {name for name, _ in UNABLE},
                         "the sources the prose names are not the sources the file measures as "
                         "answered-and-unreadable")

    def test_the_prose_figures(self):
        html = page_text()
        doc = record()
        counts = recounted(doc["sources"])
        self.assertIn("Thirty-five public sources", html,
                      "the lead no longer states the number of sources")
        self.assertEqual(counts["sources"], WORDS["thirty-five"])
        self.assertIn("Thirty-five public data sources", html,
                      "the meta description no longer states the number of sources")
        self.assertIn("Four sources advertise one", html,
                      "the 'a key is not a wall' bullet no longer gives its count")
        self.assertEqual(counts["advertise_key"], WORDS["four"],
                         "the number of sources asking for a key changed; the bullet says four")
        self.assertIn("six of them answer a server happily and are invisible to a browser", html,
                      "the rule line that carries the entry's finding was edited")

    def test_the_2026_10_17_correction_agrees_with_the_drift_record(self):
        """The page's correction is quoted from research/source-drift.md; pin both sides."""
        drift = DRIFT.read_text(encoding="utf-8")
        self.assertIn("| answered *and* carried data | — | 29 |", drift,
                      "the drift record no longer holds the 29 the page quotes")
        self.assertIn("| readable by a browser page (CORS) | 25 | 26 |", drift,
                      "the drift record no longer holds the 25-then-26 the page's correction is "
                      "arithmetic over")
        self.assertIn("| Europe PMC | answered/server-only | answered/page-readable | improved |",
                      drift)
        html = page_text()
        self.assertIn("twenty-nine", html,
                      "the page no longer says how many rows carried data on re-measurement")
        self.assertIn("six, not five", html,
                      "the page no longer states the corrected gap")
        self.assertEqual(WORDS["thirty-five"], record()["counts"]["sources"])
        # 31 answered − 25 readable = six in the September file; 31 − 26 = five on 2026-10-17.
        self.assertEqual(31 - 25, WORDS["six"])
        self.assertEqual(31 - 26, WORDS["five"])

    def test_arxiv_is_unreadable_and_clinicaltrials_is_readable(self):
        """The harness's two named row assertions, re-derived from the record."""
        doc = {s["name"]: s for s in record()["sources"]}
        self.assertTrue(answered(doc["arXiv"]))
        self.assertFalse(usable(doc["arXiv"]),
                         "arXiv is the row the harness asserts renders as NOT readable")
        self.assertTrue(answered(doc["ClinicalTrials.gov"]))
        self.assertTrue(usable(doc["ClinicalTrials.gov"]))
        self.assertIn("clinicaltrials.gov/api/v2", doc["ClinicalTrials.gov"]["url"])


class TestFetchableRendering(unittest.TestCase):
    def test_one_row_and_one_button_per_source(self):
        script = inline_script(page_text())
        self.assertEqual(script.count('data-url="'), 1,
                         "the row template must emit exactly one live-check button per row; "
                         "the harness counts one per source")
        self.assertIn("doc.sources.forEach", script,
                      "the page no longer walks doc.sources, so a source can go unrendered")
        self.assertIn("by[f].map(row)", script,
                      "each field's rows are no longer rendered from the record's own order")
        self.assertIn("esc(s.name)", script, "the row template no longer prints the source name")

    def test_every_field_has_a_heading(self):
        script = inline_script(page_text())
        order = re.search(r"const FIELD_ORDER = \[([^\]]*)\]", script)
        self.assertIsNotNone(order, "the page no longer declares FIELD_ORDER")
        listed = re.findall(r'"(\w+)"', order.group(1))
        fields = {s["field"] for s in record()["sources"]}
        self.assertEqual(set(listed), fields,
                         "a field in the record is not in FIELD_ORDER (it would render under a "
                         "raw key) or FIELD_ORDER names a field the record no longer has")
        labels = re.search(r"const FIELD_LABEL = \{([\s\S]*?)\};", script).group(1)
        for field in fields:
            self.assertIn(f"{field}:", labels, f"no human label for the {field!r} field")

    def test_every_row_can_render_and_prints_its_own_request(self):
        script = inline_script(page_text())
        self.assertIn("GET ${esc(s.url)}", script,
                      "the row no longer prints the exact request it made")
        self.assertIn("access-control-allow-origin: ${esc(s.cors)}", script,
                      "the row no longer prints the CORS answer that decides its verdict")
        missing = []
        for s in record()["sources"]:
            for field in ("name", "field", "holds", "url", "http_status", "bytes", "cors",
                          "witness", "advertised_key", "browser_usable"):
                if field not in s:
                    missing.append(f"{s.get('name', '?')}: {field}")
            if not str(s.get("url", "")).startswith("https://"):
                missing.append(f"{s.get('name', '?')}: url is not https")
        self.assertEqual(missing, [], "rows the template cannot render as the page describes")

    def test_source_names_are_unique_so_a_row_is_identifiable(self):
        names = [s["name"] for s in record()["sources"]]
        dupes = {n for n in names if names.count(n) > 1}
        self.assertEqual(dupes, set(),
                         "two rows share a name; the page's own 'every source is rendered by "
                         "name' check and the reader's eye both fail on that")
        self.assertTrue(all(n.strip() for n in names))

    def test_a_blocked_fetch_is_reported_as_the_answer(self):
        script = inline_script(page_text())
        self.assertIn("this is the CORS answer", script,
                      "the browser check no longer says a refusal IS the answer; that sentence "
                      "is the reason the button exists")
        self.assertNotIn("Failed to fetch\", \"bug\"", script)


class TestFetchableHonesty(unittest.TestCase):
    def test_the_honesty_markers(self):
        html = page_text()
        for marker in ("This is a snapshot, not a guarantee.",
                       "we are not affiliated",
                       "which is <em>not</em> review",
                       "It does not tell you what is true."):
            self.assertIn(marker, html, f"the page lost its honest marker: {marker!r}")

    def test_the_page_says_which_checks_run_here(self):
        """The amended claim this change made: no job executes the harness, so say so."""
        html = page_text()
        self.assertRegex(
            html, r"tests/validate_fetchable_page\.mjs(?![\w.-])",
            "the page no longer names its harness exactly; the map test pins that it does. The "
            "trailing lookahead is deliberate: a plain substring check accepts "
            "'tests/validate_fetchable_page.mjs.bak', which names a file that does not exist")
        self.assertIn("tests/test_fetchable_page_claims.py", html,
                      "the page does not name the Python test that does run here")
        self.assertIn("no job in this repository runs it", html,
                      "the page no longer says that nothing executes the harness — that "
                      "sentence is the whole amendment")


if __name__ == "__main__":
    unittest.main(verbosity=2)
