#!/usr/bin/env python3
"""Tests for the review-state reader (`scripts/review_state.py`).

These pin the rules the human and Desi settled in Telegram on 2026-10-07, because the whole point of
the sharper reading is that it maintains nothing new — it earns its keep only if the classification
is exactly the settled rule and nothing looser:

  * a postponement is P only if a reason is on disk, otherwise W;
  * an exemption is N only if the record says so, otherwise the item reads as V;
  * the day's movement is Δ(V−W) (drainage) against ΔW (backlog), and a zero Δ(V−W) with a growing
    ΔW is the unambiguous "broken" case.

The rule that matters most here is the narrowness of N: a self-granted exemption is how N becomes the
new dumping ground, so a stray "minor" or "clear" must NOT create one.
"""
import datetime as dt
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.review_state import (  # noqa: E402
    classify, deltas, render, snapshot, states_no_review,
)

NOW = dt.datetime(2026, 10, 7, 14, 0, 0, tzinfo=dt.timezone.utc)


def rec(rid, filed, amigo="desi", state=None, state_utc=None, reason=None, scope="internal"):
    return {"id": rid, "filed_utc": filed, "amigo": amigo, "scope": scope,
            "state": state, "state_utc": state_utc, "reason": reason}


def iso(days_ago=0, hours=0):
    return (NOW - dt.timedelta(days=days_ago, hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")


class TestClassification(unittest.TestCase):
    def test_an_accomplished_item_is_A(self):
        r = rec("a", iso(1), state="accomplished", state_utc=iso(1),
                reason="landed on main (lander's test gate passed)")
        self.assertEqual(classify(r), "A")

    def test_a_rejected_item_is_R(self):
        self.assertEqual(classify(rec("r", iso(1), state="rejected", state_utc=iso(1),
                                      reason="superseded")), "R")

    def test_a_postponement_with_a_reason_is_P(self):
        self.assertEqual(classify(rec("p", iso(1), state="postponed", state_utc=iso(1),
                                      reason="not now: no address to verify")), "P")

    def test_a_postponement_with_no_reason_is_W_not_P(self):
        # The rule, verbatim: no reason on disk -> W, however it was labelled.
        for bad in (None, "", "   "):
            self.assertEqual(classify(rec("w", iso(1), state="postponed", state_utc=iso(1),
                                          reason=bad)), "W")

    def test_an_unlooked_item_is_W(self):
        self.assertEqual(classify(rec("w", iso(1))), "W")

    def test_a_stated_exemption_is_N(self):
        for reason in ("no review needed", "No review was required — a typo fix",
                       "review not needed", "exempt from review"):
            self.assertEqual(classify(rec("n", iso(1), reason=reason)), "N", reason)

    def test_a_stray_word_does_not_create_an_exemption(self):
        # Narrow phrases only: these must all stay waiting, or N becomes the dumping ground.
        for reason in ("minor", "clear", "small change", "obvious fix", "reviewed by none"):
            self.assertFalse(states_no_review(rec("x", iso(1), reason=reason)), reason)
            self.assertEqual(classify(rec("x", iso(1), reason=reason)), "W", reason)

    def test_an_outcome_beats_a_later_exemption_claim(self):
        # An item that actually reached an outcome is A/P/W/R regardless of any prose.
        r = rec("a", iso(1), state="accomplished", state_utc=iso(1),
                reason="no review needed (landed on main)")
        self.assertEqual(classify(r), "A")


class TestTimeTravel(unittest.TestCase):
    def test_an_item_not_yet_filed_is_not_counted(self):
        self.assertIsNone(classify(rec("f", iso(hours=1)), at=NOW - dt.timedelta(hours=2)))

    def test_an_item_resolved_after_the_moment_reads_as_waiting_then(self):
        r = rec("a", iso(days=2), state="accomplished", state_utc=iso(hours=1))
        self.assertEqual(classify(r, at=NOW - dt.timedelta(hours=2)), "W")
        self.assertEqual(classify(r, at=NOW), "A")


class TestSnapshot(unittest.TestCase):
    def test_V_is_the_outcomes_and_N_sits_outside_them(self):
        items = {
            "a": rec("a", iso(1), state="accomplished", state_utc=iso(1), reason="landed"),
            "p": rec("p", iso(1), state="postponed", state_utc=iso(1), reason="not now"),
            "w": rec("w", iso(1)),
            "r": rec("r", iso(1), state="rejected", state_utc=iso(1), reason="no"),
            "n": rec("n", iso(1), reason="no review needed"),
        }
        s = snapshot(items, None)
        self.assertEqual((s["N"]["total"], s["A"]["total"], s["P"]["total"],
                          s["W"]["total"], s["R"]["total"]), (1, 1, 1, 1, 1))
        self.assertEqual(s["V"]["total"], 4)                     # A+P+W+R
        self.assertEqual(s["performed"], 5)                      # N+V
        # The human's equation holds as two ways to count the same performed set.
        self.assertEqual(s["N"]["total"] + s["V"]["total"],
                         s["A"]["total"] + s["P"]["total"] + s["W"]["total"] + s["R"]["total"])


class TestDeltas(unittest.TestCase):
    def test_a_stopped_drain_is_broken(self):
        # Three items filed inside the window, nothing ever resolved -> Δ(V−W)=0, ΔW>0.
        items = {f"i{i}": rec(f"i{i}", iso(hours=2)) for i in range(3)}
        d = deltas(items, 24, NOW)
        self.assertEqual(d["delta_v_minus_w"], 0)
        self.assertEqual(d["delta_w"], 3)
        self.assertIn("broken", d["diagnosis"])

    def test_a_healthy_drain_is_not_an_alarm(self):
        # Four old items, two resolved inside the window, none new -> Δ(V−W)>0, ΔW<=0.
        items = {
            "a": rec("a", iso(days=3), state="accomplished", state_utc=iso(hours=2), reason="landed"),
            "b": rec("b", iso(days=3), state="accomplished", state_utc=iso(hours=4), reason="landed"),
            "c": rec("c", iso(days=3)),
            "d": rec("d", iso(days=3)),
        }
        d = deltas(items, 24, NOW)
        self.assertEqual(d["delta_v_minus_w"], 2)
        self.assertEqual(d["delta_w"], -2)
        self.assertIn("healthy", d["diagnosis"])

    def test_draining_but_filling_faster_is_capacity_not_a_leak(self):
        items = {}
        for i in range(5):
            items[f"old{i}"] = rec(f"old{i}", iso(days=3))
        items["a"] = rec("a", iso(days=3), state="accomplished", state_utc=iso(hours=2), reason="landed")
        for i in range(5):
            items[f"new{i}"] = rec(f"new{i}", iso(hours=2))
        d = deltas(items, 24, NOW)
        self.assertEqual(d["delta_v_minus_w"], 1)
        self.assertGreater(d["delta_w"], 0)
        self.assertIn("capacity", d["diagnosis"])


class TestRender(unittest.TestCase):
    def test_the_six_letters_and_the_deltas_are_printed(self):
        out = render(24, NOW, items={"w": rec("w", iso(1)), "n": rec("n", iso(1),
                                                                    reason="no review needed")})
        for token in ("N=", "V=", "A=", "P=", "W=", "R=", "Δ(V−W)", "ΔW", "Drainage"):
            self.assertIn(token, out, token)
        self.assertIn("N=1", out)

    def test_the_equation_is_shown_and_reconciled(self):
        out = render(24, NOW, items={"a": rec("a", iso(1), state="accomplished",
                                              state_utc=iso(1), reason="landed")})
        self.assertIn("N+V", out)
        self.assertIn("A+P+W+R", out)


class TestRealLedgerConsistency(unittest.TestCase):
    """The reader against whatever is actually on disk: it must never crash, and the two ways of
    counting the performed set must agree."""

    def test_the_partition_holds_on_the_live_ledger(self):
        from channels.item_ledger import load
        items = load()
        s = snapshot(items, None)
        self.assertEqual(s["performed"], len(items))
        self.assertEqual(s["N"]["total"] + s["V"]["total"],
                         s["A"]["total"] + s["P"]["total"] + s["W"]["total"] + s["R"]["total"])
        self.assertEqual(s["V"]["total"],
                         s["A"]["total"] + s["P"]["total"] + s["W"]["total"] + s["R"]["total"])

    def test_the_cli_runs_and_emits_json(self):
        r = subprocess.run([sys.executable, str(REPO / "scripts" / "review_state.py"), "--json"],
                           capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertIn("deltas", data)
        self.assertIn("delta_v_minus_w", data["deltas"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
