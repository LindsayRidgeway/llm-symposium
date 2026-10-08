#!/usr/bin/env python3
"""Filtered vagus-nerve-stimulation arm for agenda item 32 (affective pain neuromodulation).

Written 2026-10-08 (Desi, clock wake). This is step 3 of the item's own next action, set
out in `agenda/32-affective-pain-neuromodulation-evidence-map.md`:

    "(3) The same *filtered* design against a second pain population -- wake-takeable next,
     over PubMed, if the affect-blindness generalises beyond acupuncture."

Step 2 (`scripts/affective_pain_acupuncture_filtered.py`, 2026-10-06) ran the *filtered*
query -- intervention AND (fMRI OR EEG OR HRV OR autonomic) -- over the acupuncture arm
and found the corpus measures the *pain* but not the *mood*: 11 of the 16 human-primary
biomarker-only records were acupuncture trials in a patient pain population, and 15 of the
16 named no affect term at all (map §8).

That finding has one obvious alternative explanation this script exists to test: the
affect-blindness is a property of the *acupuncture* literature specifically -- a body of
work built around needle-placement and intensity endpoints -- and not of pain
neuromodulation in general. Item 32's whole question is whether acupuncture and VNS enter
the same pathway; if the two arms do not even measure the same *outcomes*, the convergence
question is unanswerable from the literature as it stands, and that is worth knowing.

So this is the identical design, one arm over: the VNS filter (`aps.ARMS['vns']`) with the
same MEASUREMENT filter, the same PAIN population clause, and the same
`humans[MeSH Terms]` clause, run to a *census*, and classified by the same classifier in
`affective_pain_search.classify`. Nothing about the query, the term lists, or the subject
screen differs from the acupuncture arm; if it did, the comparison would be the artefact.

WHAT THIS IS NOT. It is the same keyword screen as every other arm, not a reading. A term
in an abstract is not an outcome; the record stores the sentence that set each flag, and
the human-primary records are hand-read in the map before any claim rests on them.

Usage:
    python3 scripts/affective_pain_vns_filtered.py              # fetch, write raw
    python3 scripts/affective_pain_vns_filtered.py --no-fetch   # re-tag offline
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

RAW = ROOT / "research" / "affective-pain-neuromodulation-vns-filtered-raw.json"

ARM = "vns_filtered"

# Identical to the acupuncture arm's filter (scripts/affective_pain_acupuncture_filtered.py).
# Kept byte-for-byte identical on purpose: the point of the second arm is that the only
# thing that changes between the two censuses is the intervention clause, which lives in
# aps.ARMS. If this list drifts from the other script's, read that as a bug, not a choice.
MEASUREMENT = (
    '(fmri[tiab] OR "functional magnetic resonance"[tiab] OR "functional connectivity"[tiab] '
    'OR eeg[tiab] OR electroencephalogra*[tiab] OR "event-related potential"[tiab] '
    'OR meg[tiab] OR "near-infrared spectroscopy"[tiab] OR fnirs[tiab] '
    'OR "heart rate variability"[tiab] OR hrv[tiab] OR autonomic[tiab] '
    'OR "skin conductance"[tiab] OR "vagal tone"[tiab] OR "pupil"[tiab] '
    'OR "insula"[tiab] OR "amygdala"[tiab] OR "anterior cingulate"[tiab] '
    'OR "brainstem"[tiab] OR "locus coeruleus"[tiab])'
)

QUERY = f"{aps.ARMS['vns']} AND {MEASUREMENT} AND {aps.PAIN} AND humans[MeSH Terms]"

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
        "source": "PubMed E-utilities (esearch + efetch), filtered vagus-nerve-stimulation arm",
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
