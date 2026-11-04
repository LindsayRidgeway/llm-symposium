#!/usr/bin/env python3
"""correspondence_audit.py — from the record alone, can a reader tell whether B read A?

Why this exists (Dmitri, 2026-11-01, agenda item 36, `agenda/36-the-free-tribe-design.md`).

The free tribe's first five bench rounds tested the wrong thing: whether a small model can read a
facts table and report it honestly. The founder's correction, recorded in item 36 at 01:20 on
2026-11-01, is structural — the Symposium built an *accumulating culture* (an agenda, amended
rules, a magazine, a gallery, letters), none of which needed correct table parsing. What it needed
was that one member could read what another wrote and answer it.

So the round-6 question is correspondence, and the audit of it is not "is this number sourced".
It is: **did this reply engage a sentence its predecessor actually wrote?** That is checkable,
because a reply that read the letter can quote it or contradict a specific phrase, while a reply
that did not will say something adjacent and agreeable and quote nothing.

What this program measures, and what it refuses to
--------------------------------------------------
Three signals, two of them mechanical and one of them only a nomination:

  quote        a verbatim run of at least `--ngram` (default 6) words shared with the letter, and
               containing at least two content words so that shared boilerplate ("the state file
               and the record") is not mistaken for engagement. Reported with the span.
  answer       a question the letter asked, where at least half of the question's content words
               appear in the reply. This is paraphrase detection by overlap; it is weaker than a
               quote and the verdict says so.
  challenge    a reply sentence carrying a negation *near* content words from a letter sentence.
               This is a **nomination, not a finding**: whether a negation contradicts or merely
               agrees in the negative ("it is not the case that X, exactly as you say") cannot be
               decided by counting. The program prints the pair and hands it to a reader.

And the thing this program cannot do, stated here rather than discovered later: a reply can quote
the letter and still say nothing. **Quote proves the letter was read; it does not prove the reply
was worth writing.** The two questions are separate and only the first is a measurement.

The failure mode this is built against is the one the founder named: correspondence that reads
like correspondence and carries nothing. Fluent engagement is easier to fake than arithmetic, so
the output is evidence a reader can check — spans, sentences, counts — never a bare score.

Usage
-----
    python3 scripts/correspondence_audit.py audit --letter A.md --reply B.md [--ngram 6] [--json]
    python3 scripts/correspondence_audit.py pair --dir channels/sent [--glob '*.md']

`pair` sorts the directory's files by name and audits each file against the one before it, which
is what a record of consecutive letters looks like with no metadata at all.

Exit status: 0 always for `audit` and `pair` (this is a reader's report, not a gate). `--strict`
makes exit 1 if any reply scores `not-shown`, for use where a caller wants a machine answer.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------------------------
# Text handling. Deliberately crude: every transformation here is one a reader can follow, because
# a cleverer tokenizer buys accuracy nobody can check.

_WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9'\u2019\-]*")
_SENTENCE = re.compile(r"[^.!?\n]*[.!?]+|[^.!?\n]+$")

STOPWORDS = frozenset(
    """a an and are as at be been but by can could did do does for from had has have he her here
    his how i if in into is it its itself may me might must my no nor not of on one only or other
    our out over own same she should so some such than that the their them then there these they
    this those through to too under until up very was we were what when where which while who
    whom why will with would you your yours also just like now still yet ever even much more most
    about above after again all am any because before being below between both down during each
    few further him himself off once s t d ll re ve m""".split()
)

NEGATIONS = frozenset(
    """not no never none cannot can't don't doesn't didn't isn't aren't wasn't weren't won't
    wouldn't shouldn't couldn't hardly neither nor without fail fails failed false wrong
    disagree disagreeing""".split()
)


def strip_markup(text: str) -> str:
    """Drop headings, code fences and the frontmatter-ish first block.

    Headings are shared boilerplate by construction ("## Journal", "## State"); left in, they would
    make every pair in a record look like it quoted the one before it.
    """
    out = []
    in_fence = False
    in_front = text.startswith("---")
    for i, line in enumerate(text.splitlines()):
        if in_front:
            if i > 0 and line.strip() == "---":
                in_front = False
            continue
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.lstrip().startswith("#"):
            continue
        out.append(line)
    return "\n".join(out)


def words(text: str) -> list[str]:
    return [w.lower().replace("\u2019", "'") for w in _WORD.findall(text)]


def is_content(word: str) -> bool:
    return word not in STOPWORDS and (len(word) > 2 or word.isdigit())


def content_words(tokens: list[str]) -> list[str]:
    return [w for w in tokens if is_content(w)]


def sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE.findall(text) if s.strip()]


# ---------------------------------------------------------------------------------------------
# Signal 1: verbatim quotation.


def _ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    return [tuple(tokens[i : i + n]) for i in range(max(0, len(tokens) - n + 1))]


def find_quotes(letter: str, reply: str, n: int = 6, boilerplate: frozenset = frozenset(),
                df: dict | None = None, max_df: int | None = None) -> list[dict]:
    """Verbatim runs of >= n words shared between the two documents.

    Consecutive n-grams merge only along one contiguous source alignment, so a ten-word quotation is reported once as ten words
    rather than five times as six. A run counts only if it carries at least two content words:
    without that rule, "and the state file is" would score as engagement.

    `df`, when given, is the document frequency of every n-gram over a corpus that CONTAINS the
    letter and the reply, so a span belonging to this pair alone has df 2. Each run then carries
    the frequency of its most specific n-gram, and `max_df` drops runs that other documents also
    contain. That is a stricter test than `boilerplate`: on 2026-11-01 the two-document ceiling
    was what separated a quotation from a paragraph two sibling letters both reused, and the
    residual false positives on `channels/sent` were exactly the runs at df 3.
    """
    letter_tokens = words(strip_markup(letter))
    reply_tokens = words(strip_markup(reply))
    if len(letter_tokens) < n or len(reply_tokens) < n:
        return []

    # Track each source/reply alignment separately. Adjacent reply windows may
    # occur in unrelated source locations and must not invent a longer quotation.
    source_positions = {}
    for j, gram in enumerate(_ngrams(letter_tokens, n)):
        if gram not in boilerplate:
            source_positions.setdefault(gram, []).append(j)
    alignments = {}
    for i, gram in enumerate(_ngrams(reply_tokens, n)):
        for j in source_positions.get(gram, ()):
            alignments.setdefault(j - i, []).append(i)

    candidates = []
    for offset, hits in alignments.items():
        start = previous = hits[0]
        for i in hits[1:] + [None]:
            if i is not None and i == previous + 1:
                previous = i
                continue
            candidates.append((start, previous + n, start + offset))
            start = previous = i

    # Keep maximal reply spans once, with one contiguous source witness each.
    # Distinct maximal spans may overlap; coverage counts their union below.
    quotes = []
    furthest_end = -1
    for start, end, source_start in sorted(candidates, key=lambda q: (q[0], -q[1], q[2])):
        if end <= furthest_end:
            continue
        furthest_end = end
        span = reply_tokens[start:end]
        n_content = sum(1 for w in span if is_content(w))
        entry = {"start": start, "end": end, "words": len(span),
                 "content_words": n_content, "source_start": source_start,
                 "source_end": source_start + len(span)}
        if df is not None:
            grams = _ngrams(span, n) or [tuple(span)]
            entry["df"] = min(df.get(g, 1) for g in grams)
        quotes.append(entry)
    kept = [q for q in quotes if q["content_words"] >= 2]
    if max_df is not None:
        kept = [q for q in kept if q.get("df", 1) <= max_df]
    return kept


# ---------------------------------------------------------------------------------------------
# Signal 0: is this a reply at all, or the letter handed back?
#
# The failure round 6 of the bench actually produced (2026-11-01, agenda item 36): `llama3.2:3b`
# "returned the letter, twice, 52 and 54 consecutive words copied, its own questions coming back
# as B's statements". Every existing signal scored that as `read`, because copying is the most
# literal possible proof that the letter was read. It is also the opposite of an answer, so a
# detector that rewards it rewards the failure it was built to catch.


def quoted_word_count(quotes: list[dict]) -> int:
    """Count covered reply words once when distinct source-backed spans overlap."""
    count = end = 0
    for quote in sorted(quotes, key=lambda q: (q["start"], q["end"])):
        count += max(0, quote["end"] - max(end, quote["start"]))
        end = max(end, quote["end"])
    return count


def echo_share(letter: str, reply: str, quotes: list[dict]) -> dict:
    """How much of the reply is the letter's own text, reported as two numbers, not a score."""
    reply_words = len(words(strip_markup(reply)))
    copied = quoted_word_count(quotes)
    return {
        "longest_run": max((q["words"] for q in quotes), default=0),
        "copied_share": round(copied / reply_words, 3) if reply_words else 0.0,
        "reply_words": reply_words,
    }


# ---------------------------------------------------------------------------------------------
# Signal 2: a question answered (by content overlap — paraphrase, not quotation).


def find_answers(letter: str, reply: str, threshold: float = 0.5) -> list[dict]:
    reply_content = set(content_words(words(strip_markup(reply))))
    out = []
    for sentence in sentences(strip_markup(letter)):
        if not sentence.rstrip().endswith("?"):
            continue
        asked = [w for w in content_words(words(sentence)) if len(w) > 3 or w.isdigit()]
        asked_set = set(asked)
        if len(asked_set) < 3:
            continue  # "What?" is not a question that can be answered checkably
        hit = sorted(asked_set & reply_content)
        coverage = len(hit) / len(asked_set)
        if coverage >= threshold:
            out.append(
                {"question": " ".join(sentence.split())[:300], "coverage": round(coverage, 3),
                 "shared": hit}
            )
    return out


# ---------------------------------------------------------------------------------------------
# Signal 3: a possible challenge — nominated, never decided, by this program.


def find_challenges(letter: str, reply: str, min_shared: int = 3) -> list[dict]:
    letter_sents = []
    for s in sentences(strip_markup(letter)):
        cw = {w for w in content_words(words(s)) if len(w) > 3}
        if cw:
            letter_sents.append((s, cw))

    out = []
    for rs in sentences(strip_markup(reply)):
        rw = words(rs)
        if not any(w in NEGATIONS for w in rw):
            continue
        rc = {w for w in content_words(rw) if len(w) > 3}
        for ls, lc in letter_sents:
            shared = rc & lc
            if len(shared) >= min_shared:
                out.append(
                    {
                        "reply_sentence": " ".join(rs.split())[:300],
                        "letter_sentence": " ".join(ls.split())[:300],
                        "shared": sorted(shared),
                    }
                )
                break
    return out


# ---------------------------------------------------------------------------------------------
# Boilerplate: the defect that made round 6 of the bench unfair before it began.
#
# Measured 2026-11-01 on `channels/sent` (74 consecutive letters, none of them a reply to the one
# before it): 39 of 74 pairs scored `read`, because every letter in a house style shares its
# greeting, its signature block and its subject line, and 6-8 of those words in a row are a
# "verbatim quotation". A detector that fires on the house style cannot say whether B read A.
#
# So a run of words that appears in many documents of a corpus is boilerplate by construction and
# may not count as a quotation. What is left is what is specific to *this* letter.


def corpus_df(paths, n: int = 6, extra_texts=()) -> dict:
    """Document frequency of every n-gram over a corpus, plus any extra documents given whole.

    `extra_texts` exists so that the letter and the reply are always counted even when they are
    not themselves in the corpus directory: a span unique to the pair then has df 2, and one rule
    ("nobody else contains this") works the same in `audit` and `pair` mode.
    """
    df: dict[tuple[str, ...], int] = {}
    texts = []
    for path in paths:
        try:
            texts.append(Path(path).read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
    texts.extend(extra_texts)
    for text in texts:
        for g in set(_ngrams(words(strip_markup(text)), n)):
            df[g] = df.get(g, 0) + 1
    return df


def corpus_boilerplate(paths, n: int = 6, max_documents: int = 3) -> frozenset:
    """n-grams that occur in more than `max_documents` documents — the house style, not a quote."""
    df = corpus_df(paths, n)
    return frozenset(g for g, c in df.items() if c > max_documents)


# ---------------------------------------------------------------------------------------------
# The verdict.


def audit(letter: str, reply: str, n: int = 6, boilerplate: frozenset = frozenset(),
          df: dict | None = None, max_df: int | None = None,
          echo_run: int = 20, echo_share_floor: float = 0.5) -> dict:
    letter_len = len(words(strip_markup(letter)))
    quotes = find_quotes(letter, reply, n, boilerplate, df, max_df)
    answers = find_answers(letter, reply)
    challenges = find_challenges(letter, reply)
    echo = echo_share(letter, reply, quotes)

    if letter_len < n:
        verdict = "untestable"
        reason = (
            f"the letter is {letter_len} words; the quotation window is {n}, so no verbatim "
            "engagement can be detected and the absence of one means nothing"
        )
    elif echo["longest_run"] >= echo_run or echo["copied_share"] >= echo_share_floor:
        verdict = "echo"
        reason = (
            f"{echo['longest_run']} consecutive words carried over verbatim, "
            f"{int(echo['copied_share'] * 100)}% of the reply copied from the letter: the letter "
            "was certainly read and the reply returned it. Reading and answering are different "
            "acts and this program can see only the first"
        )
    elif quotes and answers:
        verdict = "read"
        reason = (
            f"quotes {quotes[0]['words']} words of the letter verbatim and answers "
            f"{len(answers)} question(s) it asked"
        )
    elif quotes:
        verdict = "read"
        reason = f"quotes {quoted_word_count(quotes)} words of the letter verbatim"
    elif answers:
        verdict = "read"
        reason = (
            f"answers {len(answers)} question(s) the letter asked, by content overlap only — "
            "no verbatim quotation, so read it before believing it"
        )
    elif challenges:
        verdict = "challenge-candidate"
        reason = (
            "no quote and no answered question, but a negation near the letter's own words: "
            "this may be agreement or contradiction and only a reader can say which"
        )
    else:
        verdict = "not-shown"
        reason = (
            "nothing in the reply points at a sentence the letter contains — no quote, no "
            "answered question, no negation near its words. It may be adjacent and agreeable"
        )

    return {
        "verdict": verdict,
        "reason": reason,
        "letter_words": letter_len,
        "reply_words": len(words(strip_markup(reply))),
        "ngram": n,
        "quotes": quotes,
        "answers": answers,
        "challenges": challenges,
        "echo": echo,
        "caveat": (
            "Quote proves the letter was read. It does not prove the reply was worth writing; "
            "that judgment is a reader's."
        ),
    }


def _quote_text(reply: str, q: dict) -> str:
    toks = words(strip_markup(reply))
    return " ".join(toks[q["start"] : q["end"]])


def render(letter_path: str, reply_path: str, result: dict, reply_text: str) -> str:
    lines = [f"letter  {letter_path}", f"reply   {reply_path}", "", f"VERDICT {result['verdict']}"]
    lines.append(f"  {result['reason']}")
    lines.append("")
    if result["quotes"]:
        lines.append("verbatim runs shared with the letter:")
        for q in result["quotes"]:
            rarity = f", in {q['df']} documents" if "df" in q else ""
            lines.append(f"  {q['words']:>3} words, {q['content_words']} content{rarity}: "
                         f"\"{_quote_text(reply_text, q)}\"")
        lines.append("")
    if result["answers"]:
        lines.append("questions the letter asked, answered:")
        for a in result["answers"]:
            lines.append(f"  {int(a['coverage'] * 100)}% of its content words in the reply: "
                         f"{a['question']}")
        lines.append("")
    if result["challenges"]:
        lines.append("negations near the letter's words — a reader must decide agree or contradict:")
        for c in result["challenges"]:
            lines.append(f"  letter: {c['letter_sentence']}")
            lines.append(f"  reply : {c['reply_sentence']}")
            lines.append(f"  shared: {', '.join(c['shared'])}")
        lines.append("")
    e = result["echo"]
    lines.append(f"copied from the letter: longest run {e['longest_run']} words, "
                 f"{int(e['copied_share'] * 100)}% of a {e['reply_words']}-word reply")
    lines.append("")
    lines.append(f"caveat: {result['caveat']}")
    return "\n".join(lines)


def _pairs_in(directory: Path, glob: str) -> list[tuple[Path, Path]]:
    files = sorted(p for p in directory.glob(glob) if p.is_file())
    return [(files[i - 1], files[i]) for i in range(1, len(files))]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("audit", help="audit one reply against one letter")
    a.add_argument("--letter", required=True)
    a.add_argument("--reply", required=True)
    a.add_argument("--ngram", type=int, default=6)
    a.add_argument("--corpus", help="directory whose house style must not count as quotation")
    a.add_argument("--max-df", type=int, default=2,
                   help="a span survives if no more than this many documents contain it; 2 means "
                        "the letter and the reply only (default)")
    a.add_argument("--json", action="store_true")
    a.add_argument("--strict", action="store_true", help="exit 1 if the verdict is not-shown")

    p = sub.add_parser("pair", help="audit consecutive files in a directory")
    p.add_argument("--dir", required=True)
    p.add_argument("--glob", default="*.md")
    p.add_argument("--ngram", type=int, default=6)
    p.add_argument("--max-df", type=int, default=2)
    p.add_argument("--json", action="store_true")
    p.add_argument("--strict", action="store_true")

    args = parser.parse_args(argv)

    if args.cmd == "audit":
        letter = Path(args.letter).read_text(encoding="utf-8", errors="replace")
        reply = Path(args.reply).read_text(encoding="utf-8", errors="replace")
        corpus_files = sorted(Path(args.corpus).glob("*.md")) if args.corpus else []
        pair = {Path(args.letter).resolve(), Path(args.reply).resolve()}
        corpus_files = [f for f in corpus_files if f.resolve() not in pair]
        df = corpus_df(corpus_files, args.ngram, extra_texts=[letter, reply])
        result = audit(letter, reply, args.ngram, frozenset(), df, args.max_df)
        result["corpus_documents"] = len(corpus_files) + 2
        if args.json:
            print(json.dumps({"letter": args.letter, "reply": args.reply, **result}, indent=2))
        else:
            print(render(args.letter, args.reply, result, reply))
        return 1 if (args.strict and result["verdict"] == "not-shown") else 0

    directory = Path(args.dir)
    if not directory.is_dir():
        print(f"not a directory: {directory}", file=sys.stderr)
        return 2
    pairs = _pairs_in(directory, args.glob)
    if not pairs:
        print(f"no consecutive file pairs in {directory} matching {args.glob}", file=sys.stderr)
        return 2

    corpus_files = sorted(directory.glob(args.glob))
    df = corpus_df(corpus_files, args.ngram)
    if not args.json:
        print(f"corpus {directory}: {len(corpus_files)} documents; a span survives only if at "
              f"most {args.max_df} of them contain it\n")

    results = []
    for letter_path, reply_path in pairs:
        letter = letter_path.read_text(encoding="utf-8", errors="replace")
        reply = reply_path.read_text(encoding="utf-8", errors="replace")
        result = audit(letter, reply, args.ngram, frozenset(), df, args.max_df)
        results.append({"letter": str(letter_path), "reply": str(reply_path), **result})
        if not args.json:
            print(render(str(letter_path), str(reply_path), result, reply))
            print("-" * 78)

    if args.json:
        print(json.dumps(results, indent=2))
    not_shown = sum(1 for r in results if r["verdict"] == "not-shown")
    echoes = sum(1 for r in results if r["verdict"] == "echo")
    if not args.json:
        print(f"{len(results)} reply(ies) audited; {not_shown} not-shown, {echoes} echo")
    return 1 if (args.strict and not_shown) else 0


if __name__ == "__main__":
    raise SystemExit(main())
