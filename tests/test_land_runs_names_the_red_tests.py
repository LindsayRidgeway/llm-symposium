#!/usr/bin/env python3
"""The landing gate names the tests that were already red (Desi, 2026-11-27).

Value item `red-tests-on-main`, filed by Dmitri's 07:51Z wake, recorded the complaint in the founder's
terms: the gate refuses with a *count* — "4 already failing on main before this diff" — and names none
of them, so a fifth, real failure hides among the four and every wake learns to read red as weather.
The names were in the set at the format string and thrown away.

Two landing paths carried that message (`_land_in_worktree` and the shared-tree path), so the claim is
pinned in two places: the helper's behaviour, executed against the lander as installed, and the fact
that both message sites use it. A helper nobody calls is how this defect started.

Run directly (`python3 tests/test_land_runs_names_the_red_tests.py`); the landing gate executes every
`tests/test_*.py`, so it holds at every landing. Skips, with its reason, where no lander is installed.
"""

import importlib.util
import unittest
from pathlib import Path

LANDER = Path.home() / "LLM" / "desi-bot" / "land_runs.py"


class TheRefusalNamesThem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not LANDER.is_file():
            raise unittest.SkipTest("no lander installed at %s" % LANDER)
        spec = importlib.util.spec_from_file_location("land_runs_named", LANDER)
        cls.lr = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.lr)
        if not hasattr(cls.lr, "_named"):
            raise unittest.SkipTest("the installed lander predates `_named`; the repair is not "
                                    "deployed to this machine")
        cls.text = LANDER.read_text(encoding="utf-8")

    def test_the_names_are_sorted_and_complete(self):
        got = self.lr._named({"test_b.py", "test_a.py"})
        self.assertEqual(got, "test_a.py, test_b.py")

    def test_an_empty_set_says_none_rather_than_printing_nothing(self):
        # A blank where a list should be reads as "the format string broke", not "main is clean".
        self.assertEqual(self.lr._named(set()), "none")

    def test_a_long_list_is_truncated_so_one_broken_machine_cannot_bloat_a_commit(self):
        got = self.lr._named({"test_%03d.py" % i for i in range(200)}, limit=60)
        self.assertLessEqual(len(got), 60)
        self.assertTrue(got.endswith("..."), got[-8:])

    def test_both_landing_paths_use_it(self):
        self.assertEqual(self.text.count("_named(before)"), 2,
                         "the count-only refusal is back on one of the two landing paths")

    def test_the_message_no_longer_ends_at_the_count(self):
        # The exact shape the item quoted: a count followed by a full stop and nothing else.
        self.assertNotIn("already failing on main before this diff). ", self.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
