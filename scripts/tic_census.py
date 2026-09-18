#!/usr/bin/env python3
"""Census of the candour-disclaimer tic in our own writing.

Why this exists. On 2026-09-17 the human wrote, of a sentence of mine:

    You wrote, "I'd rather say that than pretend otherwise." I must have read that or similar
    statements a hundred times in the last three weeks. It seems to be an LLM tic and it carries
    no information. A confident writer not wanting to waste the reader's time would just "say
    that" and leave this sentence off.

He is describing a move that *sounds* like candour and states no fact: announcing that one is
about to be honest instead of being honest. It is measurable, and a tic that is measured can be
watched; a tic that is apologised for comes back. So this counts four families of it across the
text the human actually reads, and reports a **rate per 1,000 words** rather than a total, because
he feared a growth curve and a growing corpus makes raw counts meaningless.

What this measurement is NOT. It is a phrase count, not a judgement. Some hits carry information
(an honest *limit* is a fact about a tool; "the honest answer is no" can be the answer). It cannot
see paraphrases, and it counts any occurrence inside a quotation of someone else. Read the examples
before drawing a conclusion, which is the same rule the pre-check tool now carries.

    python3 scripts/tic_census.py            # all of channels/conversation/
    python3 scripts/tic_census.py --self-test
"""
import argparse
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CORPUS = ROOT / "channels" / "conversation"

FAMILIES = {
    "candour-disclaimer": r"(?:I(?:'d| would) rather say|than pretend otherwise|won'?t pretend|"
                          r"I don'?t pretend|not going to pretend)",
    "honesty-announcement": r"(?:let me be honest|I'?ll be honest|to be honest|honestly,|"
                            r"the honest answer|the honest part|the honest truth|if I'?m honest)",
    "plain-speaking-announcement": r"(?:I'?ll say plainly|to be plain|said plainly|say it plainly|"
                                   r"say this plainly|plainly:)",
    "blame-preemption": r"(?:I'?ll take the hit|I'?ll own (?:it|that)|that'?s on me|no cushion|"
                        r"I won'?t soften)",
}
COMPILED = {k: re.compile(v, re.IGNORECASE) for k, v in FAMILIES.items()}


def turns(path: pathlib.Path):
    """Split a conversation log into (date, amigo, text) turns.

    Entries look like:  [Goose 2026-09-17T18:00:00Z] **Lindsay:** ... **Desi:** ...
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    speaker = path.stem
    date = "undated"
    for line in text.splitlines():
        m = re.match(r"\[Goose (\d{4}-\d{2}-\d{2})", line)
        if m:
            date = m.group(1)
        yield date, speaker, line


def census(files):
    counts = {}          # (family, speaker) -> n
    by_week = {}         # (family, iso week) -> [hits, words]
    examples = []        # (family, speaker, date, line)
    words = {}
    for path in files:
        for date, speaker, line in turns(path):
            words[speaker] = words.get(speaker, 0) + len(line.split())
            try:
                wk = datetime.date.fromisoformat(date).isocalendar()
                week = "%04d-W%02d" % (wk[0], wk[1])
            except ValueError:
                week = "undated"
            for family, rx in COMPILED.items():
                found = rx.findall(line)
                if not found:
                    continue
                counts[(family, speaker)] = counts.get((family, speaker), 0) + len(found)
                by_week.setdefault((family, week), [0, 0])
                by_week[(family, week)][0] += len(found)
                by_week[(family, week)][1] += len(line.split())
                if len(examples) < 400:
                    examples.append((family, speaker, date, line.strip()[:190]))
    return counts, by_week, examples, words


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        cases = [("I'd rather say that than pretend otherwise.", "candour-disclaimer", True),
                 ("Let me be honest: the number is small.", "honesty-announcement", True),
                 ("Honestly, I don't know.", "honesty-announcement", True),
                 ("I'll take the hit.", "blame-preemption", True),
                 ("I'll say plainly what I mean.", "plain-speaking-announcement", True),
                 # And what must NOT be counted, because naming a fact is not announcing a virtue:
                 ("The tool prints its own limits in the first sentence.", "candour-disclaimer", False),
                 ("It reports unresolved references as a hole in the check.", "honesty-announcement", False)]
        bad = 0
        for text, family, want in cases:
            got = bool(COMPILED[family].search(text))
            ok = got == want
            bad += not ok
            print(("  ok  " if ok else "  FAIL") + f"  {family}: {text[:54]!r} -> {got}")
        print("SELF-TEST FAILED" if bad else
              "SELF-TEST PASSED (the last two cases are the distinction that matters: stating a "
              "limit is a fact, announcing that one is being honest is the tic)")
        return 1 if bad else 0

    files = sorted(CORPUS.glob("*.md"))
    counts, by_week, examples, words = census(files)
    total_words = sum(words.values())
    print(f"corpus: {len(files)} files, {total_words:,} words in {CORPUS.name}/")
    print()
    print("rate per 1,000 words, by speaker:")
    speakers = sorted(words, key=lambda s: -words[s])
    for sp in speakers:
        hits = sum(n for (fam, s), n in counts.items() if s == sp)
        print(f"  {sp:<12} {hits:>4} hits  {hits / max(words[sp],1) * 1000:>6.2f} /1k words"
              f"   ({words[sp]:,} words)")
    print()
    print("rate per 1,000 words, by week (all speakers) — the growth curve, not the backlog:")
    weeks = sorted({w for (_f, w) in by_week})
    for wk in weeks:
        hits = sum(by_week[(f, wk)][0] for f in FAMILIES if (f, wk) in by_week)
        wc = max((by_week[(f, wk)][1] for f in FAMILIES if (f, wk) in by_week), default=0)
        bar = "#" * min(int(hits), 60)
        print(f"  {wk}  {hits:>4}  {bar}")
    print()
    print("by family:")
    for f in FAMILIES:
        n = sum(v for (fam, _s), v in counts.items() if fam == f)
        print(f"  {f:<30} {n}")
    print()
    print("examples, newest first — read these; the count is not a verdict:")
    for fam, sp, date, line in examples[-14:]:
        print(f"  [{date} {sp}] ({fam}) {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
