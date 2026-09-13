#!/usr/bin/env python3
"""Offline orchestrator integration tests with a fake worker, real checker and git."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("mission_runner", ROOT / "scripts/run_autonomous_mission.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
TARGET = "discussions/2026-09-13-test-critique.md"

FAKE = r'''
import json, sys, time
from pathlib import Path
args = sys.argv
mode = args[1]
state = Path('.git/fake-calls.json')
calls = json.loads(state.read_text()) if state.exists() else []
prompt = Path(args[args.index('--instructions') + 1]).read_text()
calls.append({'turns': int(args[args.index('--max-turns') + 1]), 'prompt': prompt})
state.write_text(json.dumps(calls))
if mode == 'timeout':
    time.sleep(10)
if mode == 'process-error':
    print('provider failed: insufficient_quota')
    sys.exit(1)
if mode == 'empty':
    sys.exit(0)
if mode == 'head-change':
    import subprocess
    subprocess.check_call(['git', 'commit', '--allow-empty', '-qm', 'bad worker commit'])
    sys.exit(0)
path = Path('discussions/2026-09-13-test-critique.md')
path.parent.mkdir(exist_ok=True)
words = 920 if mode == 'good' or (mode == 'repair' and len(calls) == 2) else 560
path.write_text('# Fixture\n**Author:** Tarik\n**Date:** 2026-09-13\n**Status:** Draft\n' + 'fixture ' * words + '\n')
if mode == 'quota-text':
    print('Rate limit exceeded: The usage limit has been reached.')
if mode == 'disallowed':
    Path('unexpected.txt').write_text('extra')
'''


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        (self.repo / 'README.md').write_text('# Fixture\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'base')
        self.base = self.git('rev-parse', 'HEAD').strip()
        self.instructions = self.root / 'instructions.md'
        self.instructions.write_text('Test mission; complete the file, not a promise.\n')
        self.mission = self.root / 'mission.md'
        self.mission.write_text(f'**Required artifact path:** `{TARGET}`\n- Minimum 900 words.\n')
        self.worker = self.root / 'fake-worker.py'
        self.worker.write_text(FAKE)
        self.artifacts = self.root / 'reports'

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], text=True)

    def execute(self, mode, timeout=10):
        return m.run(self.repo, self.instructions, self.mission,
                     ROOT / 'scripts/check_autonomous_mission.py', self.base,
                     self.artifacts, [sys.executable, str(self.worker), mode], timeout)

    def calls(self):
        return json.loads((self.repo / '.git/fake-calls.json').read_text())

    def test_first_pass_success_skips_repair(self):
        r = self.execute('good')
        self.assertTrue(r['ok'], r)
        self.assertEqual(len(self.calls()), 1)
        self.assertFalse((self.artifacts / 'repair-instructions.md').exists())

    def test_feedback_once_within_original_total_turn_budget(self):
        r = self.execute('repair')
        self.assertTrue(r['ok'], r)
        self.assertEqual([c['turns'] for c in self.calls()], [25, 15])
        self.assertIn('mission requires at least 900', self.calls()[1]['prompt'])
        first = json.loads((self.artifacts / 'attempt-1/mission-check.json').read_text())
        last = json.loads((self.artifacts / 'attempt-2/mission-check.json').read_text())
        self.assertFalse(first['ok'])
        self.assertTrue(last['ok'])
        self.assertNotEqual((self.artifacts / 'attempt-1/mission-original.md').read_text(),
                            (self.artifacts / 'attempt-2/mission-original.md').read_text())

    def test_repair_never_loops(self):
        r = self.execute('short')
        self.assertFalse(r['ok'])
        self.assertEqual(len(self.calls()), 2)
        self.assertFalse((self.artifacts / 'attempt-3').exists())

    def test_no_retry_for_provider_error(self):
        r = self.execute('process-error')
        self.assertFalse(r['ok'])
        self.assertEqual(len(self.calls()), 1)

    def test_quota_text_with_zero_exit_still_not_retried(self):
        r = self.execute('quota-text')
        self.assertFalse(r['ok'])
        self.assertEqual(len(self.calls()), 1)

    def test_no_retry_for_absent_artifact(self):
        r = self.execute('empty')
        self.assertFalse(r['ok'])
        self.assertEqual(len(self.calls()), 1)

    def test_no_retry_for_disallowed_diff(self):
        r = self.execute('disallowed')
        self.assertFalse(r['ok'])
        self.assertEqual(len(self.calls()), 1)

    def test_changed_head_fails_before_repair(self):
        r = self.execute('head-change')
        self.assertFalse(r['ok'])
        self.assertIn('changed HEAD', r['reason'])
        self.assertEqual(len(self.calls()), 1)

    def test_timeout_stops_worker_without_retry(self):
        r = self.execute('timeout', timeout=1)
        self.assertFalse(r['ok'])
        self.assertEqual(r['attempts'][0]['worker_exit'], 124)
        self.assertEqual(len(self.calls()), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
