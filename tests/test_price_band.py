#!/usr/bin/env python3
"""Tests for the monthly price band — who is cheap *this month*, decided once and dated.

The band exists because "assign to the cheapest" hardcodes today's prices into the assignment rule.
The properties that make it safe rather than merely cheap, all three from the human (2026-10-09):
it names a band and not a winner, it is dated so a stale list is visible, and a monthly job writes
it so the pool stays current while the decision stays frozen.
"""
import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import price_band as pb  # noqa: E402


def prices(rates, as_of="2026-08-25"):
    return {"as_of": as_of, "basis": "made up for the test",
            "rates_usd_per_million": {k: {"blended": v} for k, v in rates.items()}}


class TestTheBand(unittest.TestCase):
    def test_the_band_is_everyone_within_the_multiplier_of_the_cheapest(self):
        band = pb.build(prices({"desi": 0.01, "dmitri": 0.01, "gemini": 0.59,
                                "claude": 1.15, "tarik": 1.86}), dt.date(2026, 10, 9))
        self.assertEqual(band["band"], ["desi", "dmitri"])
        self.assertEqual(band["cheapest"], "desi")

    def test_the_band_is_a_band_not_a_winner(self):
        """A one-member band collapses the random branch; two cheap amigos keep it a pool."""
        band = pb.build(prices({"desi": 0.01, "dmitri": 0.012, "gemini": 9.0}),
                        dt.date(2026, 10, 9))
        self.assertGreater(len(band["band"]), 1)
        self.assertIn("2x", band["rule"])

    def test_a_price_change_widens_the_band_without_touching_the_rule(self):
        before = pb.build(prices({"desi": 0.01, "gemini": 0.59}), dt.date(2026, 10, 9))
        after = pb.build(prices({"desi": 0.01, "gemini": 0.015}), dt.date(2026, 10, 9))
        self.assertEqual(before["band"], ["desi"])
        self.assertEqual(after["band"], ["desi", "gemini"])
        self.assertEqual(before["rule"], after["rule"])

    def test_an_old_price_list_says_so_instead_of_pretending(self):
        band = pb.build(prices({"desi": 0.01, "dmitri": 0.01}, as_of="2025-01-01"),
                        dt.date(2026, 10, 9))
        self.assertIn("STALE", band["note"])
        self.assertIn("2025-01-01", band["note"])

    def test_current_prices_say_that_instead(self):
        band = pb.build(prices({"desi": 0.01}, as_of="2026-10-01"), dt.date(2026, 10, 9))
        self.assertEqual(band["note"], "prices are current")

    def test_the_band_file_is_named_for_its_month_and_carries_both_dates(self):
        with tempfile.TemporaryDirectory() as td:
            usage = Path(td)
            (usage / "model-prices.json").write_text(
                json.dumps(prices({"desi": 0.01, "dmitri": 0.01, "tarik": 1.86})), encoding="utf-8")
            out = pb.write(usage, dt.date(2026, 10, 9))
            self.assertEqual(out.name, "price-band-2026-10.json")
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["written"], "2026-10-09")
            self.assertEqual(data["as_of"], "2026-08-25")

    def test_the_next_month_is_a_different_file(self):
        self.assertNotEqual(pb.path_for(dt.date(2026, 10, 31)), pb.path_for(dt.date(2026, 11, 1)))

    def test_a_rate_that_is_not_a_number_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "model-prices.json"
            path.write_text(json.dumps({"as_of": "2026-10-01",
                                        "rates_usd_per_million": {"desi": {"blended": "cheap"}}}),
                            encoding="utf-8")
            with self.assertRaises(ValueError):
                pb.load_prices(path)

    def test_no_rates_at_all_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "model-prices.json"
            path.write_text(json.dumps({"as_of": "2026-10-01", "rates_usd_per_million": {}}),
                            encoding="utf-8")
            with self.assertRaises(ValueError):
                pb.load_prices(path)


class TestTheRealPriceFile(unittest.TestCase):
    """The shipped table must be readable, sourced, and dated — not a placeholder."""

    def test_the_shipped_prices_load_and_name_every_amigo(self):
        data = pb.load_prices()
        self.assertEqual(set(data["rates_usd_per_million"]),
                         {"desi", "claude", "gemini", "tarik", "dmitri"})
        self.assertTrue(data["basis"].strip())

    def test_the_shipped_band_is_already_written_for_a_month(self):
        latest = pb.newest()
        self.assertIsNotNone(latest, "run scripts/price_band.py --write")
        data = json.loads(latest.read_text(encoding="utf-8"))
        self.assertTrue(data["band"])
        self.assertIn("rule", data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
