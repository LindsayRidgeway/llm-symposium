#!/usr/bin/env python3
# Owner: Dmitri
"""canon_cancrizans.py — builds and verifies "The Argus Ledger", a crab canon in D.

What the piece is
-----------------
One line of 32 quarter notes (8 bars of 4/4). Voice 1 plays it forward; voice 2 plays the same
line backwards, transposed down a twelfth (19 semitones). The two voices therefore meet in the
middle and the score is its own retrograde with the parts exchanged: read the page from the last
note to the first and swap the staves, and you are holding the page you started with.

Why a script, and not just a score
----------------------------------
The form is almost entirely constrained, and the constraint is arithmetic rather than taste.
At the moment when voice 1 plays note t, voice 2 is playing note 33-t. Write d(t) for
x[t] - x[33-t], the interval between the two notes *measured before transposition*. Then the
sonority heard at time t is d(t) + 19 and the sonority heard at time 33-t is 19 - d(t). Both are
the same pair of notes, heard at two different moments of the same piece. So every choice of d is
a choice of *two* intervals at once, and the admissible set collapses: with a twelfth between the
voices, only d in {-2, 0, +2} leaves both sonorities consonant, and no d at all can produce a
perfect octave or unison (both would need |d| = 5 or 7, which puts a second or a seventh on the
other end of the mirror). That is the finding this script exists to state with numbers: a strict
crab canon at the twelfth has almost no freedom in its vertical intervals.

What the script chooses, and what it does not
---------------------------------------------
The first half — the sixteen notes that go out — is written by hand (FIRST_HALF below). The
second half is not written: it is the first half read backwards, with each note allowed to move by
at most one diatonic step (d in {-2, 0, +2}). The script picks those sixteen inflections by
dynamic programming for the least-bad walk: small melodic leaps, and no two consecutive sonorities
of the same perfect interval, because a run of those is what a listener hears as organum.

So the composition is the hand-written half; the returning half is the form's own logic applied to
it. Both are in the file, and `--verify` re-derives the second half from the first and refuses a
score that does not mirror.

Usage
-----
    python3 scripts/canon_cancrizans.py --write      # emit docs/music/canon-cancrizans.abc
    python3 scripts/canon_cancrizans.py --verify     # check the landed score mirrors itself
    python3 scripts/canon_cancrizans.py --table      # the 32 sonorities, one per line
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCORE = ROOT / "docs" / "music" / "canon-cancrizans.abc"

THETA = 19  # the interval between the voices: a perfect twelfth
PITCH1 = {72: "c", 74: "d", 76: "e", 77: "f", 79: "g", 81: "a", 84: "c'"}   # cantus, treble
PITCH2 = {53: "F,", 55: "G,", 57: "A,", 58: "B,", 60: "C", 62: "D"}          # comes, bass
PITCH = {**PITCH1, **PITCH2}
NAME = {72: "C5", 74: "D5", 76: "E5", 77: "F5", 79: "G5", 81: "A5", 84: "C6"}

# The sixteen notes that go out: D D E F | G A G F | E F G A | G F E D
# (D minor without the sixth degree — no Bb enters the line, which is also what keeps the
# transposed voice inside the bass clef without a single accidental.)
FIRST_HALF = [74, 74, 76, 77, 79, 81, 79, 77, 76, 77, 79, 81, 79, 77, 76, 74]

# Hand-set anchors: the hinge and the last note. d(16)=0 puts a repeated D at the midpoint
# (both voices strike it; they are the same note an octave and a fifth apart) and d(1)=0 makes
# the piece end on the tonic it began on.
ANCHORS = {16: 0, 1: 0}


def _class(d: int) -> int:
    """The sonority heard at time t when d(t) is d, reduced to an interval class."""
    return (d + THETA) % 12


def _is_consonant(cls: int) -> bool:
    return cls in (0, 3, 4, 5, 7, 8, 9)


def admissible_d() -> list[int]:
    """The d values for which BOTH mirrored sonorities are consonant."""
    return [d for d in range(-12, 13) if _is_consonant((THETA + d) % 12) and _is_consonant((THETA - d) % 12)]


def choose_inflections() -> list[int]:
    """Dynamic program over the sixteen mirrored pairs.

    Step k fixes x[33-k] from x[k] - d(k). The cost is paid on the second half as a melody
    (leaps) and on both halves as a sequence of sonorities (runs of one interval class).
    """
    allowed = [d for d in (-2, 0, 2)]
    INF = 10**6
    # state: (k, pitch chosen for x[34-k]) -> cost  (x[34-k] is the note before this one in time)
    best: dict[tuple[int, int], tuple[int, list[int]]] = {}
    for k in (16,):
        for d in allowed:
            if k in ANCHORS and d != ANCHORS[k]:
                continue
            p = FIRST_HALF[k - 1] - d
            if p not in PITCH:
                continue
            cls = _class(d)
            if not _is_consonant(cls):
                continue
            best[(k, p)] = (0, [d])
    for k in range(15, 0, -1):
        nxt: dict[tuple[int, int], tuple[int, list[int]]] = {}
        for (kn, prev_pitch), (cost, path) in best.items():
            for d in allowed:
                if k in ANCHORS and d != ANCHORS[k]:
                    continue
                p = FIRST_HALF[k - 1] - d
                if p not in PITCH1:
                    continue
                cls = _class(d)
                if not _is_consonant(cls):
                    continue
                leap = abs(p - prev_pitch)
                # step is free; a repeated note is not (it is the cheapest way to satisfy the
                # leap test and it is what makes a mirrored line sound like a pedal point)
                c = cost + (0 if 1 <= leap <= 2 else 4 if leap == 0 else 6 if leap <= 4 else INF)
                # a run of the same interval class is what sounds like organum: buy it off
                prev_cls = _class(path[-1])
                if cls == prev_cls:
                    c += 5
                if cls == 7 and prev_cls == 7:
                    c += 20
                key = (k, p)
                if key not in nxt or c < nxt[key][0]:
                    nxt[key] = (c, path + [d])
        best = nxt
    if not best:
        raise SystemExit("no admissible inflection set: the anchors and the constraint disagree")
    cost, path = min(best.values(), key=lambda cv: cv[0])
    # path was built from k=16 down to k=1 but appended in decreasing k, so read it back
    ds = {k: d for k, d in zip(range(16, 0, -1), path)}
    return [ds[k] for k in range(1, 17)]


def build_line() -> tuple[list[int], list[int]]:
    ds = choose_inflections()
    line = list(FIRST_HALF)
    for k in range(16, 0, -1):
        line.append(FIRST_HALF[k - 1] - ds[k - 1])
    return line, ds


def voices(line: list[int]) -> tuple[list[int], list[int]]:
    v1 = list(line)
    v2 = [line[31 - t] - THETA for t in range(32)]  # reverse, down a twelfth
    return v1, v2


def bars(pitches: list[int]) -> list[list[int]]:
    return [pitches[i : i + 4] for i in range(0, len(pitches), 4)]


def abc() -> str:
    line, _ = build_line()
    v1, v2 = voices(line)
    out = [
        "X: 21",
        'T: The Argus Ledger — Canon Cancrizans at the Twelfth',
        "C: Dmitri S. Amigo (DeepSeek)",
        "M: 4/4",
        "L: 1/4",
        "Q: 1/4=63",
        "K: Dm",
        'V: 1 clef=treble name="Cantus (forward)"',
        'V: 2 clef=bass name="Comes (backward, a twelfth below)"',
        "% Voice 1 plays the line forward; voice 2 plays it backward, a twelfth lower.",
        "% Read the last bar backwards with the staves exchanged and you have bar 1.",
    ]
    for label, ps in (("1", v1), ("2", v2)):
        body = []
        for i, b in enumerate(bars(ps)):
            tail = "|]" if i == 7 else "|"
            names = PITCH1 if label == "1" else PITCH2
            body.append(" ".join(names[p] for p in b) + " " + tail)
        # two bars per printed line, so the mirror is visible on the page
        for i in range(0, 8, 2):
            out.append(f"[V:{label}] " + " ".join(body[i : i + 2]))
    return "\n".join(out) + "\n"


def verify(text: str | None = None) -> list[str]:
    """Re-derive the score from the first half and compare it to what is on disk."""
    problems: list[str] = []
    line, ds = build_line()
    v1, v2 = voices(line)

    for t in range(32):
        if v2[31 - t] + THETA != v1[t]:
            problems.append(f"slot {t + 1}: retrograde broken (v2 at {32 - t} + twelfth != v1 at {t + 1})")
    if len(v1) != 32 or len(v2) != 32:
        problems.append(f"expected 32 quarter notes per voice, got {len(v1)} and {len(v2)}")

    for t in range(32):
        cls = (v1[t] - v2[t]) % 12
        if cls == 0:
            problems.append(f"slot {t + 1}: perfect octave/unison between the voices")
        if t and cls == 7 and (v1[t - 1] - v2[t - 1]) % 12 == 7 and v1[t] != v1[t - 1]:
            problems.append(f"slot {t + 1}: parallel fifth")
    for i in range(31):
        if abs(v2[i + 1] - v2[i]) > 4:
            problems.append(f"slot {i + 1}: leap of {abs(v2[i + 1] - v2[i])} semitones in voice 2")
    if not all(p in PITCH for p in v1 + v2):
        problems.append("a pitch outside the D-minor set {D E F G A C} appears in the score")

    if text is None and SCORE.exists():
        text = SCORE.read_text(encoding="utf-8")
    if text is not None:
        notes = {
            "1": {v: k for k, v in PITCH1.items()},
            "2": {v: k for k, v in PITCH2.items()},
        }
        landed: dict[str, list[int]] = {"1": [], "2": []}
        for row in text.splitlines():
            if not row.startswith("[V:"):
                continue
            voice = row[3]
            for token in row.split("]", 1)[1].replace("|", " ").replace("]", " ").split():
                if token in notes.get(voice, {}):
                    landed[voice].append(notes[voice][token])
                else:
                    problems.append(f"unreadable token {token!r} in {SCORE.name}")
        if landed["1"] != v1:
            problems.append("the landed voice 1 is not the line this script derives")
        if landed["2"] != v2:
            problems.append("the landed voice 2 is not the retrograde this script derives")
    return problems


def table() -> str:
    line, ds = build_line()
    v1, v2 = voices(line)
    rows = ["slot bar beat  cantus comes  semitones  class  d(t)"]
    for t in range(32):
        rows.append(
            f"{t + 1:4d} {t // 4 + 1:3d} {t % 4 + 1:4d}  {NAME[v1[t]]:>6} {v2[t]:7d}  "
            f"{v1[t] - v2[t]:9d} {(v1[t] - v2[t]) % 12:6d} {ds[t] if t < 16 else ds[31 - t]:5d}"
        )
    return "\n".join(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write docs/music/canon-cancrizans.abc")
    ap.add_argument("--verify", action="store_true", help="check the landed score mirrors itself")
    ap.add_argument("--table", action="store_true", help="the 32 sonorities, one per line")
    ap.add_argument("--admissible", action="store_true", help="the d values the form permits")
    args = ap.parse_args()

    if args.admissible:
        print("admissible d (both mirrored sonorities consonant):", admissible_d())
        print("admissible |d| <= 2 (also consonant in the octave class):", [d for d in admissible_d() if abs(d) <= 2])
    if args.table:
        print(table())
    if args.write:
        SCORE.write_text(abc(), encoding="utf-8")
        print(f"wrote {SCORE.relative_to(ROOT)}")
    if args.verify:
        problems = verify()
        if problems:
            print(f"FAIL — {len(problems)} problem(s)")
            for p in problems:
                print("  " + p)
            return 1
        print("ok   score mirrors itself: 32 slots, no octave, no parallel fifth, no leap over a third")
    return 0


if __name__ == "__main__":
    sys.exit(main())
