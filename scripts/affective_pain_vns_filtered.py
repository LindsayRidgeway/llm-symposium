#!/usr/bin/env python3
"""Filtered VNS arm for agenda item 32 (affective pain neuromodulation).

Written 2026-10-09 (Desi, clock wake). This is step 3 of the item's own next action, set
out in `research/affective-pain-neuromodulation-evidence-map.md` §6/§7:

    "(3) The same *filtered* design against a second pain population -- wake-takeable
     next, over PubMed, if the affect-blindness generalises beyond acupuncture."

Why this script exists. §7 replaced the acupuncture arm's top-80 relevance slice with a
*filtered* census -- acupuncture AND (a measurement filter naming brain/autonomic
measures) AND the pain block AND humans[MeSH Terms] -- and hand-read it. Its finding, made
sharper by §8, is that the acupuncture corpus in a pain population measures the **brain
and the pain, but not the mood**: of the 16 human-primary records that set the biomarker
flag only, 15 name no affect term at all. The obvious next question, and the one the item
asks, is whether that blind spot is a property of *acupuncture* or a property of *how this
literature measures pain*.

The sharpest available test is the symmetry the item itself proposes. Item 32's whole
premise is that acupuncture and VNS might relieve the affective burden of chronic pain
"through a shared brainstem-limbic pathway". If the affect-blindness is shared too, it is a
property of the design of these trials, not of needling; if VNS trials measure mood and
acupuncture trials do not, then the omission is specific to the acupuncture arm and the
item's asymmetry claim gains a measurement component.

WHAT THIS IS. The *same filtered design*, applied to the item's own second arm. The
measurement filter is imported verbatim from `affective_pain_acupuncture_filtered` (see
MEASUREMENT below), the pain block and the classifier are the first arm's own, and the only
thing changed is the intervention block -- acupuncture -> VNS. That is deliberate: the two
arms have to be countable against each other, and they are only countable if every
component but the intervention is identical. It is a census of a *filtered* query, not a
reading: a term in an abstract is not an outcome, every flag stores the sentence that set
it, and the human-primary records that set both flags are hand-read in the map (§9) before
any claim rests on them.

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
import affective_pain_acupuncture_filtered as apf  # noqa: E402

RAW = ROOT / "research" / "affective-pain-neuromodulation-vns-filtered-raw.json"

ARM = "vns_filtered"

# The *same* filter §7 ran, imported rather than retyped so the two arms cannot drift: if
# the measurement filter is ever corrected, both arms move together, and a reader of one
# arm's census is reading the other's definition of "names a brain or autonomic measure".
MEASUREMENT = apf.MEASUREMENT

# The item's own second arm (aps.ARMS['vns']) AND that filter AND the same pain block AND
# the same human restriction. Only the intervention block differs from §7's query.
QUERY = f"{aps.ARMS['vns']} AND {MEASUREMENT} AND {aps.PAIN} AND humans[MeSH Terms]"

# A census needs a fetch ceiling as a safety valve, not as a plan. If the filtered query
# ever outgrows this, the run records `censored: true` and the map must say so.
FETCH_LIMIT = apf.FETCH_LIMIT


def build(snapshot_end):
    res = aps.esearch(QUERY, retmax=FETCH_LIMIT, date_from="2015-01-01", date_to=snapshot_end)
    pmids = res["pmids"]

    recs = apf.fetch_all(pmids)
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
    hp_biomark_only = sorted(r["pmid"] for r in record["records"]
                             if r["is_human_primary"] and r["neural_or_autonomic_biomarker"]
                             and not r["affective_outcome"])
    print(f"  human-primary biomarker-only : {len(hp_biomark_only)} -> {hp_biomark_only}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
