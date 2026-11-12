#!/usr/bin/env python3
"""Run the recovered offline EPMC page guards in the Python verification suite."""
from pathlib import Path
import shutil
import subprocess
import unittest


class RetractionEpmcTest(unittest.TestCase):
    def test_actual_page_epmc_contract(self):
        node = shutil.which('node')
        if node is None:
            self.skipTest('Node is required for the offline EPMC page guard')
        root = Path(__file__).resolve().parent.parent
        result = subprocess.run([node, str(root / 'tests/test_retraction_epmc.mjs')],
                                cwd=root, text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        print(result.stdout.strip())


if __name__ == '__main__':
    unittest.main()
