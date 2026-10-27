#!/usr/bin/env python3
"""The one-off endometriosis screen must not overwrite the general instrument's artefact.

Found by the reading queue on 2026-10-24: `scripts/screen_endometriosis.py` writes
`research/endometriosis-screen.json`, and that path has held `scripts/disease_screen.py`'s payload
(229 rows, keys any_field/strict/open_targets_score/verdict) since 2026-09-19. Running the old
script would have replaced a cited artefact with 187 rows in an incompatible schema, with no error
— both files are JSON about the same condition, and both are named "endometriosis".

Written in `unittest`, like every other file in this directory, and runnable as a plain script
(`python3 tests/test_screen_endometriosis_clobber.py`): the landing gate executes each test file
with the interpreter that is on the machine and no test runner, so a `pytest`-style file fails at
import on a host without pytest even when every assertion in it would pass. That is exactly how
this file was first refused (2026-10-24T01:22Z), one wake after the guard it tests was written.
"""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "screen_endometriosis.py"


def _load():
    spec = importlib.util.spec_from_file_location("screen_endometriosis", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


se = _load()


class ScreenEndometriosisClobberTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, name, payload):
        path = self.tmp / name
        path.write_text(payload if isinstance(payload, str) else json.dumps(payload))
        return path

    def test_missing_output_is_writable(self):
        self.assertEqual(se._refuse_to_clobber(str(self.tmp / "nothing-here.json")), "")

    def test_general_instrument_payload_is_refused(self):
        target = self._write("screen.json",
                             {"disease": "endometriosis", "n_targets": 229, "targets": []})
        refusal = se._refuse_to_clobber(str(target))
        self.assertTrue(refusal.startswith("refusing to overwrite"), refusal)
        self.assertIn("disease_screen.py", refusal)
        self.assertIn("229", refusal,
                      "the refusal should say how many rows it is protecting")

    def test_own_payload_is_overwritten(self):
        target = self._write("screen.json",
                             {"condition": "endometriosis", "disease_papers_full_text": 1,
                              "targets": []})
        self.assertEqual(se._refuse_to_clobber(str(target)), "")

    def test_unparseable_existing_file_is_refused(self):
        target = self._write("screen.json", "not json{")
        refusal = se._refuse_to_clobber(str(target))
        self.assertTrue(refusal.startswith("refusing to overwrite"), refusal)
        self.assertIn("does not parse", refusal)

    def test_the_real_artefact_on_disk_is_protected(self):
        """The guard is only worth anything if it fires on the file the repository actually has."""
        real = ROOT / "research" / "endometriosis-screen.json"
        if not real.exists():
            self.skipTest("artefact not present in this checkout")
        refusal = se._refuse_to_clobber(str(real))
        self.assertTrue(refusal.startswith("refusing to overwrite"),
                        "running the one-off screen today would replace the general "
                        "screen's artefact")


if __name__ == "__main__":
    unittest.main(verbosity=2)
