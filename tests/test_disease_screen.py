#!/usr/bin/env python3
"""Offline tests for the disease-target screen: no network, synthetic counts only.

The band that matters on a dense disease — components co-mentioned but never named together in a
title or abstract — was missing from the first version of the summary, so the screen printed
"(none)" while 26 targets sat in exactly that band. These tests pin the classification so it
cannot silently disappear again, and pin the rule that a failed query (-1) is not read as a zero.

Added 2026-09-19, after two clock runs found the screen lying in opposite directions: it invents
*absences* (a symbol-only query calls `NGF` unjoined while the literature writes "nerve growth
factor") and *presences* (`AR` matched "augmented reality", `KIT` matched "mesh kit"). So the
tests below also pin three things the count alone cannot: that a row is unjoined only if it is
unjoined under every name supplied; that every strict join carries the documents behind it; and
that a short symbol is flagged instead of being allowed to close a lead silently.
"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/disease_screen.py"
spec = importlib.util.spec_from_file_location("disease_screen", SCRIPT)
ds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ds)


class _StubNet:
    """Replace every network call in the module; restore on exit."""

    def __init__(self, any_fn=None, strict_fn=None, epmc_fn=None, hits_fn=None, trials_fn=None):
        self._saved = {}
        self._new = {
            "any_field": any_fn or (lambda sym, dis: 0),
            "strict": strict_fn or (lambda sym, dis: 0),
            "epmc": epmc_fn or (lambda term: 0),
            "epmc_hits": hits_fn or (lambda term, size=3: []),
            "trials": trials_fn or (lambda cond: 0),
            "ot_disease": lambda name: (None, None),
            "ot_score": lambda sym, efo: None,
        }

    def __enter__(self):
        for name, fn in self._new.items():
            self._saved[name] = getattr(ds, name)
            setattr(ds, name, fn)
        return self

    def __exit__(self, *exc):
        for name, fn in self._saved.items():
            setattr(ds, name, fn)
        return False


class VerdictTests(unittest.TestCase):
    def test_failed_query_is_not_a_zero(self):
        self.assertIn("QUERY FAILED", ds.verdict(-1, 0))
        self.assertNotIn("unjoined", ds.verdict(-1, 0).lower())

    def test_strict_join_is_prior_work(self):
        self.assertIn("already published together", ds.verdict(9, 1))

    def test_true_zero_is_a_candidate_not_a_finding(self):
        v = ds.verdict(0, 0)
        self.assertIn("unjoined", v)
        self.assertIn("NOT a finding", v)

    def test_incidental_band_says_read_them(self):
        self.assertIn("incidental", ds.verdict(3, 0))

    def test_co_mentioned_band_is_named(self):
        self.assertIn("discussed", ds.verdict(50, 0))

    def test_short_symbol_join_must_not_close_a_lead(self):
        """`AR` → augmented reality, `KIT` → mesh kit. A real match, the wrong meaning."""
        v = ds.verdict(4, 1, ambiguous_symbol=True)
        self.assertNotIn("already published together", v)
        self.assertIn("REFUSING", v)
        self.assertIn("strict_hits", v)
        # and the unambiguous case is unchanged
        self.assertNotIn("REFUSING", ds.verdict(4, 1, ambiguous_symbol=False))


class SummaryBandTests(unittest.TestCase):
    def _run(self, rows, **kwargs):
        """Feed synthetic counts through run() by stubbing every network call."""
        counts = {sym: (a, s) for sym, a, s in rows}
        with _StubNet(any_fn=lambda sym, dis: counts[sym][0],
                      strict_fn=lambda sym, dis: counts[sym][1],
                      epmc_fn=lambda term: 10,
                      trials_fn=lambda cond: 5):
            targets = [{"category": "t", "symbol": sym} for sym, _, _ in rows]
            return ds.run("endometriosis", targets, use_ot=False, **kwargs)

    def test_all_four_bands_are_separated(self):
        res = self._run([
            ("JOINED", 500, 40),   # title/abstract join -> prior work
            ("ZERO", 0, 0),        # nothing anywhere -> candidate
            ("INC", 3, 0),         # incidental only
            ("THIN", 25, 0),       # co-mentioned, never studied  <-- the band that was hidden
        ])
        self.assertEqual(res["joined_in_title_or_abstract"], ["JOINED"])
        self.assertEqual(res["unjoined"], ["ZERO"])
        self.assertEqual(res["incidental_any_field_only"], ["INC"])
        self.assertEqual(res["no_strict_join_but_discussed"], ["THIN"])
        self.assertEqual(res["no_title_abstract_join"], ["ZERO", "INC", "THIN"])

    def test_empty_candidate_band_is_reported_as_empty_not_omitted(self):
        res = self._run([("JOINED", 100, 9)])
        self.assertEqual(res["unjoined"], [])
        self.assertEqual(res["no_title_abstract_join"], [])


class NameCoverageTests(unittest.TestCase):
    """A target is a symbol and the names a paper would actually use for it."""

    def _run(self, target):
        # The literature names the protein, never the symbol.
        def strict_fn(name, form):
            return 42 if name == "nerve growth factor" else 0

        def any_fn(name, form):
            return 300 if name == "nerve growth factor" else 0

        with _StubNet(any_fn=any_fn, strict_fn=strict_fn, epmc_fn=lambda t: 2000):
            return ds.run("pudendal neuralgia", [target], use_ot=False)

    def test_named_row_is_joined_even_though_the_symbol_is_not(self):
        res = self._run({"category": "neurotrophin", "symbol": "NGF",
                         "names": ["nerve growth factor"]})
        row = res["targets"][0]
        self.assertEqual(row["strict"], 42)
        self.assertEqual(row["matched_name"], "nerve growth factor")
        self.assertTrue(row["naming_sensitive"])
        self.assertEqual(row["symbol_only_strict"], 0)
        self.assertEqual(res["false_gaps_repaired_by_names"], ["NGF"])
        self.assertNotIn("NGF", res["unjoined"])

    def test_symbol_only_target_is_not_marked_naming_sensitive(self):
        res = self._run({"category": "x", "symbol": "NGF"})
        row = res["targets"][0]
        self.assertFalse(row["naming_sensitive"])
        self.assertEqual(res["false_gaps_repaired_by_names"], [])

    def test_disease_synonyms_are_searched_and_recorded(self):
        seen = []

        def strict_fn(name, form):
            seen.append(form)
            return 0

        with _StubNet(any_fn=lambda n, f: 0, strict_fn=strict_fn, epmc_fn=lambda t: 5000):
            res = ds.run("pudendal neuralgia", [{"symbol": "NGF"}],
                         use_ot=False, forms=["pudendal nerve entrapment"])
        self.assertEqual(res["disease_forms_searched"],
                         ["pudendal neuralgia", "pudendal nerve entrapment"])
        self.assertIn("pudendal nerve entrapment", seen)


class JoinEvidenceTests(unittest.TestCase):
    """A count cannot tell a paper about the pair from a coincidence of English."""

    def test_join_carries_the_document_that_produced_it(self):
        hit = [{"pmid": "38560457",
                "title": "Accuracy of augmented reality-guided needle placement ...",
                "year": "2024"}]
        with _StubNet(any_fn=lambda n, f: 3, strict_fn=lambda n, f: 1,
                      epmc_fn=lambda t: 2000, hits_fn=lambda term, size=3: hit):
            res = ds.run("pudendal neuralgia", [{"symbol": "AR"}], use_ot=False)
        row = res["targets"][0]
        self.assertEqual(row["strict_hits"], hit)
        self.assertTrue(row["ambiguous_symbol"])
        self.assertEqual(res["ambiguous_joins_to_read"], ["AR"])

    def test_no_join_fetches_nothing(self):
        called = []
        with _StubNet(any_fn=lambda n, f: 0, strict_fn=lambda n, f: 0,
                      epmc_fn=lambda t: 2000,
                      hits_fn=lambda term, size=3: called.append(term) or []):
            res = ds.run("pudendal neuralgia", [{"symbol": "SCN9A"}], use_ot=False)
        self.assertEqual(res["targets"][0]["strict_hits"], [])
        self.assertEqual(called, [])
        self.assertEqual(res["ambiguous_joins_to_read"], [])


class DensityFloorTests(unittest.TestCase):
    """Below the floor the unjoined band saturates: a zero is the corpus, not a discovery."""

    def test_thin_corpus_warns_and_dense_corpus_does_not(self):
        self.assertIsNotNone(ds.floor_warning(221))       # pudendal neuralgia
        self.assertIsNotNone(ds.floor_warning(0))
        self.assertIsNone(ds.floor_warning(ds.FLOOR_STRICT))
        self.assertIsNone(ds.floor_warning(16558))        # fibromyalgia

    def test_warning_reaches_the_artefact(self):
        with _StubNet(any_fn=lambda n, f: 0, strict_fn=lambda n, f: 0, epmc_fn=lambda t: 221,
                      trials_fn=lambda c: 25):
            res = ds.run("pudendal neuralgia", [{"symbol": "SCN9A"}], use_ot=False)
        self.assertIsNotNone(res["density_warning"])
        self.assertIn("saturates", res["density_warning"])

    def test_density_bands_the_condition(self):
        with _StubNet(epmc_fn=lambda t: 221, trials_fn=lambda c: 25):
            rows = ds.density(["pudendal neuralgia"])
        self.assertIn("below floor", rows[0]["band"])
        with _StubNet(epmc_fn=lambda t: 16558, trials_fn=lambda c: 218):
            rows = ds.density(["fibromyalgia"])
        self.assertEqual(rows[0]["band"], "screenable")


class AmbiguityTests(unittest.TestCase):
    def test_short_symbols_are_flagged(self):
        for sym in ("AR", "KIT", "NOS"):
            self.assertTrue(ds.ambiguous(sym), sym)
        for sym in ("SCN9A", "TRPV1", "SLC19A3"):
            self.assertFalse(ds.ambiguous(sym), sym)




class NullControlTests(unittest.TestCase):
    """A string that names nothing is the screen's null.

    Added 2026-09-20 from the 09:32 run of that day, which put three nonsense strings in a
    222-target list and never said what they were for. Scored next to the real targets they are
    the sharpest evidence the floor argument has: on a thin condition a string that cannot
    possibly be a gene is exactly as "unjoined" as a real one, so the band is the corpus's
    density and not a gap in the literature.
    """

    def _run(self, targets, real_counts):
        def any_fn(sym, dis):
            return real_counts.get(sym, (0, 0))[0]

        def strict_fn(sym, dis):
            return real_counts.get(sym, (0, 0))[1]

        with _StubNet(any_fn=any_fn, strict_fn=strict_fn, epmc_fn=lambda t: 221):
            return ds.run("pudendal neuralgia", targets, use_ot=False)

    def test_control_is_scored_but_kept_out_of_every_band(self):
        res = self._run(
            [{"category": "ion channel", "symbol": "SCN9A"},
             {"category": "null", "symbol": "XQZWKJ", "control": True}],
            {"SCN9A": (3, 0), "XQZWKJ": (0, 0)})
        self.assertEqual(res["n_targets"], 1)
        self.assertEqual(res["n_controls"], 1)
        self.assertEqual(res["no_title_abstract_join"], ["SCN9A"])
        self.assertEqual([c["symbol"] for c in res["controls"]], ["XQZWKJ"])
        self.assertNotIn("XQZWKJ", res["incidental_any_field_only"])
        self.assertNotIn("XQZWKJ", res["no_title_abstract_join"])
        self.assertNotIn("XQZWKJ", res["unjoined"])
        # The control was still scored: it is the point of the row.
        self.assertEqual(res["controls"][0]["any_field"], 0)

    def test_a_control_that_scores_is_an_alarm_not_a_count(self):
        """If a string that names nothing comes back joined, the matching is not a string search."""
        res = self._run([{"symbol": "SCN9A"},
                         {"symbol": "XQZWKJ", "control": True}],
                        {"SCN9A": (3, 0), "XQZWKJ": (7, 2)})
        self.assertIn("suspect", res["control_check"])
        self.assertNotIn("already published together", res["controls"][0]["verdict"])

    def test_controls_scoring_zero_like_the_genes_says_the_band_is_the_corpus(self):
        targets = [{"symbol": "G%d" % i} for i in range(4)]
        targets.append({"symbol": "XQZWKJ", "control": True})
        res = self._run(targets, {s: (0, 0) for s in ("G0", "G1", "G2", "G3", "XQZWKJ")})
        self.assertIn("measures the condition's literature", res["control_check"])
        self.assertEqual(len(res["unjoined"]), 4)  # the four real genes, not the control

    def test_control_verdict_names_itself_rather_than_offering_a_candidate(self):
        res = self._run([{"symbol": "XQZWKJ", "control": True}], {"XQZWKJ": (0, 0)})
        self.assertTrue(res["controls"][0]["verdict"].startswith("null control"))

    def test_no_controls_means_no_claim(self):
        res = self._run([{"symbol": "SCN9A"}], {"SCN9A": (3, 0)})
        self.assertIsNone(res["control_check"])
        self.assertEqual(res["n_controls"], 0)


class FailedCountTests(unittest.TestCase):
    """A failed search (-1) is not a zero, and it is not a row.

    Added 2026-09-23 from `research/vulvodynia-screen.json` as it then stood: 44 of 128 rows
    carried a failed count. A -1 was already kept distinct from a 0 in `verdict`, but the
    *summary* dropped those rows out of every band, so the unjoined band shrank and
    `control_check` divided by rows it had never scored. Both errors point the same way — a
    saturated condition reads as separable, and three rows (P2RY12, MGLL, SORT1) printed
    "unjoined — a candidate, NOT a finding" on a strict query that had failed outright.
    """

    def _run(self, targets, counts):
        def any_fn(sym, dis):
            return counts[sym][0]

        def strict_fn(sym, dis):
            return counts[sym][1]

        with _StubNet(any_fn=any_fn, strict_fn=strict_fn, epmc_fn=lambda t: 2000):
            return ds.run("endometriosis", targets, use_ot=False)

    def test_a_failed_strict_query_is_not_offered_as_a_candidate(self):
        """`any_field == 0, strict == -1` used to read "unjoined ... NOT a finding"."""
        v = ds.verdict(0, -1)
        self.assertIn("QUERY FAILED", v)
        self.assertNotIn("unjoined", v.lower())
        self.assertNotIn("candidate", v.lower())

    def test_a_row_with_a_failed_count_stays_out_of_every_band(self):
        res = self._run([{"symbol": "GOOD"}, {"symbol": "HALF"}, {"symbol": "DEAD"}],
                        {"GOOD": (0, 0), "HALF": (-1, 0), "DEAD": (-1, -1)})
        self.assertEqual(res["unjoined"], ["GOOD"])
        self.assertEqual(res["no_title_abstract_join"], ["GOOD"])
        self.assertEqual(res["n_scored"], 1)
        self.assertEqual(res["n_failed"], 2)
        self.assertEqual(res["n_targets"], 3)          # submitted, not scored
        self.assertEqual(res["failed_queries"],
                         [{"symbol": "HALF", "failed_scopes": ["any_field"],
                           "any_field": -1, "strict": 0},
                          {"symbol": "DEAD", "failed_scopes": ["strict", "any_field"],
                           "any_field": -1, "strict": -1}])
        self.assertIn("Re-run those rows", res["failed_queries_note"])
        # The rows are still visible, with their verdicts, rather than silently absent.
        for sym in ("HALF", "DEAD"):
            row = next(r for r in res["targets"] if r["symbol"] == sym)
            self.assertIn("QUERY FAILED", row["verdict"])

    def test_no_failed_rows_means_the_note_is_silent(self):
        res = self._run([{"symbol": "GOOD"}], {"GOOD": (0, 0)})
        self.assertEqual(res["n_scored"], 1)
        self.assertEqual(res["n_failed"], 0)
        self.assertEqual(res["failed_queries"], [])
        self.assertIsNone(res["failed_queries_note"])

    def test_the_control_fraction_divides_by_what_was_scored(self):
        """3 scorable zeros + 1 unscorable row is 100% of 3, not 75% of 4."""
        targets = [{"symbol": "G%d" % i} for i in range(3)]
        targets += [{"symbol": "BAD"}, {"symbol": "XQZWKJ", "control": True}]
        counts = {s: (0, 0) for s in ("G0", "G1", "G2", "XQZWKJ")}
        counts["BAD"] = (-1, 0)
        res = self._run(targets, counts)
        self.assertIn("3 of 3 scorable real targets (100%)", res["control_check"])
        self.assertIn("1 of 4 real targets could not be scored", res["control_check"])
        self.assertIn("measures the condition's literature", res["control_check"])

    def test_a_failed_control_is_not_an_alarm_about_the_matching(self):
        """A -1 control is evidence about the run, not about the string search."""
        res = self._run([{"symbol": "SCN9A"},
                         {"symbol": "XQZWKJ", "control": True},
                         {"symbol": "QQQQQQ", "control": True}],
                        {"SCN9A": (3, 0), "XQZWKJ": (0, 0), "QQQQQQ": (-1, -1)})
        self.assertNotIn("suspect", res["control_check"])
        self.assertIn("control query failed", res["control_check"])
        self.assertIn("not evidence either way", res["control_check"])

    def test_no_scorable_control_means_no_null_and_no_claim(self):
        res = self._run([{"symbol": "SCN9A"}, {"symbol": "XQZWKJ", "control": True}],
                        {"SCN9A": (3, 0), "XQZWKJ": (-1, 0)})
        self.assertIn("no null", res["control_check"])
        self.assertNotIn("separates a gene", res["control_check"])

    def test_a_failed_spelling_does_not_overwrite_a_real_count(self):
        """Ranking on (strict, any_field) alone let a -1 ride in on a higher strict count."""
        def strict_fn(name, form):
            return 9 if name == "BAD NAME" else 5

        def any_fn(name, form):
            return -1 if name == "BAD NAME" else 100

        with _StubNet(any_fn=any_fn, strict_fn=strict_fn, epmc_fn=lambda t: 2000):
            res = ds.run("endometriosis",
                         [{"symbol": "GOOD", "names": ["BAD NAME"]}], use_ot=False)
        row = res["targets"][0]
        self.assertEqual((row["strict"], row["any_field"], row["matched_name"]), (5, 100, "GOOD"))
        self.assertEqual(row["failed_scopes"], [])
        self.assertEqual(res["n_scored"], 1)

    def test_density_says_a_failed_count_is_a_failed_count(self):
        with _StubNet(epmc_fn=lambda t: -1, trials_fn=lambda c: 0):
            rows = ds.density(["vulvodynia"])
        self.assertEqual(rows[0]["band"], "query failed — no count; re-run before reading this "
                                          "condition")



class AmbiguousJoinRefusalTests(unittest.TestCase):
    def _run(self, alias=None, alias_s=0, alias_a=0, symbol_s=9, symbol_a=100,
             control=False, forms=None):
        target = {"symbol": "AR", "control": control}
        if alias is not None:
            target["names"] = [alias]
        def count(name, form, scope):
            if name == "AR":
                return symbol_s if scope == "strict" else symbol_a
            if forms and form != forms[0]:
                return 0
            return alias_s if scope == "strict" else alias_a
        def hits(query, size=3):
            return [{"pmid": "gene" if 'androgen receptor' in query else "collision",
                     "title": query, "year": "2026"}]
        with _StubNet(strict_fn=lambda n, f: count(n, f, "strict"),
                      any_fn=lambda n, f: count(n, f, "any"),
                      epmc_fn=lambda q: 2000, hits_fn=hits):
            return ds.run("pudendal neuralgia", [target], use_ot=False, forms=forms)

    def test_bare_positive_is_neither_prior_work_nor_zero_even_when_dense(self):
        result = self._run(symbol_s=500, symbol_a=900)
        row = result["targets"][0]
        self.assertEqual(row["strict"], 500)
        self.assertEqual(row["strict_hits"][0]["pmid"], "collision")
        self.assertEqual(result["ambiguous_unverified_joins"], ["AR"])
        self.assertEqual(result["joined_in_title_or_abstract"], [])
        self.assertEqual(result["no_title_abstract_join"], [])
        self.assertEqual(result["unjoined"], [])
        self.assertEqual((result["n_scored"], result["n_failed"]), (1, 0))
        self.assertIn("REFUSING", row["verdict"])

    def test_smaller_positive_full_name_retains_its_own_evidence(self):
        result = self._run("androgen receptor", 1, 7)
        row = result["targets"][0]
        self.assertEqual((row["strict"], row["matched_name"]), (9, "AR"))
        self.assertEqual(row["strict_hits"][0]["pmid"], "collision")
        confirmation = row["name_confirmation"]
        self.assertEqual((confirmation["name"], confirmation["strict"],
                          confirmation["any_field"]), ("androgen receptor", 1, 7))
        self.assertEqual(confirmation["strict_hits"][0]["pmid"], "gene")
        self.assertIn('androgen receptor', confirmation["query"])
        self.assertEqual(result["joined_in_title_or_abstract"], ["AR"])
        self.assertEqual(result["ambiguous_unverified_joins"], [])

    def test_alias_needs_two_positive_successful_counts(self):
        for strict_count, any_count in [(0, 7), (1, -1), (1, 0)]:
            with self.subTest(strict=strict_count, any=any_count):
                result = self._run("androgen receptor", strict_count, any_count)
                self.assertIsNone(result["targets"][0]["name_confirmation"])
                self.assertEqual(result["ambiguous_unverified_joins"], ["AR"])

    def test_case_variants_and_short_aliases_do_not_clear_ambiguity(self):
        for alias in ["ar", " AR ", "ABC"]:
            with self.subTest(alias=alias):
                result = self._run(alias, 1, 7)
                self.assertIsNone(result["targets"][0]["name_confirmation"])
                self.assertEqual(result["ambiguous_unverified_joins"], ["AR"])

    def test_confirmation_records_the_actual_disease_form(self):
        result = self._run("androgen receptor", 1, 7, forms=["pelvic neuropathy"])
        confirmation = result["targets"][0]["name_confirmation"]
        self.assertEqual(confirmation["disease_form"], "pelvic neuropathy")
        self.assertIn("pelvic neuropathy", confirmation["query"])

    def test_failed_row_is_failed_rather_than_unresolved(self):
        result = self._run(symbol_a=-1)
        self.assertEqual(result["ambiguous_unverified_joins"], [])
        self.assertEqual((result["n_scored"], result["n_failed"]), (0, 1))
        self.assertIn("QUERY FAILED", result["targets"][0]["verdict"])

    def test_null_control_never_enters_unresolved_or_joined(self):
        result = self._run(control=True)
        self.assertEqual(result["ambiguous_unverified_joins"], [])
        self.assertEqual(result["joined_in_title_or_abstract"], [])
        self.assertEqual(result["n_controls"], 1)
        self.assertIn("suspect", result["control_check"])


    def test_disease_form_alone_cannot_claim_a_repaired_symbol_gap(self):
        with _StubNet(strict_fn=lambda n, f: 5 if f == "alternate" else 0,
                      any_fn=lambda n, f: 20, epmc_fn=lambda q: 2000):
            result = ds.run("condition", [{"symbol": "AR"}], use_ot=False,
                            forms=["alternate"])
        self.assertEqual(result["ambiguous_unverified_joins"], ["AR"])
        self.assertEqual(result["false_gaps_repaired_by_names"], [])

    def test_cli_shows_confirming_evidence_and_missing_document_status(self):
        import contextlib
        import io
        import tempfile
        from unittest.mock import patch
        result = self._run("androgen receptor", 1, 7)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as target_file:
            target_file.write("[]")
            target_file.flush()
            for available in [True, False]:
                with self.subTest(available=available):
                    confirmation = result["targets"][0]["name_confirmation"]
                    if not available:
                        confirmation["strict_hits"] = []
                        confirmation["hits_available"] = False
                    output = io.StringIO()
                    with patch.object(ds, "run", return_value=result), patch.object(
                            ds.sys, "argv", ["disease_screen.py", "condition", target_file.name,
                                             "--no-ot"]), contextlib.redirect_stdout(output):
                        self.assertEqual(ds.main(), 0)
                    text = output.getvalue()
                    self.assertIn("Expanded-name evidence: 'androgen receptor'", text)
                    self.assertIn("PMID collision", text)
                    if available:
                        self.assertIn("PMID gene", text)
                    else:
                        self.assertIn("Document retrieval unavailable", text)


class CandidateDensityGateTests(unittest.TestCase):
    def _run(self, density_counts, forms=None):
        def epmc_count(query):
            form = next((f for f in density_counts if '"' + f + '"' in query), "condition")
            return density_counts[form]
        with _StubNet(epmc_fn=epmc_count):
            return ds.run("condition", [{"symbol": "SCN9A"}], use_ot=False, forms=forms)

    def test_below_floor_keeps_observation_but_withholds_candidate_status(self):
        result = self._run({"condition": 221})
        self.assertEqual(result["unjoined"], ["SCN9A"])
        self.assertEqual(result["density_qualified_unjoined"], [])
        self.assertEqual(result["density_status"], "below_floor")
        self.assertFalse(result["candidates_certified"])
        self.assertIn("WITHHELD", result["targets"][0]["verdict"])
        self.assertIn("BELOW DENSITY FLOOR", result["targets"][0]["verdict"])
        self.assertNotIn("a candidate,", result["targets"][0]["verdict"])

    def test_boundary_is_999_vs_1000_not_scientific_certification(self):
        for count, qualified in [(999, False), (1000, True)]:
            with self.subTest(count=count):
                result = self._run({"condition": count})
                self.assertEqual(result["density_qualified"], qualified)
                self.assertEqual(result["density_qualified_unjoined"],
                                 ["SCN9A"] if qualified else [])
                self.assertFalse(result["candidates_certified"])

    def test_failed_density_differs_from_known_zero_density(self):
        failed = self._run({"condition": -1})
        zero = self._run({"condition": 0})
        self.assertEqual(failed["density_status"], "unknown")
        self.assertEqual(zero["density_status"], "below_floor")
        self.assertFalse(failed["density_qualified"])
        self.assertIn("UNKNOWN", failed["targets"][0]["verdict"])
        self.assertNotIn("saturates", failed["density_warning"])

    def test_failed_form_prevents_an_unproven_below_floor_claim(self):
        result = self._run({"condition": 221, "alternate": -1}, ["alternate"])
        self.assertEqual(result["disease_papers_strict"], 221)
        self.assertEqual(result["density_status"], "unknown")
        self.assertFalse(result["density_strict_queries_complete"])
        self.assertEqual([q["strict"] for q in result["density_queries"]], [221, -1])
        self.assertEqual(result["density_qualified_unjoined"], [])

    def test_successful_dense_form_proves_floor_despite_incomplete_coverage(self):
        result = self._run({"condition": 1500, "alternate": -1}, ["alternate"])
        self.assertEqual(result["density_status"], "meets_floor")
        self.assertTrue(result["density_qualified"])
        self.assertFalse(result["density_strict_queries_complete"])
        self.assertEqual(result["density_qualified_unjoined"], ["SCN9A"])
        self.assertFalse(result["candidates_certified"])

    def test_gate_preserves_failed_control_joined_and_ambiguous_bands(self):
        counts = {"ZERO": (0, 0), "JOINED": (100, 5), "AR": (100, 9),
                  "FAILED": (-1, 0), "NULL": (0, 0)}
        with _StubNet(any_fn=lambda n, f: counts[n][0],
                      strict_fn=lambda n, f: counts[n][1], epmc_fn=lambda q: 221):
            result = ds.run("condition", [{"symbol": s, "control": s == "NULL"}
                                         for s in counts], use_ot=False)
        self.assertEqual(result["unjoined"], ["ZERO"])
        self.assertEqual(result["joined_in_title_or_abstract"], ["JOINED"])
        self.assertEqual(result["ambiguous_unverified_joins"], ["AR"])
        self.assertEqual((result["n_scored"], result["n_failed"], result["n_controls"]),
                         (3, 1, 1))
        self.assertEqual(result["density_qualified_unjoined"], [])
        failed = next(r for r in result["targets"] if r["symbol"] == "FAILED")
        self.assertIn("QUERY FAILED", failed["verdict"])
        joined = next(r for r in result["targets"] if r["symbol"] == "JOINED")
        self.assertIn("prior work", joined["verdict"])

    def test_cli_labels_raw_zeros_and_density_qualification_separately(self):
        import contextlib
        import io
        import tempfile
        from unittest.mock import patch
        result = self._run({"condition": 221})
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as target_file:
            target_file.write("[]")
            target_file.flush()
            output = io.StringIO()
            with patch.object(ds, "run", return_value=result), patch.object(
                    ds.sys, "argv", ["disease_screen.py", "condition", target_file.name,
                                     "--no-ot"]), contextlib.redirect_stdout(output):
                self.assertEqual(ds.main(), 0)
        self.assertIn("density status: below_floor", output.getvalue())
        self.assertIn("density-qualified zero rows: (none)", output.getvalue())
        self.assertIn("raw 0/0 observations", output.getvalue())

class IncompleteSpellingCoverageTests(unittest.TestCase):
    """Probe D1 from Desi's 2026-10-17 density review, and gap 1 from the ambiguity review.

    D1: a row scored 0/0 from one spelling while another supplied spelling FAILED entered
    `density_qualified_unjoined` as a certified zero. The failure was computed and then thrown
    away, so a failed query was read as a zero at the band-selection layer. Gap 1: a failed
    expanded-name query left no trace, making it identical to no name having been supplied.
    """

    def _run(self, counts, names=None, density=1500):
        def any_fn(n, f):
            return counts.get((n, f), (0, 0))[0]

        def strict_fn(n, f):
            return counts.get((n, f), (0, 0))[1]

        target = {"symbol": "SCN9A"}
        if names is not None:
            target["names"] = names
        with _StubNet(any_fn=any_fn, strict_fn=strict_fn, epmc_fn=lambda q: density):
            return ds.run("condition", [target], use_ot=False)

    def test_failed_alias_keeps_the_zero_out_of_the_qualified_band(self):
        names = ["sodium channel Nav1.7"]
        result = self._run({("SCN9A", "condition"): (0, 0),
                            ("sodium channel Nav1.7", "condition"): (-1, -1)}, names)
        row = result["targets"][0]
        self.assertEqual((row["strict"], row["any_field"]), (0, 0))
        self.assertEqual(result["density_status"], "meets_floor")
        self.assertTrue(result["density_qualified"])
        self.assertFalse(row["coverage_complete"])
        self.assertTrue(row["unmeasured_zero"])
        self.assertEqual(row["expanded_name_failed"], names)
        self.assertEqual(row["failed_spelling_pairs"],
                         [{"name": names[0], "disease_form": "condition"}])
        # Still an observation, no longer a certified zero.
        self.assertEqual(result["unjoined"], ["SCN9A"])
        self.assertEqual(result["unjoined_incomplete_coverage"], ["SCN9A"])
        self.assertEqual(result["density_qualified_unjoined"], [])
        self.assertIn("INCOMPLETE SPELLING COVERAGE", row["verdict"])
        self.assertIn("WITHHELD", row["verdict"])
        self.assertNotIn("a candidate, NOT a finding", row["verdict"])

    def test_every_spelling_answered_zero_is_still_certified(self):
        names = ["sodium channel Nav1.7"]
        result = self._run({("SCN9A", "condition"): (0, 0),
                            ("sodium channel Nav1.7", "condition"): (0, 0)}, names)
        row = result["targets"][0]
        self.assertTrue(row["coverage_complete"])
        self.assertFalse(row["unmeasured_zero"])
        self.assertEqual(row["expanded_name_failed"], [])
        self.assertEqual(result["density_qualified_unjoined"], ["SCN9A"])
        self.assertEqual(result["unjoined_incomplete_coverage"], [])
        self.assertIsNone(result["incomplete_coverage_note"])

    def test_a_positive_join_with_a_failed_alias_stays_joined(self):
        names = ["sodium channel Nav1.7"]
        result = self._run({("SCN9A", "condition"): (100, 5),
                            ("sodium channel Nav1.7", "condition"): (-1, -1)}, names)
        row = result["targets"][0]
        self.assertFalse(row["coverage_complete"])
        self.assertEqual(result["joined_in_title_or_abstract"], ["SCN9A"])
        self.assertEqual(result["n_rows_incomplete_coverage"], 1)
        self.assertIsNotNone(result["incomplete_coverage_note"])
        self.assertEqual(sorted(row["failed_spelling_pairs"][0]), ["disease_form", "name"])

    def test_failed_expanded_name_is_recorded_not_read_as_no_name(self):
        """Gap 1: 'the alias did not answer' must not look like 'no alias was supplied'."""
        failed = self._run({("SCN9A", "condition"): (0, 0),
                            ("sodium channel Nav1.7", "condition"): (-1, 0)},
                           ["sodium channel Nav1.7"])
        absent = self._run({("SCN9A", "condition"): (0, 0)}, [])
        self.assertEqual(failed["targets"][0]["expanded_name_failed"],
                         ["sodium channel Nav1.7"])
        self.assertEqual(absent["targets"][0]["expanded_name_failed"], [])
        self.assertTrue(absent["targets"][0]["coverage_complete"])
        self.assertTrue(any(sp["failed_scopes"] == ["any_field"]
                            for sp in failed["targets"][0]["spellings"]))

    def test_the_row_carries_every_spelling_it_queried(self):
        names = ["sodium channel Nav1.7", "Nav1.7"]
        result = self._run({("SCN9A", "condition"): (0, 0)}, names, density=221)
        row = result["targets"][0]
        self.assertEqual([(sp["name"], sp["disease_form"]) for sp in row["spellings"]],
                         [("SCN9A", "condition"), (names[0], "condition"), (names[1], "condition")])
        # Below the density floor, the spelling coverage is complete; the verdict names density.
        self.assertTrue(row["coverage_complete"])
        self.assertIn("BELOW DENSITY FLOOR", row["verdict"])
        self.assertNotIn("INCOMPLETE SPELLING COVERAGE", row["verdict"])

    def test_cli_says_whether_the_density_vector_answered(self):
        import contextlib
        import io
        import tempfile
        from unittest.mock import patch
        result = self._run({("SCN9A", "condition"): (0, 0),
                            ("sodium channel Nav1.7", "condition"): (-1, -1)},
                           ["sodium channel Nav1.7"])
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as target_file:
            target_file.write("[]")
            target_file.flush()
            output = io.StringIO()
            with patch.object(ds, "run", return_value=result), patch.object(
                    ds.sys, "argv", ["disease_screen.py", "condition", target_file.name,
                                     "--no-ot"]), contextlib.redirect_stdout(output):
                self.assertEqual(ds.main(), 0)
        text = output.getvalue()
        self.assertIn("density queries complete: True", text)
        self.assertIn("zeros NOT certified", text)
        self.assertIn("SCN9A", text)


if __name__ == "__main__":
    unittest.main()
