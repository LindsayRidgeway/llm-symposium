#!/usr/bin/env python3
"""The cadence measurement must count wakes, not columns, and must not flatter a dead one.

Written 2026-10-25 with `scripts/wake_cadence.py`, after the table it checks was found wrong twice
in one week and both times by a person noticing rather than by anything running.

Four defects are pinned here, and each one is a mistake the first draft actually made or would
have made:

1. **An append-only ledger multiplies wakes.** `channels/items.jsonl` carries one row per state
   change, so the id `codex-20261016T200444Z-14786fb8` appears six times. Counting rows would say
   Tarik woke six times in that minute. Counting *ids* is the only honest count, and the real
   ledger is asserted here to agree.

2. **A file in the runs directory is not a run.** `~/LLM/desi-bot/tick-state/runs/report.txt`
   exists — a report written one level too high — and a scan that counted every child would score
   it as a wake. Only directories carrying a timestamped id count.

3. **The run tree is not the roster.** On 2026-10-23 the Tarik app filed five times in a day while
   `tarik-bot`'s newest run directory was already four days cold. A measurement from runs alone
   would have called that body dead while it was working; a measurement from the ledger alone would
   have called Tarik-goose alive on the app's rows. The union is asserted to be a union.

4. **Zero is not "no evidence".** An amigo with no rows at all and an amigo measured at zero wakes
   per day are different statements, and only one of them is a table error. `None` and `0.0` are
   kept apart because collapsing them lets a silent participant print as a quiet one.

Offline and deterministic: every fixture is a temp directory and every clock is passed in. The two
tests that read the real tree are marked with what they read.
"""
import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import wake_cadence as wc  # noqa: E402

NOW = dt.datetime(2026, 10, 25, 11, 25, 40, tzinfo=dt.timezone.utc)


class ParseStamp(unittest.TestCase):
    def test_compact_id_form(self):
        self.assertEqual(wc.parse_stamp("20261025T112540Z-afa56ed9"), NOW)

    def test_iso_form(self):
        self.assertEqual(wc.parse_stamp("2026-10-25T11:25:40Z"), NOW)

    def test_iso_with_offset_is_not_double_shifted(self):
        self.assertEqual(wc.parse_stamp("2026-10-25T11:25:40+00:00"), NOW)

    def test_garbage_is_none_not_an_exception(self):
        for junk in ("", None, "no timestamp here", "20261345T996699Z-x", "2026-10-25T99:99:99Z"):
            self.assertIsNone(wc.parse_stamp(junk), junk)


class ScanRuns(unittest.TestCase):
    def test_only_timestamped_directories_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            runs = Path(tmp) / "desi-bot" / "tick-state" / "runs"
            (runs / "20261025T012445Z-80ad5e8f").mkdir(parents=True)
            (runs / "20261024T232445Z-aaaaaaaa").mkdir()
            (runs / "report.txt").write_text("a report written one level too high")
            (runs / "scratch").mkdir()
            got = wc.scan_runs(Path(tmp))["desi"]
            self.assertEqual([t.strftime("%Y-%m-%dT%H:%M:%SZ") for t in sorted(got)],
                             ["2026-10-24T23:24:45Z", "2026-10-25T01:24:45Z"])

    def test_a_missing_tree_is_empty_not_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            got = wc.scan_runs(Path(tmp))
            self.assertEqual(sorted(got), sorted(wc.AMIGOS))
            self.assertEqual(sum(len(v) for v in got.values()), 0)


class ScanLedger(unittest.TestCase):
    def fixture(self, rows):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        p = Path(tmp.name) / "items.jsonl"
        p.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        return p

    def test_one_id_counts_once_however_many_states_it_went_through(self):
        # The real shape: the same id appended six times as its state moved.
        rows = [{"id": "codex-20261016T200444Z-14786fb8", "amigo": "tarik", "state": s}
                for s in (None, "accomplished", None, None, "accomplished", "accomplished")]
        got = wc.scan_ledger(self.fixture(rows))["tarik"]
        self.assertEqual(len(got), 1)

    def test_amigo_is_read_from_the_row_not_guessed_from_the_prefix(self):
        rows = [{"id": "codex-20261021T195929Z-ca4d8ba5", "amigo": "tarik"},
                {"id": "20261025T012445Z-80ad5e8f", "amigo": "desi"}]
        got = wc.scan_ledger(self.fixture(rows))
        self.assertEqual(len(got["tarik"]), 1)
        self.assertEqual(len(got["desi"]), 1)
        self.assertEqual(len(got["gemini"]), 0)

    def test_a_row_with_no_usable_timestamp_is_dropped_not_stamped_now(self):
        got = wc.scan_ledger(self.fixture([{"id": "no-stamp-here", "amigo": "desi"}]))
        self.assertEqual(got["desi"], [])

    def test_unreadable_lines_do_not_stop_the_scan(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        p = Path(tmp.name) / "items.jsonl"
        p.write_text('{"id": "20261025T012445Z-80ad5e8f", "amigo": "desi"}\nnot json\n',
                     encoding="utf-8")
        self.assertEqual(len(wc.scan_ledger(p)["desi"]), 1)


class Union(unittest.TestCase):
    def test_an_app_filing_survives_a_cold_run_tree(self):
        """The 2026-10-23 case: ledger alive, run tree four days cold, and it was working."""
        with tempfile.TemporaryDirectory() as tmp:
            runs = Path(tmp) / "tarik-bot" / "tick-state" / "runs"
            (runs / "20261019T170221Z-c56a22e8").mkdir(parents=True)
            ledger = Path(tmp) / "items.jsonl"
            ledger.write_text(json.dumps({"id": "codex-20261023T200050Z-61cf96dc",
                                          "amigo": "tarik"}) + "\n", encoding="utf-8")
            events = {a: wc.scan_runs(Path(tmp)).get(a, []) + wc.scan_ledger(ledger).get(a, [])
                      for a in wc.AMIGOS}
            measured = wc.cadence(events, NOW, 7)["tarik"]
            self.assertEqual(measured["wakes_in_window"], 2)
            self.assertEqual(measured["last_utc"], "2026-10-23T20:00:50Z")
            self.assertAlmostEqual(measured["hours_since"], 39.4, places=1)


class Cadence(unittest.TestCase):
    def test_window_normalisation_does_not_flatter_a_stopped_body(self):
        # Three wakes, all in the first ten minutes of a seven-day window.
        start = NOW - dt.timedelta(days=7) + dt.timedelta(minutes=5)
        events = {"tarik": [start, start + dt.timedelta(minutes=1), start + dt.timedelta(minutes=2)]}
        m = wc.cadence(events, NOW, 7)["tarik"]
        self.assertAlmostEqual(m["wakes_per_day"], 3 / 7, places=3)

    def test_out_of_window_wakes_do_not_count_but_still_date_the_last_one(self):
        old = NOW - dt.timedelta(days=30)
        m = wc.cadence({"claude": [old]}, NOW, 7)["claude"]
        self.assertEqual(m["wakes_in_window"], 0)
        self.assertEqual(m["last_utc"], old.strftime("%Y-%m-%dT%H:%M:%SZ"))

    def test_no_evidence_is_none_not_zero(self):
        m = wc.cadence({}, NOW, 7)["gemini"]
        self.assertIsNone(m["hours_since"])
        self.assertIsNone(m["last_utc"])
        self.assertEqual(m["wakes_per_day"], 0.0)


class CheckTable(unittest.TestCase):
    TABLE = {"desi": 12, "dmitri": 12, "gemini": 6, "claude": 1, "tarik": 3}

    def measured(self, **over):
        base = {a: {"wakes_in_window": self.TABLE[a] * 7, "wakes_per_day": float(self.TABLE[a]),
                    "last_utc": "2026-10-25T09:00:00Z", "hours_since": 2.4} for a in wc.AMIGOS}
        for k, v in over.items():
            base[k] = dict(base[k], **v)
        return base

    def test_a_matching_table_is_silent(self):
        self.assertEqual(wc.check_table(self.measured(), self.TABLE, NOW), [])

    def test_silence_past_the_threshold_is_reported_with_the_last_sighting(self):
        w = wc.check_table(self.measured(tarik={"hours_since": 39.4,
                                                "last_utc": "2026-10-23T20:00:50Z"}),
                           self.TABLE, NOW)
        self.assertEqual(len(w), 1)
        self.assertIn("2026-10-23T20:00:50Z", w[0])
        self.assertIn("39.4h", w[0])

    def test_silence_inside_the_threshold_is_not(self):
        self.assertEqual(wc.check_table(self.measured(claude={"hours_since": 18.3}), self.TABLE,
                                        NOW), [])

    def test_no_evidence_at_all_reads_differently_from_silence(self):
        w = wc.check_table(self.measured(dmitri={"hours_since": None, "last_utc": None,
                                                 "wakes_in_window": 0, "wakes_per_day": 0.0}),
                           self.TABLE, NOW)
        self.assertEqual(len(w), 1)
        self.assertIn("no evidence of any wake", w[0])
        self.assertNotIn("past", w[0])

    def test_a_weight_that_is_out_by_half_is_reported(self):
        w = wc.check_table(self.measured(gemini={"wakes_in_window": 7, "wakes_per_day": 1.0}),
                           self.TABLE, NOW)
        self.assertEqual(len(w), 1)
        self.assertIn("table says 6", w[0])
        self.assertIn("measured 1.0", w[0])

    def test_a_weight_within_tolerance_is_not_nagged_about(self):
        # claude is 1/day and the window will not divide evenly; 1.1 must not raise.
        self.assertEqual(wc.check_table(self.measured(claude={"wakes_per_day": 1.1}), self.TABLE,
                                        NOW), [])

    def test_weights_line_reproduces_the_shape_the_draw_expects(self):
        line = wc.weights_line(self.measured())
        self.assertTrue(line.startswith("WAKES_PER_DAY = {"))
        self.assertIn('"tarik": 3', line)
        self.assertIn('"claude": 1', line)

    def test_weights_line_never_emits_zero_even_for_a_body_with_no_evidence(self):
        """A zero weight is a division by nothing waiting to happen; the silent case is a report."""
        measured = self.measured(tarik={"wakes_in_window": 0, "wakes_per_day": 0.0,
                                        "hours_since": None, "last_utc": None})
        self.assertIn('"tarik": 1', wc.weights_line(measured))


class TheRealFiles(unittest.TestCase):
    """Two assertions against the repository's own data, because fixtures cannot drift."""

    LEDGER = ROOT / "channels" / "items.jsonl"

    def test_the_real_ledger_yields_no_duplicate_ids_per_amigo(self):
        got = wc.scan_ledger(self.LEDGER)
        for amigo, stamps in got.items():
            self.assertEqual(len(stamps), len(set(stamps)), f"{amigo} counted an id twice")

    def test_every_amigo_has_some_evidence_in_the_real_ledger(self):
        """If this fails, one of the five has never filed anything and the roster is wrong."""
        got = wc.scan_ledger(self.LEDGER)
        for amigo in wc.AMIGOS:
            self.assertTrue(got[amigo], f"{amigo} has no timestamped row in channels/items.jsonl")

    def test_the_live_table_is_readable_and_covers_all_five(self):
        table, why = wc.table_from_item_ledger()
        self.assertEqual(why, "")
        self.assertEqual(sorted(table), sorted(wc.AMIGOS))


class Registration(unittest.TestCase):
    def test_the_script_is_reachable_from_the_index(self):
        """gen_index.py builds scripts/README.md from the tree; a script it cannot reach is a
        file nobody will find, which is the defect that created gen_index.py in the first place."""
        index = (ROOT / "scripts" / "README.md").read_text(encoding="utf-8")
        self.assertIn("wake_cadence.py", index)


if __name__ == "__main__":
    unittest.main(verbosity=2)


class Obligations(unittest.TestCase):
    """What a body returns, not how often it wakes — added 2026-10-28.

    The table in `item_ledger.py` scales drawn names by wakes per day. Measured over the ledger's
    whole history, claude wakes once a day and has never returned a verdict; gemini wakes 5.9 times
    a day and reads at a fifth of dmitri's rate. A weight built from heartbeats cannot see either
    fact, so the debt those names carry was invisible. These tests pin the counting rules that
    make it visible, and the three ways a naive count gets it wrong.
    """

    def fixture(self, rows):
        d = tempfile.mkdtemp()
        p = Path(d) / "items.jsonl"
        p.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        return p

    def test_a_verdict_counts_once_per_item_not_once_per_row(self):
        # An append-only ledger copies the record on every state change, so the same verdict can
        # appear in four rows. Counting rows would inflate a reader's capacity by the number of
        # times the item was copied (measured on the real file: 141 rows against 119 items).
        rows = [
            {"id": "20261024T000000Z-aaaaaaaa", "amigo": "dmitri", "state": None},
            {"id": "20261024T000000Z-aaaaaaaa", "amigo": "dmitri", "state": "accomplished",
             "reviewer": "desi", "state_utc": "2026-10-24T01:00:00Z"},
            {"id": "20261024T000000Z-aaaaaaaa", "amigo": "dmitri", "state": "accomplished",
             "reviewer": "desi", "state_utc": "2026-10-24T01:00:00Z", "assigned_to": "dmitri"},
        ]
        got = wc.obligations(self.fixture(rows), NOW)
        self.assertEqual(got["desi"]["verdicts_lifetime"], 1)
        self.assertEqual(got["desi"]["verdicts_in_window"], 1)

    def test_a_machine_closure_is_not_a_verdict_and_is_counted_as_debt(self):
        # `auto:path` closes an item because its files exist. That is delivery, not a read, and the
        # debt it leaves is the never-read pile — counted against the name the reading carries.
        rows = [
            {"id": "20261024T000000Z-bbbbbbbb", "amigo": "gemini", "state": "accomplished",
             "reviewer": "auto:path", "state_utc": "2026-10-24T01:00:00Z",
             "reading_assigned_to": "gemini"},
            {"id": "20261024T000000Z-cccccccc", "amigo": "desi", "state": None,
             "assigned_to": "claude"},
        ]
        got = wc.obligations(self.fixture(rows), NOW)
        self.assertEqual(got["gemini"]["verdicts_lifetime"], 0)
        self.assertEqual(got["gemini"]["unread"], 1)
        self.assertEqual(got["gemini"]["total"], 1)
        self.assertEqual(got["claude"]["waiting"], 1)

    def test_a_machine_postponement_is_debt_and_is_not_hidden_in_either_pile(self):
        # It is a closure with no reader behind it. It is not waiting (it has a state) and not
        # "accomplished, unread" (it is postponed), so a counter that knew only those two piles
        # would drop it — the fifth state the commons' rule forbids.
        rows = [{"id": "20261024T000000Z-dddddddd", "amigo": "claude", "state": "postponed",
                 "reviewer": "auto:path", "state_utc": "2026-10-24T01:00:00Z",
                 "assigned_to": "dmitri"}]
        got = wc.obligations(self.fixture(rows), NOW)
        self.assertEqual(got["dmitri"]["machine_postponed"], 1)
        self.assertEqual(got["dmitri"]["total"], 1)

    def test_debt_on_a_body_that_never_returns_a_verdict_is_named(self):
        rows = [{"id": "20261024T000000Z-eeeeeeee", "amigo": "desi", "state": None,
                 "assigned_to": "claude"},
                {"id": "20261024T000000Z-ffffffff", "amigo": "desi", "state": "accomplished",
                 "reviewer": "desi", "state_utc": "2026-10-24T01:00:00Z"}]
        warnings = wc.check_obligations(wc.obligations(self.fixture(rows), NOW))
        self.assertEqual(len(warnings), 1)
        self.assertIn("claude", warnings[0])
        self.assertIn("never returned a verdict", warnings[0])

    def test_a_body_carrying_nothing_is_not_nagged_about(self):
        rows = [{"id": "20261024T000000Z-gggggggg", "amigo": "desi", "state": "accomplished",
                 "reviewer": "desi", "state_utc": "2026-10-24T01:00:00Z"}]
        self.assertEqual(wc.check_obligations(wc.obligations(self.fixture(rows), NOW)), [])

    def test_a_body_that_read_this_fortnight_but_not_this_week_is_reported_as_such(self):
        # Different sentence, because "stopped this week" and "has never read" call for different
        # responses: one is a bad week, the other is a name on nothing.
        rows = [{"id": "20261001T000000Z-hhhhhhhh", "amigo": "desi", "state": "accomplished",
                 "reviewer": "gemini", "state_utc": "2026-10-01T01:00:00Z"},
                {"id": "20261024T000000Z-iiiiiiii", "amigo": "desi", "state": None,
                 "assigned_to": "gemini"}]
        warnings = wc.check_obligations(wc.obligations(self.fixture(rows), NOW))
        self.assertEqual(len(warnings), 1)
        self.assertIn("no verdict in the window", warnings[0])

    def test_an_unnamed_never_read_item_is_counted_rather_than_dropped(self):
        # The blind spot a census inherits if it only counts named debt: an unread item with no
        # name is in no queue at all, and `--holes` covers waiting items only.
        rows = [{"id": "20261024T000000Z-jjjjjjjj", "amigo": "desi", "state": "accomplished",
                 "reviewer": "auto:path", "state_utc": "2026-10-24T01:00:00Z"}]
        got = wc.obligations(self.fixture(rows), NOW)
        self.assertEqual(got["_unnamed_unread"], 1)
        warnings = wc.check_obligations(got)
        self.assertTrue(any("no name at all" in w for w in warnings), warnings)
