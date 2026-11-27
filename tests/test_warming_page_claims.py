#!/usr/bin/env python3
"""The warming page's own offline checks, re-derived in the suite that actually runs — 2026-11-26.

Why this file exists. `docs/works/warming.html` is Works entry 2, the flagship of agenda item 12 —
"type a place, see what its recorded temperature has actually done since 1950" — and it is the one
data-driven Works page whose checking work is visible nowhere: `tests/validate_warming_page.mjs`
(2026-10-03) checks it by running the page's OWN inline script against a stub DOM and a stub
`fetch`, and no page and no registered job ever names or runs that harness. It is an orphan, and
`.github/workflows/test-and-report.yml` hands `.mjs` files only to `node --check`, a syntax check
that skips entirely when Node is absent — which it is on this checkout (no node, nodejs, deno or bun
on PATH, measured 2026-11-25). So the harness's 28 `ok(...)` assertions have been a claim about
another machine on another day for seven weeks. (This paragraph said 24 until 2026-11-27; the map
guard's comment said 40; Dmitri's audit of 2026-11-25 said 30. Three numbers, one file, none of
them measured. 28 is `grep -o '\bok(' tests/validate_warming_page.mjs | wc -l`, and it is pinned
below rather than restated, so the fourth number cannot appear.)

This file is the warming page's share of the value-queue item `js-harness-claims`: the half that
Dmitri's audit of 2026-11-25 called offline and re-derivable. It re-implements, from the page's own
inline script and `docs/works/index.html` alone, every harness assertion that needs no runtime:

  1. exactly one inline script, and the document elements the script writes into;
  2. the accent-fold regression the harness was written to catch: the accent-dropped spelling of a
     name must survive the filter that drops the string the reader typed compared against `base`,
     never against `fold` — the defect the harness found on 2026-10-03 and the page still records;
  3. `variants()`'s shape re-derived in Python and run on the harness's own five fixtures
     (München, KualaLumpur, Mississippi, Bostn, and the "no variant shorter than 3" rule);
  4. `levSim()` re-derived, including the case the page's comment names: edit distance ranks
     "Boston" above the village "Bost" for the typo "Bostn" where bigram overlap does not;
  5. `annualMeans()`'s three filters — null days skipped rather than counted as zero, years with
     more than 300 missing days dropped, the current incomplete year excluded — re-derived against
     the harness's synthetic daily series, and the archive query's own parameters pinned;
  6. `decadeMeans()`'s grouping and its ">= 6 usable years" filter, against the harness's four-row
     decade fixture;
  7. the numbers `render()` prints — endpoint delta, the two decades it spans, the per-decade trend,
     the warmest year, the year range and count, and the dropped short decade never reaching the
     reader — recomputed in Python from that same fixture;
  8. the privacy boundary: the page contacts the two keyless Open-Meteo hosts and no other host;
  9. the honesty markers: an empty answer says it is empty, the exact query is linked so a reader
     can reproduce every number, the caveat block is revealed with a result, and the page says what
     it is not;
 10. the Works index's Boston figure — 76 complete years, +1.40 °C from the 1950s to the 2020s —
     which only a network run can re-derive, pinned here as the sentence that must not drift
     silently, together with the page's own arithmetic check of the same figure (11.16 − 9.77 =
     1.39 against a headline of +1.40, one rounding step and not two answers).

What it does NOT do, deliberately. It does not execute the page's inline script, stub a DOM, or draw
the SVG chart: `render()`'s DOM writes, `chart()`, the concurrent geocoder workers and the live
`WARMING_LIVE=1` Boston re-derivation need a JavaScript runtime and a network, and they stay the
harness's job on a machine that can run it. The numbers those functions would print are recomputed
here from the same fixture, so a moved threshold or a changed formula fails this file first.

Sibling ports: `tests/test_heat_page_claims.py`, `tests/test_air_page_claims.py`,
`tests/test_co_safety_page_claims.py`, `tests/test_food_safety_page_claims.py`,
`tests/test_fetchable_page_claims.py` and `tests/test_nonreplication_page_claims.py`. With this file
all seven offline pages are ported; five have a proven-red sensitivity pair.

Run: python3 tests/test_warming_page_claims.py
"""

import datetime
import math
import re
import unicodedata
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PAGE = REPO / "docs" / "works" / "warming.html"
INDEX = REPO / "docs" / "works" / "index.html"
HARNESS = REPO / "tests" / "validate_warming_page.mjs"

INLINE = re.compile(r"<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>")

HOSTS_ALLOWED = ("geocoding-api.open-meteo.com", "archive-api.open-meteo.com")


def page_text():
    return PAGE.read_text(encoding="utf-8")


def inline_code():
    blocks = INLINE.findall(page_text())
    return blocks


def index_text():
    return INDEX.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------------------------
# The page's own functions, re-derived. Each mirrors the inline script's arithmetic exactly; when
# one of these and the page disagree, the test says which assertion the page's comment promises.
# ---------------------------------------------------------------------------------------------

def fold(s):
    """JS: s.normalize("NFD").replace(/[\\u0300-\\u036f]/g, "") — strip the combining accents."""
    return "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c))


def variants(q):
    """The page's spelling fallback, in the same order (JS Set preserves insertion order)."""
    base = q.strip()
    f = fold(base)
    out = [base, f, re.sub(r"(.)\1+", r"\1", f)]
    for i in range(len(f)):                       # one letter deleted
        out.append(f[:i] + f[i + 1:])
    for i in range(len(f) - 1):                   # two letters swapped
        out.append(f[:i] + f[i + 1] + f[i] + f[i + 2:])
    lowest = max(4, math.ceil(len(f) * 0.6))      # the tail cut off
    for n in range(len(f) - 1, lowest - 1, -1):
        out.append(f[:n])
    out.append(re.sub(r"([a-z])([A-Z])", r"\1 \2", base))   # a missing space, camel case
    if re.fullmatch(r"[A-Za-z]{7,}", f):
        for i in range(3, len(f) - 2):
            out.append(f[:i] + " " + f[i:])
    seen, result = set(), []
    for v in out:
        if len(v) >= 3 and v.strip().lower() != base.lower() and v not in seen:
            seen.add(v)
            result.append(v)
    return result[:26]


def lev_sim(a, b):
    x = re.sub(r"[^a-z]", "", a.lower())
    y = re.sub(r"[^a-z]", "", b.lower())
    if not x or not y:
        return 0.0
    prev = list(range(len(y) + 1))
    for i in range(1, len(x) + 1):
        cur = [i] + [0] * len(y)
        for j in range(1, len(y) + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1,
                         prev[j - 1] + (0 if x[i - 1] == y[j - 1] else 1))
        prev = cur
    return 1 - prev[len(y)] / max(len(x), len(y))


def annual_means(times, vals, current_year):
    """annualMeans()'s three filters, without the fetch: null days skipped, > 300 days to count,
    nothing after the last full year."""
    by_year = {}
    for t, v in zip(times, vals):
        if v is None:
            continue
        y = t[:4]
        e = by_year.setdefault(y, {"sum": 0.0, "n": 0})
        e["sum"] += v
        e["n"] += 1
    rows = [{"year": int(y), "mean": e["sum"] / e["n"], "n": e["n"]}
            for y, e in by_year.items() if e["n"] > 300]
    return sorted((r for r in rows if 1950 <= r["year"] <= current_year - 1),
                  key=lambda r: r["year"])


def decade_means(rows):
    buckets = {}
    for r in rows:
        d = r["year"] // 10 * 10
        e = buckets.setdefault(d, {"sum": 0.0, "n": 0})
        e["sum"] += r["mean"]
        e["n"] += 1
    out = [{"decade": d, "mean": e["sum"] / e["n"], "years": e["n"]} for d, e in buckets.items()]
    return sorted((x for x in out if x["years"] >= 6), key=lambda x: x["decade"])


def printed_numbers(rows):
    """The three figures render() prints, in the form it prints them."""
    dec = decade_means(rows)
    first, last = dec[0], dec[-1]
    delta = last["mean"] - first["mean"]
    trend = (last["mean"] - first["mean"]) / ((last["decade"] - first["decade"]) / 10) \
        if len(dec) > 1 else None
    warmest = max(rows, key=lambda r: r["mean"])
    return {
        "delta": f"{'+' if delta >= 0 else ''}{delta:.2f} °C",
        "span": f"{first['decade']}s → {last['decade']}s",
        "trend": "—" if trend is None else f"{'+' if trend >= 0 else ''}{trend:.2f} °C",
        "warmest": f"{warmest['mean']:.1f} °C",
        "warmest_year": f"warmest year ({warmest['year']})",
        "range": f"{len(rows)} complete years, {rows[0]['year']}–{rows[-1]['year']}",
        "decades": [f"{d['decade']}s" for d in dec],
        "means": [f"{d['mean']:.2f}" for d in dec],
    }


# The harness's decade fixture, verbatim: three complete decades and one five-year decade that the
# >=6-year filter must drop, so the reader never sees a "2020s" row computed from half a decade.
def harness_decade_rows():
    rows = []
    for y in range(1950, 1960):
        rows.append({"year": y, "mean": 10.0, "n": 365})
    for y in range(1980, 1990):
        rows.append({"year": y, "mean": 11.0, "n": 365})
    for y in range(2010, 2020):
        rows.append({"year": y, "mean": 12.0, "n": 365})
    for y in range(2020, 2025):
        rows.append({"year": y, "mean": 10.5, "n": 365})
    return rows


def harness_daily_series(current_year):
    """The harness's synthetic daily series: a 200-day year, two full years with ten null days
    each, and the current year complete but not yet over."""
    times, vals = [], []

    def put(year, days, value):
        start = datetime.date(year, 1, 1)
        for i in range(days):
            times.append((start + datetime.timedelta(days=i)).isoformat())
            vals.append(value if days == 200 else (None if i < 10 else value))

    put(current_year - 3, 200, 8.0)
    for y in (current_year - 2, current_year - 1):
        put(y, 365, 10.0 + (y % 10) * 0.01)
    put(current_year, 365, 99.0)
    return times, vals


class TestWarmingPageStructure(unittest.TestCase):
    def test_exactly_one_inline_script(self):
        self.assertEqual(len(inline_code()), 1,
                         "the page must carry exactly one inline script; a second one puts the "
                         "printed numbers outside the code this port re-derives")

    def test_the_elements_the_script_writes_into_exist(self):
        html = page_text()
        for element_id in ("pz", "go", "status", "pick", "out", "caveats"):
            self.assertIn(f'id="{element_id}"', html,
                          f'#{element_id} is written by the script and must exist in the page')

    def test_the_harness_still_exists_and_checks_something(self):
        self.assertTrue(HARNESS.is_file(),
                        "tests/validate_warming_page.mjs is gone; this port was written against it")
        text = HARNESS.read_text(encoding="utf-8")
        # Measured, not remembered: 28 on 2026-11-27. Three separate records gave three different
        # counts for this one file (24 in this port's own header, 40 in the map guard, 30 in the
        # 11-25 audit), which is what a number nobody measures looks like after two months.
        # `>=` and not `==`: an assertion added is fine, an assertion lost is the failure here.
        self.assertGreaterEqual(text.count("ok("), 28,
                                "the harness has lost assertions — this port covers what it "
                                "checked, and 28 is the count it was written against")


class TestVariants(unittest.TestCase):
    """Section 3 of the harness, re-derived. The first test is the regression it was written for."""

    def test_the_accent_dropped_spelling_is_reachable(self):
        for name in ("München", "Zürich", "São Paulo", "Bogotá"):
            got = variants(name)
            self.assertIn(fold(name).lower(), [v.lower() for v in got],
                          f'the unaccented spelling of "{name}" must be queried — the 2026-10-03 '
                          f"defect was that the filter compared against fold and threw it away")

    def test_the_page_compares_the_typed_string_against_base_not_fold(self):
        code = inline_code()[0]
        self.assertIn("!== base.toLowerCase()", code,
                      "the filter must drop the typed string by comparing against `base`")
        self.assertNotIn("!== fold.toLowerCase()", code,
                         "comparing against `fold` is the defect of 2026-10-03: it silently "
                         "discards the accent-dropped spelling the page promises to try")

    def test_the_typed_string_is_not_requeried(self):
        self.assertNotIn("Bostn", variants("Bostn"),
                         "the page asks the geocoder about the typed string verbatim first")

    def test_a_missing_space_is_proposed(self):
        self.assertIn("Kuala Lumpur", variants("KualaLumpur"),
                      'a camel-joined name must yield "Kuala Lumpur"')

    def test_a_doubled_letter_is_collapsed(self):
        self.assertIn("Misisipi", variants("Mississippi"),
                      "the doubled-letter variant must be generated")

    def test_no_variant_is_shorter_than_three_characters(self):
        for q in ("Bostn", "Å", "Li", "KualaLumpur"):
            short = [v for v in variants(q) if len(v) < 3]
            self.assertEqual(short, [], f"short variants are sent for {q!r}")

    def test_the_variant_list_is_capped(self):
        self.assertLessEqual(len(variants("KualaLumpur")), 26,
                             "the page caps the queries it sends at 26; an uncapped list turns a "
                             "typo into a flood of requests to a free API")


class TestRanking(unittest.TestCase):
    def test_edit_distance_prefers_the_longer_correct_name(self):
        self.assertGreater(lev_sim("Bostn", "Boston"), lev_sim("Bostn", "Bost"),
                           "levSim must rank Boston above the village Bost for the typo Bostn — "
                           "this is the case the page's comment names")

    def test_edit_distance_is_normalised_by_length(self):
        self.assertAlmostEqual(lev_sim("Bostn", "Boston"), 1 - 1 / 6, places=9)
        self.assertEqual(lev_sim("Boston", "Boston"), 1.0)


class TestAnnualMeans(unittest.TestCase):
    """Section 7 of the harness: nulls, partial years, and the last-full-year rule."""

    def setUp(self):
        self.cy = datetime.date.today().year
        self.times, self.vals = harness_daily_series(self.cy)
        self.rows = annual_means(self.times, self.vals, self.cy)

    def test_a_year_with_too_much_missing_data_is_dropped(self):
        self.assertNotIn(self.cy - 3, [r["year"] for r in self.rows],
                         "a 200-day year must not be averaged as if it were a year")

    def test_the_current_incomplete_year_is_excluded(self):
        self.assertNotIn(self.cy, [r["year"] for r in self.rows],
                         "the year in progress is not a complete year")

    def test_null_days_are_skipped_not_counted_as_zero(self):
        self.assertEqual(len(self.rows), 2)
        self.assertEqual([r["n"] for r in self.rows], [355, 355],
                         "ten null days leave 355 usable days, and a zero would drag the mean down")
        self.assertNotIn(0.0, [r["mean"] for r in self.rows])

    def test_the_rows_are_sorted_and_carry_their_own_mean(self):
        self.assertEqual([r["year"] for r in self.rows], [self.cy - 2, self.cy - 1])
        for r in self.rows:
            self.assertAlmostEqual(r["mean"], 10.0 + (r["year"] % 10) * 0.01, places=9)

    def test_the_archive_query_spans_1950_to_now_for_the_chosen_grid_point(self):
        code = inline_code()[0]
        for needle in ("start_date=1950-01-01", "timezone=auto", "daily=temperature_2m_mean",
                       "latitude=${lat}&longitude=${lon}"):
            self.assertIn(needle, code, f"the archive query lost {needle!r}")
        self.assertIn("Date.now() - 6*864e5", code,
                      "the archive lags a few days; the page must not ask for today")


class TestDecadeMeans(unittest.TestCase):
    def setUp(self):
        self.dec = decade_means(harness_decade_rows())

    def test_a_decade_with_fewer_than_six_years_is_dropped(self):
        self.assertEqual([d["decade"] for d in self.dec], [1950, 1980, 2010],
                         "the five-year 2020s bucket must not reach the reader as a decade")
        self.assertIn("x.years >= 6", inline_code()[0],
                      "the page's own filter is the >= 6 usable years rule")

    def test_decade_means_are_the_mean_of_their_own_years(self):
        self.assertEqual([d["mean"] for d in self.dec], [10.0, 11.0, 12.0])
        self.assertEqual([d["years"] for d in self.dec], [10, 10, 10])


class TestWhatTheReaderSees(unittest.TestCase):
    """Section 5: the printed numbers are the arithmetic, not a second opinion."""

    def setUp(self):
        self.n = printed_numbers(harness_decade_rows())
        self.code = inline_code()[0]

    def test_the_endpoint_delta_is_last_decade_minus_first(self):
        self.assertEqual(self.n["delta"], "+2.00 °C")
        self.assertIn("last.mean - first.mean", self.code,
                      "the headline change is computed from the unrounded decade means")

    def test_the_delta_names_the_two_decades_it_spans(self):
        self.assertEqual(self.n["span"], "1950s → 2010s")
        self.assertIn("${first.decade}s → ${last.decade}s", self.code)

    def test_the_trend_is_the_delta_divided_by_the_decades_spanned(self):
        self.assertEqual(self.n["trend"], "+0.33 °C", "2.00 °C over six decades is +0.33 °C")
        self.assertIn("(last.decade - first.decade)/10", self.code)
        self.assertIn("per decade, endpoint fit", self.code,
                      "the trend must be labelled as an endpoint fit, not a regression")

    def test_the_warmest_year_and_its_value_are_printed(self):
        self.assertEqual(self.n["warmest"], "12.0 °C")
        self.assertEqual(self.n["warmest_year"], "warmest year (2010)")

    def test_the_year_range_and_count_are_printed(self):
        self.assertEqual(self.n["range"], "35 complete years, 1950–2024")
        self.assertIn("complete years, ${rows[0].year}–${rows[rows.length-1].year}", self.code)

    def test_the_dropped_decade_never_reaches_the_reader(self):
        self.assertNotIn("2020s", self.n["decades"])
        self.assertEqual(self.n["decades"], ["1950s", "1980s", "2010s"])

    def test_the_table_means_are_rounded_once_each(self):
        self.assertEqual(self.n["means"], ["10.00", "11.00", "12.00"])
        self.assertIn("d.mean.toFixed(2)", self.code)

    def test_the_sign_is_only_printed_when_it_is_a_sign(self):
        self.assertIn('delta>=0?"+":""', self.code,
                      "a rising figure is printed with its plus; a falling one is not")

    def test_the_caveats_block_is_revealed_with_the_result(self):
        self.assertIn('$("caveats").style.display = "block"', self.code,
                      "the caveats must not stay hidden once a number is on screen")

    def test_the_status_line_reports_how_many_years_were_used(self):
        self.assertIn("`Done — ${rows.length} years at ${place}.`", self.code)

    def test_an_empty_answer_says_so_plainly(self):
        self.assertIn("No usable years came back", self.code,
                      "an empty result must say it is empty, not draw a chart of nothing")


class TestPrivacyAndHonesty(unittest.TestCase):
    def test_the_page_contacts_no_host_but_the_two_keyless_open_meteo_apis(self):
        code = inline_code()[0]
        hosts = {h for h in re.findall(r"https?://([^/\"'`\s)]+)", code)}
        self.assertEqual(hosts, set(HOSTS_ALLOWED),
                         "a third host would be a new recipient of the reader's search terms")

    def test_the_page_promises_no_account_and_keeps_it(self):
        html = page_text()
        self.assertIn("No account, no install, nothing sent to us", html)
        self.assertNotIn("api_key", html.lower())
        self.assertNotIn("Authorization", html)

    def test_every_number_is_reproducible_by_the_reader(self):
        self.assertIn("Reproduce every number here yourself", inline_code()[0])
        self.assertIn("the exact query this page ran", inline_code()[0])

    def test_the_page_says_what_it_is_not(self):
        html = page_text()
        self.assertIn("It is not a forecast, not a projection, and not an argument.", html)
        self.assertIn("This is a measurement of the past at one grid point.", html)
        self.assertIn("The number is a grid cell, not your garden thermometer.", html)
        self.assertIn("One year tells you nothing.", html)

    def test_the_rounding_caveat_names_its_own_arithmetic(self):
        """The page publishes a table/headline gap and calls it one rounding step. Pinned because
        it is the sentence that keeps the two figures from reading as two answers."""
        html = page_text()
        self.assertIn("11.16 − 9.77 = 1.39 against a headline of +1.40", html)
        self.assertIn("that gap is one rounding step, not two answers", html)

    def test_the_reanalysis_is_named_on_the_result_itself(self):
        self.assertIn("Reanalysis for this grid cell, not a local station.", inline_code()[0],
                      "the caveat must travel with the number, not only live in the block below")

    def test_a_wrong_match_is_asked_about_rather_than_charted(self):
        code = inline_code()[0]
        self.assertIn("does not closely match anything", code)
        self.assertIn("Which place did you mean?", code)
        self.assertIn("pick one", code,
                      "a page that silently charts the wrong town is worse than one that asks")


class TestTheWorksIndex(unittest.TestCase):
    def test_the_index_links_the_page(self):
        self.assertIn('href="warming.html"', index_text())

    def test_the_index_figure_is_the_one_the_page_reports(self):
        text = index_text()
        self.assertRegex(text, r"Boston, 76 complete years, \+1\.40 °C from the 1950s to the 2020s",
                         "the index's Boston figure is a live re-measurement; if it moved, say so "
                         "in the same change as the page's caveat about it")

    def test_the_index_says_what_the_page_is(self):
        text = index_text()
        self.assertIn("grid-cell reanalysis rather than your nearest thermometer", text)
        self.assertIn("one year is not a trend", text)
        self.assertIn("a measurement rather than an argument", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
