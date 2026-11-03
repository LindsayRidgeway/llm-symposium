#!/usr/bin/env python3
"""The admission checker runs nowhere; this is the smallest thing that stops it decaying.

Found 2026-11-02 (Desi) and decided 2026-11-03: `grep -rln tribe_admission_check` matched only the
checker itself — the same defect `test_auto_reply.py` had before 2026-10-09, a green check in a file
no runner opens. It cannot be wired into CI as a failing step, and that is arithmetic rather than
reluctance: `python3 scripts/tribe_admission_check.py` exits non-zero while any declared tribe fails
a clause, and five of six currently do, so a failing gate would be a permanent red for everyone and
would be switched off within a day — which is exactly how a check stops being a check.

So the floor is held instead of the ceiling. This test asserts the number of tribes that pass every
clause the checker can check here has not gone DOWN. Two pass today (Desi, Dmitri, both by written
declaration of provenance). When a third declaration lands, raise FLOOR and this file is the record
of when the commons stopped being able to lose a member silently. A record edited into failing
clause 3 an hour after it passed is the failure this pins.
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FLOOR = 2  # 2026-11-03: Desi and Dmitri. Raise this only upward.


def run_checker() -> tuple[int, dict]:
    out = subprocess.run([sys.executable, str(REPO / "scripts" / "tribe_admission_check.py"), "--json"],
                         capture_output=True, text=True, cwd=REPO, timeout=120)
    return out.returncode, json.loads(out.stdout)


class TribeAdmissionFloor(unittest.TestCase):
    def test_members_do_not_fall_below_the_recorded_floor(self):
        _rc, data = run_checker()
        tribes = data.get("tribes") or data
        passed = [t.get("name") for t in tribes if t.get("verdict") == "member"] \
            if isinstance(tribes, list) else [k for k, v in tribes.items() if v == "member"]
        self.assertGreaterEqual(len(passed), FLOOR,
                                f"{len(passed)} tribe(s) pass every checkpoint here, floor is {FLOOR}: "
                                f"{passed}. A declaration was removed or a record broke clause 3.")

    def test_the_checker_still_tells_the_failing_ones_apart(self):
        """A checker that called everyone a member would satisfy the floor vacuously."""
        rc, data = run_checker()
        tribes = data.get("tribes") or data
        names = ([t.get("name") for t in tribes] if isinstance(tribes, list) else list(tribes))
        self.assertGreaterEqual(len(names), 5, f"only {len(names)} tribe(s) declared: {names}")
        self.assertNotEqual(rc, 0, "the checker now exits 0, so five tribes pass — raise FLOOR, "
                                   "and only then consider a failing CI step")


if __name__ == "__main__":
    unittest.main(verbosity=2)
