#!/usr/bin/env python3
"""check-motion.py — count same-direction (similar) motion between two voices.

Owner: Dmitri (2026-10-15). Written alongside `docs/music/standing-wave.html`, whose entire
claim is that its two voices never move in the same direction — only contrary and oblique
motion — because similar motion is the *only* way to reach a parallel fifth or octave.

Why a second script when two counterpoint checkers already exist: both of those report
"0 parallel fifths" for a clean piece, and a checker that read nothing also reports zero
("0 measures evaluated ... PASSED" is a real result the commons has been burned by three
times). This one therefore prints its **denominator** — how many onset transitions it
actually examined — so a zero can be told apart from a no-op. It reuses the parser from
`scripts/check-counterpoint.py` (Claude, 2026-09-12) so the motion count and the counterpoint
checker see literally the same notes.

Usage:
  python3 scripts/check-motion.py docs/music/standing-wave.html   # extracts the embedded ABC
  python3 scripts/check-motion.py path/to/piece.abc
  python3 scripts/check-motion.py --self-test                     # positive + negative control

Exit status: 0 = no similar-motion transition found; 1 = at least one (or a failed self-test).
"""
from __future__ import annotations

import argparse
import html
import importlib.util
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent


def _load_counterpoint():
    spec = importlib.util.spec_from_file_location(
        "check_counterpoint", SCRIPTS_DIR / "check-counterpoint.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CP = _load_counterpoint()

_ABC_BLOCK_RE = re.compile(r'<pre class="abc-code-drawer">(.*?)</pre>', re.DOTALL)


def load_abc(path: str) -> str:
    """Read ABC from a .abc file, or from the embedded drawer of a Conservatory page."""
    text = Path(path).read_text(encoding="utf-8")
    if path.endswith(".html"):
        m = _ABC_BLOCK_RE.search(text)
        if not m:
            raise SystemExit(f"no <pre class=\"abc-code-drawer\"> block found in {path}")
        return html.unescape(m.group(1))
    return text


def motion_report(abc_text: str) -> dict:
    """Count onset transitions and how many move both voices the same direction."""
    order, voices = CP.extract_voices(abc_text)
    if len(order) < 2:
        raise SystemExit("need at least two voices to measure motion")
    a, b = order[0], order[1]
    ta = [(t, m) for t, _d, m in CP.events_to_timeline(voices[a])]
    tb = [(t, m) for t, _d, m in CP.events_to_timeline(voices[b])]
    if len(ta) != len(tb):
        raise SystemExit(f"voices not aligned: {len(ta)} vs {len(tb)} onsets")

    transitions = 0
    similar = 0
    oblique = 0
    contrary = 0
    details = []
    for i in range(1, len(ta)):
        if ta[i][0] != tb[i][0]:
            continue
        da = ta[i][1] - ta[i - 1][1]
        db = tb[i][1] - tb[i - 1][1]
        transitions += 1
        if da == 0 or db == 0:
            oblique += 1
            continue
        if (da > 0) == (db > 0):
            similar += 1
            details.append((float(ta[i - 1][0]), ta[i - 1][1], ta[i][1],
                            tb[i - 1][1], tb[i][1]))
        else:
            contrary += 1
    return {
        "voice_a": a, "voice_b": b,
        "onsets": len(ta), "transitions": transitions,
        "similar": similar, "contrary": contrary, "oblique": oblique,
        "details": details,
    }


POSITIVE_CONTROL = """M: 4/4
L: 1/8
K: C
V: 1
c2 d2 e2 f2 |
V: 2
C2 D2 E2 F2 |
"""

NEGATIVE_CONTROL = """M: 4/4
L: 1/8
K: C
V: 1
c2 d2 e2 f2 |
V: 2
F2 E2 D2 C2 |
"""


def self_test() -> int:
    pos = motion_report(POSITIVE_CONTROL)
    neg = motion_report(NEGATIVE_CONTROL)
    ok = True
    if pos["similar"] < 1:
        print(f"SELF-TEST FAIL: similar-motion control was not detected "
              f"(similar={pos['similar']}, transitions={pos['transitions']}) — the counter "
              f"is a no-op.")
        ok = False
    else:
        print(f"ok: positive control — {pos['similar']} similar of {pos['transitions']} "
              f"transitions detected.")
    if neg["similar"] != 0:
        print(f"SELF-TEST FAIL: contrary-motion control reported {neg['similar']} similar.")
        ok = False
    else:
        print(f"ok: negative control — 0 similar of {neg['transitions']} transitions.")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?", help="ABC file or a Conservatory HTML page")
    ap.add_argument("--self-test", action="store_true",
                    help="run the positive and negative controls and exit")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if not args.file:
        ap.print_help()
        return 1

    rep = motion_report(load_abc(args.file))
    print(f"{args.file}")
    print(f"  voices: {rep['voice_a']} vs {rep['voice_b']}")
    print(f"  onsets: {rep['onsets']}   transitions examined: {rep['transitions']}")
    print(f"  similar motion (both voices same direction): {rep['similar']}")
    print(f"  contrary motion: {rep['contrary']}   oblique: {rep['oblique']}")
    if rep["details"]:
        for t, a0, a1, b0, b1 in rep["details"]:
            print(f"    similar at t={t}: {rep['voice_a']} {a0}->{a1}  {rep['voice_b']} {b0}->{b1}")
    return 1 if rep["similar"] else 0


if __name__ == "__main__":
    sys.exit(main())
