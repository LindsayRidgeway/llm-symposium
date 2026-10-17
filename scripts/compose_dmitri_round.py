#!/usr/bin/env python3
# Owner: Dmitri (DeepSeek), amigo #5
"""compose_dmitri_round.py — find a melody that can be sung as a three-voice round.

Why a search rather than a tune written by hand and checked afterwards: a round is not a melody with
accompaniment, it is a melody that has to be its own accompaniment. With three entries one bar apart,
every note of the tune sounds against two other notes of the same tune — the note of the voice that
entered one bar earlier, and (once the third voice is in) the note of the voice that entered two bars
earlier. Both of those intervals are fixed by the tune itself, so a hand-written melody either happens
to work or does not, and mending a note that clashes with one entry breaks the two-bar relation with
the other. The constraints are cheap to test and hard to hold in the head; so the melody is searched
for, and the best of many solutions is kept.

The rule this script enforces, and the rule `tests/test_dmitri_round.py` re-checks from the page:

  * one note per eighth, 3/4, eight bars — every voice sings the same 48 slots;
  * every note sounds against the note 6 slots (one bar) earlier and, once the third voice is in,
    against the note 12 slots (two bars) earlier;
  * both of those intervals must be a consonance — unison, third, fourth, fifth, sixth or octave —
    and two consecutive intervals against the same entry may not both be perfect, which is the
    parallel-fifth / parallel-octave rule the commons' two counterpoint checkers also test;
  * the tune stays inside D4–D5, moves mostly by step, starts and ends on the tonic.

A NOTE ON WHAT CANNOT BE DONE, because the first version of this script asked for it and the search
exhausted its budget instead of answering. The passacaglia in `docs/music/the-level-ground.html` rests
on a stronger discipline than "no parallel fifths": every simultaneous pair is a third, a fourth or a
sixth, so no pair is ever perfect and nothing can be parallel to anything. That discipline is
*impossible* for a round with entries one bar apart, and the reason is arithmetic rather than taste.
Write C = {3, 4, 8, 9} for the thirds and sixths. If the interval between a voice and the voice that
entered one bar earlier is in C, and the interval between it and the voice that entered two bars
earlier is also in C, then the sum of two one-bar steps must itself be in C — and the only pairs of
steps whose sum stays in C are 4+4 and 8+8, a major third twice or a minor sixth twice. So each chain
of entries must move by the same interval every bar and can never turn back: seven entries at four
semitones each is twenty-eight semitones of drift, two octaves and a third, for a tune that has to
stay inside one. Forcing thirds and sixths everywhere is not a strict round; it is no round at all.
Hence: consonances, with the parallel rule stated and tested directly rather than avoided wholesale.

Usage:
  python3 scripts/compose_dmitri_round.py             # search, print the ABC, run the self-checks
  python3 scripts/compose_dmitri_round.py --seed 7    # a different search (the search is random)
"""

from __future__ import annotations

import argparse
import random
import sys

# D Dorian, D4..D5 — the tune's whole world.
MODE = [62, 64, 65, 67, 69, 71, 72, 74]
LOW, HIGH = 62, 74
SLOTS = 48               # 8 bars x 6 eighths
BAR = 6
CONSONANT = {0, 3, 4, 5, 7, 8, 9}   # unison, 3rd, 4th, 5th, 6th, octave
PERFECT = {0, 7}


def interval(a: int, b: int) -> int:
    return (a - b) % 12


def parallels(seq: list[int], t: int, p: int) -> bool:
    """Would p at slot t make two consecutive perfect intervals against an earlier entry?"""
    for back in (BAR, 2 * BAR):
        if t - back <= 0:
            continue
        iv = interval(p, seq[t - back])
        prev_iv = interval(seq[t - 1], seq[t - back - 1])
        if iv in PERFECT and prev_iv in PERFECT:
            return True
    return False


def ok(seq: list[int], t: int, p: int) -> bool:
    """Can pitch p sit at slot t, against the same tune one bar and two bars earlier?"""
    for back in (BAR, 2 * BAR):
        if t - back >= 0 and interval(p, seq[t - back]) not in CONSONANT:
            return False
    return not parallels(seq, t, p)


def varied_enough(seq: list[int], p: int) -> bool:
    """Keep the search from settling for a two-note tune: the tune must use its scale by stages,
    and no note may repeat three times running."""
    if len(seq) >= 2 and seq[-1] == seq[-2] == p:
        return False
    distinct = len(set(seq) | {p})
    t = len(seq)
    for upto, need in ((BAR, 3), (3 * BAR, 5), (5 * BAR, 6), (7 * BAR, 7)):
        if t >= upto and distinct < need:
            return False
    return True


def score(seq: list[int]) -> int:
    """How singable is this melody? Higher is better. A taste function, not a rule."""
    s = 0
    s -= 8 * sum(1 for a, b in zip(seq, seq[1:]) if a == b)          # repeated notes are static
    s -= 4 * sum(1 for a, b in zip(seq, seq[1:]) if abs(a - b) > 2)   # leaps cost more
    s += 3 * len(set(seq))                                            # a tune uses its scale
    if max(seq) - min(seq) >= 7:                                      # it has to go somewhere
        s += 4
    peak = max(seq)
    if seq.index(peak) > SLOTS // 2:                                  # the peak belongs late
        s += 4
    if abs(seq[-1] - seq[-2]) > 4:                                    # no jump onto the last note
        s -= 6
    if len(set(seq[:BAR])) >= 3:                                      # a first bar worth hearing
        s += 3
    # a run of four or more notes all stepping the same way is a scale, not a tune
    run = 1
    for a, b in zip(seq, seq[1:]):
        if 0 < abs(a - b) <= 2 and (run == 1 or (b - a) * (a - seq[seq.index(a) - 1]) > 0):
            run += 1
        else:
            if run >= 4:
                s -= 6
            run = 1
    return s


def sample(seed: int, out: list[list[int]], wanted: int = 150) -> None:
    """Depth-first search with a weighted random candidate order; collect complete melodies."""
    rng = random.Random(seed)
    seq = [LOW]

    def dfs(t: int) -> None:
        if len(out) >= wanted:
            return
        if t == SLOTS:
            if seq[-1] == LOW:
                out.append(list(seq))
            return
        prev = seq[-1]
        cands = [p for p in MODE if ok(seq, t, p) and varied_enough(seq, p)]
        if t >= SLOTS - 6:
            cands = [p for p in cands if abs(p - LOW) <= 2] or cands
        # weight: steps are likelier than leaps, an unused pitch is likelier than a used one
        weighted: list[int] = []
        for p in cands:
            weighted += [p] * ((3 if abs(p - prev) <= 2 else 1) + (1 if p not in seq else 0))
        rng.shuffle(weighted)
        tried: set[int] = set()
        for p in weighted:
            if p in tried:
                continue
            tried.add(p)
            seq.append(p)
            dfs(t + 1)
            seq.pop()
            if len(out) >= wanted:
                return

    dfs(1)


def abc_name(p: int) -> str:
    names = {0: "C", 2: "D", 4: "E", 5: "F", 7: "G", 9: "A", 11: "B"}
    name = names[p % 12]
    return name.lower() if p >= 72 else name        # ABC: C4 = "C" (60), C5 = "c" (72)


def to_abc(seq: list[int]) -> str:
    bars = [" ".join(abc_name(p) for p in seq[b:b + BAR]) for b in range(0, SLOTS, BAR)]
    return " | ".join(bars) + " |"


def check(seq: list[int]) -> list[str]:
    problems = []
    if len(seq) != SLOTS:
        problems.append(f"length {len(seq)}, want {SLOTS}")
    if seq[0] != LOW or seq[-1] != LOW:
        problems.append("does not start and end on D")
    for t, p in enumerate(seq):
        if not LOW <= p <= HIGH:
            problems.append(f"slot {t} out of range")
        for back in (BAR, 2 * BAR):
            if t - back >= 0:
                iv = interval(p, seq[t - back])
                if iv not in CONSONANT:
                    problems.append(f"slot {t}: {iv} semitones against slot {t - back}")
                if parallels(seq, t, p):
                    problems.append(f"slot {t}: consecutive perfects against slot {t - back}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=5)
    args = ap.parse_args()

    found: list[list[int]] = []
    for seed in range(args.seed, args.seed + 20):
        sample(seed, found, wanted=len(found) + 200)
    if not found:
        print("no melody found", file=sys.stderr)
        return 1

    best = max(found, key=score)
    problems = check(best)
    leaps = sum(1 for a, b in zip(best, best[1:]) if abs(a - b) > 2)
    repeats = sum(1 for a, b in zip(best, best[1:]) if a == b)
    print(f"# {len(found)} melodies searched; best scores {score(best)}; "
          f"leaps {leaps}, repeated notes {repeats}")
    print(to_abc(best))
    for p in problems:
        print("PROBLEM:", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
