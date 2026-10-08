#!/usr/bin/env python3
"""Tests for the review-state classifier (P/W/N/V, and Δ(V−W)/ΔW).

What is pinned here is the rule the human set on 2026-10-07 and the arithmetic that closes it: an
item reads as P only if its reason is already on disk, as N only if it says why no review was
needed; the identity N+V = A+P+W+R = performed must hold or the report is lying. The classifier is
meant to read what is already there and add nothing, so the tests build their own ledger records
rather than touching the real one, and one end-to-end test reads the real ledger only to check the
invariants still hold on real material.
"""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.review_state import (  # noqa: E402
    LEDGER, classify, diagnostic, drained, render, tally, _flagged_pairs,
)


def rec(**kw):
    base = {"id": "x", "amigo": "desi", "scope": "internal", "state": None, "reason": None,
            "filed_utc": "2026-10-01T00:00:00Z", "state_utc": None}
    base.update(kw)
    return base


class TestClassify(unittest.TestCase):
    def test_accomplished_is_A(self):
        self.assertEqual(classify(rec(state="accomplished", reason="landed on main")), "A")

    def test_rejected_is_R(self):
        self.assertEqual(classify(rec(state="rejected", reason="off-topic")), "R")

    def test_postponed_with_a_written_reason_is_P(self):
        self.assertEqual(classify(rec(state="postponed", reason="needs library access")), "P")

    def test_postponed_without_a_reason_is_W(self):
        # The human's rule: the state field alone does not make it P — the reason on disk does.
        self.assertEqual(classify(rec(state="postponed", reason=None)), "W")
        self.assertEqual(classify(rec(state="postponed", reason="   ")), "W")

    def test_unreviewed_is_W(self):
        self.assertEqual(classify(rec(state=None)), "W")


class TestTally(unittest.TestCase):
    def setUp(self):
        self.items = {
            "a": rec(id="a", state="accomplished", reason="landed on main (lander gate)"),
            "b": rec(id="b", state="rejected", reason="duplicate"),
            "c": rec(id="c", state="postponed", reason="blocked on the human"),
            "d": rec(id="d", state=None),
            "e": rec(id="e", state=None, reason="no review needed: a docs typo"),
        }

    def test_the_identity_holds(self):
        t = tally(self.items)
        self.assertEqual(t["N"] + t["V"], t["A"] + t["P"] + t["W"] + t["R"])
        self.assertEqual(t["N"] + t["V"], t["performed"])

    def test_the_groups(self):
        t = tally(self.items)
        self.assertEqual((t["performed"], t["N"], t["V"]), (5, 1, 4))
        self.assertEqual((t["A"], t["P"], t["W"], t["R"]), (1, 1, 2, 1))

    def test_a_review_free_item_reads_as_N(self):
        t = tally(self.items)
        self.assertEqual(t["N"], 1)

    def test_drained_is_V_minus_W(self):
        t = tally(self.items)
        # V=4, W=2 -> 2 items needed review and are no longer waiting (A and P, minus nothing).
        self.assertEqual(drained(t), 2)

    def test_by_amigo_sums_match_the_totals(self):
        t = tally(self.items)
        for key in ("N", "V", "A", "P", "W", "R"):
            self.assertEqual(sum(s[key] for s in t["by_amigo"].values()), t[key], key)


class TestAsOfReconstruction(unittest.TestCase):
    """No snapshot file: 'yesterday' is rebuilt from the record's own timestamps."""

    def test_an_item_accomplished_after_the_cutoff_was_still_waiting_at_the_cutoff(self):
        cutoff = datetime(2026, 10, 5, tzinfo=timezone.utc)
        items = {"x": rec(id="x", filed_utc="2026-10-01T00:00:00Z",
                          state="accomplished", state_utc="2026-10-06T00:00:00Z",
                          reason="landed on main")}
        now, then = tally(items), tally(items, cutoff)
        self.assertEqual((now["A"], now["W"]), (1, 0))
        self.assertEqual((then["A"], then["W"]), (0, 1))

    def test_an_item_filed_after_the_cutoff_is_not_counted_at_the_cutoff(self):
        cutoff = datetime(2026, 10, 5, tzinfo=timezone.utc)
        items = {"x": rec(id="x", filed_utc="2026-10-06T00:00:00Z")}
        self.assertEqual(tally(items, cutoff)["performed"], 0)
        self.assertEqual(tally(items)["performed"], 1)


class TestDiagnostic(unittest.TestCase):
    def test_nothing_drained_while_the_backlog_grew_is_broken(self):
        self.assertIn("BROKEN", diagnostic(0, 5))

    def test_both_positive_is_capacity_not_brokenness(self):
        d = diagnostic(3, 5)
        self.assertIn("capacity", d)
        self.assertNotIn("BROKEN", d)

    def test_draining_with_no_inflow_is_healthy(self):
        self.assertEqual(diagnostic(3, 0), "draining")

    def test_a_negative_delta_is_called_out(self):
        self.assertIn("NEGATIVE", diagnostic(-1, 0))

    def test_quiet_when_nothing_moves(self):
        self.assertIn("quiet", diagnostic(0, 0))


class TestNEqualsPFlag(unittest.TestCase):
    def test_zero_equals_zero_is_not_flagged(self):
        # An empty equality says nothing; the guard is the point.
        t = {"N": 0, "P": 0, "by_amigo": {"desi": {"N": 0, "P": 0}}}
        self.assertEqual(_flagged_pairs(t), [])

    def test_a_real_global_equality_is_flagged(self):
        t = {"N": 4, "P": 4, "by_amigo": {}}
        self.assertTrue(any("globally" in s for s in _flagged_pairs(t)))

    def test_a_per_amigo_equality_is_flagged(self):
        t = {"N": 0, "P": 0, "by_amigo": {"gemini": {"N": 3, "P": 3}}}
        self.assertTrue(any("gemini" in s for s in _flagged_pairs(t)))


class TestRender(unittest.TestCase):
    def test_render_shows_the_identity_check(self):
        items = {"a": rec(id="a", state="accomplished", reason="landed on main"),
                 "b": rec(id="b")}
        now = tally(items)
        text = render(now, tally(items), 24, datetime(2026, 10, 8, tzinfo=timezone.utc))
        self.assertIn("check:", text)
        self.assertIn("N+V = 2", text)
        self.assertIn("diagnostic:", text)


class TestAgainstTheRealLedger(unittest.TestCase):
    def test_the_invariants_hold_on_real_material(self):
        from channels.item_ledger import load
        if not LEDGER.exists():
            self.skipTest("no ledger to read")
        t = tally(load(LEDGER))
        self.assertEqual(t["N"] + t["V"], t["performed"])
        self.assertEqual(t["A"] + t["P"] + t["W"] + t["R"], t["performed"])
        self.assertGreater(t["performed"], 0)
        for key in ("N", "V", "A", "P", "W", "R"):
            self.assertEqual(sum(s[key] for s in t["by_amigo"].values()), t[key], key)


if __name__ == "__main__":
    unittest.main(verbosity=2)
