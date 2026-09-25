#!/usr/bin/env python3
"""Offline tests for the screen-rule audit: it must read the screens, not re-run them.

`scripts/screen_rule_audit.py` measures what the disease screen's two 2026-09-20 rules change,
from the JSON artefacts on disk and with no network. These tests pin the three facts the audit
exists to state, so a later edit cannot quietly turn it into a query tool or a flatterer:

  * the pudendal screen is below the density floor, so its "unjoined" band is refused;
  * every pudendal strict join is a token collision (both are three-character symbols);
  * the two earlier screens carry joins with no document behind them, so they predate rule 2.
"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/screen_rule_audit.py"
spec = importlib.util.spec_from_file_location("screen_rule_audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

SCREENS = ROOT / "research"


def _by_name():
    return {a["file"]: a for a in audit.audit_files(sorted(SCREENS.glob("*-screen.json")))}


class AuditTests(unittest.TestCase):
    def test_runs_without_network(self):
        # audit_one must not call epmc/strict/epmc_hits; those live in disease_screen and are
        # only used here for their constants. Blow up if anything tries to reach out.
        for name in ("epmc", "strict", "epmc_hits", "any_field", "trials"):
            if hasattr(audit.ds, name):
                setattr(audit.ds, name,
                        lambda *a, **k: (_ for _ in ()).throw(AssertionError("network in audit")))
        rows = _by_name()
        self.assertIn("pudendal-neuralgia-screen.json", rows)

    def test_pudendal_is_below_the_floor(self):
        a = _by_name()["pudendal-neuralgia-screen.json"]
        self.assertTrue(a["below_floor"])
        self.assertLess(a["strict_papers"], audit.FLOOR_STRICT)

    def test_every_pudendal_join_is_flagged_ambiguous(self):
        a = _by_name()["pudendal-neuralgia-screen.json"]
        self.assertEqual(a["joined"], 2)
        self.assertEqual(a["ambiguous_joins"], a["joined"])
        self.assertEqual(a["joined_if_collisions_refused"], 0)

    def test_earlier_screens_predate_rule_two(self):
        rows = _by_name()
        endo = rows["endometriosis-screen.json"]
        self.assertFalse(endo["rule2_adopted"])
        self.assertGreater(endo["joined"], 0)
        self.assertEqual(endo["joined_without_document"], endo["joined"])

    def test_dense_screens_are_above_the_floor(self):
        rows = _by_name()
        for f in ("endometriosis-screen.json", "me-cfs-screen.json"):
            self.assertFalse(rows[f]["below_floor"], f)


if __name__ == "__main__":
    unittest.main()
