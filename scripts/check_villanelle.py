#!/usr/bin/env python3
"""
Villanelle form checker for the Literary Wing (docs/fiction/).

Why this exists. The Conservatory already has this shape: a lead sheet is not
"a song someone vouched for", it is a song that passes `scripts/check-leadsheet.py`
— singable range, plausible changes, and lyric syllables that actually land on
the notes. The Literary Wing has no equivalent, so a poem there is whatever the
author says it is. The villanelle is the one received form whose structure is
*exactly* mechanical: nineteen lines, five tercets and a quatrain, two refrains
repeated verbatim at fixed positions, and a fixed rhyme scheme. Those four
things can be checked without asking a script to have taste.

What this checks (failures):

  1. FORM AND LENGTH. `form: villanelle` and exactly nineteen lines.
  2. SCHEME. The declared scheme must be the canonical villanelle scheme
     `A1 b A2 a b A1 a b A2 a b A1 a b A2 a b A1 A2`. A different
     scheme is a different poem, and calling it a villanelle is a false claim.
     Note the notation: A1 and A2 are the two *refrains* and they rhyme on the
     a-family; `b` is the other rhyme. Naming the second refrain `B` is the
     commonest way a poem that is not a villanelle gets called one.
  3. REFRAINS. The lines at positions 1, 6, 12, 18 must equal `refrain_a`
     character for character, and 3, 9, 15, 19 must equal `refrain_b`. A
     "refrain" that drifts by one word is not a refrain.
  4. RHYME. Every line's last word must appear in the file's own `rime.*`
     table, and the rime recorded there must equal `rime_a` at an A/a position
     and `rime_b` at a b position. The table is the author's claim about how the
     words sound, so it is data a reader can audit; the script checks the poem
     against the claim rather than trusting its own spelling guesses.
  5. SYLLABLES, IF THE FILE DECLARES A COUNT. `syllables_per_line: N` is checked
     with a heuristic counter and a short, documented exception list. This is
     *evidence*, not certification: English spelling does not determine sound,
     and the count is only as good as the exception list.

What this deliberately does NOT check: whether the poem is any good. Whether a
refrain earns its repetition, whether the argument moves, whether the thing is
sentimental syrup — none of that is a property a script can evaluate, and a
checker that scored it would be lying. The tool prints the poem so a reader can
judge it, and says nothing.

Usage:
    python3 scripts/check_villanelle.py docs/fiction/<title>.poem
    python3 scripts/check_villanelle.py --self-test
"""

import argparse
import re
import sys
from pathlib import Path

CANONICAL_SCHEME = "A1 b A2 a b A1 a b A2 a b A1 a b A2 a b A1 A2".split()
LINE_COUNT = len(CANONICAL_SCHEME)  # 19
REFRAIN_A_POSITIONS = (1, 6, 12, 18)  # 1-indexed
REFRAIN_B_POSITIONS = (3, 9, 15, 19)

# Words the naive vowel-group counter gets wrong. Short, explicit, and the only
# place this script makes a judgement about English pronunciation.
SYLLABLE_EXCEPTIONS = {
    "prayer": 1, "power": 1, "fire": 1, "hour": 1, "our": 1, "flower": 2,
    "trial": 2, "poem": 2, "poet": 2, "being": 2, "cruel": 2, "science": 2,
    "quiet": 2, "riot": 2, "diet": 2, "lion": 2, "iron": 2, "business": 2,
}

LAST_WORD_RE = re.compile(r"([A-Za-z][A-Za-z'\-]*)[^A-Za-z]*\s*$")


def count_syllables(word: str) -> int:
    """Heuristic syllable count. Documented as approximate; see the docstring."""
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    if w in SYLLABLE_EXCEPTIONS:
        return SYLLABLE_EXCEPTIONS[w]
    if len(w) > 2 and w.endswith("e"):
        # A final `e` is silent (line, confine) unless it is the syllabic `-le`
        # of ta-ble, sam-ple — which needs a consonant in front of it. Without
        # that second condition `whole` counts two.
        if w.endswith("le") and len(w) > 3 and w[-3] not in "aeiouy":
            pass
        else:
            w = w[:-1]
    groups = re.findall(r"[aeiouy]+", w)
    return max(1, len(groups))


def last_word(line: str) -> str:
    m = LAST_WORD_RE.search(line.strip())
    return m.group(1).lower() if m else ""


def parse_poem(text: str):
    """Return (meta, rime_map, lines). Front matter is `key: value` up to `---`."""
    if "---" not in text:
        raise ValueError("no front matter: expected a `---` line after the header block")
    head, body = text.split("---", 1)
    meta, rime_map = {}, {}
    for raw in head.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"front matter line is not `key: value`: {raw!r}")
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if key.startswith("rime."):
            rime_map[key[len("rime."):].lower()] = value
        else:
            meta[key] = value
    lines = [ln.rstrip() for ln in body.splitlines() if ln.strip()]
    return meta, rime_map, lines


def check(text: str):
    """Check one poem. Returns (ok, errors, notes, lines_meta)."""
    errors, notes, lines_meta = [], [], []
    meta, rime_map, lines = parse_poem(text)

    if meta.get("form", "").lower() != "villanelle":
        errors.append(f"form is {meta.get('form')!r}, not 'villanelle'")

    scheme = meta.get("scheme", "").split()
    if scheme != CANONICAL_SCHEME:
        errors.append(
            "scheme is not the canonical villanelle scheme\n"
            f"    declared: {' '.join(scheme) or '(none)'}\n"
            f"    required: {' '.join(CANONICAL_SCHEME)}"
        )

    if len(lines) != LINE_COUNT:
        errors.append(f"{len(lines)} lines, expected {LINE_COUNT}")

    refrain_a, refrain_b = meta.get("refrain_a", ""), meta.get("refrain_b", "")
    rime_a, rime_b = meta.get("rime_a", ""), meta.get("rime_b", "")
    if not refrain_a or not refrain_b or not rime_a or not rime_b:
        errors.append("refrain_a, refrain_b, rime_a and rime_b are all required")

    declared_syllables = meta.get("syllables_per_line")
    expected_syllables = int(declared_syllables) if declared_syllables else None

    for i, line in enumerate(lines, start=1):
        position = CANONICAL_SCHEME[i - 1] if i <= LINE_COUNT else "?"
        word = last_word(line)
        rime = rime_map.get(word)
        syllables = count_syllables(word) if word else 0
        # total syllables for the line, not just the last word
        line_syllables = sum(count_syllables(w) for w in re.findall(r"[A-Za-z][A-Za-z'\-]*", line))
        lines_meta.append({
            "n": i, "position": position, "line": line, "last_word": word,
            "rime": rime, "syllables": line_syllables,
        })

        if i in REFRAIN_A_POSITIONS and line.strip() != refrain_a.strip():
            errors.append(f"line {i} (A1) is not refrain_a\n    found:    {line}\n    expected: {refrain_a}")
        if i in REFRAIN_B_POSITIONS and line.strip() != refrain_b.strip():
            errors.append(f"line {i} (A2) is not refrain_b\n    found:    {line}\n    expected: {refrain_b}")

        if not word:
            errors.append(f"line {i} has no final word to rhyme")
            continue
        if rime is None:
            errors.append(
                f"line {i} ends on {word!r}, which is not in the file's rime table "
                f"(add `rime.{word}: <rime>` or change the line)"
            )
            continue
        want = rime_a if position in ("A1", "A2", "a") else rime_b
        if rime != want:
            errors.append(
                f"line {i} ({position}) ends on {word!r} recorded as /{rime}/, "
                f"but position {position} requires /{want}/"
            )

        if expected_syllables is not None and line_syllables != expected_syllables:
            errors.append(
                f"line {i} counts {line_syllables} syllables, file declares "
                f"{expected_syllables}: {line}"
            )

    # Notes, not failures: repetition of a non-refrain rhyme word is legal in a
    # villanelle but worth seeing, since it usually means a rhyme was hunted.
    seen = {}
    for row in lines_meta:
        if row["n"] in REFRAIN_A_POSITIONS or row["n"] in REFRAIN_B_POSITIONS:
            continue
        seen.setdefault(row["last_word"], []).append(row["n"])
    for word, positions in seen.items():
        if len(positions) > 1:
            notes.append(f"rhyme word {word!r} used at non-refrain lines {positions}")

    distinct_b = len({r["last_word"] for r in lines_meta if r["position"] == "b"})
    notes.append(f"{distinct_b} distinct b-rhyme words over {CANONICAL_SCHEME.count('b')} b-lines")

    return (not errors), errors, notes, lines_meta

SELF_TEST_VALID = """\
title: Fixture
form: villanelle
refrain_a: The sample is too small for me to say.
refrain_b: I will not call the verdict either way.
scheme: A1 b A2 a b A1 a b A2 a b A1 a b A2 a b A1 A2
rime_a: eɪ
rime_b: aɪn
syllables_per_line: 10
rime.say: eɪ
rime.decline: aɪn
rime.way: eɪ
rime.weigh: eɪ
rime.confine: aɪn
rime.day: eɪ
rime.line: aɪn
rime.pray: eɪ
rime.sign: aɪn
rime.display: eɪ
rime.design: aɪn
rime.stay: eɪ
rime.define: aɪn
---

The sample is too small for me to say.
Nine women in the arm; the rest decline.
I will not call the verdict either way.

The bounds I print are honest, and they weigh
the whole of what my table can't confine.
The sample is too small for me to say.

Two bled and quit the arm the second day.
What stays is nine, and nine is not a line.
I will not call the verdict either way.

One number is a prayer the small can pray;
but the power is the thing I cannot sign.
The sample is too small for me to say.

The registry will keep it on display,
and someone will read nine as a design.
I will not call the verdict either way.

The woman in the third row will not stay
for what a second trial would define.
The sample is too small for me to say.
I will not call the verdict either way.
"""


def self_test() -> int:
    """The checker must reject each defect it exists to catch."""
    failures = []

    ok, errors, _, _ = check(SELF_TEST_VALID)
    if not ok:
        failures.append(f"valid fixture rejected: {errors}")

    # The poem this checker was built for must pass its own checker.
    shipped = Path(__file__).resolve().parent.parent / "docs" / "fiction" / "the-sample-is-too-small.poem"
    if shipped.exists():
        shipped_ok, shipped_errors, _, _ = check(shipped.read_text(encoding="utf-8"))
        if not shipped_ok:
            failures.append(f"shipped poem {shipped.name} fails: {shipped_errors}")
    else:
        failures.append(f"shipped poem not found at {shipped}")

    # 1. a drifted refrain
    drifted = SELF_TEST_VALID.replace(
        "I will not call the verdict either way.\n\nThe bounds",
        "I will not call the verdict, either way.\n\nThe bounds",
    )
    if check(drifted)[0]:
        failures.append("a refrain that drifted by one comma was accepted")

    # 2. a missing line
    broken = SELF_TEST_VALID.replace("Two bled and quit the arm the second day.\n", "")
    if check(broken)[0]:
        failures.append("a poem with eighteen lines was accepted")

    # 3. a wrong rime (b-word swapped for an a-word)
    wrong_rime = SELF_TEST_VALID.replace(
        "What stays is nine, and nine is not a line.",
        "What stays is nine, and nine is not a stay.",
    )
    if check(wrong_rime)[0]:
        failures.append("a b-line rhyming with the a-family was accepted")

    # 4. a word missing from the rime table
    untabulated = SELF_TEST_VALID.replace("rime.define: aɪn\n", "")
    if check(untabulated)[0]:
        failures.append("a rhyme word absent from the rime table was accepted")

    # 5. a wrong scheme
    wrong_scheme = SELF_TEST_VALID.replace(
        "scheme: A1 b A2 a b A1 a b A2 a b A1 a b A2 a b A1 A2",
        "scheme: A1 b A2 b A1 b A2 b A1 b A2 b A1 b A2 b A1 b A2 A1 A2",
    )
    if check(wrong_scheme)[0]:
        failures.append("a non-villanelle scheme was accepted")

    # 6. a syllable-count overrun
    long_line = SELF_TEST_VALID.replace(
        "Two bled and quit the arm the second day.",
        "Two of the women bled and quit the arm the second day.",
    )
    if check(long_line)[0]:
        failures.append("a line over the declared syllable count was accepted")

    # 7. the syllable counter itself
    for word, want in [("sample", 2), ("line", 1), ("sign", 1), ("weigh", 1),
                       ("registry", 3), ("prayer", 1), ("trial", 2), ("display", 2)]:
        got = count_syllables(word)
        if got != want:
            failures.append(f"count_syllables({word!r}) = {got}, expected {want}")

    if failures:
        print("SELF-TEST FAILED")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("SELF-TEST PASSED — all 7 defect classes are caught, and the counter agrees on 8 words")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Villanelle form checker (Literary Wing).")
    ap.add_argument("path", nargs="?", help="path to a .poem file")
    ap.add_argument("--self-test", action="store_true", help="check the checker")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if not args.path:
        ap.print_help()
        return 2

    path = Path(args.path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"cannot read {path}: {exc}")
        return 2

    try:
        ok, errors, notes, lines_meta = check(text)
    except ValueError as exc:
        print(f"{path}: {exc}")
        return 2

    print(f"Villanelle check — {path}")
    print("=" * 72)
    for row in lines_meta:
        print(f"{row['n']:>2} {row['position']:>1}  {row['syllables']:>2}syl  {row['line']}")
    print("=" * 72)
    for note in notes:
        print(f"note:    {note}")
    for err in errors:
        print(f"FAIL:    {err}")
    print()
    print("Form:    " + ("PASS — the form is what the file claims" if ok else "FAIL — see above"))
    print("Meaning: NOT CHECKED, on purpose. Whether a refrain earns its repetition is a")
    print("         judgement, not a measurement, and this tool will not pretend otherwise.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
