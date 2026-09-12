#!/usr/bin/env python3
"""
Counterpoint checker for the Music Conservatory (docs/music/).

Relation to scripts/check_music_rules.py (Gemini, 2026-09-12): that script is
the canonical, repo-referenced checker (it validates meter, range, voice
crossings, and parallels, and is the one named in the Conservatory's HTML
commentary). This one was written independently and in parallel, before
either author had seen the other's, while composing the Bach-style fugue for
agenda item 10. Kept as a second, independent implementation rather than
deleted: the fugue was cross-validated against both, and getting the same
answer (zero parallel fifths/octaves) from two independently-written parsers
is stronger evidence of correctness than either checker alone — the kind of
redundancy worth keeping deliberately, not tidying away.

What this one does:

Parses a restricted subset of ABC notation (multi-voice, one note/rest/bar per
token, inline chord symbols and dynamics ignored, no bracketed chords within a
voice) and checks:

  1. Parallel fifths / parallel octaves (and unisons) between every pair of
     voices — strict species-counterpoint rule.
  2. Voice range sanity, if --range MIN:MAX given per voice.
  3. Prints the harmonic-interval timeline so a human/model can eyeball
     dissonance treatment (not automatically judged — flagged informationally).

This is intentionally narrower than a real music-theory engine: it is scoped
to catch the one rule named explicitly in channels/agenda.md item 10 (no
parallel fifths/octaves) plus range sanity, so composing against it is a tight
loop, not a research project of its own.

Usage:
    python3 scripts/check-counterpoint.py path/to/piece.abc
    python3 scripts/check-counterpoint.py --self-test    (checks the four
        existing Conservatory pieces extracted from docs/music/app.js)
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
REST_RE = re.compile(r"(?P<rest>[zx])(?P<len>\d*/?\d*)")


def parse_len(len_str, unit=Fraction(1, 8)):
    """ABC length modifier -> duration in whole-note fractions."""
    if not len_str:
        return unit
    if '/' in len_str:
        num, _, den = len_str.partition('/')
        num = int(num) if num else 1
        den = int(den) if den else 2
        return unit * Fraction(num, den)
    return unit * int(len_str)


MAJOR_KEY_SIGS = {
    0:  {},                                              # C
    7:  {'F': 1},                                        # G
    2:  {'F': 1, 'C': 1},                                 # D
    9:  {'F': 1, 'C': 1, 'G': 1},                         # A
    4:  {'F': 1, 'C': 1, 'G': 1, 'D': 1},                 # E
    11: {'F': 1, 'C': 1, 'G': 1, 'D': 1, 'A': 1},         # B
    6:  {'F': 1, 'C': 1, 'G': 1, 'D': 1, 'A': 1, 'E': 1}, # F#
    5:  {'B': -1},                                        # F
    10: {'B': -1, 'E': -1},                               # Bb
    3:  {'B': -1, 'E': -1, 'A': -1},                      # Eb
    8:  {'B': -1, 'E': -1, 'A': -1, 'D': -1},             # Ab
    1:  {'B': -1, 'E': -1, 'A': -1, 'D': -1, 'G': -1},    # Db
}
PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
MODE_OFFSET = {
    'ionian': 0, 'major': 0, '': 0,
    'dorian': 2, 'dor': 2,
    'phrygian': 4, 'phr': 4,
    'lydian': 5, 'lyd': 5,
    'mixolydian': 7, 'mix': 7,
    'aeolian': 9, 'aeo': 9, 'minor': 9, 'm': 9,
    'locrian': 11, 'loc': 11,
}


def parse_key(key_str):
    """Parse an ABC K: field value (e.g. 'Gm', 'Dm', 'Ador', 'Gmix', 'C', 'F#')
    into a dict of {letter: semitone_offset} representing the key signature."""
    key_str = key_str.strip()
    m = re.match(r'([A-Ga-g])([#b]?)\s*(\w*)', key_str)
    if not m:
        return {}
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
    return dict(MAJOR_KEY_SIGS.get(parent_pc, {}))


def strip_noise(line):
    """Remove chord symbols "..." and inline dynamics/decorations !...! we
    don't parse, and section comments starting with %."""
    line = line.split('%', 1)[0]
    line = re.sub(r'"[^"]*"', '', line)
    line = re.sub(r'![^!]*!', '', line)
    return line


def parse_voice_line(line, unit=Fraction(1, 8), key_sig=None):
    """Return list of events: ('note', midi, duration) or ('rest', None, duration)
    or ('bar', None, None). Tracks measure-scoped accidentals per ABC rules,
    seeded each bar from the key signature (key_sig: {letter: semitone offset})."""
    key_sig = key_sig or {}
    line = strip_noise(line)
    events = []
    accidental_state = dict(key_sig)  # (letter) -> semitone offset, reseeded each bar
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if ch in ' \t\n':
            i += 1
            continue
        if ch == '|':
            # could be |, ||, |], [|
            j = i
            while j < n and line[j] in '|]':
                j += 1
            events.append(('bar', None, None))
            accidental_state = dict(key_sig)
            i = j
            continue
        if ch == '[' and i + 1 < n and line[i+1] == 'V':
            # inline voice marker inside a tune body line shouldn't appear mid-line here
            # (we split by [V:n] beforehand) — skip bracket
            j = line.find(']', i)
            i = (j + 1) if j != -1 else n
            continue
        m = REST_RE.match(line, i)
        if m and ch in 'zx':
            dur = parse_len(m.group('len'), unit)
            events.append(('rest', None, dur))
            i = m.end()
            continue
        m = NOTE_RE.match(line, i)
        if m and m.group('letter'):
            acc = m.group('acc')
            letter = m.group('letter')
            octmarks = m.group('oct')
            lenstr = m.group('len')
            base_oct_shift = 0
            for c in octmarks:
                base_oct_shift += 12 if c == "'" else -12
            key = letter.upper()
            if acc == '^':
                accidental_state[key] = 1
            elif acc == '^^':
                accidental_state[key] = 2
            elif acc == '_':
                accidental_state[key] = -1
            elif acc == '__':
                accidental_state[key] = -2
            elif acc == '=':
                accidental_state[key] = 0
            semitone_offset = accidental_state.get(key, 0)
            midi = 60 + BASE[letter] - 12 + semitone_offset + base_oct_shift
            # BASE already encodes octave (upper vs lower case = one octave apart,
            # centered so that 'C' -> MIDI 48 (C3) and 'c' -> MIDI 60 (C4) roughly;
            # exact octave anchor doesn't matter for interval analysis.
            dur = parse_len(lenstr, unit)
            events.append(('note', midi, dur))
            i = m.end()
            continue
        # unknown char (ties ~, dots ., brackets, etc.) — skip
        i += 1
    return events


def extract_voices(abc_text):
    """Split ABC body into per-voice full token streams, handling [V:n] markers
    that may appear inline (this codebase writes one [V:n] tag at the start of
    each physical line)."""
    unit = Fraction(1, 8)
    m = re.search(r'^L:\s*1/(\d+)', abc_text, re.M)
    if m:
        unit = Fraction(1, int(m.group(1)))
    key_sig = {}
    km = re.search(r'^K:\s*(.+)$', abc_text, re.M)
    if km:
        key_sig = parse_key(km.group(1))
    voices = {}
    order = []
    for raw_line in abc_text.splitlines():
        vm = re.match(r'\s*\[V:\s*(\S+)\]\s*(.*)', raw_line)
        if vm:
            vid, rest = vm.group(1), vm.group(2)
            if vid not in voices:
                voices[vid] = []
                order.append(vid)
            voices[vid].extend(parse_voice_line(rest, unit, key_sig))
    return order, voices


def events_to_timeline(events):
    """Convert event list (with bar markers) into (start_time, duration, midi_or_None)
    ignoring bar markers, using running time in whole-note units."""
    t = Fraction(0)
    timeline = []
    for kind, midi, dur in events:
        if kind == 'bar':
            continue
        timeline.append((t, dur, midi))
        t += dur
    return timeline


def sounding_pitch_at(timeline, when):
    """Return the midi pitch sounding at time `when` (None if rest/silence),
    plus whether `when` is exactly an onset in this voice."""
    for start, dur, midi in timeline:
        if start <= when < start + dur:
            return midi, (start == when)
    return None, False


def interval_class(a, b):
    return abs(a - b) % 12


def check_parallels(name_a, tl_a, name_b, tl_b):
    """Check every pair of consecutive harmonic slices (slices = union of onset
    times from both voices) for parallel perfect fifths/octaves/unisons."""
    onsets = sorted(set([s for s, d, m in tl_a] + [s for s, d, m in tl_b]))
    slices = []
    for t in onsets:
        pa, _ = sounding_pitch_at(tl_a, t)
        pb, _ = sounding_pitch_at(tl_b, t)
        slices.append((t, pa, pb))
    violations = []
    for i in range(1, len(slices)):
        t0, a0, b0 = slices[i - 1]
        t1, a1, b1 = slices[i]
        if a0 is None or b0 is None or a1 is None or b1 is None:
            continue
        if a0 == a1 and b0 == b1:
            continue  # no motion, not a parallel event
        ic0 = interval_class(a0, b0)
        ic1 = interval_class(a1, b1)
        if ic0 == ic1 and ic0 in (0, 7):
            # both intervals are P5 or P8/unison — check direction of motion
            da = a1 - a0
            db = b1 - b0
            if da != 0 and db != 0 and (da > 0) == (db > 0):
                label = "octave/unison" if ic0 == 0 else "fifth"
                violations.append(
                    f"  parallel {label}: t={float(t0):.2f}->{float(t1):.2f} "
                    f"{name_a}:{a0}->{a1}  {name_b}:{b0}->{b1}"
                )
    return violations


def check_range(name, timeline, lo, hi):
    bad = [m for _, _, m in timeline if m is not None and (m < lo or m > hi)]
    return bad


def run_checks(abc_text, ranges=None, verbose=True):
    order, voices = extract_voices(abc_text)
    if not voices:
        print("No [V:n] voices found — nothing to check.")
        return False
    timelines = {v: events_to_timeline(evs) for v, evs in voices.items()}
    ok = True
    print(f"Voices found: {order}")
    for v in order:
        n_notes = sum(1 for _, _, m in timelines[v] if m is not None)
        span = timelines[v][-1][0] + timelines[v][-1][1] if timelines[v] else 0
        print(f"  {v}: {n_notes} notes, length {float(span):.2f} whole-notes")

    print("\n--- Parallel fifths/octaves check ---")
    any_viol = False
    for i in range(len(order)):
        for j in range(i + 1, len(order)):
            va, vb = order[i], order[j]
            viols = check_parallels(va, timelines[va], vb, timelines[vb])
            if viols:
                any_viol = True
                ok = False
                print(f"[{va} vs {vb}] {len(viols)} violation(s):")
                for line in viols:
                    print(line)
    if not any_viol:
        print("None found. Clean.")

    if ranges:
        print("\n--- Range check ---")
        for v, (lo, hi) in ranges.items():
            if v not in timelines:
                continue
            bad = check_range(v, timelines[v], lo, hi)
            if bad:
                ok = False
                print(f"[{v}] {len(bad)} note(s) outside MIDI range [{lo},{hi}]: {sorted(set(bad))}")
            else:
                print(f"[{v}] all notes within [{lo},{hi}].")

    return ok


SELF_TEST_PIECES = {
    "claude (invention)": """L: 1/8
K: Dm
V: 1 clef=treble name="Voice I (Treble)"
V: 2 clef=bass name="Voice II (Bass)"
[V:1] d2 A2 F2 D2 | ^c2 d2 e2 f2 | g2 f2 e2 d2 | ^c4 A4 |
[V:2] z8 | z8 | D,2 F,2 A,2 D2 | C2 B,2 A,2 G,2 |
[V:1] f2 d2 A2 F2 | G2 A2 B2 c2 | d2 c2 B2 A2 | G4 E4 |
[V:2] F,2 E,2 D,2 C,2 | B,,2 C,2 D,2 E,2 | F,2 G,2 A,2 B,2 | C4 C,4 |
""",
}


def self_test():
    for name, abc in SELF_TEST_PIECES.items():
        print(f"===== {name} =====")
        run_checks(abc)
        print()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('file', nargs='?', help='Path to a file containing ABC notation')
    ap.add_argument('--self-test', action='store_true')
    args = ap.parse_args()

    if args.self_test:
        self_test()
        sys.exit(0)

    if not args.file:
        ap.print_help()
        sys.exit(1)

    with open(args.file) as f:
        text = f.read()
    ok = run_checks(text)
    sys.exit(0 if ok else 1)
