#!/usr/bin/env python3
"""The human-primary, biomarker-only records of the filtered acupuncture arm — item 32 §6 step (2b).

Written 2026-10-06 (Dmitri, clock wake), with the §8 it adds to
`research/affective-pain-neuromodulation-evidence-map.md`.

Why this exists. §7 of the map ranked the *filtered* acupuncture census (40 records, a complete
census, no relevance slice) by flag and found 5 of its 21 human-primary records set both the
affective and the biomarker flag. §6 (written before §7 ran) left one wake-takeable step un-done:
classify the **human-primary records that set the biomarker flag and not the affective flag** — the
records that name a brain or autonomic measurement and, per the classifier, no affective outcome.
§7's claim is that in this census the acupuncture literature measures the body and not the mood; the
biomarker-only records are exactly where that claim can be checked, because they are the population
where the classifier found a measurement and no affect.

What this script does, and does not. It re-derives the flags from title+abstract with the item's own
classifier (`affective_pain_search.classify` / `classify_subject`), so it does not trust the stored
booleans — an artefact that prints a number its script no longer produces is the failure this
repository has already paid for. It cannot re-run the PubMed query (tests and this script run
offline); it works on the stored census. The *hand* classification — is the reported outcome actually
a brain or autonomic measure, and in which population — is NOT computed here. That is read by hand
into §8 of the map; this script emits the record list and the counts that §8 must agree with.

Usage:
  python3 scripts/affective_pain_biomarker_only_classify.py            # human-readable table
  python3 scripts/affective_pain_biomarker_only_classify.py --json     # the counts §8 must match
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import affective_pain_search as aps  # noqa: E402

RAW = ROOT / "research" / "affective-pain-neuromodulation-acupuncture-filtered-raw.json"


def _flags(rec):
    """Re-derive the item's flags from title+abstract; do not trust the stored booleans."""
    f = aps.classify(rec)
    f.update(aps.classify_subject(rec))
    return f


def select(record):
    """Return the human-primary, biomarker-only records, and the counts they sit inside."""
    rows = []
    n_human = n_both = 0
    for r in record["records"]:
        f = _flags(r)
        if not f["is_human_primary"]:
            continue
        n_human += 1
        if f["both_affective_and_biomarker"]:
            n_both += 1
        elif f["neural_or_autonomic_biomarker"]:
            rows.append((r, f))
    rows.sort(key=lambda rf: (-int(rf[0]["year"]), rf[0]["pmid"]))
    return rows, n_human, n_both


def summary(record):
    rows, n_human, n_both = select(record)
    return {
        "n_human_primary": n_human,
        "n_human_primary_both": n_both,
        "n_biomarker_only": len(rows),
        "pmids": [r["pmid"] for r, _ in rows],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="emit the summary as JSON")
    args = ap.parse_args()

    record = json.loads(RAW.read_text())
    if args.json:
        print(json.dumps(summary(record), indent=2))
        return

    rows, n_human, n_both = select(record)
    print(f"filtered acupuncture arm: {len(record['records'])} records")
    print(f"  human primary:            {n_human}")
    print(f"  human primary, both flags: {n_both}")
    print(f"  human primary, biomarker only: {len(rows)}  <- the records §8 classifies by hand")
    print()
    for r, f in rows:
        bio = f["biomarker"]["term"] if f["biomarker"] else "?"
        print(f"  {r['pmid']}  {r['year']}  {r['journal']}")
        print(f"      {r['title']}")
        print(f"      biomarker term: {bio}   types: {r['publication_types']}")
        print()


if __name__ == "__main__":
    main()
