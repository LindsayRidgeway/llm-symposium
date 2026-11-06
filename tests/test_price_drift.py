"""Tests for scripts/price_drift.py — the check that a seat is priced as the model it ran.

The failure this instrument exists for is arithmetic that looks right: `burn_ledger.py` multiplies
each seat's tokens by that seat's blended rate, so a run that used a different model is not unpriced
and does not warn — it is priced at the wrong name and added to the total. Desi's 2026-10-26 report
measured the consequence once, in prose that cannot be re-run. These cases pin the judgement that
would have caught it: a match is a suffix on a `-` boundary, or it is drift.
"""
import importlib.util
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("price_drift", REPO / "scripts" / "price_drift.py")
pd = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pd)


def rec(amigo, model, tokens, date="20261106"):
    return {"amigo": amigo, "model": model, "tokens": tokens, "date": date,
            "run_id": f"{date}T000000Z-deadbeef"}


class MatchTest(unittest.TestCase):
    def test_exact_and_suffix_match(self):
        self.assertTrue(pd.matches("v4-flash", "deepseek-v4-flash"))
        self.assertTrue(pd.matches("sonnet-4-5", "sonnet-4-5"))

    def test_a_longer_variant_is_drift_not_a_match(self):
        # The experimental variant is the whole case: it is a different model, not a version bump.
        self.assertFalse(pd.matches("v4-flash", "deepseek-v4-flash-vision-exp"))

    def test_a_different_version_is_drift(self):
        self.assertFalse(pd.matches("3.6-flash", "gemini-3.8-flash"))
        self.assertFalse(pd.matches("sonnet-4-5", "claude-sonnet-5"))

    def test_case_and_emptiness(self):
        self.assertTrue(pd.matches("V4-Flash", "DeepSeek-V4-Flash"))
        self.assertFalse(pd.matches("", "anything"))
        self.assertFalse(pd.matches("v4-flash", ""))


class DriftRowsTest(unittest.TestCase):
    RATES = {"dmitri": {"model": "v4-flash", "blended": 0.01},
             "claude": {"model": "sonnet-4-5", "blended": 1.15},
             "gemini": {"model": "3.6-flash", "blended": 0.59}}

    def test_current_seat(self):
        rows = pd.drift_rows([rec("dmitri", "deepseek-v4-flash", 100)], self.RATES)
        self.assertEqual(rows[0]["status"], pd.CURRENT)
        self.assertTrue(rows[0]["models"][0]["matches_price"])

    def test_drifted_seat(self):
        rows = pd.drift_rows([rec("claude", "claude-sonnet-5", 100)], self.RATES)
        self.assertEqual(rows[0]["status"], pd.DRIFTED)

    def test_partial_seat_names_both_models_and_their_shares(self):
        rows = pd.drift_rows([rec("dmitri", "deepseek-v4-flash", 25),
                              rec("dmitri", "deepseek-v4-flash-vision-exp", 75)], self.RATES)
        row = rows[0]
        self.assertEqual(row["status"], pd.PARTIAL)
        self.assertEqual([m["model"] for m in row["models"]],
                         ["deepseek-v4-flash-vision-exp", "deepseek-v4-flash"])
        self.assertAlmostEqual(row["models"][0]["share"], 0.75)

    def test_a_seat_with_no_rate_row_is_unpriced_not_free(self):
        rows = pd.drift_rows([rec("gwen", "qwen3.8-max-0902", 100)], self.RATES)
        self.assertEqual(rows[0]["status"], pd.UNPRICED)
        self.assertIsNone(rows[0]["rate_usd_per_million"])

    def test_days_filter_uses_the_run_id_date(self):
        records = [rec("dmitri", "deepseek-v4-flash", 100, "2026-10-01".replace("-", "")),
                   rec("dmitri", "deepseek-v4-flash", 100, "20261106")]
        rows = pd.drift_rows(records, self.RATES, days=2)
        self.assertEqual(rows[0]["runs"], 1)
        self.assertEqual(rows[0]["tokens"], 100)

    def test_render_marks_the_mismatched_model(self):
        rows = pd.drift_rows([rec("claude", "claude-sonnet-5", 100)], self.RATES)
        text = pd.render(rows)
        self.assertIn("drifted", text)
        self.assertIn("! claude-sonnet-5", text)
        self.assertIn("claude", text.splitlines()[-1])


class PriceFileTest(unittest.TestCase):
    def test_the_repository_price_file_loads_as_a_map(self):
        rates = pd.load_prices()
        self.assertIn("dmitri", rates)
        self.assertIn("blended", rates["dmitri"])

    def test_a_missing_file_is_an_empty_map_not_an_exception(self):
        self.assertEqual(pd.load_prices(REPO / "channels" / "usage" / "no-such-file.json"), {})


if __name__ == "__main__":
    unittest.main()
