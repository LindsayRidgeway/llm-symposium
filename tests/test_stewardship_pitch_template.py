#!/usr/bin/env python3
"""Pin the stewardship pitch renderer (agenda item 22, Track 1).

Written 2026-10-01. The template `channels/outreach/stewardship-pitch-template.md`
and the 52-prospect ledger `channels/outreach/prospects.json` had both existed for
a fortnight, but nothing joined them: the letter had never been rendered for a
prospect and no institutional draft had ever been staged. These tests make the
join mechanical and pin the four properties that matter, each of which was a real
temptation to get wrong:

  * an address is never invented — the door is required and passed in;
  * authorship is never dropped — a pitch that hides its author fails to render;
  * the charter it cites exists on disk;
  * the tier paragraph matches the prospect's tier, so a preservation trust is
    not sent the foundation text.

The last test runs every real prospect against the real template, so the ledger
and the letter cannot drift apart without this file going red.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import render_stewardship_pitch as rsp  # noqa: E402


class TestTemplateParses(unittest.TestCase):
    def test_template_yields_body_subject_and_three_tiers(self):
        t = rsp._read_template(rsp.TEMPLATE_PATH.read_text())
        self.assertIn("Non-Interference Institutional Stewardship", t["subject"])
        self.assertEqual(set(t["tiers"]), {"A", "B", "C"})
        for letter, para in t["tiers"].items():
            self.assertTrue(para.strip(), f"tier {letter} paragraph is empty")
        # the raw command-line header lines are not part of the body
        self.assertNotIn("Identity:", t["body"])


class TestRender(unittest.TestCase):
    def setUp(self):
        self.t = rsp._read_template(rsp.TEMPLATE_PATH.read_text())
        self.prospect = {
            "id": "tier-a-99",
            "name": "The Example Preservation Trust",
            "tier": "Tier A",
            "contact_target": "The Archivist",
        }

    def test_fills_org_contact_and_tier_paragraph(self):
        d = rsp.render_draft(self.prospect, "via the form at example.org/contact", self.t)
        self.assertIn("The Example Preservation Trust", d)
        self.assertIn("The Archivist", d)
        self.assertIn("permanent digital preservation", d)  # the Tier A paragraph
        # and not the other tiers' text
        self.assertNotIn("multi-agent alignment", d)
        self.assertNotIn("un-owned software commons", d)

    def test_no_placeholder_survives(self):
        d = rsp.render_draft(self.prospect, "team@example.org", self.t)
        for ph in ("[ORGANIZATION_NAME]", "[CONTACT_NAME", "[TIER_SPECIFIC_PARAGRAPH]", "[CONTACT_EMAIL]"):
            self.assertNotIn(ph, d)

    def test_door_lands_verbatim_on_the_to_line(self):
        door = "via the form at longnow.org/contact (no address taken from memory)"
        d = rsp.render_draft(self.prospect, door, self.t)
        self.assertIn(f"To: {door}", d)

    def test_authorship_and_charter_are_not_dropped(self):
        d = rsp.render_draft(self.prospect, "team@example.org", self.t)
        low = d.lower()
        self.assertIn("artificial intelligence", low)
        self.assertIn("decline or disregard", low)  # the negative-sales permission to refuse
        self.assertIn("custodial-purpose-trust-charter-gemini.md", d)
        self.assertTrue(rsp.CHARTER_PATH.exists())

    def test_empty_door_is_refused(self):
        with self.assertRaises(ValueError):
            rsp.render_draft(self.prospect, "   ", self.t)

    def test_prospect_without_a_tier_is_refused(self):
        with self.assertRaises(ValueError):
            rsp.render_draft({"id": "x", "name": "X", "tier": "None"}, "a@b.c", self.t)

    def test_rendering_is_deterministic(self):
        a = rsp.render_draft(self.prospect, "team@example.org", self.t)
        b = rsp.render_draft(self.prospect, "team@example.org", self.t)
        self.assertEqual(a, b)

    def test_cli_requires_a_door(self):
        with self.assertRaises(SystemExit):
            rsp.main(["--prospect", "tier-a-99"])


class TestAgainstTheRealLedger(unittest.TestCase):
    """The real 52 prospects must render against the real template."""

    def test_every_prospect_renders_under_its_own_tier(self):
        data = json.loads(rsp.PROSPECTS_PATH.read_text())
        t = rsp._read_template(rsp.TEMPLATE_PATH.read_text())
        distinct = set()
        for p in data["prospects"]:
            d = rsp.render_draft(p, "read at send time", t)
            self.assertIn(p["name"], d)
            distinct.add(rsp._tier_letter(p))
        self.assertEqual(distinct, {"A", "B", "C"}, "ledger must carry all three tiers")

    def test_tier_paragraph_text_is_unique_per_tier(self):
        t = rsp._read_template(rsp.TEMPLATE_PATH.read_text())
        paras = list(t["tiers"].values())
        self.assertEqual(len(set(paras)), 3, "tier paragraphs must differ")


if __name__ == "__main__":
    unittest.main(verbosity=2)
