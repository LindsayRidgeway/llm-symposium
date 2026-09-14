#!/usr/bin/env python3
"""Offline retirement/idempotency checks; no credentials or model calls."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import preflight_autonomous_mission as m

MISSION = 'recipes/autonomous-goose/tarik-mission.md'
TARGET = 'discussions/2026-09-13-worker.md'
COMPLETION = 'discussions/2026-09-14-interactive.md'


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.put(MISSION, f'# Mission\n**Required artifact path:** `{TARGET}`\n- Minimum 900 words.\n')
        self.commit()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], text=True)

    def put(self, path, text):
        p = self.repo / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        return p

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture')

    def retire(self):
        with (self.repo / MISSION).open('a') as f:
            f.write(f'**State:** retired\n**Completion artifact:** `{COMPLETION}`\n')

    def test_legacy_active_mission_runs(self):
        self.assertTrue(m.decide(self.repo, MISSION)['run_worker'])

    def test_retired_mission_skips_repeatably(self):
        self.put(COMPLETION, '# Interactive review\n')
        self.retire()
        self.commit()
        first = m.decide(self.repo, MISSION)
        self.assertFalse(first['run_worker'])
        self.assertEqual(first['state'], 'retired')
        self.assertEqual(first, m.decide(self.repo, MISSION))
        self.assertFalse((self.repo / TARGET).exists())

    def test_retirement_needs_committed_completion(self):
        self.put(COMPLETION, '# Review\n')
        self.retire()
        with self.assertRaisesRegex(ValueError, 'committed'):
            m.decide(self.repo, MISSION)

    def test_retirement_needs_actual_completion(self):
        self.retire()
        with self.assertRaises(ValueError):
            m.decide(self.repo, MISSION)

    def test_existing_target_skips_without_claiming_acceptance(self):
        self.put(TARGET, '# Earlier output\n')
        self.commit()
        result = m.decide(self.repo, MISSION)
        self.assertFalse(result['run_worker'])
        self.assertEqual(result['state'], 'already_present')

    def test_untracked_target_is_error(self):
        self.put(TARGET, '# Local stray output\n')
        with self.assertRaises(ValueError):
            m.decide(self.repo, MISSION)

    def test_malformed_state_is_error(self):
        with (self.repo / MISSION).open('a') as f:
            f.write('**State:** finished\n')
        with self.assertRaises(ValueError):
            m.decide(self.repo, MISSION)

    def test_duplicate_state_is_error(self):
        with (self.repo / MISSION).open('a') as f:
            f.write('**State:** active\n**State:** retired\n')
        with self.assertRaises(ValueError):
            m.decide(self.repo, MISSION)

    def test_completion_symlink_is_error(self):
        p = self.repo / COMPLETION
        p.parent.mkdir()
        p.symlink_to(self.repo / MISSION)
        self.retire()
        self.commit()
        with self.assertRaisesRegex(ValueError, 'symlink'):
            m.decide(self.repo, MISSION)

    def test_cli_outputs_skip(self):
        self.put(COMPLETION, '# Review\n')
        self.retire()
        self.commit()
        out, report = self.root / 'outputs', self.root / 'report.json'
        process = subprocess.run([sys.executable, str(ROOT/'scripts/preflight_autonomous_mission.py'),
                                  '--repo', str(self.repo), '--mission', MISSION,
                                  '--report', str(report), '--github-output', str(out)],
                                 capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(out.read_text(), 'run_worker=false\nstate=retired\n')
        self.assertEqual(json.loads(report.read_text())['state'], 'retired')


if __name__ == '__main__':
    unittest.main(verbosity=2)
