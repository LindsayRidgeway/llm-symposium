#!/usr/bin/env python3
"""Filtered acupuncture arm for agenda item 32 (affective pain neuromodulation).

Written 2026-10-04 (Desi, clock wake). This is step 2 of the item's own next action, set
out in `research/affective-pain-neuromodulation-evidence-map.md` §6:

    "0 of 38 human-primary acupuncture hits set both flags in a top-80 relevance slice of
     791 matches. Before that becomes a claim, the arm needs a *filtered* search
     (acupuncture AND (fMRI OR EEG OR HRV OR autonomic)) rather than a relevance slice --
     which is a different script call, not a re-read of this one."

Why it matters. The first map's acupuncture numbers are a *floor*, not a census: PubMed
returned 791 matches and the script kept the top 80 by relevance, which is a slice chosen
by an algorithm the reader cannot inspect. The claim it supports -- that acupuncture
trials in pain do not measure affective and autonomic outcomes together -- could be an
artefact of the slice, because relevance ranking has no reason to surface measurement-rich
trials. This script replaces the slice with a query that *names* the measurements: the
only studies it can return are ones whose own title or abstract mentions a brain or
autonomic measure, so the count is a census of the relevant sub-literature, not a sample
of everything.

WHAT THIS IS NOT. It is the same keyword screen as the first arm, not a reading. A term in
an abstract is not an outcome; every flag stores the sentence that set it, and the
human-primary records that set both flags are hand-read in the evidence map before any
claim rests on them.

Deliberate differences from `affective_pain_search.py`, both stated in the map:
  * it is a census of a *filtered* query, so partial coverage of the arm is bounded and
    reported rather than silent;
  * it does NOT reuse the acupuncture slice's records; it fetches its own, so a record's
    flags here are reproducible from this file alone.

Usage:
    python3 scripts/affective_pain_acupuncture_filtered.py              # fetch, write raw
    python3 scripts/affective_pain_acupuncture_filtered.py --no-fetch   # re-tag offline
"""

import argparse
import json
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import affective_pain_search as aps  # noqa: E402

RAW = ROOT / "research" / "affective-pain-neuromodulation-acupuncture-filtered-raw.json"

ARM = "acupuncture_filtered"

# The filter step 2 of §6 names: acupuncture AND (fMRI OR EEG OR HRV OR autonomic).
# Widened only to synonyms of the same measurement families, so no door is closed by a
# missing spelling; nothing that is not a brain/autonomic measurement was added.
MEASUREMENT = (
    '(fmri[tiab] OR "functional magnetic resonance"[tiab] OR "functional connectivity"[tiab] '
    'OR eeg[tiab] OR electroencephalogra*[tiab] OR "event-related potential"[tiab] '
    'OR meg[tiab] OR "near-infrared spectroscopy"[tiab] OR fnirs[tiab] '
    'OR "heart rate variability"[tiab] OR hrv[tiab] OR autonomic[tiab] '
    'OR "skin conductance"[tiab] OR "vagal tone"[tiab] OR "pupil"[tiab] '
    'OR "insula"[tiab] OR "amygdala"[tiab] OR "anterior cingulate"[tiab] '
    'OR "brainstem"[tiab] OR "locus coeruleus"[tiab])'
)

QUERY = f"{aps.ARMS['acupuncture']} AND {MEASUREMENT} AND {aps.PAIN} AND humans[MeSH Terms]"

# A census needs a fetch ceiling as a safety valve, not as a plan. If the filtered query
# ever outgrows this, the run records `censored: true` and the map must say so.
FETCH_LIMIT = 2000
PAGE = 200


def fetch_all(pmids):
    out = []
    for i in range(0, len(pmids), PAGE):
        chunk = pmids[i:i + PAGE]
        for attempt in range(3):
            try:
                out.extend(aps.parse_records(aps.efetch(chunk)))
                break
            except Exception as exc:  # transient upstream; retry, then fail loudly
                if attempt == 2:
                    raise
                print(f"  efetch retry {attempt + 1} for chunk {i}: {exc}", file=sys.stderr)
                time.sleep(2 * (attempt + 1))
        time.sleep(0.4)
    return out


def build(snapshot_end):
    res = aps.esearch(QUERY, retmax=FETCH_LIMIT, date_from="2015-01-01", date_to=snapshot_end)
    pmids = res["pmids"]

    recs = fetch_all(pmids)
    for r in recs:
        r["arm"] = ARM
        r.update(aps.classify(r))
        r.update(aps.classify_subject(r))
        r["co_mention_sentence"] = aps.same_sentence_affective_and_biomarker(r)

    return {
        "generated": date.today().isoformat(),
        "source": "PubMed E-utilities (esearch + efetch), filtered acupuncture arm",
        "arms": {ARM: {
            "query": QUERY,
            "filter": MEASUREMENT,
            "total_matching": res["count"],
            "fetched": len(pmids),
            "censored": res["count"] > len(pmids),
            "pmids": pmids,
            "query_translation": res["query_translation"],
        }},
        "records": recs,
        "tallies": aps.tally(recs),
    }


def retag(record):
    record["records"] = [dict(r, **aps.classify(r), **aps.classify_subject(r))
                         for r in record["records"]]
    record["tallies"] = aps.tally(record["records"])
    return record


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-fetch", action="store_true", help="re-tag the stored record offline")
    ap.add_argument("--snapshot-end", default=date.today().isoformat(),
                    help="latest publication date included (YYYY-MM-DD)")
    args = ap.parse_args()

    record = retag(json.loads(RAW.read_text())) if args.no_fetch else build(args.snapshot_end)

    RAW.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_text(json.dumps(record, indent=1) + "\n")

    a = record["arms"][ARM]
    t = record["tallies"]
    print(f"wrote {RAW.relative_to(ROOT)}")
    print(f"  query: {a['total_matching']} matching, {a['fetched']} fetched"
          f"{'  (CENSORED)' if a['censored'] else '  (census)'}")
    print(f"  records            : {t['n_records']}")
    print(f"  review/protocol    : {t['n_review']}/{t['n_protocol']}")
    print(f"  animal-subject     : {t['n_animal_subject']}")
    print(f"  human primary      : {t['n_human_primary']}")
    print(f"  affective term     : {t['n_affective_outcome']}")
    print(f"  biomarker term     : {t['n_neural_or_autonomic_biomarker']}")
    print(f"  both               : {t['n_both_affective_and_biomarker']}")
    print(f"  neither            : {t['n_neither']}")
    hp_both = sorted(r["pmid"] for r in record["records"]
                     if r["is_human_primary"] and r["both_affective_and_biomarker"])
    print(f"  human-primary both : {len(hp_both)} -> {hp_both}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
