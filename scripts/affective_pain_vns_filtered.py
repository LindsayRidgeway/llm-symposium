#!/usr/bin/env python3
"""Filtered vagus-nerve-stimulation arm for agenda item 32 (affective pain neuromodulation).

Written 2026-10-10 (Desi, clock wake). This is step 3 of the item's own next action, set out
in `research/affective-pain-neuromodulation-evidence-map.md` §7:

    "(3) The same *filtered* design against a second pain population -- wake-takeable next,
     over PubMed, if the affect-blindness generalises beyond acupuncture."

Why the VNS arm is the right 'second population'. Item 32 asks whether acupuncture AND
vagus-nerve stimulation improve the *affective* burden of chronic pain through a shared
pathway (§1 of the map). The filtered acupuncture arm (§7-§8) found that the corpus measures
the *brain* and the *pain* but is blind to the *mood*. The question that finding leaves open
is whether that blindness is a property of acupuncture research or of pain-neuromodulation
research in general. The item's own second modality is the clean test: if the VNS arm is also
affect-blind, the blindness is not an acupuncture artefact; if VNS studies *do* carry affective
outcomes, the two arms differ on the exact axis the item cares about.

WHAT THIS IS NOT. The same keyword screen as the other arms, not a reading. A term in an
abstract is not an outcome; every flag stores the sentence that set it, and the human-primary
records that set both flags are hand-read before any claim rests on them. It reuses the shared
classifier in `affective_pain_search.py` so the three arms are countable against each other.

Deliberate differences from `affective_pain_search.py` (the first, relevance-sliced arm) and
from `affective_pain_acupuncture_filtered.py`, both stated in the map:
  * it is a census of a *filtered* query, so partial coverage of the arm is bounded and
    reported rather than silent;
  * it does NOT reuse either earlier arm's records; it fetches its own, so a record's flags
    here are reproducible from this file alone.

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

# The same measurement filter step 2 of §6 named, applied to the VNS arm of the item. Widened
# only to synonyms of the same measurement families, so no door is closed by a missing spelling;
# nothing that is not a brain/autonomic measurement was added.
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
            except Exception:  # transient upstream; retry, then fail loudly
                if attempt == 2:
                    raise
                print(f"  efetch retry {attempt + 1} for chunk {i}", file=sys.stderr)
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
        "source": "PubMed E-utilities (esearch + efetch), filtered VNS arm",
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
