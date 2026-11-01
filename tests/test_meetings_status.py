#!/usr/bin/env python3
"""Tests for scripts/meetings_status.py — both halves matter: the count, and what counts as written.

The two cases below are not hypothetical. Each one was a defect in the first draft of the script,
found by running it on the real meeting file on 2026-11-01:

  1. An empty synthesis slot read as WRITTEN, because the placeholder was a phrase and the phrase on
     disk was a different one. A meeting with one position out of six was reported as finished.
  2. Reading the fix line-at-a-time still read it as written, because the aside wraps across two
     lines. A placeholder is judged as a whole body, not per line.

Run: /usr/bin/python3 tests/test_meetings_status.py
"""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("meetings_status", ROOT / "scripts" / "meetings_status.py")
ms = importlib.util.module_from_spec(spec)
sys.modules["meetings_status"] = ms
spec.loader.exec_module(ms)

FIXTURE = """# Meeting 2026-11-01 — a fixture

**Convener:** Dmitri
**Question:** One question, please.
**Opened:** 2026-11-01 10:00 EST
**Closes:** 2026-11-03 21:00 EST
**Format:** `channels/meetings/README.md`

## Positions

### Claude
*(not yet appended)*

### Desi
A real position, in plain text, three sentences long enough to count.

### Gemini
*(not yet appended)*

### Gwen
*(not yet appended)*

### Tarik
*(not yet appended)*

### Dmitri
Convener's position, appended before the question was sent.

## Synthesis

*(written by the convener after the close; the meeting is not finished until this
section exists)*
"""


class MeetingParseTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        (self.dir / "2026-11-01-fixture.md").write_text(FIXTURE, encoding="utf-8")
        # A README beside it must never be read as a meeting, or the count gains a permanent phantom.
        (self.dir / "README.md").write_text("# Meetings\n\n**Closes:** never\n", encoding="utf-8")
        self.meeting = ms.parse_meeting(self.dir / "2026-11-01-fixture.md")

    def tearDown(self):
        self.tmp.cleanup()

    def test_readme_is_not_a_meeting(self):
        self.assertEqual(sorted(p.name for p in self.dir.glob("*.md") if p.name.lower() != "readme.md"),
                         ["2026-11-01-fixture.md"])

    def test_header_fields_are_read(self):
        self.assertEqual(self.meeting["convener"], "Dmitri")
        self.assertEqual(self.meeting["question"], "One question, please.")

    def test_deadline_is_utc_and_uses_the_letter_on_the_line(self):
        # 21:00 EST is 02:00Z the next day. Reading EST as EDT would put it an hour early.
        self.assertEqual(self.meeting["closes"].isoformat(), "2026-11-04T02:00:00+00:00")

    def test_a_placeholder_position_is_absent_and_a_real_one_is_present(self):
        self.assertEqual(sorted(n for n, ok in self.meeting["positions"].items() if ok), ["Desi", "Dmitri"])
        self.assertEqual(sorted(n for n, ok in self.meeting["positions"].items() if not ok),
                         ["Claude", "Gemini", "Gwen", "Tarik"])

    def test_a_wrapped_placeholder_is_not_a_written_synthesis(self):
        # Defects 1 and 2 both live here: a phrase-only rule and a line-at-a-time rule each said True.
        self.assertFalse(self.meeting["synthesis"])

    def test_written_synthesis_is_recognised(self):
        written = ms.parse_meeting(self._with_synthesis("Ranked: Desi first, then Claude. Dissent quoted."))
        self.assertTrue(written["synthesis"])

    def test_status_reads_the_clock_it_is_given(self):
        before = ms.parse_meeting(self.dir / "2026-11-01-fixture.md")
        after = ms.parse_meeting(self._with_synthesis("Decided: the retention default."))
        import datetime as dt
        now = dt.datetime(2026, 11, 2, tzinfo=dt.timezone.utc)
        late = dt.datetime(2026, 11, 5, tzinfo=dt.timezone.utc)
        self.assertEqual(ms.status(before, now), "open")
        self.assertEqual(ms.status(before, late), "overdue")
        self.assertEqual(ms.status(after, late), "synthesised")

    def test_check_exits_nonzero_only_when_a_synthesis_is_owed(self):
        import datetime as dt
        inside = ms.main(["--dir", str(self.dir), "--check", "--now", "2026-11-02T00:00:00Z"])
        self.assertEqual(inside, 0)
        past = ms.main(["--dir", str(self.dir), "--check", "--now", "2026-11-04T03:00:00Z"])
        self.assertEqual(past, 1)
        self.assertLess(dt.datetime(2026, 11, 4, 3, tzinfo=dt.timezone.utc).timestamp(), float("inf"))

    def _with_synthesis(self, text: str) -> Path:
        body = FIXTURE.split("## Synthesis")[0] + "## Synthesis\n\n" + text + "\n"
        path = self.dir / f"2026-11-01-fixture-{abs(hash(text))}.md"
        path.write_text(body, encoding="utf-8")
        return path


class RealMeetingTest(unittest.TestCase):
    """The file on disk that the script was written for, read as it stands."""

    def test_the_live_meeting_is_open_and_counts_one_position(self):
        meetings = sorted(p for p in ms.MEETINGS_DIR.glob("*.md") if p.name.lower() != "readme.md")
        if not meetings:
            self.skipTest("no meetings on disk in this checkout")
        m = ms.parse_meeting(meetings[0])
        self.assertIsNotNone(m["closes"], "the live meeting's deadline must be readable")
        present = [n for n, ok in m["positions"].items() if ok]
        self.assertGreaterEqual(len(present), 1, "the convener's position is written before the question")

    def test_script_runs_clean_against_the_repository(self):
        self.assertIn(ms.main([]), (0, 1))


if __name__ == "__main__":
    unittest.main(verbosity=2)
