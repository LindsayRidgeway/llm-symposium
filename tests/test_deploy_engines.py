#!/usr/bin/env python3
# Owner: Dmitri
"""The deploy step: the commons is the source, the six directories are copies, and one command
makes them equal.

Written 2026-11-03 with the wake-engine extraction. Extracting six files into one removes the six
implementations; it does not remove the six directories, and until something copies into them, every
change still needs a person at a keyboard six times. That is how the copies drifted.

These tests run against a fake `~/LLM`-shaped tree, never the live bot directories.

Run: python3 tests/test_deploy_engines.py
"""

from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO / "tests"))
import live_tree  # noqa: E402  — the live-tree gate in tests/live_tree.py, see its docstring
BODIES = ("desi", "dmitri", "claude", "gemini", "tarik", "gwen")


def load():
    spec = importlib.util.spec_from_file_location(
        "deploy_engines_under_test", str(REPO / "scripts" / "deploy_engines.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeployTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="deploy-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.commons = self.tmp / "llm-symposium"
        (self.commons / "channels").mkdir(parents=True)
        for name in ("wake_engine.py", "wake_heartbeat.py", "record.py", "record_push.py"):
            (self.commons / "channels" / name).write_text("# %s\n" % name, encoding="utf-8")
        for body in BODIES:
            (self.tmp / ("%s-bot" % body)).mkdir()
        self.m = load()
        self.said = []

    def deploy(self, **kwargs):
        return self.m.deploy(self.commons, self.tmp, out=self.said.append, **kwargs)

    def test_it_copies_every_shared_module_into_every_body(self):
        actions = self.deploy()
        for body in BODIES:
            for name in self.m.SHARED:
                copy = self.tmp / ("%s-bot" % body) / name
                self.assertTrue(copy.is_file(), "%s-bot did not get %s" % (body, name))
                self.assertEqual(copy.read_bytes(),
                                 (self.commons / "channels" / name).read_bytes(),
                                 "%s-bot/%s is not the commons copy" % (body, name))
        self.assertEqual(len(actions), len(BODIES) * len(self.m.SHARED))

    def test_a_second_run_changes_nothing(self):
        self.deploy()
        self.said.clear()
        actions = self.deploy()
        self.assertTrue(all(a[2] == "unchanged" for a in actions),
                        "a second deploy rewrote files that already matched")
        self.assertIn("already identical", " ".join(self.said))

    def test_it_reports_what_it_updated(self):
        (self.tmp / "claude-bot" / "wake_engine.py").write_text("old", encoding="utf-8")
        self.deploy()
        self.assertIn("claude", " ".join(self.said))
        self.assertIn("wake_engine.py", " ".join(self.said))
        self.assertIn("updated", " ".join(self.said), "an update was not reported as one")

    def test_a_dry_run_writes_nothing(self):
        self.deploy(dry_run=True)
        self.assertFalse((self.tmp / "desi-bot" / "wake_engine.py").exists(),
                         "a dry run wrote a file")

    def test_a_missing_bot_directory_is_an_error_not_a_skip(self):
        shutil.rmtree(self.tmp / "gemini-bot")
        with self.assertRaises(FileNotFoundError):
            self.deploy()
        self.assertFalse((self.tmp / "desi-bot" / "wake_engine.py").exists(),
                         "the deploy wrote some bodies before failing on a missing one")

    def test_a_missing_source_is_an_error(self):
        (self.commons / "channels" / "record.py").unlink()
        with self.assertRaises(FileNotFoundError):
            self.deploy()

    def test_the_shared_list_is_the_four_modules_the_engine_reads(self):
        self.assertEqual(self.m.SHARED,
                         ("wake_engine.py", "wake_heartbeat.py", "record.py", "record_push.py"))
        for name in self.m.SHARED:
            self.assertTrue((REPO / "channels" / name).is_file(),
                            "the commons has no channels/%s to deploy" % name)


class SchedulingTests(unittest.TestCase):
    """The same command, run by a timer: two things have to be true before it may act.

    A wake in flight must not be interrupted — a restart kills the worker mid-run and leaves a
    verdict with no lander, which is the defect `finish_unlanded` exists to clean up. And an engine
    that does not import must not be copied over six working copies: the point of a scheduled deploy
    is to remove the person, so the checks that person would have made have to be in the script.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="deploy-when-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.commons = self.tmp / "llm-symposium"
        (self.commons / "channels").mkdir(parents=True)
        for name in ("wake_engine.py", "wake_heartbeat.py", "record.py", "record_push.py"):
            (self.commons / "channels" / name).write_text("# %s\n" % name, encoding="utf-8")
        self.stub = "from pathlib import Path\nBODY = Path(__file__).resolve().parent.name\n"
        for body in BODIES:
            bot = self.tmp / ("%s-bot" % body)
            bot.mkdir()
            (bot / "local_tick.py").write_text(self.stub, encoding="utf-8")
        self.m = load()
        self.said = []

    def main(self, *argv):
        return self.m.main(list(argv), commons=self.commons, bots_root=self.tmp, commands="",
                           out=self.said.append, restart_runner=lambda body: self.said.append(
                               "restart %s" % body))

    def running(self, body, run_id="20261103T190000Z-aaaaaaaa", finished=False, age_minutes=0.0):
        run = self.tmp / ("%s-bot" % body) / "tick-state" / "runs" / run_id
        run.mkdir(parents=True)
        if finished:
            (run / "result.json").write_text("{}", encoding="utf-8")
        import os
        stamp = __import__("time").time() - age_minutes * 60
        os.utime(run, (stamp, stamp))
        return run

    def test_a_wake_in_flight_is_not_interrupted(self):
        self.running("desi")
        self.assertEqual(self.main("--when-idle", "--restart"), 0)
        self.assertIn("in flight", " ".join(self.said))
        self.assertFalse((self.tmp / "desi-bot" / "wake_engine.py").exists(),
                         "the deploy wrote files during a wake and then declined to restart")
        self.assertNotIn("restart desi", self.said)

    def test_a_finished_run_does_not_count_as_in_flight(self):
        self.running("desi", finished=True)
        self.assertEqual(self.main("--when-idle"), 0)
        self.assertTrue((self.tmp / "desi-bot" / "wake_engine.py").is_file(),
                        "a run that finished hours ago blocked the deploy")

    def test_an_abandoned_run_stops_counting_after_half_an_hour(self):
        self.running("gemini", age_minutes=45)
        self.assertEqual(self.main("--when-idle"), 0)
        self.assertTrue((self.tmp / "gemini-bot" / "wake_engine.py").is_file(),
                        "a run directory left behind by a kill blocked every future deploy")

    def test_an_engine_that_does_not_import_is_never_deployed(self):
        (self.commons / "channels" / "wake_engine.py").write_text("def broken(:\n", encoding="utf-8")
        self.assertEqual(self.main("--verify"), 1)
        self.assertIn("does not import", " ".join(self.said))
        self.assertFalse((self.tmp / "desi-bot" / "wake_engine.py").exists(),
                         "a syntax error was copied into six working directories")

    def test_a_stub_that_no_longer_imports_the_engine_is_never_deployed(self):
        (self.commons / "channels" / "wake_engine.py").write_text("CONFIG = 1\n", encoding="utf-8")
        (self.tmp / "gwen-bot" / "local_tick.py").write_text(
            "CORE = None\nCONFIG = CORE.Config(engine='standard', providers=('custom_alibaba',))\n",
            encoding="utf-8")
        self.assertEqual(self.main("--verify"), 1)
        self.assertIn("gwen", " ".join(self.said),
                      "a stub that calls a name the engine no longer has was deployed anyway")

    def test_it_restarts_only_when_it_wrote_something(self):
        self.assertEqual(self.main("--restart"), 0)
        self.assertIn("restart desi", self.said)
        self.said.clear()
        self.assertEqual(self.main("--restart"), 0)
        self.assertEqual([s for s in self.said if s.startswith("restart")], [],
                         "the timer restarted six bots to load files that had not changed")


class LiveDriftTests(unittest.TestCase):
    """The live tree, read-only: every deployed copy must already equal the commons.

    Skipped, with the reason printed, when none of the six bot directories is beside this
    checkout — a private worktree, or the GitHub runner. A tree that is here and missing one
    copy is not skipped: that is the drift this test exists to catch (tests/live_tree.py).
    """

    def test_the_live_bot_directories_match_the_commons(self):
        llm = live_tree.require_live_tree(self)
        for name in ("wake_engine.py", "wake_heartbeat.py", "record.py", "record_push.py"):
            wanted = (REPO / "channels" / name).read_bytes()
            for body in BODIES:
                copy = llm / ("%s-bot" % body) / name
                self.assertTrue(copy.is_file(), "%s-bot/%s is missing" % (body, name))
                self.assertEqual(copy.read_bytes(), wanted,
                                 "%s-bot/%s differs from the commons — run "
                                 "scripts/deploy_engines.py" % (body, name))


if __name__ == "__main__":
    unittest.main(verbosity=2)
