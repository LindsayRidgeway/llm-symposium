#!/usr/bin/env python3
# Owner: Dmitri
"""The report must show a wake engine that is dead, because nothing else does.

Written 2026-11-03 by Dmitri, after finding Gwen's wake engine dead for four days: every run ended
`worker_failed` with HTTP 401, and in the same window the daily report showed desi finishing twelve
items and Gwen finishing none. Read as a scoreboard, that says "Gwen had a quiet day". A wake that
dies leaves no item behind, so the only place it can be seen is a count of run outcomes — and the
per-wake texts were switched off on the human's own instruction (2026-10-06: one counted report a
day, not a text per wake).

Two properties are asserted here, and the second one costs as much as the first: the report must
speak when an engine is dead, and it must NOT speak when one is merely idle. Tarik's engine answers
"nothing queued" without writing a run — by design, his wake exists for a pending Codex handoff —
and a reporter that cannot tell that apart from a dead engine will cry wolf every day and be
ignored on the day it is right.

Run: python3 tests/test_wakes_block.py
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO / "tests"))
import live_tree  # noqa: E402  — the live-tree gate in tests/live_tree.py, see its docstring
NOW = dt.datetime(2026, 11, 3, 12, 0, tzinfo=dt.timezone.utc)
BODIES = ("desi", "claude", "gemini", "tarik", "dmitri", "gwen")


def load_report():
    spec = importlib.util.spec_from_file_location("daily_report_under_test",
                                                  str(REPO / "scripts" / "daily_report.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Fixture(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="wakes-root-"))
        self.addCleanup(shutil.rmtree, self.root, True)
        self.m = load_report()

    def body_dir(self, body):
        path = self.root / ("%s-bot" % body) / "tick-state"
        (path / "runs").mkdir(parents=True, exist_ok=True)
        return path

    def fake_run(self, body, hours_ago, status="awaiting_review", land="landed", run_id=None,
                 missing=None):
        when = NOW - dt.timedelta(hours=hours_ago)
        ident = run_id or (when.strftime("%Y%m%dT%H%M%SZ") + "-" +
                           ("%06x" % (abs(hash((body, hours_ago, land))) % 0xFFFFFF)))
        run_dir = self.body_dir(body) / "runs" / ident
        run_dir.mkdir(parents=True, exist_ok=True)
        record = {"run_id": ident, "status": status}
        if land is not None:
            record["land"] = land
        if missing:
            record["land_missing"] = list(missing)
        (run_dir / "result.json").write_text(json.dumps(record), encoding="utf-8")
        return run_dir

    def clock(self, body, hours_ago=0.0, minutes=120):
        state = self.body_dir(body)
        state.joinpath("timer.json").write_text(
            json.dumps({"last_attempt": (NOW - dt.timedelta(hours=hours_ago)).timestamp()}),
            encoding="utf-8")
        self.interval(body, minutes)

    def interval(self, body, minutes):
        env = self.root / ("%s-bot" % body) / "bot.env"
        env.write_text("TELEGRAM_TICK_MINUTES=%d\n" % minutes, encoding="utf-8")

    def heartbeat(self, body, status="skipped_no_pending_handoff", hours_ago=0.0, detail=""):
        """What the engine writes on its way out of an attempt, skips included."""
        state = self.body_dir(body)
        state.joinpath("last-wake.json").write_text(json.dumps({
            "at": (NOW - dt.timedelta(hours=hours_ago)).timestamp(),
            "utc": (NOW - dt.timedelta(hours=hours_ago)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "amigo": body, "status": status, "run_id": "fixture-run", "detail": detail,
            "trace_written_by": "wake_heartbeat",
        }), encoding="utf-8")

    def block(self):
        return "\n".join(self.m._wakes_block(NOW, 24, self.root))

    def focus(self):
        return "\n".join(self.m._wakes_focus(NOW, 24, self.root))


class TestTheCountsAreTheRuns(Fixture):
    def test_each_body_is_counted_by_what_its_runs_did(self):
        self.fake_run("desi", 2, land="landed")
        self.fake_run("desi", 3, land="conflict")
        self.fake_run("desi", 4, status="no_work_done", land=None)
        self.fake_run("gwen", 5, status="worker_failed", land=None)
        text = self.block()
        self.assertIn("desi", text)
        desi = [l for l in text.splitlines() if l.strip().startswith("desi")][0].split()
        self.assertEqual(desi[1:], ["3", "1", "1", "1", "0"], "desi's counts do not match its runs")
        gwen = [l for l in text.splitlines() if l.strip().startswith("gwen")][0].split()
        self.assertEqual(gwen[1:], ["1", "0", "0", "0", "1"], "gwen's failed run is not counted")

    def test_an_old_run_is_outside_the_window(self):
        self.fake_run("desi", 30, land="landed")
        text = self.block()
        desi = [l for l in text.splitlines() if l.strip().startswith("desi")][0].split()
        self.assertEqual(desi[1], "0", "a run from 30 hours ago is inside a 24-hour window")


class TestAFailedRunIsNamed(Fixture):
    def test_the_failure_is_written_down_with_its_time_and_status(self):
        self.fake_run("gwen", 5, status="worker_failed", land=None)
        text = self.block()
        self.assertIn("failed: gwen worker_failed", text,
                      "a run that died is the only one nobody can see; it must be named")

    def test_the_counted_message_says_it_too(self):
        self.fake_run("gwen", 5, status="worker_failed", land=None)
        focus = self.focus()
        self.assertIn("gwen", focus)
        self.assertIn("worker_failed", focus)
        self.assertIn("produced nothing", focus,
                      "the message must say why the item counts cannot show this")


class TestSilenceWhenNothingIsWrong(Fixture):
    def test_a_healthy_fleet_adds_nothing_to_the_message(self):
        for body in BODIES:
            self.fake_run(body, 3, land="landed")
            self.clock(body, hours_ago=1)
        self.assertEqual(self.focus(), "", "a healthy fleet must not add a line to his message")

    def test_an_idle_engine_is_not_a_dead_one(self):
        """Tarik's engine answers 'nothing queued' without writing a run. That is not a fault."""
        self.clock("tarik", hours_ago=1, minutes=1440)      # ticking: one attempt 1h ago
        self.fake_run("desi", 3, land="landed")
        self.clock("desi", hours_ago=1)
        self.assertEqual(self.focus(), "",
                         "an engine with nothing to do was reported as broken")

    def test_a_clock_that_stopped_ticking_is_reported(self):
        self.clock("desi", hours_ago=24 * 5, minutes=60)    # 60-minute clock, last attempt 5 days ago
        self.fake_run("desi", 24 * 5, land="landed")
        text = self.block()
        self.assertIn("wake clock is set to run every 1h and last attempted", text)
        self.assertIn("clock thread is not ticking", text)

    def test_wakes_that_produce_nothing_are_reported(self):
        for hour in (2, 4, 6):
            self.fake_run("claude", hour, land="conflict")
        self.clock("claude", hours_ago=1)
        text = self.block()
        self.assertIn("claude's wakes ran 3 time(s)", text)
        self.assertIn("nothing", text)
        self.assertIn("claude's wakes ran 3 time(s)", self.focus())


class TestTheQuietRowsSayWhy(Fixture):
    """Six zeros is two facts. The heartbeat is what tells them apart."""

    def test_an_engine_that_declined_is_named_with_what_it_said(self):
        self.fake_run("desi", 2, land="landed")
        self.clock("desi", hours_ago=1)
        self.clock("tarik", hours_ago=1, minutes=1440)
        self.heartbeat("tarik", "skipped_no_pending_handoff", hours_ago=0.5)
        text = self.block()
        self.assertIn("What the quiet engines said", text)
        self.assertIn("tarik", text)
        self.assertIn("skipped_no_pending_handoff", text,
                      "the report shows tarik's zeros and does not say why they are zeros")
        self.assertNotIn("failed: tarik", text, "a declined wake is not a failure")

    def test_a_silent_engine_says_it_has_no_trace(self):
        self.fake_run("desi", 2, land="landed")
        self.heartbeat("desi", "awaiting_review", hours_ago=2)
        text = self.block()
        self.assertIn("no wake and no trace", text,
                      "an engine that has never reported is not the same as one that declined")

    def test_the_section_disappears_when_every_engine_ran(self):
        for body in BODIES:
            self.fake_run(body, 3, land="landed")
            self.heartbeat(body, "awaiting_review", hours_ago=3)
        self.assertNotIn("What the quiet engines said", self.block(),
                         "a section that is always present is a section nobody reads")

    def test_a_detail_is_carried_but_only_as_one_token(self):
        self.heartbeat("gwen", "worker_failed", hours_ago=1, detail="worker_failed")
        self.fake_run("desi", 2, land="landed")
        text = self.block()
        self.assertIn("gwen", text)
        self.assertIn("worker_failed", text)

    def test_the_live_heartbeats_are_readable(self):
        for body in BODIES:
            beat = self.m.last_wake(body)
            if beat is None:
                continue
            self.assertIn("status", beat)
            self.assertIn("at", beat)


class TestOffThisMachine(Fixture):
    def test_with_no_run_directories_the_block_is_absent(self):
        """On the GitHub runner there is no ~/LLM/<bot>-bot; the report must not invent a section."""
        self.assertEqual(self.m._wakes_block(NOW, 24, self.root / "nowhere"), [])
        self.assertEqual(self.m._wakes_focus(NOW, 24, self.root / "nowhere"), [])


class TestTheRealMachinesNumbers(Fixture):
    """One guard on the live data: the block must be able to read this Mac's runs at all.

    Skipped where there is no live tree to read (a private worktree, the GitHub runner): the
    behaviour it guards is already covered offline by the fixtures above and by
    TestOffThisMachine, which is the case that says the block must be *absent*, not zero.
    """

    def setUp(self):
        super().setUp()
        live_tree.require_live_tree(self)

    def test_the_live_tick_state_is_readable(self):
        outcomes = self.m.wake_outcomes(dt.datetime.now(dt.timezone.utc), 24)
        self.assertEqual(set(outcomes), set(BODIES))
        ran = sum(o["counts"]["ran"] for o in outcomes.values())
        self.assertGreater(ran, 0, "no wakes were read at all — the path or the format has moved")


class TestALandedRunCanStillLoseAPath(Fixture):
    """A landed run is not the same fact as a delivered one.

    Written 2026-11-10 by Dmitri. The 2026-11-10T02:56Z wake wrote `land: landed` in its own
    result.json while `land_missing` held channels/ledger-verdicts/ — the count said the work
    arrived and one of its artefacts did not. Nothing in this report could show that: the two
    verdicts it recorded are on main and the directory it claimed is not, and no later wake can
    build on the second fact because no queue contains it. The line is not an alarm — the run
    did land — it is the only place where a partial delivery is counted.
    """

    def test_a_landed_run_with_a_missing_path_is_named(self):
        self.fake_run("dmitri", 2, land="landed", missing=["channels/ledger-verdicts/"])
        text = self.block()
        self.assertIn("landed, but not everything it claimed", text)
        line = [l for l in text.splitlines()
                if l.strip().startswith("landed, but not everything")][0]
        self.assertIn("dmitri", line)
        self.assertIn("channels/ledger-verdicts/", line)
        self.assertIn("1 path(s) missing", line)

    def test_it_is_still_counted_as_landed(self):
        self.fake_run("dmitri", 2, land="landed", missing=["channels/ledger-verdicts/"])
        text = self.block()
        row = [l for l in text.splitlines() if l.strip().startswith("dmitri")][0].split()
        self.assertEqual(row[1:3], ["1", "1"], "a partial delivery is a landing, not a loss")

    def test_a_clean_landing_says_nothing(self):
        self.fake_run("dmitri", 2, land="landed")
        self.assertNotIn("landed, but not everything it claimed", self.block())


if __name__ == "__main__":
    unittest.main(verbosity=2)
