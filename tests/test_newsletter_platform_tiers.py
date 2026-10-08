#!/usr/bin/env python3
"""The newsletter platform's tiers: the stored numbers must agree with the fetched page.

The 2026-10-07 question ("What does a Buttondown membership add?") had no answer on the record,
because no one had read the platform's own pricing page. On 2026-10-08 a wake read it
(`https://buttondown.com/pricing`) and stored the result in
`channels/outreach/newsletter-platform-tiers.json`, with the write-up in
`channels/outreach/newsletter-platform-tiers.md`.

This test is fully offline. It does three things the write-up claims and nothing else:

  * the normalised `plans` are the raw offers re-derived, not a second, hand-typed set — the
    subscriber cap in each normalised plan is parsed back out of the offer string the page printed,
    and a mismatch fails;
  * the tiers are internally sane (a higher price buys a strictly higher cap), so a typo that
    reorders them cannot pass;
  * the prose page agrees with the stored numbers and names its source and fetch date.

It deliberately does NOT try to re-fetch the page: a wake is not always on a network, and the point
of the JSON is that a later live fetch can be diffed against it by hand.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "channels" / "outreach" / "newsletter-platform-tiers.json"
PAGE = ROOT / "channels" / "outreach" / "newsletter-platform-tiers.md"
WORKFLOW = ROOT / ".github" / "workflows" / "test-and-report.yml"

CAP = re.compile(r"Up to (\d+) subscribers")


class NewsletterPlatformTiersTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text())
        cls.page = PAGE.read_text()

    def test_the_free_tier_is_100_subscribers_at_no_cost(self):
        free = self.data["free_tier"]
        self.assertEqual(free["subscriber_cap"], 100)
        self.assertEqual(free["price_usd_month"], 0)
        self.assertIn("100", free["page_copy"])

    def test_normalised_plans_are_re_derived_from_the_raw_offers(self):
        # The cap in each normalised plan must equal the cap printed in the raw offer string.
        # This is what stops the normalised list drifting from the page it came from.
        raw = {o["name"]: o for o in self.data["raw_offers"]}
        for plan in self.data["plans"]:
            offer = raw[plan["name"]]
            m = CAP.search(offer["description"])
            self.assertIsNotNone(m, f"raw offer for {plan['name']} prints no subscriber cap")
            self.assertEqual(
                int(m.group(1)), plan["subscriber_cap"],
                f"{plan['name']}: normalised cap {plan['subscriber_cap']} != page's {m.group(1)}")

    def test_price_and_cap_increase_together(self):
        paid = [p for p in self.data["plans"] if p["price_usd_month"] is not None]
        self.assertGreaterEqual(len(paid), 4)
        self.assertEqual(paid[0]["price_usd_month"], 0, "the first tier must be the free one")
        for lo, hi in zip(paid, paid[1:]):
            self.assertLess(lo["price_usd_month"], hi["price_usd_month"],
                            f"{lo['name']} is not cheaper than {hi['name']}")
            self.assertLess(lo["subscriber_cap"], hi["subscriber_cap"],
                            f"{lo['name']} does not hold fewer subscribers than {hi['name']}")

    def test_the_only_free_boundary_is_100(self):
        # Guard the specific number the human asked about; a silent edit to 1000 would pass
        # everything else.
        self.assertIn("100 subscribers", json.dumps(self.data))
        self.assertNotIn('"subscriber_cap": 1000, "price_usd_month": 0', json.dumps(self.data))

    def test_the_page_agrees_with_the_stored_numbers(self):
        for plan in self.data["plans"]:
            if plan["subscriber_cap"] is None:
                continue
            self.assertIn(f"{plan['subscriber_cap']:,}", self.page,
                          f"{plan['name']}'s cap is not shown on the page")
        for plan in self.data["plans"]:
            if plan["price_usd_month"] in (None, 0):
                continue
            self.assertIn(f"${plan['price_usd_month']}", self.page,
                          f"{plan['name']}'s price is not shown on the page")

    def test_the_page_names_its_source_and_date(self):
        self.assertIn("https://buttondown.com/pricing", self.page)
        self.assertIn("2026-10-08", self.page)

    def test_the_page_carries_the_api_on_free_correction(self):
        # The load-bearing correction: the API is already available on Free, so paying buys
        # capacity, not the automation. If this sentence goes, the record points the decision the
        # wrong way again.
        self.assertIn("already available on Free", self.page)

    def test_the_guard_itself_is_registered(self):
        self.assertIn("tests/test_newsletter_platform_tiers.py", WORKFLOW.read_text(),
                      "a guard outside the verification workflow protects nothing")


if __name__ == "__main__":
    unittest.main(verbosity=2)
