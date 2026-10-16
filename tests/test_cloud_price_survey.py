#!/usr/bin/env python3
"""Tests for `scripts/cloud_price_survey.py`. Offline — canned plan JSON, no network.

Why these exist. The document `research/2026-10-16-what-a-server-would-cost.md`
tells the founder a figure, and he should be able to trust it without reading a
vendor's API. Two things can quietly break that trust:

  1. the picker choosing the $0 promotional plan as "cheapest IPv4" (it ships no
     bandwidth and can be withdrawn), which would put a number in the report that
     is not a price he can actually buy; and
  2. the pinned table drifting away from reality with nobody noticing.

Both are pinned here. The network path is deliberately not tested: a test that
needs Vultr to be up fails for the wrong reason.
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import cloud_price_survey as cps  # noqa: E402

DOC = ROOT / "research" / "2026-10-16-what-a-server-would-cost.md"

# A trimmed slice of the real 2026-10-16 payload, so the test judges the same
# shapes the live API returns.
PLANS = [
    {"id": "vc2-1c-0.5gb-free", "vcpu_count": 1, "ram": 512, "disk": 10,
     "monthly_cost": 0, "bandwidth": 0, "locations": ["a", "b", "c"]},
    {"id": "vc2-1c-0.5gb-v6", "vcpu_count": 1, "ram": 512, "disk": 10,
     "monthly_cost": 2.5, "bandwidth": 512, "locations": ["a", "b"]},
    {"id": "vc2-1c-0.5gb", "vcpu_count": 1, "ram": 512, "disk": 10,
     "monthly_cost": 3.5, "bandwidth": 512, "locations": ["a"]},
    {"id": "vc2-1c-1gb", "vcpu_count": 1, "ram": 1024, "disk": 25,
     "monthly_cost": 5, "bandwidth": 1024, "locations": ["a"] * 31},
]


class SurveyTest(unittest.TestCase):
    def test_free_tier_is_not_the_cheapest_payable_plan(self):
        picks = cps.survey(PLANS)
        self.assertEqual(picks["cheapest_ipv4"]["id"], "vc2-1c-0.5gb")
        self.assertEqual(picks["cheapest_ipv4"]["monthly_cost"], 3.5)

    def test_free_tier_is_reported_separately(self):
        self.assertEqual(cps.survey(PLANS)["free_tier"]["id"], "vc2-1c-0.5gb-free")

    def test_ipv6_only_plan_is_not_chosen_as_ipv4(self):
        ids = {p["id"] for p in PLANS}
        self.assertIn("vc2-1c-0.5gb-v6", ids)
        self.assertNotEqual(cps.survey(PLANS)["cheapest_ipv4"]["id"], "vc2-1c-0.5gb-v6")

    def test_one_cpu_one_gig_is_found(self):
        self.assertEqual(cps.survey(PLANS)["one_c_one_gb"]["id"], "vc2-1c-1gb")

    def test_empty_list_returns_none_not_a_crash(self):
        picks = cps.survey([])
        self.assertIsNone(picks["cheapest_ipv4"])
        self.assertIsNone(picks["one_c_one_gb"])


class PinnedTableTest(unittest.TestCase):
    def test_table_has_the_sourced_rows(self):
        prices = {q[0] + ":" + q[1]: q[6] for q in cps.QUOTES}
        self.assertEqual(prices["Vultr:vc2-1c-1gb"], 5.00)
        self.assertEqual(prices["Vultr:vc2-1c-0.5gb"], 3.50)
        self.assertIn("AWS Lightsail:Linux 1 GB", prices)

    def test_every_quote_names_a_source(self):
        for q in cps.QUOTES:
            self.assertTrue(q[7].strip(), f"row {q[0]} {q[1]} has no source")

    def test_document_states_the_same_figure(self):
        # The doc is what he reads; it must not disagree with the table.
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("$5.00", text)
        self.assertIn("$3.50", text)
        self.assertIn(cps.FETCHED_ON, text)


if __name__ == "__main__":
    unittest.main()
