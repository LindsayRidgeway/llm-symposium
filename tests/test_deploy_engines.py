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
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
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


class LiveDriftTests(unittest.TestCase):
    """The live tree, read-only: every deployed copy must already equal the commons."""

    def test_the_live_bot_directories_match_the_commons(self):
        llm = REPO.parent
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
