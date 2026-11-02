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

    def test_the_note_states_an_age_not_a_currency_claim(self):
        """A generated sentence about the present goes false as the file ages; an age does not.

        The October band was written on 2026-10-09 saying "prices are current" and still said it
        on 2026-10-27, when its own `as_of` (2026-08-25) made it 63 days old. The note now records
        the age at write time, which stays true when read later.
        """
        band = pb.build(prices({"desi": 0.01}, as_of="2026-10-01"), dt.date(2026, 10, 9))
        self.assertIn("8 days old", band["note"])
        self.assertIn("2026-10-01", band["note"])
        self.assertNotIn("current", band["note"])

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


class TestTheUnratedAreCarriedNotDropped(unittest.TestCase):
    """An amigo the file has no rate for must come out of the band named, not vanished.

    The defect this covers (found 2026-11-02 while reading Gwen's 2026-10-30 run): `build()` read
    only `rates_usd_per_million` and silently discarded `unrated`, so every written band was
    indistinguishable between "expensive, so outside the band" and "nobody has ever measured this
    amigo". Gwen was invited on 2026-10-29 and is in the second category; the band could not say
    so, `--show` did not print her at all, and the draw that the band feeds therefore had a
    blind spot with no record of having one.
    """

    def priced(self, rates, unrated=None, as_of="2026-08-25"):
        data = prices(rates, as_of=as_of)
        if unrated is not None:
            data["unrated"] = unrated
        return data

    def test_an_unmeasured_amigo_is_named_in_the_band_and_is_not_in_it(self):
        band = pb.build(self.priced({"desi": 0.01, "dmitri": 0.01},
                                    {"gwen": {"why": "no measured blended rate yet"}}),
                        dt.date(2026, 11, 2))
        self.assertEqual(band["band"], ["desi", "dmitri"])
        self.assertIn("gwen", band["unrated"])
        self.assertIn("no measured blended rate", band["unrated"]["gwen"])
        self.assertNotIn("gwen", band["rates_usd_per_million"])

    def test_no_guess_is_made_for_an_unmeasured_amigo(self):
        """The file's basis is measured cost. An unmeasured amigo gets a name, never a number."""
        band = pb.build(self.priced({"desi": 0.01}, {"gwen": {"why": "unmeasured"}}),
                        dt.date(2026, 11, 2))
        self.assertNotIn("gwen", band["rates_usd_per_million"])
        self.assertEqual(band["unrated"], {"gwen": "unmeasured"})

    def test_expensive_and_unmeasured_are_different_states(self):
        band = pb.build(self.priced({"desi": 0.01, "tarik": 1.86},
                                    {"gwen": {"why": "unmeasured"}}), dt.date(2026, 11, 2))
        self.assertNotIn("tarik", band["band"])       # priced, outside the band
        self.assertNotIn("tarik", band["unrated"])
        self.assertIn("gwen", band["unrated"])        # unpriced, in no band at all
        self.assertNotIn("gwen", band["rates_usd_per_million"])

    def test_a_file_with_nothing_unrated_gets_an_empty_map_not_a_missing_key(self):
        band = pb.build(prices({"desi": 0.01}), dt.date(2026, 11, 2))
        self.assertEqual(band["unrated"], {})

    def test_an_unmeasured_name_that_someone_later_priced_is_not_listed_twice(self):
        """A stale `unrated` entry beside a real rate must lose to the rate, not confuse the reader."""
        data = prices({"desi": 0.01})
        data["unrated"] = {"desi": {"why": "priced on 2026-10-30"}}
        band = pb.build(data, dt.date(2026, 11, 2))
        self.assertEqual(band["unrated"], {})
        self.assertIn("desi", band["rates_usd_per_million"])

    def test_the_written_file_carries_the_unrated_block(self):
        with tempfile.TemporaryDirectory() as td:
            usage = Path(td)
            data = prices({"desi": 0.01})
            data["unrated"] = {"gwen": {"why": "no measured blended rate yet"}}
            (usage / "model-prices.json").write_text(json.dumps(data), encoding="utf-8")
            out = pb.write(usage, dt.date(2026, 11, 2))
            written = json.loads(out.read_text(encoding="utf-8"))
            self.assertIn("gwen", written["unrated"])
            self.assertNotIn("gwen", written["rates_usd_per_million"])


class TestTheShippedBandNamesItsBlindSpot(unittest.TestCase):
    """The band on disk must still say who it cannot name — the regression guard."""

    def test_the_shipped_band_carries_the_unrated_map(self):
        latest = pb.newest()
        data = json.loads(latest.read_text(encoding="utf-8"))
        self.assertIn("unrated", data,
                      "regenerate with scripts/price_band.py --write: the band predates the "
                      "unrated block and reads as a complete roster of five")

    def test_every_shipped_amigo_is_either_priced_or_named_unrated(self):
        data = pb.load_prices()
        latest = json.loads(pb.newest().read_text(encoding="utf-8"))
        priced = set(data["rates_usd_per_million"])
        known = priced | set(data.get("unrated") or {})
        self.assertEqual(known - priced, set(latest["unrated"]) - priced,
                         "an amigo in the price file is in neither the rates nor the band's "
                         "unrated map, so the band cannot say where she went")


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
