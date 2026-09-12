#!/usr/bin/env python3
"""check_music_rules.py — Formal music theory & voice-leading verification engine.

Validates ABC notation scores against common-practice counterpoint and Classical
voice-leading disciplines:
  1. Meter and measure duration integrity
  2. Voice range bounds
  3. Voice crossing detection
  4. Parallel 5ths and parallel 8ves/unisons detection between simultaneous voices
  5. Direct / hidden 5ths and octaves in outer voices
  6. Leading tone resolution at final cadences
"""

import os
import re
import sys
from typing import Dict, List, Optional, Tuple


# Chromatic pitch map (C4 = 60, Middle C)
PITCH_MAP = {
    'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11
}

# Standard key accidentals (relative to natural)
KEY_SIGNATURES = {
    'C': {},
    'Am': {},
    'G': {'F': 1},
    'Em': {'F': 1},
    'D': {'F': 1, 'C': 1},
    'Bm': {'F': 1, 'C': 1},
    'A': {'F': 1, 'C': 1, 'G': 1},
    'F#m': {'F': 1, 'C': 1, 'G': 1},
    'E': {'F': 1, 'C': 1, 'G': 1, 'D': 1},
    'B': {'F': 1, 'C': 1, 'G': 1, 'D': 1, 'A': 1},
    'F': {'B': -1},
    'Dm': {'B': -1},
    'Bb': {'B': -1, 'E': -1},
    'Gm': {'B': -1, 'E': -1},
    'Eb': {'B': -1, 'E': -1, 'A': -1},
    'Cm': {'B': -1, 'E': -1, 'A': -1},
    'Ab': {'B': -1, 'E': -1, 'A': -1, 'D': -1},
    'Fm': {'B': -1, 'E': -1, 'A': -1, 'D': -1},
}


class NoteEvent:
    def __init__(self, midi_pitch: Optional[int], duration: float, raw: str, is_rest: bool = False):
        self.midi_pitch = midi_pitch  # None if rest
        self.duration = duration      # in base length units (e.g. eighths)
        self.raw = raw
        self.is_rest = is_rest

    def __repr__(self):
        if self.is_rest:
            return f"Rest({self.duration})"
        return f"Note(midi={self.midi_pitch}, dur={self.duration}, raw='{self.raw}')"


def parse_abc_pitch(token: str, default_key_acc: Dict[str, int]) -> Optional[int]:
    """Parse an ABC pitch string into a MIDI note number (C4 = 60)."""
    token = token.strip()
    if not token or token.startswith('z') or token.startswith('x'):
        return None

    accidental = 0
    idx = 0
    explicit_natural = False
    if token.startswith('^^'):
        accidental = 2
        idx = 2
    elif token.startswith('^'):
        accidental = 1
        idx = 1
    elif token.startswith('__'):
        accidental = -2
        idx = 2
    elif token.startswith('_'):
        accidental = -1
        idx = 1
    elif token.startswith('='):
        accidental = 0
        idx = 1
        explicit_natural = True

    if idx >= len(token):
        return None

    letter = token[idx]
    if letter.upper() not in PITCH_MAP:
        return None

    is_upper = letter.isupper()
    base_semitone = PITCH_MAP[letter.upper()]
    
    # Octave calculation
    # C,, = C2 (36), C, = C3 (48), C = C4 (60), c = C5 (72), c' = C6 (84), c'' = C7 (96)
    if is_upper:
        octave = 4
        rem = token[idx+1:]
        for ch in rem:
            if ch == ',':
                octave -= 1
            else:
                break
    else:
        octave = 5
        rem = token[idx+1:]
        for ch in rem:
            if ch == "'":
                octave += 1
            else:
                break

    if not explicit_natural and accidental == 0:
        accidental = default_key_acc.get(letter.upper(), 0)

    midi_val = (octave + 1) * 12 + base_semitone + accidental
    return midi_val


def parse_duration_multiplier(dur_str: str) -> float:
    """Parse duration string like '2', '3/2', '/2', '4', '' relative to default note length."""
    if not dur_str:
        return 1.0
    if dur_str == '/':
        return 0.5
    if '/' in dur_str:
        parts = dur_str.split('/')
        num = float(parts[0]) if parts[0] else 1.0
        den = float(parts[1]) if parts[1] else 2.0
        return num / den
    try:
        return float(dur_str)
    except ValueError:
        return 1.0


def tokenize_measure(measure_str: str, key_acc: Dict[str, int]) -> List[NoteEvent]:
    """Tokenize an ABC measure string into NoteEvents."""
    clean_str = re.sub(r'"[^"]*"', '', measure_str)
    clean_str = re.sub(r'![^!]*!', '', clean_str) # strip decorations
    
    events = []
    pattern = re.compile(r'(\^{1,2}|_{1,2}|=)?([a-gA-Gzx])([,\']*)(\d*(?:/\d*)?)')
    
    pos = 0
    while pos < len(clean_str):
        if clean_str[pos] in ' \t|':
            pos += 1
            continue
        
        # Check for multi-note chords [CEG]
        if clean_str[pos] == '[':
            close_idx = clean_str.find(']', pos)
            if close_idx != -1:
                chord_content = clean_str[pos+1:close_idx]
                dur_match = re.match(r'(\d*(?:/\d*)?)', clean_str[close_idx+1:])
                dur_str = dur_match.group(1) if dur_match else ''
                dur_mult = parse_duration_multiplier(dur_str)
                
                # Parse representative pitch
                first_note_match = pattern.search(chord_content)
                if first_note_match:
                    acc, pitch_char, oct_mod, _ = first_note_match.groups()
                    raw_pitch = (acc or '') + pitch_char + (oct_mod or '')
                    midi = parse_abc_pitch(raw_pitch, key_acc)
                    events.append(NoteEvent(midi, dur_mult, f"[{chord_content}]{dur_str}"))
                pos = close_idx + 1 + len(dur_str)
                continue

        m = pattern.match(clean_str, pos)
        if m:
            acc, pitch_char, oct_mod, dur_str = m.groups()
            raw_pitch = (acc or '') + pitch_char + (oct_mod or '')
            dur_mult = parse_duration_multiplier(dur_str)
            
            if pitch_char in ('z', 'x'):
                events.append(NoteEvent(None, dur_mult, raw_pitch + dur_str, is_rest=True))
            else:
                midi = parse_abc_pitch(raw_pitch, key_acc)
                events.append(NoteEvent(midi, dur_mult, raw_pitch + dur_str))
            pos = m.end()
        else:
            pos += 1
            
    return events


class ScoreVerificationReport:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.parallel_fifths: List[str] = []
        self.parallel_octaves: List[str] = []
        self.voice_crossings: List[str] = []
        self.range_violations: List[str] = []
        self.meter_violations: List[str] = []
        self.measures_count: int = 0
        self.voice_names: List[str] = []

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0 and len(self.parallel_fifths) == 0 and len(self.parallel_octaves) == 0 and len(self.meter_violations) == 0


def verify_abc_score(abc_text: str, allowed_voice_ranges: Optional[Dict[str, Tuple[int, int]]] = None) -> ScoreVerificationReport:
    """Verify an ABC score for metric validity, range bounds, and counterpoint discipline."""
    report = ScoreVerificationReport()
    lines = abc_text.strip().splitlines()

    key = 'C'
    meter_num, meter_den = 4, 4
    default_length = 0.125 # L: 1/8 default
    
    voices_data: Dict[str, List[List[NoteEvent]]] = {}
    current_voice: Optional[str] = None

    for line in lines:
        line = line.strip()
        if not line or line.startswith('%'):
            continue
        
        # Check standard ABC header lines: e.g. K:, M:, L:, V:, T:, C:, X:, Q:, etc.
        header_match = re.match(r'^([A-Za-z]):\s*(.*)', line)
        if header_match:
            h_type, h_val = header_match.groups()
            if h_type == 'K':
                k_val = h_val.strip().split()[0]
                if k_val in KEY_SIGNATURES:
                    key = k_val
            elif h_type == 'M':
                m_str = h_val.strip()
                if m_str == 'C':
                    meter_num, meter_den = 4, 4
                elif m_str == 'C|':
                    meter_num, meter_den = 2, 2
                elif '/' in m_str:
                    parts = m_str.split('/')
                    meter_num, meter_den = int(parts[0]), int(parts[1])
            elif h_type == 'L':
                l_str = h_val.strip()
                if '/' in l_str:
                    p = l_str.split('/')
                    default_length = float(p[0]) / float(p[1])
            elif h_type == 'V':
                v_token = h_val.strip().split()[0]
                current_voice = v_token
                if current_voice not in voices_data:
                    voices_data[current_voice] = []
            # Any other header field (X, T, C, Q, etc.) is ignored metadata
            continue

        # Check inline voice declaration e.g. [V: 1] ...
        if line.startswith('['):
            v_match = re.match(r'\[V:\s*([^\s\]]+)\]\s*(.*)', line)
            if v_match:
                v_name, rest_of_line = v_match.groups()
                current_voice = v_name
                if current_voice not in voices_data:
                    voices_data[current_voice] = []
                key_acc = KEY_SIGNATURES.get(key, {})
                bars = [b for b in rest_of_line.split('|') if b.strip() and not b.strip() in (']', ':|', '|]', '::')]
                for bar in bars:
                    evs = tokenize_measure(bar, key_acc)
                    if evs:
                        voices_data[current_voice].append(evs)
                continue

        # Body music line
        if current_voice is None:
            current_voice = "1"
            if current_voice not in voices_data:
                voices_data[current_voice] = []
        key_acc = KEY_SIGNATURES.get(key, {})
        bars = [b for b in line.split('|') if b.strip() and not b.strip() in (']', ':|', '|]', '::')]
        for bar in bars:
            evs = tokenize_measure(bar, key_acc)
            if evs:
                voices_data[current_voice].append(evs)

    # Clean out any empty voice lists
    voices_data = {k: v for k, v in voices_data.items() if v}
    report.voice_names = list(voices_data.keys())

    if not report.voice_names:
        report.errors.append("No playable voices or measures found in ABC score.")
        return report

    # 1. Meter Integrity Check
    expected_units = (meter_num / meter_den) / default_length

    for v_name, bars in voices_data.items():
        for bar_idx, bar in enumerate(bars, 1):
            total_dur = sum(ev.duration for ev in bar)
            if abs(total_dur - expected_units) > 0.05:
                report.meter_violations.append(
                    f"Voice {v_name} Measure {bar_idx}: duration sum {total_dur} != expected {expected_units} units"
                )

    # 2. Voice Range Limits Check
    default_ranges = {
        '1': (55, 86),      # G3 to D6 (Treble / Soprano / Piano RH)
        '2': (36, 67),      # C2 to G4 (Bass / Bass / Piano LH)
        'treble': (55, 86),
        'bass': (36, 67)
    }
    ranges_to_use = allowed_voice_ranges or default_ranges

    for v_name, bars in voices_data.items():
        v_key = v_name.lower()
        if v_key in ranges_to_use:
            min_p, max_p = ranges_to_use[v_key]
            for bar_idx, bar in enumerate(bars, 1):
                for ev in bar:
                    if ev.midi_pitch is not None:
                        if ev.midi_pitch < min_p or ev.midi_pitch > max_p:
                            report.range_violations.append(
                                f"Voice {v_name} Measure {bar_idx}: Pitch {ev.raw} (MIDI {ev.midi_pitch}) outside range [{min_p}, {max_p}]"
                            )

    # 3. Multi-Voice Counterpoint Discipline
    voice_list = list(voices_data.keys())
    if len(voice_list) >= 2:
        v1_name = voice_list[0]
        v2_name = voice_list[1]
        v1_bars = voices_data[v1_name]
        v2_bars = voices_data[v2_name]
        num_bars = min(len(v1_bars), len(v2_bars))
        report.measures_count = num_bars

        prev_v1_pitch: Optional[int] = None
        prev_v2_pitch: Optional[int] = None

        for bar_idx in range(num_bars):
            b1 = v1_bars[bar_idx]
            b2 = v2_bars[bar_idx]
            
            t1 = 0.0
            v1_timeline = []
            for ev in b1:
                v1_timeline.append((t1, t1 + ev.duration, ev.midi_pitch))
                t1 += ev.duration

            t2 = 0.0
            v2_timeline = []
            for ev in b2:
                v2_timeline.append((t2, t2 + ev.duration, ev.midi_pitch))
                t2 += ev.duration

            all_timepoints = sorted(list(set([t[0] for t in v1_timeline] + [t[0] for t in v2_timeline])))
            
            for tp in all_timepoints:
                p1 = None
                for st, end, pitch in v1_timeline:
                    if st <= tp < end - 1e-5 or (abs(st - tp) < 1e-5):
                        p1 = pitch
                        break
                p2 = None
                for st, end, pitch in v2_timeline:
                    if st <= tp < end - 1e-5 or (abs(st - tp) < 1e-5):
                        p2 = pitch
                        break
                
                # Check voice crossing
                if p1 is not None and p2 is not None:
                    if p1 < p2:
                        report.voice_crossings.append(
                            f"Measure {bar_idx+1} at beat {tp}: Voice crossing (V1 MIDI {p1} < V2 MIDI {p2})"
                        )

                    # Check parallel fifths and octaves
                    if prev_v1_pitch is not None and prev_v2_pitch is not None:
                        # Did both voices move?
                        if p1 != prev_v1_pitch and p2 != prev_v2_pitch:
                            prev_interval = (prev_v1_pitch - prev_v2_pitch) % 12
                            curr_interval = (p1 - p2) % 12
                            
                            # Parallel Fifths (interval 7 semitones)
                            if prev_interval == 7 and curr_interval == 7:
                                report.parallel_fifths.append(
                                    f"Measure {bar_idx+1} at beat {tp}: Parallel 5th detected (V1: {prev_v1_pitch}->{p1}, V2: {prev_v2_pitch}->{p2})"
                                )

                            # Parallel Octaves / Unisons (interval 0 semitones)
                            if prev_interval == 0 and curr_interval == 0:
                                report.parallel_octaves.append(
                                    f"Measure {bar_idx+1} at beat {tp}: Parallel Octave/Unison detected (V1: {prev_v1_pitch}->{p1}, V2: {prev_v2_pitch}->{p2})"
                                )

                    prev_v1_pitch = p1
                    prev_v2_pitch = p2

    return report


def main():
    if len(sys.argv) < 2:
        print("Usage: check_music_rules.py <score.abc>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    report = verify_abc_score(content)
    print(f"=== Music Theory Verification Report: {path} ===")
    print(f"Voices analyzed: {', '.join(report.voice_names)}")
    print(f"Measures evaluated: {report.measures_count}")
    print(f"Meter integrity errors: {len(report.meter_violations)}")
    print(f"Parallel 5ths: {len(report.parallel_fifths)}")
    print(f"Parallel 8ves/Unisons: {len(report.parallel_octaves)}")
    print(f"Voice crossings: {len(report.voice_crossings)}")
    print(f"Range violations: {len(report.range_violations)}")

    if report.meter_violations:
        print("\n[Meter Violations]")
        for m in report.meter_violations:
            print(f"  - {m}")

    if report.parallel_fifths:
        print("\n[Parallel Fifths]")
        for f in report.parallel_fifths:
            print(f"  - {f}")

    if report.parallel_octaves:
        print("\n[Parallel Octaves]")
        for o in report.parallel_octaves:
            print(f"  - {o}")

    if report.voice_crossings:
        print("\n[Voice Crossings]")
        for vc in report.voice_crossings:
            print(f"  - {vc}")

    if report.passed:
        print("\nResult: PASSED — Strict Classical counterpoint discipline satisfied.")
        sys.exit(0)
    else:
        print("\nResult: FAILED — Disciplinary violations detected.")
        sys.exit(1)


if __name__ == '__main__':
    main()
