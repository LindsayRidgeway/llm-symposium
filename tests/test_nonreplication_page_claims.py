#!/usr/bin/env python3
"""The nonreplication page's 32 offline checks, re-derived in the suite that actually runs.

Why this file exists. `docs/works/index.html` tells the reader that the page is

    "Verified before release: `tests/validate_nonreplication_page.mjs` (37 checks — 32 offline
     against the page's own code, 5 against the two live keyless records)"

and that sentence is true of the harness and false of this repository: no registered job
*executes* a `.mjs` validator. `.github/workflows/test-and-report.yml` hands them to
`node --check` — a syntax check — and skips cleanly when Node is absent, which it is here (no
node, nodejs, deno or bun on PATH, measured 2026-11-25). So the guard the index entry points at
has never run on any push, and a page that drifted would keep a green build.

This is the nonreplication page's share of `js-harness-claims`, and it is the sixth of the seven
offline pages to be ported (air, co-safety, fetchable, food-safety, heat, and this one; warming
remains). Unlike the five that read a `*-sources.json` record, this page has no record: its
numbers come from two live APIs, and the 32 offline checks are assertions about *its own code*.
So the port has two halves:

  1. a reference implementation, in Python, of the four pure decisions the page makes — the
     p-value parser, the threshold classifier, the per-study reducer and the aggregator — run
     against the same fixtures the harness uses. That is the record of what the behaviour is
     supposed to be, and it says in one place what "reached", "did not reach", "indeterminate"
     and "none" mean.
  2. a pin, on the page's own inline script, of every decision that half depends on: the
     leading `=` strip, the number pattern, the strict `p < 0.05` line with the two inequality
     branches, the PRIMARY-only filter, the `withP + none == primary` bookkeeping, the phrase
     families kept apart, the four page-size constants, the exact request strings, and the
     privacy boundary of two keyless hosts.

A red run means the page stopped making the claim it shipped with. What it does NOT do is
execute JavaScript: the harness's behavioural calls stay the harness's job, for a machine that
runs it. The page's sentence stays honest because section 6 of this file requires the index to
say which half runs here and which half does not — the amendment recommended by
`discussions/2026-11-25-dmitri-the-ten-pages-and-the-sixteen-harnesses.md`.

Run: python3 tests/test_nonreplication_page_claims.py
"""

import re
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

REPO = Path(__file__).resolve().parent.parent
PAGE = REPO / "docs" / "works" / "nonreplication.html"
INDEX = REPO / "docs" / "works" / "index.html"
HARNESS = REPO / "tests" / "validate_nonreplication_page.mjs"

# The harness's own constants, restated here so neither side can move alone without a failure.
REPL_PHRASES = [
    "failure to replicate",
    "failed to replicate",
    "did not replicate",
    "unable to replicate",
]
NULL_PHRASES = ["negative results", "null results", "non-replication"]
TRIAL_PAGE = 25
LIST_PER_PHRASE = 8
MAX_LIST = 24

EPMC_HOST = "www.ebi.ac.uk"
CTGOV_HOST = "clinicaltrials.gov"


# --------------------------------------------------------------------------------------------
# reading the page
# --------------------------------------------------------------------------------------------

def page_text() -> str:
    return PAGE.read_text(encoding="utf-8")


def prose(html: str) -> str:
    """The page with its tags removed and its whitespace collapsed — what a reader sees, so a
    sentence split by <em> or a line break still reads as one sentence here."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html))


def index_text() -> str:
    return INDEX.read_text(encoding="utf-8")


def inline_script(html: str) -> str:
    blocks = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>", html)
    assert len(blocks) == 1, f"the page should carry exactly one inline script, found {len(blocks)}"
    return blocks[0]


def function_body(script: str, name: str) -> str:
    """The text between `function name(...) {` and its matching brace."""
    m = re.search(r"function\s+" + re.escape(name) + r"\s*\(([^)]*)\)\s*\{", script)
    assert m is not None, f"the page no longer defines {name}()"
    depth, i = 1, m.end()
    while i < len(script) and depth:
        if script[i] == "{":
            depth += 1
        elif script[i] == "}":
            depth -= 1
        i += 1
    return script[m.end(): i - 1]


def const_array(script: str, name: str) -> list:
    m = re.search(r"const\s+" + re.escape(name) + r"\s*=\s*\[([^\]]*)\]", script)
    assert m is not None, f"the page no longer declares `const {name} = [...]`"
    return re.findall(r'"([^"]*)"', m.group(1))


def const_int(script: str, name: str) -> int:
    m = re.search(r"const\s+" + re.escape(name) + r"\s*=\s*(\d+)", script)
    assert m is not None, f"the page no longer declares `const {name} = <number>`"
    return int(m.group(1))


def code_comment_stripped(text: str) -> str:
    """Comments in this script are prose and repeat phrases the assertions pin; strip them so a
    claim is checked against code, not against a comment that describes it."""
    text = re.sub(r"/\*[\s\S]*?\*/", "", text)
    return re.sub(r"(?m)^\s*//.*$", "", text)


# --------------------------------------------------------------------------------------------
# the reference implementation — what the four decisions mean, independent of the JavaScript
# --------------------------------------------------------------------------------------------

P_VALUE = re.compile(r"^([<>]?)\s*([0-9]*\.?[0-9]+)$")


def parse_p(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    text = re.sub(r"^=", "", text).strip()
    m = P_VALUE.match(text)
    if not m:
        return None
    return {"op": m.group(1) or "=", "num": float(m.group(2))}


def classify_p(parsed: str) -> str:
    if not parsed:
        return "none"
    if parsed["op"] == "<":
        return "reached" if parsed["num"] <= 0.05 else "indeterminate"
    if parsed["op"] == ">":
        return "didnot" if parsed["num"] >= 0.05 else "indeterminate"
    return "reached" if parsed["num"] < 0.05 else "didnot"


def summarize_study(study: dict) -> dict:
    ident = ((study.get("protocolSection") or {}).get("identificationModule") or {})
    outcomes = (((study.get("resultsSection") or {}).get("outcomeMeasuresModule") or {})
                .get("outcomeMeasures") or [])
    primary = [o for o in outcomes if str((o or {}).get("type") or "").upper() == "PRIMARY"]
    result = {
        "nct": ident.get("nctId", ""), "title": ident.get("briefTitle", ""),
        "primary": len(primary), "withP": 0, "reached": 0, "didnot": 0,
        "indeterminate": 0, "none": 0,
    }
    for outcome in primary:
        raw = None
        for analysis in (outcome or {}).get("analyses") or []:
            if analysis and analysis.get("pValue") is not None and str(analysis["pValue"]).strip():
                raw = analysis["pValue"]
                break
        cls = classify_p(parse_p(raw))
        if cls == "none":
            result["none"] += 1
            continue
        result["withP"] += 1
        result[cls] += 1
    return result


def aggregate(studies: list) -> dict:
    agg = {"studies": len(studies), "primary": 0, "withP": 0, "reached": 0, "didnot": 0,
           "indeterminate": 0, "none": 0, "studiesWithNonSignificant": 0}
    for study in studies:
        for key in ("primary", "withP", "reached", "didnot", "indeterminate", "none"):
            agg[key] += study[key]
        if study["didnot"] > 0:
            agg["studiesWithNonSignificant"] += 1
    return agg


def epmc_query(phrase: str, topic: str) -> str:
    base = 'TITLE:"' + str(phrase).replace('"', "") + '"'
    topic = (topic or "").strip()
    return f"{base} AND ({topic})" if topic else base


def epmc_url(query: str, page_size: int, core: bool) -> str:
    params = {"query": query, "format": "json", "pageSize": str(page_size or 1)}
    if core:
        params["resultType"] = "core"
    joined = "&".join(f"{k}={v}" for k, v in params.items())
    return f"https://{EPMC_HOST}/europepmc/webservices/rest/search?{joined}"


def ctgov_url(topic: str) -> str:
    params = {
        "query.cond": topic,
        "filter.advanced": "AREA[HasResults]true",
        "pageSize": str(TRIAL_PAGE),
        "countTotal": "true",
        "fields": "NCTId|BriefTitle|ResultsSection",
    }
    joined = "&".join(f"{k}={v}" for k, v in params.items())
    return f"https://{CTGOV_HOST}/api/v2/studies?{joined}"


# --------------------------------------------------------------------------------------------
# 1. the reference implementation against the harness's own fixtures
# --------------------------------------------------------------------------------------------

class TestReferenceImplementation(unittest.TestCase):
    """These are the harness's section-1 fixtures, restated. If the meaning of a bucket moves,
    this fails before any page can drift quietly underneath it."""

    def test_prefixed_and_bare_numbers_both_parse(self):
        self.assertEqual(parse_p("=0.7158"), {"op": "=", "num": 0.7158})
        self.assertEqual(parse_p("0.488"), {"op": "=", "num": 0.488})
        self.assertEqual(parse_p(" 0.04 "), {"op": "=", "num": 0.04})

    def test_inequalities_keep_their_operator(self):
        self.assertEqual(parse_p("<0.0001"), {"op": "<", "num": 0.0001})
        self.assertEqual(parse_p(">0.999"), {"op": ">", "num": 0.999})

    def test_missing_and_free_text_are_null_not_zero(self):
        for value in ("", None, "not reported", "NA"):
            self.assertIsNone(parse_p(value), f"{value!r} was coerced instead of refused")

    def test_the_conventional_line_is_strict(self):
        self.assertEqual(classify_p(parse_p("0.04")), "reached")
        self.assertEqual(classify_p(parse_p("0.05")), "didnot")
        self.assertEqual(classify_p(parse_p("0.71")), "didnot")

    def test_inequalities_resolve_only_when_the_whole_interval_is_on_one_side(self):
        self.assertEqual(classify_p(parse_p("<0.001")), "reached")
        self.assertEqual(classify_p(parse_p("<0.05")), "reached")
        self.assertEqual(classify_p(parse_p(">0.05")), "didnot")
        self.assertEqual(classify_p(parse_p(">0.001")), "indeterminate")

    def test_no_p_value_is_its_own_bucket(self):
        self.assertEqual(classify_p(None), "none")

    def test_one_study_counts_primary_outcomes_and_keeps_the_blanks(self):
        study = {
            "protocolSection": {"identificationModule": {"nctId": "NCT00000001",
                                                         "briefTitle": "A trial"}},
            "resultsSection": {"outcomeMeasuresModule": {"outcomeMeasures": [
                {"type": "PRIMARY", "title": "p1", "analyses": [{"pValue": "=0.7158"}]},
                {"type": "PRIMARY", "title": "p2", "analyses": [{"pValue": "0.03"}]},
                {"type": "PRIMARY", "title": "p3", "analyses": []},
                {"type": "SECONDARY", "title": "s1", "analyses": [{"pValue": "0.9"}]},
            ]}},
        }
        counts = summarize_study(study)
        self.assertEqual(counts["primary"], 3, "secondary outcomes must not be counted")
        self.assertEqual(counts["none"], 1, "a primary outcome with no p-value is counted, not dropped")
        self.assertEqual((counts["reached"], counts["didnot"]), (1, 1))
        self.assertEqual(counts["withP"] + counts["none"], counts["primary"],
                         "no outcome may vanish between the two counts")
        self.assertEqual(counts["nct"], "NCT00000001")

    def test_the_first_printed_p_value_is_the_one_read(self):
        study = {"resultsSection": {"outcomeMeasuresModule": {"outcomeMeasures": [
            {"type": "PRIMARY", "title": "p", "analyses": [{"pValue": ""}, {"pValue": "0.02"}]},
        ]}}}
        self.assertEqual(summarize_study(study)["reached"], 1,
                         "an empty first analysis must not shadow the printed one behind it")

    def test_aggregation_counts_studies_not_outcomes_for_its_study_tally(self):
        one = summarize_study({"resultsSection": {"outcomeMeasuresModule": {"outcomeMeasures": [
            {"type": "PRIMARY", "analyses": [{"pValue": "0.9"}]},
            {"type": "PRIMARY", "analyses": [{"pValue": "0.8"}]},
        ]}}})
        two = summarize_study({"resultsSection": {"outcomeMeasuresModule": {"outcomeMeasures": []}}})
        agg = aggregate([one, two])
        self.assertEqual(agg["studies"], 2)
        self.assertEqual(agg["primary"], 2)
        self.assertEqual(agg["studiesWithNonSignificant"], 1,
                         "one study with two non-significant outcomes is one study")
        self.assertEqual(agg["withP"] + agg["none"], agg["primary"])

    def test_the_query_builders(self):
        self.assertEqual(epmc_query("failure to replicate", ""), 'TITLE:"failure to replicate"')
        self.assertEqual(epmc_query("failure to replicate", "depression"),
                         'TITLE:"failure to replicate" AND (depression)')
        self.assertEqual(epmc_query('a"b', ""), 'TITLE:"ab"',
                         "a quote in the phrase must not be able to break the query")

        lit = parse_qs(urlparse(epmc_url(epmc_query("failed to replicate", "chronic fatigue"),
                                         8, True)).query)
        self.assertEqual(lit["format"], ["json"])
        self.assertEqual(lit["pageSize"], ["8"])
        self.assertEqual(lit["resultType"], ["core"], "the title list needs core records")

        counts = parse_qs(urlparse(epmc_url(epmc_query("null results", "x"), 1, False)).query)
        self.assertNotIn("resultType", counts, "a count request must not pay for core records")

        trials = parse_qs(urlparse(ctgov_url("pancreatic cancer")).query)
        self.assertEqual(trials["filter.advanced"], ["AREA[HasResults]true"],
                         "the trial question is about studies that posted results")
        self.assertEqual(trials["countTotal"], ["true"])
        self.assertEqual(trials["fields"], ["NCTId|BriefTitle|ResultsSection"],
                         "the results section and the id are both needed")
        self.assertEqual(trials["pageSize"], [str(TRIAL_PAGE)])

    def test_the_phrase_families_do_not_overlap(self):
        self.assertEqual(sorted(REPL_PHRASES), sorted(set(REPL_PHRASES)))
        self.assertEqual(set(REPL_PHRASES) & set(NULL_PHRASES), set(),
                         "a phrase in both families could be summed by accident")
        self.assertEqual(len(REPL_PHRASES) + len(NULL_PHRASES), 7)


# --------------------------------------------------------------------------------------------
# 2. the page's own code, pinned decision by decision
# --------------------------------------------------------------------------------------------

class TestPageScript(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = page_text()
        cls.script = inline_script(cls.html)
        cls.code = code_comment_stripped(cls.script)

    def test_one_inline_script_and_it_is_the_harness_target(self):
        self.assertIn("all logic inline", self.script,
                      "the harness extracts this block; the page should say so")
        self.assertGreater(len(self.script), 5000, "the inline script is suspiciously small")

    def test_the_p_value_parser_strips_the_registrys_leading_equals(self):
        body = function_body(self.code, "parseP")
        self.assertIn('s.replace(/^=/, "")', body,
                      "the registry prints '=0.7158'; a parser without this strip drops those rows")
        self.assertIn("/^([<>]?)\\s*([0-9]*\\.?[0-9]+)$/", body,
                      "the number pattern must accept a bare or prefixed number and nothing else")
        self.assertIn("if (!m) return null;", body, "free text must be refused, not coerced")
        self.assertIn("if (!s) return null;", body, "an empty string must not become zero")

    def test_the_classifier_keeps_the_strict_line_and_the_inequalities(self):
        body = function_body(self.code, "classifyP")
        self.assertIn('if (p.op === "<")', body)
        self.assertIn("p.num <= 0.05", body,
                      "'<0.05' is bounded above, so the whole interval is below the line")
        self.assertIn('if (p.op === ">")', body)
        self.assertIn("p.num >= 0.05", body)
        self.assertIn('return p.num < 0.05 ? "reached" : "didnot";', body,
                      "exactly 0.05 is 'did not reach' — the line is p<0.05, not p<=0.05")

    def test_only_primary_outcomes_are_read(self):
        body = function_body(self.code, "summarizeStudy")
        self.assertIn('.toUpperCase() === "PRIMARY"', body,
                      "the registry's type field is not always upper-cased, and secondary "
                      "outcomes are not this page's subject")
        self.assertIn("res.none++", body,
                      "a primary outcome that printed no p-value is counted in its own bucket")
        self.assertIn("res.withP++", body)

    def test_a_study_with_a_non_significant_outcome_is_flagged_once(self):
        body = function_body(self.code, "aggregateStudies")
        self.assertIn("if (st.didnot > 0) agg.studiesWithNonSignificant++;", body,
                      "the count is of studies, not of outcomes")
        for key in ("primary", "withP", "reached", "didnot", "indeterminate", "none"):
            self.assertIn(f"agg.{key} += st.{key};", body,
                          f"the aggregate must carry {key} through rather than recompute it")

    def test_the_phrase_families_are_the_seven_the_page_names(self):
        self.assertEqual(const_array(self.code, "REPL_PHRASES"), REPL_PHRASES)
        self.assertEqual(const_array(self.code, "NULL_PHRASES"), NULL_PHRASES)
        self.assertIn("REPL_PHRASES.concat(NULL_PHRASES)", self.code,
                      "the combined list exists only for the count pass and is labelled as such")

    def test_the_page_sizes_are_the_ones_the_harness_states(self):
        self.assertEqual(const_int(self.code, "TRIAL_PAGE"), TRIAL_PAGE)
        self.assertEqual(const_int(self.code, "LIST_PER_PHRASE"), LIST_PER_PHRASE)
        self.assertEqual(const_int(self.code, "MAX_LIST"), MAX_LIST)

    def test_the_epmc_requests_are_title_scoped(self):
        self.assertIn("TITLE:\"", function_body(self.code, "epmcQuery"),
                      "the page's whole honesty argument rests on title scope, not title-or-abstract")
        self.assertIn('.replace(/"/g, "")', function_body(self.code, "epmcQuery"),
                      "a typed quote must be stripped, not interpolated into the query")
        body = function_body(self.code, "epmcUrl")
        self.assertIn("resultType", body)
        self.assertIn("if (core)", body, "core records must be optional — counts are cheap")

    def test_the_trial_request_asks_for_posted_results_only(self):
        body = function_body(self.code, "ctgovUrl")
        self.assertIn("AREA[HasResults]true", body)
        self.assertIn("NCTId|BriefTitle|ResultsSection", body.replace("fields: ", ""))

    def test_the_page_contacts_two_keyless_hosts_and_nothing_else(self):
        """Two hosts are *asked* for data. Two more appear only as links on a title row, for the
        reader's own click, and must stay in the link builder rather than the fetch path."""
        hosts = {h for h in re.findall(r"https?://([^/\"'\s)]+)", self.code)}
        self.assertEqual(sorted(hosts), sorted({EPMC_HOST, CTGOV_HOST, "doi.org", "europepmc.org"}),
                         f"a host arrived that the privacy sentence does not cover: {sorted(hosts)}")
        links = function_body(self.code, "titleList")
        for host in ("doi.org", "europepmc.org"):
            self.assertIn(host, links,
                          f"{host} belongs on a title link, not in a data request")
        self.assertNotIn("doi.org", function_body(self.code, "epmcUrl"))
        self.assertNotIn("doi.org", function_body(self.code, "ctgovUrl"))

    def test_the_two_signals_render_apart_and_the_count_pass_covers_both(self):
        """The page's argument is that the two records answer different questions. The count
        pass therefore runs over ALL_PHRASES, while the title list — the thing a reader could
        mistake for evidence — is read from the replication family only."""
        body = function_body(self.code, "run")
        self.assertIn("for (const phrase of ALL_PHRASES)", body,
                      "the counts must cover both families, or the null-result columns vanish")
        self.assertIn("for (const phrase of REPL_PHRASES)", body,
                      "the title list is the replication family only (the null-result family is a "
                      "publishing convention, not a claim)")
        self.assertIn("isNull: NULL_PHRASES.indexOf(phrase) >= 0", body,
                      "each row must carry its family, because the page refuses to sum them")
        self.assertIn('Signal 1 · posted trial results', body)
        self.assertIn('Signal 2 · title-declared replication failure', body)

    def test_no_count_is_summed_across_the_two_records(self):
        for pattern in ("counts.reduce", "hitCount +", "counts.map(c => c.n).reduce"):
            self.assertNotIn(pattern, self.code,
                             "the page refuses a total across the two records; a reduce over the "
                             "phrase counts is exactly that total")
        self.assertIn("shown but not mixed into the list", prose(self.html))


# --------------------------------------------------------------------------------------------
# 3. the page's prose — the honesty this entry is worth reading for
# --------------------------------------------------------------------------------------------

class TestPageProse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = page_text()

    def test_the_two_numbers_it_refuses_to_print_are_still_refused(self):
        text = prose(self.html)
        self.assertIn("never added together", text,
                      "the refusal is the page's whole argument")
        self.assertIn('a total count of "failed science"', text)
        self.assertIn("a count of anything summed across the two records", text)

    def test_did_not_reach_is_attributed_to_the_page_and_not_the_registry(self):
        text = prose(self.html)
        self.assertIn("the registry does not label an outcome met or not met", text.lower())
        self.assertIn("non-inferiority", text)
        self.assertIn("equivalence", text)
        self.assertIn("safety endpoint", text.lower())

    def test_a_zero_is_explained_as_an_absent_phrase(self):
        text = prose(self.html)
        self.assertIn("the phrase is not in the titles", text)
        self.assertIn("not a finding that the literature replicates", text)

    def test_title_scope_is_stated_with_its_measurement(self):
        text = prose(self.html)
        self.assertIn("1,219", text, "the title-vs-abstract measurement is what justifies the scope")
        self.assertIn("only two were replication studies", text)

    def test_every_request_is_printed_for_the_reader(self):
        self.assertIn("Every request this page sent", page_text())


# --------------------------------------------------------------------------------------------
# 4. the claim — what the index says now, and what it must say
# --------------------------------------------------------------------------------------------

class TestTheClaim(unittest.TestCase):
    """The index sentence is the page's promise to a stranger. Before this port it named a
    harness no job runs; after the amendment it must say which half runs on every push."""

    def setUp(self):
        self.text = prose(index_text())

    def test_the_index_still_names_the_harness_and_its_shape(self):
        self.assertIn("tests/validate_nonreplication_page.mjs", self.text)
        self.assertIn("37 checks", self.text)
        self.assertIn("32 offline", self.text)
        self.assertIn("5 against the two live keyless records", self.text)

    def test_the_index_says_which_half_runs_here(self):
        missing = [phrase for phrase in
                   ("tests/test_nonreplication_page_claims.py",
                    "no job here executes",
                    "runs on every push")
                   if phrase not in self.text]
        self.assertEqual(missing, [],
                         "the index sentence must say what runs on every push; a sentence that "
                         "names only the harness rests on a guard no job executes. Missing: "
                         + ", ".join(missing))

    def test_the_harness_itself_still_exists_and_can_fail(self):
        source = HARNESS.read_text(encoding="utf-8")
        self.assertIn("process.exit(1)", source, "the harness must be able to fail the shell")
        self.assertIn("if (fail) {", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
