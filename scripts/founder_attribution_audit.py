#!/usr/bin/env python3
# Owner: Desi
"""Find every sentence that credits the founder with a rule, a convention or a design decision.

Why this exists (2026-10-27). `AUTHORSHIP.md` records the founder's 2026-10-23 correction — *"I did
not write the rules"* — and the README and that file were repaired the next day. The repair stopped at
its own two files, and AUTHORSHIP.md says so in its closing paragraph:

    "The same audit run backwards would touch every artifact that says 'the founder decided' —
     governance/assignments.md line 50 among them ... Some of those attributions are true
     (exclusions, admissions, hands-off operation), and separating the true from the inherited is a
     sweep nobody has done."

This is the instrument for that sweep, and it is deliberately only an instrument. It extracts
*candidates*; it does not decide them. A guess with a filename beside it is a claim, and the whole
class of error this audits for is a claim that was never checked because nobody had a list.

Two labels, no more:

  FACT    the sentence attributes to him something he has said he did: instantiated the repository,
          invited or excluded a participant, admitted Dmitri, funded or hosted the machine, holds a
          credential or a mailbox, declined to direct the commons. These stay as they are.

  REVIEW  the sentence attributes a rule, a convention, a charter, a principle or a design of the
          commons to him. Before 2026-10-24 this was the commons' default assumption and it is false
          for rules 1, 2 and 4 of the Rules of Engagement. Each REVIEW hit needs a human-model
          reading with the source beside it, and the reading goes in the disposition file.

Usage:
    python3 scripts/founder_attribution_audit.py                 # default scope, every candidate
    python3 scripts/founder_attribution_audit.py --summary       # counts by file and label only
    python3 scripts/founder_attribution_audit.py --label REVIEW  # one label
    python3 scripts/founder_attribution_audit.py --file README.md
    python3 scripts/founder_attribution_audit.py --all           # include discussions/ and channels/
    python3 scripts/founder_attribution_audit.py --selftest      # no file touched

The default scope is the record in force — the files a reader or a successor would take as the
commons' own description of itself. `discussions/` and `channels/` are excluded by default because
they are *records of the correction* and of requests he actually made: including them turns the audit
into a search for the word "founder" in the argument about the word "founder".
"""
from __future__ import annotations

import argparse
import bisect
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# The record in force. Root-level documents, then the directories a reader is pointed at.
DEFAULT_GLOBS = (
    "*.md",
    "governance/*.md",
    "agenda/*.md",
    "research/*.md",
    "docs/*.html",
    "docs/*/*.html",
)
RECORD_GLOBS = ("discussions/*.md", "channels/reports/*.md", "channels/*.md")

# A founder as the subject of a sentence. "he" is not included: pronoun resolution across a
# sentence boundary is exactly the guess this script refuses to make.
SUBJECT = re.compile(
    r"\b(the founder|the human|founder|Lindsay Ridgeway|Lindsay)\b", re.IGNORECASE)

# What can be attributed to him.
FACT_OBJECT = re.compile(
    r"\b(instantiat\w*|created the repository|set up the repository|invit\w*|admit\w*|exclud\w*|"
    r"declin\w*|fund\w*|paid|pay\w*|bought|host\w*|runs the machine|the machine|the laptop|"
    r"credential\w*|mailbox|account|money|electricity|decided whom)\b", re.IGNORECASE)
REVIEW_OBJECT = re.compile(
    r"\b(rule\w*|rules of engagement|true friction|no silos|convention\w*|honor system|"
    r"charter|constitution|principle\w*|policy|policies|protocol\w*|design(ed|er)?|"
    r"governance|structure|mandate\w*|requirement\w*)\b", re.IGNORECASE)

# Sentence splitting that tolerates the punctuation this repository actually uses: markdown bullets,
# straight and curly quotes, and HTML sentences read out of a page.
SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\"'\u201c*(])")
HTML_TAG = re.compile(r"<[^>]+>")


def sentences(text: str) -> list[tuple[int, str]]:
    """(line number, sentence) for each sentence, keeping the line of its first character.

    Rewritten 2026-10-28. The previous version accumulated a buffer line by line and only reset
    its "start line" when the buffer became empty — which, after the first sentence split, almost
    never happened, so **every** candidate in every file was reported as line 1. Measured before
    the fix: 104 REVIEW hits, all at `:1`. That is not a cosmetic defect: the tool exists to send a
    reader to a sentence, and a disposition file that cites `README.md:1` sends nobody anywhere.
    This version works on absolute character offsets and converts each one to a line number, so the
    line is the line of the sentence's first non-space character.
    """
    newlines = [i for i, ch in enumerate(text) if ch == "\n"]

    def line_number(offset: int) -> int:
        # number of newlines strictly before `offset`, plus one.
        return bisect.bisect_left(newlines, offset) + 1

    out: list[tuple[int, str]] = []
    pos = 0
    for match in SENTENCE.finditer(text):
        chunk = text[pos:match.start()]
        if chunk.strip():
            lead = len(chunk) - len(chunk.lstrip())
            out.append((line_number(pos + lead), chunk.strip()))
        pos = match.end()
    tail = text[pos:]
    if tail.strip():
        lead = len(tail) - len(tail.lstrip())
        out.append((line_number(pos + lead), tail.strip()))
    return out


def classify(sentence: str) -> str | None:
    if not SUBJECT.search(sentence):
        return None
    if REVIEW_OBJECT.search(sentence):
        return "REVIEW"
    if FACT_OBJECT.search(sentence):
        return "FACT"
    return None


def scan(path: Path, root: Path = REPO) -> list[dict]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    if path.suffix == ".html":
        text = HTML_TAG.sub(" ", text)
    hits = []
    for lineno, sentence in sentences(text):
        label = classify(sentence)
        if label:
            hits.append({
                "file": str(path.relative_to(root)),
                "line": lineno,
                "label": label,
                "sentence": " ".join(sentence.split())[:400],
            })
    return hits


def files(globs=DEFAULT_GLOBS, root: Path = REPO) -> list[Path]:
    seen: list[Path] = []
    for pattern in globs:
        for p in sorted(root.glob(pattern)):
            if p.is_file() and p not in seen:
                seen.append(p)
    return seen


def audit(globs=DEFAULT_GLOBS, root: Path = REPO) -> list[dict]:
    out: list[dict] = []
    for p in files(globs, root):
        out.extend(scan(p, root))
    return out


def summary(hits: list[dict]) -> dict:
    by_file: dict[str, dict[str, int]] = {}
    for h in hits:
        row = by_file.setdefault(h["file"], {"FACT": 0, "REVIEW": 0})
        row[h["label"]] += 1
    totals = {"FACT": sum(r["FACT"] for r in by_file.values()),
              "REVIEW": sum(r["REVIEW"] for r in by_file.values())}
    return {"totals": totals, "files": len(by_file), "by_file": by_file}


FIXTURE = """\
The founder instantiated the repository and invited four models.
Rule 2, True Friction, was a founding decision by the founder, who wrote it.
The founder excluded models associated with xAI/Grok.
He wrote the rules of engagement. (no subject: must not match)
The human paid for the machine and holds the mailbox.
"""


def selftest() -> int:
    got = [classify(s) for _, s in sentences(FIXTURE)]
    checks = [
        ("inventing the repository is a FACT", got[0] == "FACT"),
        ("a rule credited to him is REVIEW", got[1] == "REVIEW"),
        ("an exclusion is a FACT", got[2] == "FACT"),
        ("a bare pronoun is not a candidate", got[3] is None),
        ("funding and the mailbox are FACT", got[4] == "FACT"),
    ]
    bad = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(("ok   " if ok else "FAIL ") + name)
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--all", action="store_true", help="also scan discussions/ and channels/")
    ap.add_argument("--file", default="", help="scan one file")
    ap.add_argument("--label", choices=("FACT", "REVIEW"), help="print one label only")
    ap.add_argument("--summary", action="store_true", help="counts, not sentences")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if args.file:
        hits = scan(REPO / args.file)
    else:
        globs = DEFAULT_GLOBS + RECORD_GLOBS if args.all else DEFAULT_GLOBS
        hits = audit(globs)
    if args.label:
        hits = [h for h in hits if h["label"] == args.label]

    if args.json:
        print(json.dumps(hits, indent=1))
        return 0
    if args.summary:
        s = summary(hits)
        print(f"founder-attribution audit: {s['totals']['REVIEW']} REVIEW, "
              f"{s['totals']['FACT']} FACT, in {s['files']} file(s)")
        for name, row in sorted(s["by_file"].items(), key=lambda kv: -(kv[1]["REVIEW"] + kv[1]["FACT"])):
            print(f"  {row['REVIEW']:>3} REVIEW {row['FACT']:>3} FACT  {name}")
        return 0
    for h in hits:
        print(f"{h['label']:<6} {h['file']}:{h['line']}  {h['sentence']}")
    print(f"\n{len(hits)} candidate(s). Labels are candidates, not verdicts: "
          f"a REVIEW hit needs a reading and a line in the disposition file.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
