#!/usr/bin/env python3
"""Does a seed row's positive count survive the primary's own numbers?

Why this exists. Seed row 19 (France) of the MCR colistin table records 49 positives out of 1701,
and the paper it cites reports 65/1561 in breeding farms plus 84/140 in fattening farms — 149 in
1701, or 8.76%, against the seed's 2.88%. The row's own arithmetic is impeccable: 49/1701 is 2.88
to the printed place, every one of the table's 38 rows recomputes exactly, and the pooled totals
add up. That is the whole problem. A recomputation guard cannot see this defect, because the
recomputation is *derived from the wrong numerator* — 149 with its leading digit dropped looks
exactly as self-consistent as 149. Found by reading the paper, not by a check, which means it will
be found again only if someone happens to read the next one.

What it measures, and how narrowly. For every seed row whose primary study is already pinned in
`research/mcr-colistin-primary-raw.json` — text this repository fetched itself, no network call
here — it asks three questions of the abstract:

  1. Does the abstract account for the row's denominator, either directly (the number appears) or
     as a sum of two numbers it does state?
  2. Does the abstract state the row's numerator anywhere?
  3. If the denominator is accounted for, does the abstract also contain a positive count that
     *ends with* the row's numerator and exceeds it by a round power of ten — 49 against 149, 12
     against 112? A count that is a suffix of a larger count in the same paper, with the same
     denominator, is the signature of transcription digit loss, and 100 is exactly the difference
     row 19 shows.

Question 3 is the instrument; it is deliberately dumb. It is a reading aid, not a verdict: it can
only ever say "this row's numerator looks like a truncated larger number in the same abstract", and
it prints the numbers it used so a reader can check in one look. It cannot see a wrong count that
is not a truncation, and it cannot see anything at all for rows whose primary is not pinned here.

The honest limit, stated because the alternative is a clean-looking screen: of the 38 seed rows,
8 have a pinned primary, and of those 8 only some state their counts in the abstract at all. This
check covers the part of the table whose sources this repository can already open, and no more.

Usage:
    python3 scripts/mcr_numerator_check.py
    python3 scripts/mcr_numerator_check.py --json
    python3 scripts/mcr_numerator_check.py --strict     # exit 1 if any row is suspicious

Exit codes: 0 nothing suspicious in the rows it could read, 1 at least one row's numerator looks
like a truncated larger count (only with --strict), 2 the pinned files are not where they should be.
"""

import argparse
import html
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = os.path.join(REPO, "research", "mcr-colistin-seed.json")
PRIMARY = os.path.join(REPO, "research", "mcr-colistin-primary-raw.json")

POWERS_OF_TEN = (10, 100, 1000, 10000, 100000)


def clean_text(text):
    """Abstracts arrive as HTML fragments with entity-escaped spaces; make them plain."""
    if not text:
        return ""
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text))).strip()


def integers(text):
    """Every whole number the text states, comma thousands separators removed, in order."""
    out = []
    for raw in re.findall(r"\d[\d,]*", text):
        digits = raw.replace(",", "")
        if digits.isdigit():
            out.append(int(digits))
    return out


def label_key(label):
    """`17 (a)` in the seed table and `17a` in the pinned studies are the same row."""
    return re.sub(r"[^0-9a-z]", "", str(label or "").lower())


def pair_sums(numbers):
    """Every sum of two distinct stated numbers, with every pair that produces it."""
    sums = {}
    uniq = sorted(set(numbers))
    for i, a in enumerate(uniq):
        for b in uniq[i + 1:]:
            sums.setdefault(a + b, []).append((a, b))
    return sums


def truncation_candidates(numerator, stated):
    """Numbers in `stated` that end with `numerator` and exceed it by a round power of ten.

    Returns [(larger, difference), ...]. 49 against 149 gives (149, 100); 49 against 249 does not
    (the difference is 200, which is not a single dropped digit).

    A numerator below ten is excluded outright. Every sum in an abstract ends in some one-digit
    number, so "2 is 12 with its leading digit dropped" would fire on half the table and teach a
    reader to ignore the check. The defect this looks for needs a numerator long enough for a
    dropped digit to leave a recognisable tail.
    """
    hits = []
    if numerator is None or numerator < 10:
        return hits
    text = str(numerator)
    for value in sorted(set(stated)):
        if value <= numerator:
            continue
        difference = value - numerator
        if difference in POWERS_OF_TEN and str(value).endswith(text):
            hits.append((value, difference))
    return hits


def check_row(row, study):
    """One seed row against one pinned primary. Returns a record of what was and was not found."""
    abstract = clean_text(study.get("abstract"))
    numbers = integers(abstract)
    sums = pair_sums(numbers)
    denominator = row.get("n_isolates")
    numerator = row.get("mcr_positive")

    record = {
        "sl": row.get("sl"),
        "country": row.get("country"),
        "numerator": numerator,
        "denominator": denominator,
        "pmid": study.get("pmid"),
        "abstract_read": bool(abstract),
        "denominator_stated": None,
        "numerator_stated": None,
        "suspicion": False,
        "evidence": [],
    }
    if not abstract or not denominator or numerator is None:
        return record

    record["denominator_stated"] = denominator in numbers
    record["denominator_parts"] = sums.get(denominator)
    record["numerator_stated"] = numerator in numbers
    denominator_accounted = record["denominator_stated"] or bool(record["denominator_parts"])

    candidates = truncation_candidates(numerator, numbers)
    for larger, difference in candidates:
        record["evidence"].append(
            "abstract states %d; the row's %d is that number with its leading digit dropped "
            "(%d apart)" % (larger, numerator, difference))
    for total, pairs in sorted(sums.items()):
        for larger, difference in truncation_candidates(numerator, [total]):
            for a, b in pairs:
                record["evidence"].append(
                    "abstract states %d + %d = %d; the row's %d is that total with its leading "
                    "digit dropped (%d apart)" % (a, b, total, numerator, difference))
            break

    # Only suspicious when the same abstract also accounts for the denominator: a suffix match on
    # its own is a coincidence waiting to happen in a table of 38 rows.
    record["suspicion"] = bool(denominator_accounted and record["evidence"])
    return record


def load(path):
    with open(path, encoding="utf8") as handle:
        return json.load(handle)


def check_all(seed, primary):
    rows = seed.get("rows", [])
    studies = primary.get("studies", {})
    by_row = {str(r.get("sl")): r for r in rows}
    records = []
    for key, study in sorted(studies.items()):
        sl = str(study.get("seed_row", "")).strip()
        row = by_row.get(sl)
        if row is None:  # a pinned study that is no longer a seed row: say so, do not guess
            records.append({
                "sl": sl, "country": study.get("country"), "pmid": study.get("pmid"),
                "numerator": None, "denominator": None, "abstract_read": True,
                "suspicion": False, "evidence": ["pinned study has no matching seed row"],
            })
            continue
        records.append(check_row(row, study))
    return records


def render(records, seed):
    lines = []
    rows = seed.get("rows", [])
    lines.append("MCR seed numerators, checked against the primaries this repository has pinned")
    lines.append("=" * 78)
    lines.append("seed rows: %d   rows with a pinned primary: %d"
                 % (len(rows), len(records)))
    read = [r for r in records if r.get("abstract_read") and r.get("denominator")]
    lines.append("rows whose abstract was read: %d   of those, denominator accounted for: %d"
                 % (len(read), sum(1 for r in read
                                   if r.get("denominator_stated") or r.get("denominator_parts"))))
    lines.append("")
    lines.append("%-6s %-12s %8s %8s  %-9s %s"
                 % ("row", "country", "pos", "N", "verdict", "what the abstract says"))
    for record in records:
        if not record.get("denominator"):
            verdict = "n/a"
        elif record.get("suspicion"):
            verdict = "SUSPECT"
        elif record.get("numerator_stated"):
            verdict = "consistent"
        else:
            verdict = "not stated"
        detail = "; ".join(record.get("evidence", [])) or (
            "numerator %s appears in the abstract" % record.get("numerator")
            if record.get("numerator_stated") else
            "numerator %s does not appear in the abstract" % record.get("numerator"))
        lines.append("%-6s %-12s %8s %8s  %-9s %s"
                     % (record.get("sl"), record.get("country"),
                        record.get("numerator"), record.get("denominator"), verdict, detail))
    lines.append("")
    suspect = [r for r in records if r.get("suspicion")]
    lines.append("suspicious rows: %d%s" % (
        len(suspect),
        "" if not suspect else " — " + ", ".join(str(r["sl"]) for r in suspect)))
    lines.append("A row not marked SUSPECT is not thereby verified: this check sees only a "
                 "truncated numerator in a pinned abstract, and says nothing about a row whose "
                 "primary is not pinned here or whose counts its abstract never states.")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", default=SEED, help="seed table json")
    parser.add_argument("--primary", default=PRIMARY, help="pinned primary-study json")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--strict", action="store_true",
                        help="exit 1 when any row is suspicious")
    args = parser.parse_args(argv)

    for path in (args.seed, args.primary):
        if not os.path.exists(path):
            sys.stderr.write("missing: %s\n" % path)
            return 2

    seed = load(args.seed)
    primary = load(args.primary)
    records = check_all(seed, primary)

    if args.json:
        print(json.dumps({"records": records,
                          "suspicious": [r["sl"] for r in records if r.get("suspicion")]},
                         indent=2))
    else:
        print(render(records, seed))

    if args.strict and any(r.get("suspicion") for r in records):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
