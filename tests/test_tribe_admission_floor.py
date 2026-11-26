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
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FLOOR = 5  # 2026-11-18: Claude, Desi, Gemini, Dmitri, Gwen. Raise this only upward.
# Was 2 (2026-11-03: Desi and Dmitri) and this file's own docstring said "when a third
# declaration lands, raise FLOOR". Three landed and nobody raised it, so for fifteen days
# the guard would have let five members' provenance disappear two at a time and stayed green.
# Measured on 2026-11-18: `python3 scripts/tribe_admission_check.py` -> 5 of 6 pass every
# clause a checkout can check; the holdout is Tarik (clauses 1 and 3), not a failure of the
# five. Raise to 6 the day his two lines land.


def run_checker() -> tuple[int, dict]:
    out = subprocess.run([sys.executable, str(REPO / "scripts" / "tribe_admission_check.py"), "--json"],
                         capture_output=True, text=True, cwd=REPO, timeout=120)
    return out.returncode, json.loads(out.stdout)


AGENDA = REPO / "agenda" / "35-the-admission-rule.md"
NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7}


def five_minute_count_mismatch(text: str) -> str | None:
    """Return a description of the miscount, or None if the rule counts its own test correctly.

    The item adopted itself by silence on 2026-11-08, so its arithmetic is unopposed by default:
    on 2026-11-26 it listed four outside checks and then required "All three". Nothing caught it
    for eighteen days, and nothing would have caught the reverse — a fifth check added without
    raising the requirement. This is that catch, on the sentence a stranger is told to run.
    """
    try:
        start = text.index("it is checkable from outside")
    except ValueError:
        return "the five-minute test's own sentences are gone from the agenda item"
    lines = text[start:].splitlines()
    block = []
    for line in lines:
        block.append(line)
        if re.match(r"^\w+ checks\.", line):
            break
    block_text = "\n".join(block)
    bullets = [line for line in block if line.startswith("- ")]
    claim = re.search(r"All (\w+), or it is not a tribe yet", block_text)
    headline = re.search(r"^(\w+) checks\.", block_text, re.MULTILINE)
    if claim is None or headline is None:
        return "the 'All <n>' / '<N> checks.' sentences are gone from the agenda item"
    words = (claim.group(1).lower(), headline.group(1).lower())
    for word in words:
        if word not in NUMBER_WORDS:
            return f"'{word}' is not a number this guard can count"
    required = {NUMBER_WORDS[word] for word in words}
    if required != {len(bullets)}:
        return (f"the rule lists {len(bullets)} outside check(s) and requires "
                f"{'/'.join(sorted(str(n) for n in required))}")
    return None


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

    def test_the_rule_counts_its_own_five_minute_test_correctly(self):
        """Four checks and 'All three' is not a rounding error, it is a weaker rule."""
        mismatch = five_minute_count_mismatch(AGENDA.read_text(encoding="utf-8"))
        self.assertIsNone(mismatch, f"agenda/35 miscounts its own test: {mismatch}")

    def test_that_guard_goes_red_on_the_defect_it_was_written_for(self):
        """The defect was live on main for eighteen days: four bullets, 'All three'.

        A guard that has only ever been run against the repaired file proves nothing, so the
        mutation is made here, against the real text, and both directions are checked.
        """
        real = AGENDA.read_text(encoding="utf-8")
        self.assertIsNone(five_minute_count_mismatch(real))
        softened = real.replace("All four, or it is not a tribe yet",
                                "All three, or it is not a tribe yet", 1)
        self.assertNotEqual(softened, real, "the sentence this guard pins is gone; fix the guard")
        softened_gap = five_minute_count_mismatch(softened)
        self.assertIsNotNone(softened_gap, "the original defect ('All three' beside four checks) is green")
        self.assertTrue("3" in softened_gap and "4" in softened_gap, softened_gap)
        extra = real.replace("- Read the first line of its record.",
                             "- Read the first line of its record.\n"
                             "- Ask a steward to confirm it by mail.", 1)
        self.assertIsNotNone(five_minute_count_mismatch(extra),
                             "a fifth check added without raising the requirement stayed green")


if __name__ == "__main__":
    unittest.main(verbosity=2)
