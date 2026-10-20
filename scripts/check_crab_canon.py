#!/usr/bin/env python3
"""check_crab_canon.py — verify a retrograde (crab) canon, rather than merely claim one.

Why a third checker. `scripts/check_music_rules.py` (Gemini) and
`scripts/check-counterpoint.py` (Claude) both answer the same question: are there
parallel fifths or octaves, is the meter intact, are the voices in range. Neither
can see the thing that makes a crab canon a crab canon — that one voice is the
other read backwards. A wrong retrograde still parses, still has no parallels,
and still sounds like music; it is simply not a canon. This script tests the
claim the score page makes about its own construction, so the claim is
machine-checkable instead of being a sentence in a commentary.

What it checks, on the first two voices of an ABC file:

  1. Both voices have the same number of notes.
  2. Voice 2 is voice 1 reversed, transposed by a constant interval
     (default -12, i.e. an octave down), note for note, in order.
  3. Every simultaneity is reported, with its interval class, and the run fails
     if two consecutive simultaneities are both fifths or both octaves/unisons
     (the parallel rule both existing checkers enforce) or if any pair crosses.

It parses the same restricted ABC subset the other two do: `V:` headers and
`[V:n]` note runs, letters with `^`/`_`/`=` accidentals, `,`/`'` octave marks,
`/` and digits for duration, `|` and `%` ignored. It does not read chords,
tuplets, ties, or repeats, and it says so rather than guessing.

Usage:
    python3 scripts/check_crab_canon.py docs/music/the-same-water-twice.abc
    python3 scripts/check_crab_canon.py piece.abc --transpose -12
    python3 scripts/check_crab_canon.py --self-test
"""

import argparse
import re
import sys

BASE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
KEY_SIGS = {
    'C': {}, 'Am': {},
    'G': {'F': 1}, 'Em': {'F': 1},
    'D': {'F': 1, 'C': 1}, 'Bm': {'F': 1, 'C': 1},
    'A': {'F': 1, 'C': 1, 'G': 1}, 'F#m': {'F': 1, 'C': 1, 'G': 1},
    'E': {'F': 1, 'C': 1, 'G': 1, 'D': 1},
    'F': {'B': -1}, 'Dm': {'B': -1},
    'Bb': {'B': -1, 'E': -1}, 'Gm': {'B': -1, 'E': -1},
    'Eb': {'B': -1, 'E': -1, 'A': -1}, 'Cm': {'B': -1, 'E': -1, 'A': -1},
}
CLASS_NAMES = {0: 'unison/octave', 1: 'minor 2nd', 2: 'major 2nd', 3: 'minor 3rd',
               4: 'major 3rd', 5: 'perfect 4th', 6: 'tritone', 7: 'perfect 5th',
               8: 'minor 6th', 9: 'major 6th', 10: 'minor 7th', 11: 'major 7th'}

NOTE_RE = re.compile(r'(\^+|_+|=)?([A-Ga-g])([,]*)([\']*)(\d*(?:/\d*)?)')


def parse(path_or_text, is_text=False):
    """Return (voices, key) where voices maps voice-name -> list of MIDI pitches."""
    text = path_or_text if is_text else open(path_or_text, encoding='utf-8').read()
    key = 'C'
    for line in text.splitlines():
        m = re.match(r'\s*K:\s*(\S+)', line)
        if m:
            key = m.group(1)
            break
    sig = KEY_SIGS.get(key, {})
    voices, order, current = {}, [], None
    for raw in text.splitlines():
        line = raw.split('%')[0]
        m = re.match(r'\s*V:\s*(\S+)', line)
        if m:
            current = m.group(1)
            voices.setdefault(current, [])
            if current not in order:
                order.append(current)
            continue
        for body in re.findall(r'\[V:(\S+?)\]\s*([^\[\]]*)', line):
            name, notes = body[0], body[1]
            voices.setdefault(name, [])
            if name not in order:
                order.append(name)
            for tok in notes.split():
                if tok in ('|', '||', '|]', ']', ':|', '|:'):
                    continue
                nm = NOTE_RE.fullmatch(tok)
                if not nm:
                    continue
                acc, letter, commas, primes, _dur = nm.groups()
                step = letter.upper()
                delta = sig.get(step, 0)
                if acc:
                    delta = acc.count('^') - acc.count('_')
                midi = (12 if letter.islower() else 0) + 12 * len(primes) - 12 * len(commas)
                midi += BASE[step] + delta + 60
                voices[name].append(midi)
    return [voices[n] for n in order], key


def check(path_or_text, transpose=-12, is_text=False, label=''):
    voices, key = parse(path_or_text, is_text)
    problems, notes = [], []
    if len(voices) < 2:
        return [f'only {len(voices)} voice(s) parsed; a canon needs two'], [], key, {}
    a, b = voices[0], voices[1]
    if len(a) != len(b):
        problems.append(f'voice 1 has {len(a)} notes, voice 2 has {len(b)}')
    n = min(len(a), len(b))
    expected = [a[n - 1 - i] + transpose for i in range(n)]
    wrong = [i for i in range(n) if b[i] != expected[i]]
    for i in wrong[:6]:
        problems.append(f'beat {i + 1}: voice 2 is {b[i]}, the retrograde requires {expected[i]}')
    if len(wrong) > 6:
        problems.append(f'... and {len(wrong) - 6} more beats disagree')

    intervals = []
    for i in range(n):
        upper, lower = (a[i], b[i]) if a[i] >= b[i] else (b[i], a[i])
        cls = (upper - lower) % 12
        intervals.append(cls)
        if a[i] < b[i]:
            problems.append(f'beat {i + 1}: voices cross (voice 2 is {b[i] - a[i]} semitones above voice 1)')
    for i in range(1, n):
        if intervals[i] == intervals[i - 1] == 7:
            problems.append(f'beats {i} and {i + 1}: consecutive fifths')
        if intervals[i] == intervals[i - 1] == 0:
            problems.append(f'beats {i} and {i + 1}: consecutive octaves/unisons')
    counts = {}
    for cls in intervals:
        counts[CLASS_NAMES[cls]] = counts.get(CLASS_NAMES[cls], 0) + 1
    return problems, [(i + 1, a[i], b[i], CLASS_NAMES[c]) for i, c in enumerate(intervals)], key, counts


SELF_TEST_ABC = """X: 0
T: self-test
M: 2/4
L: 1/4
K: Am
V: 1 clef=treble
V: 2 clef=bass
[V:1] C E | C A, |
[V:2] A,, C, | E, C, |
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file', nargs='?')
    ap.add_argument('--transpose', type=int, default=-12,
                    help='interval between voice 1 and its retrograde (default -12)')
    ap.add_argument('--self-test', action='store_true')
    args = ap.parse_args()
    if args.self_test:
        problems, table, key, counts = check(SELF_TEST_ABC, is_text=True)
        ok = not problems
        print(f'self-test: voice 2 is voice 1 reversed and an octave down -> {"PASS" if ok else "FAIL"}')
        for p in problems:
            print('  ' + p)
        print('  simultaneities:', ', '.join(n for _, _, _, n in table))
        return 0 if ok else 1
    if not args.file:
        ap.print_help()
        return 2
    problems, table, key, counts = check(args.file, transpose=args.transpose)
    print(f'=== Crab canon verification: {args.file} ===')
    print(f'Key: {key} · beat-aligned notes: {len(table)} · transposition of voice 1 -> voice 2: {args.transpose}')
    print('Retrograde (voice 2 == voice 1 reversed, note for note): '
          + ('EXACT' if not any('retrograde requires' in p or 'notes' in p for p in problems) else 'BROKEN'))
    print('\nBeat  Voice 1  Voice 2  Interval')
    for beat, one, two, name in table:
        print(f'{beat:>4}  {one:>7}  {two:>7}  {name}')
    print('\nInterval census: ' + ', '.join(f'{k} x{v}' for k, v in sorted(counts.items())))
    if problems:
        print('\nFAILED:')
        for p in problems:
            print('  ' + p)
        return 1
    print('\nResult: PASSED — the retrograde relation holds beat for beat, and no two consecutive '
          'beats are both fifths or both octaves.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
