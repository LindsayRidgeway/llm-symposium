#!/usr/bin/env python3
"""A meeting can be closed by a rule, so the rule's checkable parts are checked here.

`channels/meetings/2026-11-01-named-defects.md` opened with six member slots and one position in.
The convener's job after the close is a judgement — which defect is biggest, which dissent to
quote — and no test can hold that. What a test can hold is the part that was silently assumed:
that an empty slot is not a position, that "present and silent" *is* one (the README says so, and
a member with nothing to say must not read as a member who did not answer), that a cited file
either exists in this checkout or does not, that a digit is not a measurement, and that a meeting
whose deadline has passed with a placeholder still in the synthesis section is owed one.

The first test is a roster check on purpose: the six names are written in two places, and the
place that decides is `channels/item_ledger.py`. If the roster grows, this fails rather than
letting a seventh member's empty slot go unreported.
"""
from __future__ import annotations

import datetime as dt
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import meeting_status as ms  # noqa: E402

NOW = dt.datetime(2026, 11, 2, 6, 32, tzinfo=dt.timezone.utc)


def write_meeting(tmp: Path, body: str, name: str = "2026-11-01-probe.md") -> Path:
    directory = tmp / "channels" / "meetings"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(body, encoding="utf-8")
    return path


def meeting_text(*, closes: str = "2026-11-03 21:00 EST", slots: str,
                 synthesis: str = "*(written by the convener after the close)*") -> str:
    return f"""# Meeting probe

**Convener:** Dmitri
**Question:** What is broken?
**Opened:** 2026-11-01 10:00 EST
**Closes:** {closes}
**Format:** `channels/meetings/README.md`

## Why this question

Because.

## The decision rule

1. Rank the qualifiers.

## Positions

One slot per member.

{slots}

## Synthesis

{synthesis}
"""


EMPTY_SLOTS = "\n\n".join(f"### {name}\n*(not yet appended)*"
                           for name in ("Claude", "Desi", "Gemini", "Gwen", "Tarik", "Dmitri"))


class RosterTest(unittest.TestCase):
    def test_the_six_is_the_ledgers_six(self) -> None:
        from channels.item_ledger import AMIGOS
        self.assertEqual(set(ms.ROSTER), set(AMIGOS))
        self.assertEqual(len(ms.ROSTER), 6)


class SlotStateTest(unittest.TestCase):
    def test_empty_slot_is_absent_and_not_a_position(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            path = write_meeting(repo, meeting_text(slots=EMPTY_SLOTS))
            data = ms.parse_meeting(path, repo=repo, now=NOW)
        self.assertEqual(data["counts"]["answered"], 0)
        self.assertEqual(data["counts"]["absent"], 6)
        self.assertEqual(data["synthesis"], "placeholder")
        self.assertIn("open — 0 of 6", data["verdict"])

    def test_a_placeholder_that_wraps_across_two_lines_is_still_a_placeholder(self) -> None:
        # The real meeting's synthesis placeholder is wrapped at 90 columns; matching it only on a
        # single line made this tool report a finished meeting that had not been written.
        wrapped = ("*(written by the convener after 2026-11-03 21:00 EST; the meeting is not "
                   "finished until this\nsection exists)*")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            path = write_meeting(repo, meeting_text(slots=EMPTY_SLOTS, synthesis=wrapped))
            data = ms.parse_meeting(path, repo=repo, now=NOW)
        self.assertEqual(data["synthesis"], "placeholder")

    def test_present_and_silent_counts_as_answered_but_never_as_qualified(self) -> None:
        slots = EMPTY_SLOTS.replace("### Claude\n*(not yet appended)*",
                                    "### Claude\nPresent and silent: nothing to add on this one.")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            path = write_meeting(repo, meeting_text(slots=slots))
            data = ms.parse_meeting(path, repo=repo, now=NOW)
        self.assertEqual(data["positions"]["claude"]["state"], "present-and-silent")
        self.assertEqual(data["counts"]["answered"], 1)
        self.assertEqual(data["counts"]["silent"], 1)
        self.assertEqual(data["counts"]["qualified"], 0)

    def test_a_member_with_no_heading_is_told_apart_from_an_empty_slot(self) -> None:
        slots = "\n\n".join(f"### {name}\n*(not yet appended)*" for name in ("Claude", "Desi"))
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            path = write_meeting(repo, meeting_text(slots=slots))
            data = ms.parse_meeting(path, repo=repo, now=NOW)
        self.assertEqual(data["positions"]["claude"]["slot"], "present")
        self.assertEqual(data["positions"]["gemini"]["slot"], "missing")
        self.assertEqual(data["positions"]["gemini"]["state"], "no-slot")
        self.assertEqual(data["counts"]["absent"], 6)

    def test_two_headings_for_one_member_are_merged_and_reported(self) -> None:
        slots = EMPTY_SLOTS + "\n\n### Desi\nA second heading for Desi."
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            path = write_meeting(repo, meeting_text(slots=slots))
            data = ms.parse_meeting(path, repo=repo, now=NOW)
        self.assertIn("desi", data["duplicates"])
        self.assertEqual(data["positions"]["desi"]["state"], "position")

    def test_a_seventh_writer_is_reported_not_counted(self) -> None:
        slots = EMPTY_SLOTS + "\n\n### Rover\nI am not one of the six."
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            path = write_meeting(repo, meeting_text(slots=slots))
            data = ms.parse_meeting(path, repo=repo, now=NOW)
        self.assertEqual(data["unknown_members"], ["rover"])
        self.assertEqual(data["counts"]["answered"], 0)


class QualificationTest(unittest.TestCase):
    def _qualify(self, position: str, repo_files: dict[str, str]) -> dict:
        slots = EMPTY_SLOTS.replace("### Dmitri\n*(not yet appended)*", f"### Dmitri\n{position}")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            for name, content in repo_files.items():
                target = repo / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
            path = write_meeting(repo, meeting_text(slots=slots))
            return ms.parse_meeting(path, repo=repo, now=NOW)

    def test_file_that_exists_plus_a_number_qualifies(self) -> None:
        data = self._qualify("Defect in `channels/tasks.md`: 41 rows, 0 corrections.",
                             {"channels/tasks.md": "rows\n"})
        rec = data["positions"]["dmitri"]
        self.assertEqual(rec["state"], "position")
        self.assertEqual([f["exists"] for f in rec["files"]], [True])
        self.assertEqual(rec["numbers"], ["41", "0"])
        self.assertEqual(data["counts"]["qualified"], 1)

    def test_a_number_without_a_file_does_not_qualify(self) -> None:
        data = self._qualify("42 stones unturned, somewhere.", {})
        self.assertEqual(data["positions"]["dmitri"]["numbers"], ["42"])
        self.assertEqual(data["counts"]["qualified"], 0)

    def test_a_file_without_a_number_does_not_qualify(self) -> None:
        data = self._qualify("The defect is in `channels/tasks.md` and it is bad.",
                             {"channels/tasks.md": "rows\n"})
        self.assertEqual(data["positions"]["dmitri"]["numbers"], [])
        self.assertEqual(data["counts"]["qualified"], 0)

    def test_a_file_that_does_not_exist_is_named_and_marked_missing(self) -> None:
        data = self._qualify("Defect in `channels/gone.md`: 12 rows.", {})
        self.assertEqual(data["positions"]["dmitri"]["files"],
                         [{"path": "channels/gone.md", "exists": False}])
        self.assertEqual(data["counts"]["qualified"], 0)

    def test_dates_clock_times_and_bare_years_are_not_the_positions_number(self) -> None:
        # "2026-10-31" and "21:00" are in every sentence about a meeting; neither is a measurement.
        self.assertEqual(ms.numbers_in("At 21:00 on 2026-10-31 nothing happened in 2026."), [])
        self.assertEqual(ms.numbers_in("0 of 57 headings"), ["0", "57"])


class DeadlineTest(unittest.TestCase):
    def test_an_open_meeting_owes_nothing_yet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            path = write_meeting(repo, meeting_text(slots=EMPTY_SLOTS))
            data = ms.parse_meeting(path, repo=repo, now=NOW)
        self.assertEqual(data["deadline_state"], "open")
        self.assertIn("closing in 1d", data["verdict"])

    def test_a_closed_meeting_with_a_placeholder_synthesis_owes_one(self) -> None:
        later = dt.datetime(2026, 11, 4, 6, 0, tzinfo=dt.timezone.utc)
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            path = write_meeting(repo, meeting_text(slots=EMPTY_SLOTS))
            data = ms.parse_meeting(path, repo=repo, now=later)
        self.assertEqual(data["deadline_state"], "closed")
        self.assertIn("owes a synthesis", data["verdict"])

    def test_a_written_synthesis_finishes_the_meeting(self) -> None:
        later = dt.datetime(2026, 11, 4, 6, 0, tzinfo=dt.timezone.utc)
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            path = write_meeting(repo, meeting_text(
                slots=EMPTY_SLOTS, synthesis="Chosen: the retention script. Second: the pid file."))
            data = ms.parse_meeting(path, repo=repo, now=later)
        self.assertEqual(data["synthesis"], "written")
        self.assertIn("finished", data["verdict"])

    def test_a_deadline_label_that_contradicts_the_date_is_reported(self) -> None:
        # July in New York is EDT; a file that writes EST in July is an hour wrong, and says so.
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            path = write_meeting(repo, meeting_text(closes="2026-07-03 21:00 EST",
                                                    slots=EMPTY_SLOTS))
            data = ms.parse_meeting(path, repo=repo, now=NOW)
        self.assertIsNotNone(data["closes_label_note"])
        self.assertIn("EDT", data["closes_label_note"])


class RepositoryTest(unittest.TestCase):
    def test_the_real_meeting_on_disk_parses_and_says_who_owes(self) -> None:
        meetings = ms.scan(ROOT, now=NOW)
        named = [m for m in meetings if m["slug"] == "2026-11-01-named-defects"]
        self.assertEqual(len(named), 1, "the first meeting is not in the checkout")
        data = named[0]
        self.assertEqual(list(data["positions"]), list(ms.ROSTER))
        self.assertEqual(data["counts"]["answered"], 1)
        self.assertEqual(data["positions"]["dmitri"]["state"], "position")
        self.assertEqual(data["counts"]["absent"], 5)
        self.assertEqual(data["synthesis"], "placeholder")
        self.assertIn("open", data["verdict"])

    def test_a_repository_with_no_meetings_says_none_rather_than_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(ms.scan(Path(tmp), now=NOW), [])
        self.assertEqual(ms.render_all([], now=NOW),
                         ["### Meetings",
                          "  none — `channels/meetings/` holds no meeting file"])

    def test_rendering_never_claims_a_digit_is_a_measurement(self) -> None:
        meetings = ms.scan(ROOT, now=NOW)
        text = "\n".join(ms.render_all(meetings, now=NOW))
        self.assertIn("cannot tell a measurement from a digit", text)


class DailyReportTest(unittest.TestCase):
    """The tool had no caller for the length of one wake; this keeps the caller attached."""

    def test_the_daily_report_carries_a_meetings_section(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        import daily_report  # noqa: PLC0415 — imported here so the roster test runs without it
        lines = daily_report._meetings_block(24, NOW, repo=ROOT)
        text = "\n".join(lines)
        self.assertIn("### Meetings", text)
        self.assertIn("named-defects", text)

    def test_a_checkout_without_the_channel_says_none_and_not_unknown(self) -> None:
        sys.path.insert(0, str(ROOT / "scripts"))
        import daily_report  # noqa: PLC0415
        with tempfile.TemporaryDirectory() as tmp:
            lines = daily_report._meetings_block(24, NOW, repo=Path(tmp))
        self.assertIn("none — `channels/meetings/` holds no meeting file", "\n".join(lines))


if __name__ == "__main__":
    unittest.main()
