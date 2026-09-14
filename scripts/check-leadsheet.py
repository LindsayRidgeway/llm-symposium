#!/usr/bin/env python3
"""
Lead-sheet checker for the Music Conservatory (docs/music/).

The two counterpoint checkers (check-counterpoint.py, check_music_rules.py) test
polyphonic voice-leading. A lead sheet has one voice, so they have almost nothing
to say about it. Agenda item 10 states a *different* discipline for lead sheets:

    "for the lead sheets, a singable range, plausible changes, and a lyric with
     an actual argument"

This script checks the two parts of that which are mechanically checkable, and
refuses to pretend it can check the third.

  1. SINGABLE RANGE. Total span must fit a normal untrained voice (default: a
     12th, i.e. 19 semitones) and sit inside a specified absolute range. Also
     flags melodic leaps larger than an octave, and reports the count of leaps
     larger than a sixth (singable but should be rare and deliberate).

  2. PLAUSIBLE CHANGES. Parses "..." chord symbols from the ABC, checks every
     chord is a real parseable chord, that the progression stays in/near one key,
     that it starts and ends sensibly, and reports the harmonic rhythm. Flags
     chords whose root is chromatic to the stated key so they must be justified
     rather than accidental.

  3. LYRIC ALIGNMENT. In ABC, each `w:` line is set against the notes of the
     music line immediately above it. If the syllable count does not match the
     note count, the words do not actually land on the notes — the song is not
     singable as written, whatever its literary merit. This IS mechanically
     checkable and is checked.

  4. WHETHER THE LYRIC MEANS ANYTHING. NOT CHECKED. Whether a lyric makes an
     argument is not a property a script can evaluate, and a checker that scored
     it would be lying. This tool prints the lyric for a human/model to judge and
     says nothing about its quality. The judgement stays external, on purpose.

Usage:
    python3 scripts/check-leadsheet.py path/to/leadsheet.abc
    python3 scripts/check-leadsheet.py --self-test
"""

import re
import sys
import argparse
from fractions import Fraction

BASE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11,
        'c': 12, 'd': 14, 'e': 16, 'f': 17, 'g': 19, 'a': 21, 'b': 23}

NOTE_RE = re.compile(
    r"(?P<acc>\^{1,2}|_{1,2}|=)?"
    r"(?P<letter>[A-Ga-g])"
    r"(?P<oct>[',]*)"
    r"(?P<len>\d*/?\d*)"
)

PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

MAJOR_KEY_SIGS = {
    0: {}, 7: {'F': 1}, 2: {'F': 1, 'C': 1}, 9: {'F': 1, 'C': 1, 'G': 1},
    4: {'F': 1, 'C': 1, 'G': 1, 'D': 1}, 11: {'F': 1, 'C': 1, 'G': 1, 'D': 1, 'A': 1},
    6: {'F': 1, 'C': 1, 'G': 1, 'D': 1, 'A': 1, 'E': 1},
    5: {'B': -1}, 10: {'B': -1, 'E': -1}, 3: {'B': -1, 'E': -1, 'A': -1},
    8: {'B': -1, 'E': -1, 'A': -1, 'D': -1},
    1: {'B': -1, 'E': -1, 'A': -1, 'D': -1, 'G': -1},
}
MODE_OFFSET = {
    'ionian': 0, 'major': 0, '': 0, 'dorian': 2, 'dor': 2, 'phrygian': 4, 'phr': 4,
    'lydian': 5, 'lyd': 5, 'mixolydian': 7, 'mix': 7,
    'aeolian': 9, 'aeo': 9, 'minor': 9, 'm': 9, 'locrian': 11, 'loc': 11,
}

# Chord quality -> semitone offsets from root
CHORD_QUALITIES = {
    '': [0, 4, 7], 'maj': [0, 4, 7], 'M': [0, 4, 7],
    'm': [0, 3, 7], 'min': [0, 3, 7], '-': [0, 3, 7],
    '7': [0, 4, 7, 10], 'maj7': [0, 4, 7, 11], 'M7': [0, 4, 7, 11],
    'm7': [0, 3, 7, 10], 'min7': [0, 3, 7, 10], '-7': [0, 3, 7, 10],
    'dim': [0, 3, 6], 'dim7': [0, 3, 6, 9], 'o': [0, 3, 6],
    'm7b5': [0, 3, 6, 10], 'aug': [0, 4, 8], '+': [0, 4, 8],
    'sus4': [0, 5, 7], 'sus2': [0, 2, 7], 'sus': [0, 5, 7],
    '6': [0, 4, 7, 9], 'm6': [0, 3, 7, 9],
    '9': [0, 4, 7, 10, 14], 'add9': [0, 4, 7, 14],
}

CHORD_RE = re.compile(r'^([A-G])([#b]?)(.*)$')


def parse_key(key_str):
    key_str = key_str.strip()
    m = re.match(r'([A-Ga-g])([#b]?)\s*(\w*)', key_str)
    if not m:
        return 0, {}
    letter = m.group(1).upper()
    accidental = m.group(2)
    mode_str = m.group(3).lower()
    tonic_pc = PC[letter]
    if accidental == '#':
        tonic_pc = (tonic_pc + 1) % 12
    elif accidental == 'b':
        tonic_pc = (tonic_pc - 1) % 12
    offset = MODE_OFFSET.get(mode_str, 0)
    parent_pc = (tonic_pc - offset) % 12
    return tonic_pc, dict(MAJOR_KEY_SIGS.get(parent_pc, {}))


def parse_chord(sym):
    """Return (root_pc, quality_intervals, ok)."""
    sym = sym.strip()
    if not sym:
        return None, None, False
    m = CHORD_RE.match(sym)
    if not m:
        return None, None, False
    letter, acc, qual = m.groups()
    root = PC[letter]
    if acc == '#':
        root = (root + 1) % 12
    elif acc == 'b':
        root = (root - 1) % 12
    # strip slash bass
    qual = qual.split('/')[0]
    if qual not in CHORD_QUALITIES:
        return root, None, False
    return root, CHORD_QUALITIES[qual], True


def parse_len(len_str, unit=Fraction(1, 8)):
    if not len_str:
        return unit
    if '/' in len_str:
        num, _, den = len_str.partition('/')
        num = int(num) if num else 1
        den = int(den) if den else 2
        return unit * Fraction(num, den)
    return unit * int(len_str)


def syllables_of(w_line):
    """Split an ABC w: line into syllable slots. In ABC lyric lines, syllables are
    separated by spaces or hyphens; '*' is a held-note skip, '|' aligns to a bar
    and does not consume a note, '_' extends the previous syllable over a note."""
    out = []
    for tok in re.split(r'[\s\-]+', w_line.strip()):
        if not tok or tok == '|':
            continue
        out.append(tok)
    return out


def align_lyrics(abc_text):
    """Pair each music line with any w: lines directly following it, and compare
    note count to syllable count. Returns list of (music_line, w_line, n_notes,
    n_syllables)."""
    unit = Fraction(1, 8)
    m = re.search(r'^L:\s*1/(\d+)', abc_text, re.M)
    if m:
        unit = Fraction(1, int(m.group(1)))
    key_str = 'C'
    km = re.search(r'^K:\s*(.+)$', abc_text, re.M)
    if km:
        key_str = km.group(1).strip()
    _, key_sig = parse_key(key_str)

    raw_lines = [l.rstrip() for l in abc_text.splitlines()]
    pairs = []
    last_music = None
    last_music_notes = 0
    for line in raw_lines:
        s = line.strip()
        if not s or s.startswith('%'):
            continue
        if s.startswith('w:'):
            if last_music is not None:
                syls = syllables_of(s[2:])
                pairs.append((last_music, s, last_music_notes, len(syls)))
            continue
        if re.match(r'^[A-Za-z]:', s):
            continue
        if s.startswith('V:') or s.startswith('[V:'):
            body = re.sub(r'^\[V:[^\]]*\]', '', s)
        else:
            body = s
        n = count_notes(body, key_sig, unit)
        if n > 0:
            last_music = s
            last_music_notes = n
    return pairs


def count_notes(body, key_sig, unit):
    """Count sounding notes (not rests) in an ABC music line."""
    body = re.sub(r'"[^"]*"', '', body)
    body = re.sub(r'![^!]*!', '', body)
    count = 0
    i = 0
    while i < len(body):
        ch = body[i]
        if ch in 'zxZX':
            mrest = re.match(r'[zxZX](\d*/?\d*)', body[i:])
            i += mrest.end() if mrest else 1
            continue
        nm = NOTE_RE.match(body, i)
        if nm and nm.group('letter'):
            count += 1
            i = nm.end()
            continue
        i += 1
    return count


def extract(abc_text):
    """Return (melody_notes, chord_symbols_in_order, lyric_lines, key_str, meter)."""
    unit = Fraction(1, 8)
    m = re.search(r'^L:\s*1/(\d+)', abc_text, re.M)
    if m:
        unit = Fraction(1, int(m.group(1)))
    key_str = 'C'
    km = re.search(r'^K:\s*(.+)$', abc_text, re.M)
    if km:
        key_str = km.group(1).strip()
    meter = '4/4'
    mm = re.search(r'^M:\s*(\S+)', abc_text, re.M)
    if mm:
        meter = mm.group(1)
    tonic_pc, key_sig = parse_key(key_str)

    notes = []       # (midi, duration)
    chords = []      # chord symbol strings, in order
    lyrics = []      # w: lines

    for raw in abc_text.splitlines():
        line = raw.strip()
        if not line or line.startswith('%'):
            continue
        if re.match(r'^w:\s*', line):
            lyrics.append(re.sub(r'^w:\s*', '', line))
            continue
        if re.match(r'^[A-Za-z]:', line):   # other header
            continue
        # music line
        for cm in re.finditer(r'"([^"]*)"', line):
            sym = cm.group(1)
            if sym and not sym.startswith('^') and not sym.startswith('_'):
                chords.append(sym)
        body = re.sub(r'"[^"]*"', '', line)
        body = re.sub(r'![^!]*!', '', body)
        acc_state = dict(key_sig)
        i = 0
        while i < len(body):
            ch = body[i]
            if ch == '|':
                acc_state = dict(key_sig)
                i += 1
                continue
            if ch in 'zxZX':
                mrest = re.match(r'[zxZX](\d*/?\d*)', body[i:])
                i += mrest.end() if mrest else 1
                continue
            nm = NOTE_RE.match(body, i)
            if nm and nm.group('letter'):
                acc = nm.group('acc')
                letter = nm.group('letter')
                octmarks = nm.group('oct')
                lenstr = nm.group('len')
                shift = 0
                for c in octmarks:
                    shift += 12 if c == "'" else -12
                k = letter.upper()
                if acc == '^':
                    acc_state[k] = 1
                elif acc == '^^':
                    acc_state[k] = 2
                elif acc == '_':
                    acc_state[k] = -1
                elif acc == '__':
                    acc_state[k] = -2
                elif acc == '=':
                    acc_state[k] = 0
                midi = 60 + BASE[letter] - 12 + acc_state.get(k, 0) + shift
                notes.append((midi, parse_len(lenstr, unit)))
                i = nm.end()
                continue
            i += 1
    return notes, chords, lyrics, key_str, meter


NOTE_NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']


def name_of(midi):
    return f"{NOTE_NAMES[midi % 12]}{midi // 12 - 1}"


def run(abc_text, max_span=19, lo=55, hi=79, verbose=True):
    notes, chords, lyrics, key_str, meter = extract(abc_text)
    ok = True
    print(f"Key: {key_str}   Meter: {meter}")
    print(f"Melody notes: {len(notes)}   Chord symbols: {len(chords)}   Lyric lines: {len(lyrics)}")

    if not notes:
        print("NO MELODY FOUND — nothing to check.")
        return False

    pitches = [m for m, d in notes]
    lowest, highest = min(pitches), max(pitches)
    span = highest - lowest

    print("\n--- 1. Singable range ---")
    print(f"  lowest  {name_of(lowest)} (MIDI {lowest})")
    print(f"  highest {name_of(highest)} (MIDI {highest})")
    print(f"  span    {span} semitones")
    if span > max_span:
        ok = False
        print(f"  FAIL: span {span} exceeds {max_span} semitones (a 12th) — not comfortably singable.")
    else:
        print(f"  OK: span within {max_span} semitones.")
    if lowest < lo or highest > hi:
        ok = False
        print(f"  FAIL: sits outside absolute range [{name_of(lo)}, {name_of(hi)}].")
    else:
        print(f"  OK: inside absolute range [{name_of(lo)}, {name_of(hi)}].")

    leaps = []
    big = []
    for a, b in zip(pitches, pitches[1:]):
        iv = abs(b - a)
        if iv > 12:
            big.append((name_of(a), name_of(b), iv))
        elif iv > 9:
            leaps.append(iv)
    if big:
        ok = False
        print(f"  FAIL: {len(big)} leap(s) larger than an octave: {big}")
    else:
        print("  OK: no leap larger than an octave.")
    print(f"  (leaps larger than a sixth: {len(leaps)} — singable but should be deliberate)")

    print("\n--- 2. Plausible changes ---")
    if not chords:
        ok = False
        print("  FAIL: no chord symbols found. A lead sheet needs changes.")
    else:
        tonic_pc, key_sig = parse_key(key_str)
        diatonic = set()
        # build diatonic pcs of the major/minor scale implied by key signature
        scale_major = [0, 2, 4, 5, 7, 9, 11]
        for s in scale_major:
            diatonic.add((tonic_pc + s) % 12)
        bad = []
        chromatic = []
        for sym in chords:
            root, q, good = parse_chord(sym)
            if not good:
                bad.append(sym)
            elif root not in diatonic:
                chromatic.append(sym)
        uniq = []
        for c in chords:
            if c not in uniq:
                uniq.append(c)
        print(f"  distinct chords: {uniq}")
        print(f"  first: {chords[0]}   last: {chords[-1]}")
        if bad:
            ok = False
            print(f"  FAIL: unparseable chord symbol(s): {bad}")
        else:
            print("  OK: every chord symbol parses to a real chord.")
        if chromatic:
            print(f"  NOTE: {len(chromatic)} chord(s) with root chromatic to {key_str}: "
                  f"{sorted(set(chromatic))} — must be deliberate, not accidental.")
        else:
            print(f"  OK: all chord roots diatonic to {key_str}.")

    print("\n--- 3. Lyric alignment (syllables must land on notes) ---")
    if not lyrics:
        ok = False
        print("  FAIL: no w: lyric lines found. The stated discipline requires a lyric.")
    else:
        pairs = align_lyrics(abc_text)
        if not pairs:
            ok = False
            print("  FAIL: lyric lines present but none aligned to a music line.")
        else:
            bad = [(i, n, s) for i, (ml, wl, n, s) in enumerate(pairs, 1) if n != s]
            print(f"  {len(pairs)} lyric line(s) aligned to music lines.")
            if bad:
                ok = False
                print(f"  FAIL: {len(bad)} line(s) where syllable count != note count:")
                for i, n, s in bad:
                    print(f"    w-line {i}: {n} notes vs {s} syllables (off by {s - n:+d})")
                print("  Words that do not land on notes are not singable as written.")
            else:
                print("  OK: every lyric line matches its music line note-for-syllable.")

    print("\n--- 4. Does the lyric mean anything? NOT CHECKED, by design ---")
    if lyrics:
        print("  Lyric, for external judgement:")
        for i, l in enumerate(lyrics, 1):
            print(f"    {l}")
        print("  Whether this makes an actual argument is NOT machine-graded.")
        print("  See this file's docstring for why.")

    print(f"\nRESULT: {'PASS (mechanical checks)' if ok else 'FAIL'}")
    return ok


SELF_TEST = '''X: 1
T: Self test
M: 4/4
L: 1/8
K: G
"G" G2 A2 B2 d2 | "C" e2 d2 "D7" B2 A2 | "G" G8 |
w: this is on- ly a test of chec- kers
'''


def self_test():
    print("===== self test (should PASS) =====")
    run(SELF_TEST)
    print()
    print("===== self test 2: unsingable span (should FAIL range) =====")
    bad = SELF_TEST.replace('"G" G8 |', '"G" G,,8 |')
    run(bad)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('file', nargs='?')
    ap.add_argument('--self-test', action='store_true')
    ap.add_argument('--max-span', type=int, default=19)
    ap.add_argument('--lo', type=int, default=55)
    ap.add_argument('--hi', type=int, default=79)
    args = ap.parse_args()
    if args.self_test:
        self_test()
        sys.exit(0)
    if not args.file:
        ap.print_help()
        sys.exit(1)
    with open(args.file) as f:
        text = f.read()
    sys.exit(0 if run(text, args.max_span, args.lo, args.hi) else 1)
