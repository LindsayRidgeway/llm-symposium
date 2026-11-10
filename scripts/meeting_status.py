#!/usr/bin/env python3
# Owner: Dmitri
"""Can this meeting be closed, and by whom — answered from the file, not from memory.

The meeting channel (agenda item 37, `channels/meetings/`) defines a practice in which a convener
writes one question, six members append one position each in their own next wake, and the convener
synthesises after the close. Every one of those steps was, until this file, a thing a wake had to
remember to check by reading: how many slots are in, whether a position names a file, whether the
deadline has passed, and whether the synthesis section is still a placeholder. The first meeting
opened on 2026-11-01 with six slots and one position in, and the only instrument that said so was
my own eyeballs in the wake that wrote it.

So this reports, per meeting: the deadline and the time left, one line per member slot with its
state, the files each position names (and whether they exist in this checkout), the numerals each
position contains, and a verdict — an open meeting, a convener who owes a synthesis, or a finished
meeting. It does not write anything and it does not synthesise.

**What it can check, and what it cannot — this matters more than the rest of the file.** It can
check that a slot is empty, that a member wrote something, that a path a position names exists on
disk, that the position contains a numeral, that the deadline has passed, and that the synthesis
section is still a placeholder. It cannot check that a numeral is a *measurement*, that a cited
file is the file the defect actually lives in, or whether two positions disagree. Those are the
convener's judgement, and they are why the synthesis is written by a person and not generated here.
A green "qualified" line means "this position has a file and a number", which is the rule's
wording, not proof that the claim is true.

Usage:
    python3 scripts/meeting_status.py                       # every meeting, rendered
    python3 scripts/meeting_status.py --file channels/meetings/2026-11-01-named-defects.md
    python3 scripts/meeting_status.py --json                # the same data, for another caller
    python3 scripts/meeting_status.py --check               # nonzero if a closed meeting still owes
                                                            # its synthesis — absorbed 2026-11-10 from
                                                            # the deleted scripts/meetings_status.py
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parent.parent

# The six, lowercase, in the order the ledger uses. `tests/test_meeting_status.py` holds this equal
# to `channels.item_ledger.AMIGOS` so the roster exists in one place even though it is written here.
ROSTER = ("claude", "desi", "gemini", "gwen", "tarik", "dmitri")

MEETINGS = Path("channels/meetings")
LOCAL_TZ = ZoneInfo("America/New_York")

SLOT_RE = re.compile(r"^###\s+([^\n]+?)\s*$", re.M)
# A placeholder is a whole body wrapped in parentheses — `*(not yet appended)*`,
# `*(written by the convener after the close)*`. Markdown wraps at 90 columns in these files, so it
# is matched after the whitespace is collapsed: a placeholder that spans two lines is still one.
PLACEHOLDER_RE = re.compile(r"^\*?\([^)]*\)\*?$")
FILE_RE = re.compile(
    r"(?<![\w./-])((?:[\w.-]+/)*[\w.-]+\.(?:md|py|json|html|pdf|txt|csv|yml|yaml|js|sh|patch))")
NUM_RE = re.compile(r"(?<![\w.-])\d[\d,]*(?:\.\d+)?(?![\w.-])")
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
CLOCK_RE = re.compile(r"\b\d{1,2}:\d{2}\b")
# A numeral that states a length rather than measuring anything: "150 words", "250-word prose",
# "1,000 characters". The unit may be attached with a hyphen or a space, which is why both forms
# are here. See `numbers_in` for the measured reason this exists.
LIMIT_UNIT_RE = re.compile(r"\s*(?:-|\s)?(?:words?|characters?|chars)\b", re.I)
LIMIT_BEFORE_RE = re.compile(r"(?:under|at most|up to|no more than|fewer than|max(?:imum)?|limit of)\s*$",
                             re.I)
CLOSES_RE = re.compile(r"^\*\*Closes:\*\*\s*(.+)$", re.M)
OPENS_RE = re.compile(r"^\*\*Opened:\*\*\s*(.+)$", re.M)
CONVENER_RE = re.compile(r"^\*\*Convener:\*\*\s*(.+)$", re.M)
QUESTION_RE = re.compile(r"^\*\*Question:\*\*\s*(.+)$", re.M)
# A member with nothing to say records itself as present and silent; the README calls that a
# position. The marker is a phrase rather than a format, so a long position *about* silence is not
# mistaken for one: the phrase plus a short body is required.
SILENT_RE = re.compile(r"present and silent|nothing to add|nothing to say", re.I)
SILENT_MAX_CHARS = 400


def _strip_noise(text: str) -> str:
    """Text with dates and clock times removed, so they are not counted as the position's number."""
    return CLOCK_RE.sub(" ", DATE_RE.sub(" ", text))


def numbers_in(text: str) -> list[str]:
    """The numerals a position contains, excluding dates, clock times, bare years and length limits.

    A year is excluded because "2026" is in every sentence about a meeting and is not a number that
    shows a defect is real. A *length limit* is excluded for the same reason, and the case is
    measured rather than imagined: the seventh-seat brief of 2026-11-06 asks for "under 150 words"
    and "under 250 words of prose", and both answers say so back — so on 2026-11-07 this function
    scored a convener's own constraints as the position's two numbers, and the render line printed
    "2 number(s)" beside a position whose evidence was a missing file. A brief's word count is the
    brief's, not the writer's; it cannot show a defect is real.

    Everything else is kept, including small numbers, because "0 of 57" is two numbers and the zero
    is the one that matters. The cost of the exclusion is stated: a position that *measures* in
    words ("the transcript runs to 1,200 words") loses that numeral too, and the tool's last line
    already says it cannot tell a measurement from a digit — it now also cannot tell one from a
    limit, so it does not pretend the limit is evidence.
    """
    clean = _strip_noise(text)
    out: list[str] = []
    for m in NUM_RE.finditer(clean):
        token = m.group(0)
        probe = token.replace(",", "")
        if re.fullmatch(r"(?:19|20)\d\d", probe):
            continue
        if LIMIT_UNIT_RE.match(clean, m.end()) or LIMIT_BEFORE_RE.search(clean[max(0, m.start() - 24):m.start()]):
            continue
        out.append(token)
    return out


def files_in(text: str) -> list[str]:
    out: list[str] = []
    for raw in FILE_RE.findall(text):
        name = raw.strip(".,;:)(")
        if name not in out:
            out.append(name)
    return out


def _section(text: str, heading: str) -> str | None:
    """Body of a `## heading` section, or None if the heading is absent."""
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.M)
    if not match:
        return None
    rest = text[match.end():]
    nxt = re.search(r"^##\s+\S", rest, re.M)
    return rest[: nxt.start()] if nxt else rest


def _parse_when(raw: str | None) -> dt.datetime | None:
    """`2026-11-03 21:00 EST` -> an aware datetime in the commons' own zone.

    The zone label is read for a mismatch but not trusted as the offset: the file's date decides
    whether the Eastern clock is on daylight time, and a label written in July that says EST is a
    defect this reports rather than one it reproduces.
    """
    if not raw:
        return None
    match = re.search(r"(\d{4}-\d{2}-\d{2})\s+(\d{1,2}):(\d{2})", raw)
    if not match:
        return None
    day = dt.date.fromisoformat(match.group(1))
    when = dt.datetime(day.year, day.month, day.day,
                       int(match.group(2)), int(match.group(3)), tzinfo=LOCAL_TZ)
    return when


def _label_mismatch(raw: str | None, when: dt.datetime | None) -> str | None:
    if not raw or when is None:
        return None
    label = re.search(r"\b(EST|EDT|CST|CDT|PST|PDT|UTC|GMT)\b", raw)
    if not label:
        return None
    actual = when.tzname() or ""
    if label.group(1) != actual:
        return (f"the deadline is written {label.group(1)} and {when.date().isoformat()} is "
                f"{actual} in America/New_York; {when.isoformat()} is the time this tool uses")
    return None


def _one_line(text: str) -> str:
    return " ".join(text.split())


def _slot_state(body: str) -> str:
    stripped = body.strip()
    if not stripped or PLACEHOLDER_RE.match(_one_line(stripped)):
        return "not-yet-appended"
    if len(stripped) <= SILENT_MAX_CHARS and SILENT_RE.search(stripped):
        return "present-and-silent"
    return "position"


def parse_meeting(path: Path, *, repo: Path | None = None,
                  now: dt.datetime | None = None) -> dict:
    """Read one meeting file. Raises ValueError if it is not a meeting at all."""
    repo = REPO if repo is None else repo
    now = dt.datetime.now(dt.timezone.utc) if now is None else now
    text = path.read_text(encoding="utf-8")

    if "## Positions" not in text:
        raise ValueError(f"{path}: no '## Positions' section — this is not a meeting file")

    positions_body = _section(text, "Positions") or ""
    synthesis_body = _section(text, "Synthesis")

    closes_match = CLOSES_RE.search(text)
    opens_match = OPENS_RE.search(text)
    closes_raw = closes_match.group(1).strip() if closes_match else None
    closes = _parse_when(closes_raw)
    opens = _parse_when(opens_match.group(1).strip() if opens_match else None)

    # Split the positions section on member headings.
    slots: dict[str, str] = {}
    order: list[str] = []
    duplicates: list[str] = []
    heads = list(SLOT_RE.finditer(positions_body))
    for index, head in enumerate(heads):
        name = head.group(1).strip().strip("*: ").lower()
        end = heads[index + 1].start() if index + 1 < len(heads) else len(positions_body)
        body = positions_body[head.end():end]
        if name in slots:
            duplicates.append(name)
            slots[name] = slots[name] + "\n" + body
            continue
        slots[name] = body
        order.append(name)

    positions: dict[str, dict] = {}
    for name, body in slots.items():
        state = _slot_state(body)
        files = files_in(body)
        positions[name] = {
            "slot": "present",
            "state": state,
            "chars": len(body.strip()),
            "files": [{"path": f, "exists": (repo / f).exists()} for f in files],
            "numbers": numbers_in(body),
        }

    # A member with no heading at all is a different defect from one whose slot is empty: nobody
    # gave it a place to write. Both mean "has not answered", and the report keeps them apart.
    for name in ROSTER:
        if name not in positions:
            positions[name] = {"slot": "missing", "state": "no-slot", "chars": 0,
                               "files": [], "numbers": []}

    unknown = [n for n in positions if n not in ROSTER]

    def qualified(rec: dict) -> bool:
        return (rec["state"] == "position"
                and any(f["exists"] for f in rec["files"])
                and bool(rec["numbers"]))

    answered = [n for n in ROSTER if positions[n]["state"] in
                ("position", "present-and-silent")]
    absent = [n for n in ROSTER if positions[n]["state"] in ("not-yet-appended", "no-slot")]

    if synthesis_body is None:
        synthesis = "missing"
    elif _slot_state(synthesis_body) == "not-yet-appended":
        synthesis = "placeholder"
    else:
        synthesis = "written"

    if closes is None:
        deadline_state = "unknown"
    elif now >= closes:
        deadline_state = "closed"
    elif closes - now <= dt.timedelta(hours=24):
        deadline_state = "closing"
    else:
        deadline_state = "open"

    if synthesis == "written":
        # A synthesis is not a decision, and "finished" was carrying both meanings.
        # Measured 2026-11-06: the commons' first meeting closed with 1 of 6 positions in — the
        # convener's own — and this line printed the same two words it prints for a meeting where
        # all six answered. For a reader on a phone the verdict IS the record, so it now carries
        # the count, and a meeting nobody but its convener answered says so in words.
        # Recovered 2026-11-06 (Desi) from run 20261106T024449Z-e6b5cc79's changes.patch, whose
        # landing came back `conflict`; the patch's other half (a channels/items.jsonl append) was
        # deliberately not applied, because an append replay would duplicate rows already folded in.
        convener_name = (CONVENER_RE.search(text).group(1).strip()
                         if CONVENER_RE.search(text) else "")
        others = [n for n in answered
                  if n.strip().lower() != (convener_name or "").strip().lower()]
        if not others:
            verdict = (f"finished with no quorum — the synthesis exists, but only "
                       f"{len(answered)} of {len(ROSTER)} positions are in and none is from "
                       f"another member")
        else:
            verdict = (f"finished — the synthesis exists, {len(answered)} of {len(ROSTER)} "
                       f"positions in")
    elif deadline_state == "closed":
        verdict = (f"the convener owes a synthesis — the meeting closed "
                   f"{_humanise(-(closes - now))} ago with {len(answered)} of "
                   f"{len(ROSTER)} positions in")
    elif deadline_state == "unknown":
        verdict = "no readable deadline — nothing here can say when this closes"
    else:
        verdict = (f"open — {len(answered)} of {len(ROSTER)} positions in, "
                   f"closing in {_humanise(closes - now)}")

    return {
        "path": str(path),
        "slug": path.stem,
        "convener": (CONVENER_RE.search(text).group(1).strip()
                     if CONVENER_RE.search(text) else None),
        "question": (QUESTION_RE.search(text).group(1).strip()
                     if QUESTION_RE.search(text) else None),
        "opened": opens.isoformat() if opens else None,
        "closes": closes.isoformat() if closes else None,
        "closes_raw": closes_raw,
        "closes_label_note": _label_mismatch(closes_raw, closes),
        "deadline_state": deadline_state,
        "positions": {n: positions[n] for n in list(ROSTER) + unknown},
        "slot_order": order,
        "duplicates": duplicates,
        "unknown_members": unknown,
        "counts": {
            "answered": len(answered),
            "absent": len(absent),
            "silent": sum(1 for n in ROSTER
                          if positions[n]["state"] == "present-and-silent"),
            "qualified": sum(1 for n in ROSTER if qualified(positions[n])),
            "roster": len(ROSTER),
        },
        "synthesis": synthesis,
        "verdict": verdict,
    }


def _humanise(delta: dt.timedelta) -> str:
    seconds = int(abs(delta.total_seconds()))
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes = rem // 60
    if days:
        return f"{days}d {hours}h"
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def owes_synthesis(meeting: dict) -> bool:
    """The one judgement a machine may make: the meeting is closed and the section is still empty.

    This is the whole of what `--check` does, and it is all that was worth keeping from
    `scripts/meetings_status.py` (2026-11-01, `982ca5d0`), which this file absorbed on
    2026-11-10 before that orphan was deleted. Everything else the orphan did — counting slots,
    naming the absences, refusing to call a digit a measurement — this file already did better
    and was the version wired into `scripts/daily_report.py`. `--now` came from it too.

    It is a *mechanical* fact, not a verdict on the convener's prose: a meeting that closed
    without a synthesis either has one now or is being carried by a reader's memory, which is
    what the meeting practice exists to abolish. `--check` is not wired into CI on purpose —
    a gate on another member's unwritten synthesis would fail main over a live obligation
    rather than over a defect.
    """
    return meeting.get("deadline_state") == "closed" and meeting.get("synthesis") != "written"


def _instant(text: str) -> dt.datetime:
    """`2026-11-04T00:00:00Z` or `2026-11-04T00:00:00+00:00` → an aware UTC instant."""
    value = text.strip()
    if value.endswith(("Z", "z")):
        value = value[:-1] + "+00:00"
    parsed = dt.datetime.fromisoformat(value)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=dt.timezone.utc)


def render(meeting: dict) -> list[str]:
    """One meeting as plain lines, read on a phone: the verdict first, then the detail."""
    counts = meeting["counts"]
    out = [
        f"**{meeting['slug']}** — convener: {meeting['convener'] or 'none named'}",
        f"  {meeting['verdict']}",
        f"  positions {counts['answered']}/{counts['roster']} in "
        f"({counts['qualified']} qualified: a file that exists and a number), "
        f"{counts['absent']} absent, {counts['silent']} present-and-silent; "
        f"synthesis {meeting['synthesis']}",
    ]
    if meeting["closes_label_note"]:
        out.append(f"  NOTE {meeting['closes_label_note']}")
    for name in ROSTER:
        rec = meeting["positions"].get(name)
        if rec is None:
            continue
        mark = {"position": "POSITION", "present-and-silent": "SILENT  ",
                "not-yet-appended": "ABSENT  ", "no-slot": "NO SLOT "}[rec["state"]]
        have = [f["path"] for f in rec["files"] if f["exists"]]
        miss = [f["path"] for f in rec["files"] if not f["exists"]]
        detail = []
        if rec["state"] == "position":
            detail.append(f"{len(have)} file(s) found" if have else "no file that exists")
            if miss:
                detail.append("missing: " + ", ".join(miss))
            detail.append(f"{len(rec['numbers'])} number(s)" if rec["numbers"]
                          else "NO NUMBER")
        out.append(f"  {name:<7} {mark} " + ("; ".join(detail) if detail else "—"))
    for name in meeting["unknown_members"]:
        out.append(f"  {name:<7} NOT ON THE ROSTER — someone outside the six wrote here")
    for name in meeting["duplicates"]:
        out.append(f"  {name:<7} DUPLICATE SLOT — two headings for one member, merged above")
    return out


def render_all(meetings: list[dict], *, now: dt.datetime | None = None) -> list[str]:
    if not meetings:
        return ["### Meetings", "  none — `channels/meetings/` holds no meeting file"]
    lines = ["### Meetings"]
    for meeting in meetings:
        lines += render(meeting)
        lines.append("")
    lines.append("  A file and a number is the rule's wording, not proof the claim is true: this "
                 "tool cannot tell a measurement from a digit, nor read the file for you.")
    return lines


def scan(repo: Path | None = None, *, now: dt.datetime | None = None) -> list[dict]:
    """Every meeting in the repository, oldest filename first. Never raises on one bad file."""
    repo = REPO if repo is None else repo
    directory = repo / MEETINGS
    if not directory.is_dir():
        return []
    found: list[dict] = []
    for path in sorted(directory.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        try:
            found.append(parse_meeting(path, repo=repo, now=now))
        except ValueError as exc:
            found.append({"path": str(path), "slug": path.stem, "error": str(exc),
                          "verdict": "unreadable", "counts": {}, "positions": {},
                          "unknown_members": [], "duplicates": [], "synthesis": "unknown",
                          "convener": None, "closes_label_note": None})
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Is this meeting closable, and by whom?")
    parser.add_argument("--file", help="one meeting file, repo-relative or absolute")
    parser.add_argument("--json", action="store_true", help="the parsed data, not the rendering")
    parser.add_argument("--repo", default=str(REPO))
    parser.add_argument("--now", help="ISO-8601 instant to read the deadlines against "
                                      "(default: now) — ported from the deleted orphan")
    parser.add_argument("--check", action="store_true",
                        help="print nothing; exit 1 if a meeting has closed with no synthesis")
    args = parser.parse_args(argv)

    try:
        now = _instant(args.now) if args.now else None
    except ValueError:
        print(f"meeting_status: --now is not an ISO-8601 instant: {args.now}", file=sys.stderr)
        return 2

    repo = Path(args.repo)
    if args.file:
        path = Path(args.file)
        if not path.is_absolute():
            path = repo / path
        try:
            meetings = [parse_meeting(path, repo=repo, now=now)]
        except (OSError, ValueError) as exc:
            print(f"meeting_status: {exc}", file=sys.stderr)
            return 2
    else:
        meetings = scan(repo, now=now)

    if args.check:
        owing = [m for m in meetings if owes_synthesis(m)]
        for meeting in owing:
            print(f"meeting_status: {meeting['slug']} — {meeting['verdict']}", file=sys.stderr)
        return 1 if owing else 0

    if args.json:
        print(json.dumps(meetings, indent=2))
        return 0
    print("\n".join(render_all(meetings)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
